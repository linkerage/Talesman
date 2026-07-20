#!/usr/bin/env python3
"""
D&D 5e Gameplay Engine for Talesman IRC Bot

Works identically in all three channels: #gentoo-weed  ##?  #jedi

Provides:
  - Channel operator tracking (from IRC MODE / NAMES)
  - DM session management per channel (anyone can claim; ops control)
  - XP awards and automatic 5e leveling
  - Gold (GP) system  — chr0n's 420 pts live here; 420 GP = gift card
  - HP management (DM deals damage / heals)
  - Item inventory (DM gives items)
  - Player rolls: skill checks, saving throws, attack rolls
  - Narration and scene-setting tools for the DM
"""

import os
import re
import time
import logging
import threading
import random
from typing import Dict, Set, Any, Optional, Tuple

from graveyard import (
    is_dead, bury_character, get_tombstone, list_graves,
    resurrect, _ts_str,
)
import loot as _loot_mod

from config import DATA_DIR, ADMINS
from persistence import (
    load_character, save_character,
    load_bank, save_bank, get_balance, set_balance,
    atomic_load, atomic_save, list_characters,
)
from dnd5e_data import (
    STAT_ORDER, STAT_NAMES, ALL_SKILLS, SKILL_ABILITY, CLASSES,
)
from utils import roll_dice

# ----------------------------------------------------------------
# Constants
# ----------------------------------------------------------------

# 5e XP thresholds — index = level - 1
XP_THRESHOLDS = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
    85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000,
]

# Average HP gained per level for each hit die
HD_AVERAGE = {6: 4, 8: 5, 10: 6, 12: 7}

# Gift card redemption
PRIZE_THRESHOLD = 420
PRIZE_LABEL     = "a $100 Visa gift card"
PRIZE_CONTACT   = "n01d"

SESSIONS_FILE  = os.path.join(DATA_DIR, "sessions.json")
DM_CONFIG_FILE = os.path.join(DATA_DIR, "dm_config.json")

# Per-player encounter tracking: {nick_lower: {monster_key, monster_hp, monster_max}}
_enc_lock   = threading.Lock()
_encounters: Dict[str, Dict[str, Any]] = {}

# ----------------------------------------------------------------
# Thread-safe in-memory state
# ----------------------------------------------------------------

_lock = threading.Lock()

# {channel: set(nick_lower)} — nicks with +o in each channel
_channel_ops: Dict[str, Set[str]] = {}

# {channel: session_dict}  — active DM session per channel
_sessions: Dict[str, Dict[str, Any]] = {}

# {channel: {locked: bool, locked_to: str|None}}
_dm_config: Dict[str, Dict[str, Any]] = {}


def _load_persistent():
    global _sessions, _dm_config
    _sessions  = atomic_load(SESSIONS_FILE,  {})
    _dm_config = atomic_load(DM_CONFIG_FILE, {})


_load_persistent()


# ----------------------------------------------------------------
# Ops tracking — called from main.py on NAMES/MODE events
# ----------------------------------------------------------------

def update_op(channel: str, nick: str, granted: bool):
    """Grant or revoke +o for nick in channel."""
    with _lock:
        ops = _channel_ops.setdefault(channel.lower(), set())
        (ops.add if granted else ops.discard)(nick.lower())


def set_names(channel: str, names_raw: str):
    """
    Parse a 353 NAMES payload and rebuild the ops set for a channel.
    Nicks prefixed with @, ~, & or % are treated as ops.
    """
    ops: Set[str] = set()
    for token in names_raw.split():
        t = token.lstrip()
        if t and t[0] in "@~&%":
            ops.add(t[1:].lower())
    with _lock:
        _channel_ops[channel.lower()] = ops


def remove_nick(channel: str, nick: str):
    """Remove a nick from ops tracking on PART/QUIT."""
    with _lock:
        _channel_ops.get(channel.lower(), set()).discard(nick.lower())


def is_op(channel: str, nick: str) -> bool:
    """True if nick is a channel op OR is in ADMINS."""
    with _lock:
        return (nick.lower() in ADMINS or
                nick.lower() in _channel_ops.get(channel.lower(), set()))


# ----------------------------------------------------------------
# Session helpers
# ----------------------------------------------------------------

def _get_session(ch: str) -> Dict[str, Any]:
    with _lock:
        return dict(_sessions.get(ch, {}))


def _put_session(ch: str, data: Dict[str, Any]):
    with _lock:
        _sessions[ch] = data
        snapshot = dict(_sessions)
    atomic_save(SESSIONS_FILE, snapshot)


def _del_session(ch: str):
    with _lock:
        _sessions.pop(ch, None)
        snapshot = dict(_sessions)
    atomic_save(SESSIONS_FILE, snapshot)


def _get_dm_cfg(ch: str) -> Dict[str, Any]:
    with _lock:
        return dict(_dm_config.get(ch, {"locked": False, "locked_to": None}))


def _put_dm_cfg(ch: str, data: Dict[str, Any]):
    with _lock:
        _dm_config[ch] = data
        snapshot = dict(_dm_config)
    atomic_save(DM_CONFIG_FILE, snapshot)


def _is_session_dm(ch: str, nick: str) -> bool:
    with _lock:
        return _sessions.get(ch, {}).get("dm", "").lower() == nick.lower()


# ----------------------------------------------------------------
# XP / levelling helpers
# ----------------------------------------------------------------

def xp_to_level(xp: int) -> int:
    for i in range(len(XP_THRESHOLDS) - 1, -1, -1):
        if xp >= XP_THRESHOLDS[i]:
            return i + 1
    return 1


def xp_to_next_level(xp: int) -> int:
    lv = xp_to_level(xp)
    return 0 if lv >= 20 else XP_THRESHOLDS[lv] - xp


def prof_for_level(level: int) -> int:
    return 2 + (level - 1) // 4


def _do_level_up(char: dict) -> Optional[str]:
    """Apply level-up(s) if XP threshold crossed. Returns announcement or None."""
    xp = char.get("xp", 0)
    old_lv  = char.get("level", 1)
    new_lv  = xp_to_level(xp)
    if new_lv <= old_lv:
        return None

    char["level"] = new_lv

    old_prof = char.get("proficiency_bonus", 2)
    new_prof = prof_for_level(new_lv)
    char["proficiency_bonus"] = new_prof

    # HP per level: average hit die roll + CON modifier (min 1)
    cls_name = char.get("class", "")
    hd       = CLASSES.get(cls_name, {}).get("hit_die", 8)
    avg_roll = HD_AVERAGE.get(hd, hd // 2 + 1)
    con_mod  = char.get("modifiers", {}).get("con", 0)
    hp_gain  = max(1, avg_roll + con_mod)
    if char.get("race") == "Hill Dwarf":
        hp_gain += 1
    levels_gained    = new_lv - old_lv
    total_hp_gain    = hp_gain * levels_gained
    char["hp_max"]     = char.get("hp_max", 1) + total_hp_gain
    char["hp_current"] = char.get("hp_current", 1) + total_hp_gain

    # Update proficiency-dependent values if prof changed
    diff = new_prof - old_prof
    if diff:
        skill_profs = char.get("skill_proficiencies", [])
        sb = char.get("skill_bonuses", {})
        for sk in skill_profs:
            if sk in sb:
                sb[sk] += diff
        char["skill_bonuses"] = sb

        cls_saves = CLASSES.get(cls_name, {}).get("saving_throws", [])
        saves = char.get("saving_throws", {})
        for st in STAT_ORDER:
            if st in cls_saves:
                saves[st] = saves.get(st, 0) + diff
        char["saving_throws"] = saves

        sc = char.get("spellcasting_ability", "")
        if sc:
            char["spell_save_dc"]   = (char.get("spell_save_dc")   or 0) + diff
            char["spell_attack_bonus"] = (char.get("spell_attack_bonus") or 0) + diff

        if "Perception" in skill_profs:
            char["passive_perception"] = 10 + char["skill_bonuses"].get("Perception", 0)

    save_character(char)
    return (
        f"\x02LEVEL UP!\x02 {char['name']} is now level {new_lv}! "
        f"+{total_hp_gain} HP (max now {char['hp_max']})  "
        f"Proficiency: +{new_prof}"
    )


# ================================================================
# !dm — DM command dispatcher
# ================================================================

def cmd_dm(bot, nick, target, args):
    if not target.startswith("#"):
        bot.send_privmsg(nick, "DM commands must be used in a channel.")
        return

    parts = args.strip().split(None, 1)
    sub   = parts[0].lower() if parts else "status"
    rest  = parts[1] if len(parts) > 1 else ""

    _DM_SUBS = {
        "claim":   _dm_claim,
        "release": _dm_release,
        "start":   _dm_start,
        "end":     _dm_end,
        "narrate": _dm_narrate,
        "n":       _dm_narrate,       # shorthand
        "scene":   _dm_scene,
        "roll":    _dm_roll,
        "award":   _dm_award,
        "give":    _dm_give,
        "heal":    _dm_heal,
        "damage":  _dm_damage,
        "dmg":     _dm_damage,        # shorthand
        "ambush":  _dm_ambush,        # monster attacks a player
        "set":     _dm_set,
        "kick":    _dm_kick,
        "lock":    _dm_lock,
        "unlock":  _dm_unlock,
        "status":  _dm_status,
        "help":    _dm_help,
    }

    handler = _DM_SUBS.get(sub, _dm_help)
    handler(bot, nick, target, rest)


# ---- DM sub-handlers ----

def _dm_help(bot, nick, target, _):
    lines = [
        "\x02!dm\x02 — \x02claim\x02/\x02release\x02  \x02start\x02 [title]  \x02end\x02  \x02narrate\x02 <text>  \x02scene\x02 <text>",
        "\x02roll\x02 <dice>  \x02award\x02 <nick> <n> [gp|xp]  \x02give\x02 <nick> <item>",
        "\x02heal\x02 <nick> <n>  \x02damage\x02 <nick> <n>  \x02status\x02  (shorthand: !dm n, !dm dmg)",
        "\x02Ops only:\x02  !dm set <nick>  kick  lock <nick>  unlock",
    ]
    for line in lines:
        bot.send_privmsg(target, line)


def _dm_claim(bot, nick, target, _):
    sess = _get_session(target)
    cfg  = _get_dm_cfg(target)

    if sess.get("dm"):
        bot.send_privmsg(target,
            f"{nick}: \x02{sess['dm']}\x02 is already the DM. "
            "They can !dm release, or ops can !dm kick.")
        return

    if cfg.get("locked") and cfg.get("locked_to", "").lower() != nick.lower():
        bot.send_privmsg(target,
            f"{nick}: DM seat is locked to \x02{cfg['locked_to']}\x02.")
        return

    _put_session(target, {
        "dm": nick, "active": False, "title": "",
        "scene": "", "started_at": None, "channel": target,
    })
    bot.send_privmsg(target,
        f"\x02{nick}\x02 claimed the DM seat in {target}. "
        "Use \x02!dm start [title]\x02 to begin.")


def _dm_release(bot, nick, target, _):
    if not _is_session_dm(target, nick) and not is_op(target, nick):
        bot.send_privmsg(target, f"{nick}: you are not the DM.")
        return
    old_dm = _get_session(target).get("dm", nick)
    _del_session(target)
    bot.send_privmsg(target, f"\x02{old_dm}\x02 released the DM seat.")


def _dm_start(bot, nick, target, args):
    if not _is_session_dm(target, nick):
        bot.send_privmsg(target,
            f"{nick}: you need to !dm claim first.")
        return
    title = args.strip() or "Untitled Adventure"
    sess  = _get_session(target)
    sess.update({"active": True, "title": title, "started_at": time.time()})
    _put_session(target, sess)
    bot.send_privmsg(target,
        f"\x02\u2694 Session Started: {title} \u2694\x02  "
        f"DM: {nick}  |  !session for info  |  !players to see the party")


def _dm_end(bot, nick, target, _):
    if not _is_session_dm(target, nick) and not is_op(target, nick):
        bot.send_privmsg(target, f"{nick}: only the DM or ops can end the session.")
        return
    sess  = _get_session(target)
    title = sess.get("title", "the session")
    dur   = ""
    if sess.get("started_at"):
        mins = int((time.time() - sess["started_at"]) / 60)
        dur  = f"  ({mins} min)"
    bot.send_privmsg(target,
        f"\x02\u2694 Session Ended: {title}{dur} \u2694\x02")
    _del_session(target)


def _dm_narrate(bot, nick, target, args):
    if not _is_session_dm(target, nick):
        bot.send_privmsg(target, f"{nick}: only the DM can narrate.")
        return
    if not args.strip():
        bot.send_privmsg(target, f"{nick}: !dm narrate <text>")
        return
    bot.send_privmsg(target, f"\u2734 \x02{args.strip()}\x02 \u2734")


def _dm_scene(bot, nick, target, args):
    if not _is_session_dm(target, nick):
        bot.send_privmsg(target, f"{nick}: only the DM can set the scene.")
        return
    if not args.strip():
        bot.send_privmsg(target, f"{nick}: !dm scene <description>")
        return
    sess = _get_session(target)
    sess["scene"] = args.strip()
    _put_session(target, sess)
    bot.send_privmsg(target, f"\x02[ Scene ]\x02 {args.strip()}")


def _dm_roll(bot, nick, target, args):
    if not _is_session_dm(target, nick):
        bot.send_privmsg(target, f"{nick}: only the DM can make secret rolls.")
        return
    expr = args.strip()
    if not expr:
        bot.send_privmsg(target, f"{nick}: !dm roll <dice>  (e.g. !dm roll 1d20)")
        return
    result = roll_dice(expr)
    bot.send_privmsg(nick, f"\x02[Secret roll]\x02 {result}")
    bot.send_privmsg(target, "* The DM rolls in secret\u2026")


def _dm_award(bot, nick, target, args):
    if not _is_session_dm(target, nick):
        bot.send_privmsg(target, f"{nick}: only the DM can award things.")
        return
    parts = args.strip().split()
    if len(parts) < 2:
        bot.send_privmsg(target,
            f"{nick}: !dm award <nick> <amount> [gp|xp]  (default: gp)")
        return
    whom = parts[0]
    try:
        amount = abs(int(parts[1]))
    except ValueError:
        bot.send_privmsg(target, f"{nick}: amount must be a whole number.")
        return
    kind = parts[2].lower() if len(parts) > 2 else "gp"

    if kind == "xp":
        char = load_character(whom)
        if not char or char.get("system") != "dnd5e":
            bot.send_privmsg(target, f"{nick}: {whom} has no 5e character.")
            return
        char["xp"] = char.get("xp", 0) + amount
        save_character(char)
        bot.send_privmsg(target,
            f"\x02{whom}\x02 gains \x02{amount} XP\x02! "
            f"Total: {char['xp']} XP (Level {xp_to_level(char['xp'])})")
        msg = _do_level_up(char)
        if msg:
            bot.send_privmsg(target, f"\x02{whom}\x02: {msg}")
    else:
        bank    = load_bank()
        old_bal = get_balance(bank, whom)
        new_bal = old_bal + amount
        set_balance(bank, whom, new_bal)
        save_bank(bank)
        bot.send_privmsg(target,
            f"\x02{whom}\x02 receives \x02{amount} GP\x02 from the DM! "
            f"Balance: {new_bal} GP"
            + (f"  \x02(eligible to !cash!)\x02" if new_bal >= PRIZE_THRESHOLD else ""))


def _dm_give(bot, nick, target, args):
    if not _is_session_dm(target, nick):
        bot.send_privmsg(target, f"{nick}: only the DM can give items.")
        return
    parts = args.strip().split(None, 1)
    if len(parts) < 2:
        bot.send_privmsg(target, f"{nick}: !dm give <nick> <item name>")
        return
    whom, item = parts[0], parts[1].strip()
    char = load_character(whom)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: {whom} has no 5e character.")
        return
    inv = char.get("inventory", [])
    inv.append(item)
    char["inventory"] = inv
    save_character(char)
    bot.send_privmsg(target,
        f"\x02{whom}\x02 receives: \x02{item}\x02")


def _dm_heal(bot, nick, target, args):
    if not _is_session_dm(target, nick):
        bot.send_privmsg(target, f"{nick}: only the DM can heal.")
        return
    parts = args.strip().split()
    if len(parts) < 2:
        bot.send_privmsg(target, f"{nick}: !dm heal <nick> <amount>")
        return
    whom = parts[0]
    try:
        amount = abs(int(parts[1]))
    except ValueError:
        bot.send_privmsg(target, f"{nick}: amount must be a number.")
        return
    char = load_character(whom)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: {whom} has no 5e character.")
        return
    old_hp = char.get("hp_current", char.get("hp_max", 1))
    new_hp = min(old_hp + amount, char.get("hp_max", old_hp + amount))
    char["hp_current"] = new_hp
    save_character(char)
    bot.send_privmsg(target,
        f"\x02{whom}\x02 is healed for \x02{amount} HP\x02. "
        f"HP: {new_hp}/{char['hp_max']}")


def _dm_damage(bot, nick, target, args):
    if not _is_session_dm(target, nick):
        bot.send_privmsg(target, f"{nick}: only the DM can deal damage.")
        return
    parts = args.strip().split()
    if len(parts) < 2:
        bot.send_privmsg(target, f"{nick}: !dm damage <nick> <amount>")
        return
    whom = parts[0]
    try:
        amount = abs(int(parts[1]))
    except ValueError:
        bot.send_privmsg(target, f"{nick}: amount must be a number.")
        return
    char = load_character(whom)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: {whom} has no 5e character.")
        return
    _apply_damage_to_player(char, amount, "the DM", f"DM dealt {amount} damage", bot, target)


# ---- Ops-only DM management ----

def _dm_set(bot, nick, target, args):
    if not is_op(target, nick):
        bot.send_privmsg(target, f"{nick}: ops only.")
        return
    whom = args.strip().split()[0] if args.strip() else ""
    if not whom:
        bot.send_privmsg(target, f"{nick}: !dm set <nick>")
        return
    _put_session(target, {
        "dm": whom, "active": False, "title": "",
        "scene": "", "started_at": None, "channel": target,
    })
    bot.send_privmsg(target, f"\x02{whom}\x02 appointed as DM by {nick}.")


def _dm_kick(bot, nick, target, _):
    if not is_op(target, nick):
        bot.send_privmsg(target, f"{nick}: ops only.")
        return
    old_dm = _get_session(target).get("dm", "nobody")
    _del_session(target)
    bot.send_privmsg(target, f"DM \x02{old_dm}\x02 removed by {nick}.")


def _dm_lock(bot, nick, target, args):
    if not is_op(target, nick):
        bot.send_privmsg(target, f"{nick}: ops only.")
        return
    whom = args.strip().split()[0] if args.strip() else ""
    if not whom:
        bot.send_privmsg(target, f"{nick}: !dm lock <nick>")
        return
    _put_dm_cfg(target, {"locked": True, "locked_to": whom})
    bot.send_privmsg(target, f"DM seat locked to \x02{whom}\x02 by {nick}.")


def _dm_unlock(bot, nick, target, _):
    if not is_op(target, nick):
        bot.send_privmsg(target, f"{nick}: ops only.")
        return
    _put_dm_cfg(target, {"locked": False, "locked_to": None})
    bot.send_privmsg(target,
        f"DM seat unlocked by {nick}. Anyone may \x02!dm claim\x02.")


def _dm_status(bot, nick, target, _):
    sess = _get_session(target)
    cfg  = _get_dm_cfg(target)
    if not sess.get("dm"):
        lock_note = (f"  (locked to \x02{cfg['locked_to']}\x02)"
                     if cfg.get("locked") else "")
        bot.send_privmsg(target,
            f"No DM active. Anyone may \x02!dm claim\x02{lock_note}.")
        return
    dm      = sess["dm"]
    active  = "Session active" if sess.get("active") else "DM seated, session not started"
    title   = sess.get("title") or "—"
    scene   = sess.get("scene") or "No scene set"
    dur     = ""
    if sess.get("active") and sess.get("started_at"):
        mins = int((time.time() - sess["started_at"]) / 60)
        dur  = f"  [{mins} min]"
    bot.send_privmsg(target,
        f"DM: \x02{dm}\x02  |  {active}: \x02{title}\x02{dur}")
    bot.send_privmsg(target, f"Scene: {scene}")


# ================================================================
# Player Commands (exported to commands.py)
# ================================================================

def cmd_gold(bot, nick, target, args):
    """`!gold [nick]` — check GP balance."""
    whom = args.strip().split()[0] if args.strip() else nick
    bank = load_bank()
    bal  = get_balance(bank, whom)
    note = (f"  \x02({PRIZE_THRESHOLD}+ GP \u2014 eligible to !cash)\x02"
            if bal >= PRIZE_THRESHOLD else "")
    bot.send_privmsg(target, f"\x02{whom}\x02: {bal} GP{note}")


def cmd_pay(bot, nick, target, args):
    """`!pay <nick> <amount>` — send GP to another player."""
    parts = args.strip().split()
    if len(parts) < 2:
        bot.send_privmsg(target, f"{nick}: !pay <nick> <amount>")
        return
    whom = parts[0]
    try:
        amount = abs(int(parts[1]))
    except ValueError:
        bot.send_privmsg(target, f"{nick}: amount must be a number.")
        return
    if amount == 0:
        bot.send_privmsg(target, f"{nick}: amount must be > 0.")
        return
    if whom.lower() == nick.lower():
        bot.send_privmsg(target, f"{nick}: you can't pay yourself.")
        return
    bank      = load_bank()
    sender_gp = get_balance(bank, nick)
    if sender_gp < amount:
        bot.send_privmsg(target,
            f"{nick}: not enough GP ({sender_gp} GP, need {amount}).")
        return
    recv_gp = get_balance(bank, whom)
    set_balance(bank, nick,  sender_gp - amount)
    set_balance(bank, whom,  recv_gp   + amount)
    save_bank(bank)
    bot.send_privmsg(target,
        f"\x02{nick}\x02 \u2192 \x02{whom}\x02: {amount} GP  "
        f"({nick}: {sender_gp - amount} GP  |  {whom}: {recv_gp + amount} GP)")


def cmd_cash(bot, nick, target, args):
    """`!cash` — check gift card eligibility / redeem 420 GP."""
    bank = load_bank()
    bal  = get_balance(bank, nick)
    if bal < PRIZE_THRESHOLD:
        need = PRIZE_THRESHOLD - bal
        bot.send_privmsg(target,
            f"{nick}: you have {bal} GP. "
            f"You need \x02{need} more GP\x02 to redeem for {PRIZE_LABEL}.")
        return
    bot.send_privmsg(target,
        f"\x02{nick}\x02: you have {bal} GP — "
        f"enough to redeem for \x02{PRIZE_LABEL}\x02!")
    bot.send_privmsg(target,
        f"PM \x02{PRIZE_CONTACT}\x02 to arrange your redemption.")
    bot.send_privmsg(nick,
        f"You have {bal} GP and are eligible to cash in "
        f"{PRIZE_THRESHOLD} GP for {PRIZE_LABEL}. "
        f"Contact {PRIZE_CONTACT} on IRC to redeem!")


def cmd_xp(bot, nick, target, args):
    """`!xp [nick]` — show XP and level progress."""
    whom = args.strip().split()[0] if args.strip() else nick
    char = load_character(whom)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target,
            f"{nick}: no 5e character for \x02{whom}\x02. Use !newchar.")
        return
    xp   = char.get("xp", 0)
    lv   = xp_to_level(xp)
    name = char.get("name", whom)
    if lv >= 20:
        bot.send_privmsg(target,
            f"\x02{name}\x02: Level \x0220\x02 (MAX!) — {xp} XP")
    else:
        to_next = xp_to_next_level(xp)
        next_lv = lv + 1
        bot.send_privmsg(target,
            f"\x02{name}\x02: Level \x02{lv}\x02 — {xp} XP "
            f"({to_next} XP to level {next_lv}, needs {XP_THRESHOLDS[lv]} total)")


def cmd_hp(bot, nick, target, args):
    """`!hp [nick]` — show current HP."""
    whom = args.strip().split()[0] if args.strip() else nick
    char = load_character(whom)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: no 5e character for \x02{whom}\x02.")
        return
    hp_cur = char.get("hp_current", 0)
    hp_max = char.get("hp_max", 0)
    name   = char.get("name", whom)
    pct    = int(hp_cur / hp_max * 100) if hp_max else 0
    if hp_cur == 0:
        cond = "\x02UNCONSCIOUS\x02"
    elif pct <= 25:
        cond = "\x02BLOODIED\x02"
    elif pct <= 50:
        cond = "Wounded"
    else:
        cond = "Healthy"
    bot.send_privmsg(target,
        f"\x02{name}\x02: HP {hp_cur}/{hp_max} ({pct}%) — {cond}")


def cmd_skill_check(bot, nick, target, args):
    """`!skill <name>` — roll a skill check using your character sheet."""
    if not args.strip():
        bot.send_privmsg(target,
            f"{nick}: !skill <skill>  e.g. !skill perception")
        return
    query = args.strip()
    # Case-insensitive partial match
    matched = next(
        (s for s in ALL_SKILLS if s.lower() == query.lower()), None
    ) or next(
        (s for s in ALL_SKILLS if s.lower().startswith(query.lower())), None
    ) or next(
        (s for s in ALL_SKILLS if query.lower() in s.lower()), None
    )
    if not matched:
        bot.send_privmsg(target,
            f"{nick}: unknown skill. Options: {', '.join(ALL_SKILLS)}")
        return
    char = load_character(nick)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: no 5e character. Use !newchar.")
        return
    bonus   = char.get("skill_bonuses", {}).get(matched, 0)
    is_prof = matched in char.get("skill_proficiencies", [])
    d20     = random.randint(1, 20)
    total   = d20 + bonus
    nat     = (" \x02\u2605 NAT 20!\x02" if d20 == 20
               else " \x02(nat 1)\x02"   if d20 == 1 else "")
    prof_m  = " \x02[prof]\x02" if is_prof else ""
    bot.send_privmsg(target,
        f"\x02{char['name']}\x02 — {matched}{prof_m}: "
        f"d20({d20}) {bonus:+d} = \x02{total}\x02{nat}")


def cmd_save_roll(bot, nick, target, args):
    """`!save <ability>` — roll a saving throw."""
    if not args.strip():
        bot.send_privmsg(target,
            f"{nick}: !save <str|dex|con|int|wis|cha>")
        return
    raw = args.strip().lower()
    _full = {"strength": "str", "dexterity": "dex", "constitution": "con",
             "intelligence": "int", "wisdom": "wis", "charisma": "cha"}
    ability = _full.get(raw, raw[:3])
    if ability not in STAT_NAMES:
        bot.send_privmsg(target,
            f"{nick}: unknown ability. Use str/dex/con/int/wis/cha.")
        return
    char = load_character(nick)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: no 5e character. Use !newchar.")
        return
    bonus   = char.get("saving_throws", {}).get(ability, 0)
    cls_sv  = CLASSES.get(char.get("class", ""), {}).get("saving_throws", [])
    is_prof = ability in cls_sv
    d20     = random.randint(1, 20)
    total   = d20 + bonus
    nat     = (" \x02\u2605 NAT 20!\x02" if d20 == 20
               else " \x02(nat 1)\x02"   if d20 == 1 else "")
    prof_m  = " \x02[prof]\x02" if is_prof else ""
    bot.send_privmsg(target,
        f"\x02{char['name']}\x02 — {STAT_NAMES[ability]} save{prof_m}: "
        f"d20({d20}) {bonus:+d} = \x02{total}\x02{nat}")


def cmd_attack(bot, nick, target, args):
    """`!attack [target]` — roll an attack."""
    char = load_character(nick)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: no 5e character. Use !newchar.")
        return
    atk_target = args.strip() or "the enemy"
    primary    = CLASSES.get(char.get("class", ""), {}).get("primary_ability", "STR")
    mods       = char.get("modifiers", {})
    # Use highest of STR/DEX when class can use either
    if "STR" in primary and "DEX" not in primary:
        ability = "str"
    elif "DEX" in primary and "STR" not in primary:
        ability = "dex"
    else:
        ability = "dex" if mods.get("dex", 0) >= mods.get("str", 0) else "str"
    ab_mod = mods.get(ability, 0)
    prof   = char.get("proficiency_bonus", 2)
    d20    = random.randint(1, 20)
    total  = d20 + ab_mod + prof
    nat    = (" \x02\u2605 CRITICAL HIT!\x02" if d20 == 20
              else " \x02FUMBLE!\x02"          if d20 == 1 else "")
    bot.send_privmsg(target,
        f"\x02{char['name']}\x02 attacks \x02{atk_target}\x02: "
        f"d20({d20}) {ab_mod:+d} ({STAT_NAMES[ability]}) +{prof} (prof) "
        f"= \x02{total}\x02{nat}")


def cmd_inventory(bot, nick, target, args):
    """`!inventory [nick]` — show inventory."""
    whom = args.strip().split()[0] if args.strip() else nick
    char = load_character(whom)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: no 5e character for \x02{whom}\x02.")
        return
    name = char.get("name", whom)
    inv  = char.get("inventory", [])
    if not inv:
        bot.send_privmsg(target, f"\x02{name}\x02's inventory is empty.")
    else:
        bot.send_privmsg(target,
            f"\x02{name}\x02's inventory ({len(inv)} item{'s' if len(inv) != 1 else ''}): "
            f"{', '.join(inv)}")


def cmd_item(bot, nick, target, args):
    """`!item` or `!item drop <name>` — view or drop an inventory item."""
    parts = args.strip().split(None, 1)
    sub   = parts[0].lower() if parts else ""
    if sub == "drop" and len(parts) > 1:
        item_name = parts[1].strip()
        char = load_character(nick)
        if not char or char.get("system") != "dnd5e":
            bot.send_privmsg(target, f"{nick}: no 5e character.")
            return
        inv = char.get("inventory", [])
        for i, it in enumerate(inv):
            if it.lower() == item_name.lower():
                inv.pop(i)
                char["inventory"] = inv
                save_character(char)
                bot.send_privmsg(target, f"{nick}: dropped \x02{it}\x02.")
                return
        bot.send_privmsg(target, f"{nick}: '{item_name}' not in inventory.")
    else:
        cmd_inventory(bot, nick, target, args)


def cmd_session(bot, nick, target, args):
    """`!session` — show the current session status."""
    if not target.startswith("#"):
        bot.send_privmsg(nick, "Use !session in a channel.")
        return
    _dm_status(bot, nick, target, args)


# Maximum player rows shown directly in a channel before overflow goes to PM
_PLAYERS_CHANNEL_CAP = 4


def cmd_players(bot, nick, target, args):
    """`!players` — up to 4 rows in channel; any extras go to the requester's PM."""
    all_chars = list_characters()
    dnd_chars = {n: c for n, c in all_chars.items()
                 if c.get("system") == "dnd5e"}
    in_channel = target.startswith("#")
    reply_target = target if in_channel else nick

    if not dnd_chars:
        bot.send_privmsg(reply_target,
            "No D&D 5e characters yet. Use !newchar to create one!")
        return

    sess   = _get_session(target) if in_channel else {}
    dm_low = sess.get("dm", "").lower()
    bank   = load_bank()
    rows   = []
    for n, c in sorted(dnd_chars.items()):
        dm_tag = " \x02[DM]\x02" if n == dm_low else ""
        hp_cur = c.get("hp_current", 0)
        hp_max = c.get("hp_max",     0)
        gp     = get_balance(bank, n)
        rows.append(
            f"  \x02{c['name']}\x02 ({n}){dm_tag} — "
            f"{c.get('race','')} {c.get('class','')} Lv.{c.get('level',1)} — "
            f"HP {hp_cur}/{hp_max} — {gp} GP"
        )

    # When there is overflow we need one extra line for the notice,
    # so cap channel rows at 3 (header + 3 rows + notice = 5 total).
    # When there is no overflow: header + up to 4 rows = 5 max.
    has_overflow  = len(rows) > _PLAYERS_CHANNEL_CAP
    ch_cap        = _PLAYERS_CHANNEL_CAP - 1 if has_overflow else _PLAYERS_CHANNEL_CAP
    channel_rows  = rows[:ch_cap]
    overflow      = rows[ch_cap:]

    bot.send_privmsg(reply_target,
        f"\x02\u2694 Adventurers ({len(rows)}) \u2694\x02")
    for row in channel_rows:
        bot.send_privmsg(reply_target, row)

    if overflow and in_channel:
        bot.send_privmsg(reply_target,
            f"  …and {len(overflow)} more — full list in your PM.")
        bot.send_privmsg(nick,
            f"\x02\u2694 Full party list \u2694\x02")
        for row in rows:
            bot.send_privmsg(nick, row)


# ================================================================
# Combat Engine
# ================================================================

def _parse_monster_attack(attacks_str: str) -> Tuple[int, int, int, int]:
    """
    Extract (atk_bonus, num_dice, die_sides, dmg_mod) from the first
    attack entry in a monster's attacks string.
    e.g. "Bite +7 2d6+4 piercing" → (7, 2, 6, 4)
    Falls back to (3, 1, 6, 0) if no match.
    """
    m = re.search(r'\+(\d+)\s+(\d+)d(\d+)([+-]\d+)?', attacks_str)
    if m:
        return (int(m.group(1)), int(m.group(2)),
                int(m.group(3)), int(m.group(4)) if m.group(4) else 0)
    return 3, 1, 6, 0


def _roll_ndm(n: int, d: int) -> int:
    return sum(random.randint(1, d) for _ in range(max(1, n)))


def _hp_bar(current: int, maximum: int, width: int = 10) -> str:
    pct    = current / maximum if maximum else 0
    filled = round(pct * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def _apply_damage_to_player(
    char: dict, amount: int,
    killer: str, killing_blow: str,
    bot, channel: str
):
    """
    Shared damage handler used by !dm damage, !fight, and !dm ambush.
    Applies damage, saves character, announces result.
    If HP reaches 0: buries the character and announces death.
    """
    whom   = char["nick"]
    old_hp = char.get("hp_current", 0)
    new_hp = max(0, old_hp - amount)
    char["hp_current"] = new_hp
    save_character(char)

    if new_hp == 0:
        # Announce hit first
        bot.send_privmsg(channel,
            f"\x02{whom}\x02 takes \x02{amount} damage\x02! "
            f"\x02\u2620 FATAL BLOW! \u2620\x02")
        _kill_character(char, killer, killing_blow, bot, channel)
    else:
        bar = _hp_bar(new_hp, char.get("hp_max", new_hp))
        bot.send_privmsg(channel,
            f"\x02{whom}\x02 takes \x02{amount} damage\x02! "
            f"[{bar}] HP: {new_hp}/{char.get('hp_max', new_hp)}")


def _kill_character(char: dict, killer: str, killing_blow: str, bot, channel: str):
    """Bury a character, strip their gold as a loot pile, announce death."""
    nick = char["nick"]
    name = char.get("name", nick)

    # Clear any active encounter
    with _enc_lock:
        _encounters.pop(nick.lower(), None)

    # Strip gold from bank — it becomes a loot pile anyone can collect
    bank = load_bank()
    gold = get_balance(bank, nick)
    if gold > 0:
        set_balance(bank, nick, 0)
        save_bank(bank)
        _loot_mod.add_loot(channel, nick, name, gold)

    bury_character(char, killer, killing_blow)

    death_msg = (
        f"\x02\u26b0 {name} has fallen! \u26b0\x02  "
        f"Slain by \x02{killer}\x02. "
        f"Use \x02!tombstone {nick}\x02 to pay your respects."
    )
    if gold > 0:
        death_msg += (
            f"  \x02{gold} GP dropped on the battlefield\x02 — "
            f"use \x02!loot {nick}\x02 to collect it!"
        )
    bot.send_privmsg(channel, death_msg)


# ----------------------------------------------------------------
# !fight <monster>  — player-initiated one-round combat
# ----------------------------------------------------------------

def cmd_fight(bot, nick, target, args):
    """`!fight <monster>` — engage a monster in combat (one round per call)."""
    if not target.startswith("#"):
        bot.send_privmsg(nick, "Use !fight in a channel.")
        return

    query = args.strip()
    if not query:
        bot.send_privmsg(target,
            f"{nick}: !fight <monster>  e.g. !fight goblin  |  !fight vampire spawn")
        return

    # Check character exists and is alive
    char = load_character(nick)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: you need a 5e character first. Use !newchar.")
        return
    if is_dead(nick):
        bot.send_privmsg(target,
            f"{nick}: your character is dead. Use !tombstone {nick} to view their record.")
        return
    if char.get("hp_current", 0) <= 0:
        bot.send_privmsg(target,
            f"{nick}: {char['name']} is unconscious! You need healing first.")
        return

    # Find monster
    from monsters_data import find_monster, cr_str, CR_XP
    key, monster = find_monster(query)
    if key is None:
        if isinstance(monster, list):
            bot.send_privmsg(target,
                f"{nick}: ambiguous — did you mean: {', '.join(monster[:5])}?")
        else:
            bot.send_privmsg(target,
                f"{nick}: monster not found. Try !cr <n> for a list.")
        return

    m_name = monster["name"]
    nick_l = nick.lower()

    # Get or init per-player encounter
    with _enc_lock:
        enc = _encounters.get(nick_l)
        if enc is None or enc["monster_key"] != key:
            enc = {
                "monster_key": key,
                "monster_hp":  monster["hp"],
                "monster_max": monster["hp"],
            }
            _encounters[nick_l] = enc
        m_hp  = enc["monster_hp"]
        m_max = enc["monster_max"]

    # ── Player attacks monster ─────────────────────────────────────
    mods    = char.get("modifiers", {})
    prof    = char.get("proficiency_bonus", 2)
    primary = CLASSES.get(char.get("class", ""), {}).get("primary_ability", "STR")
    if "STR" in primary and "DEX" not in primary:
        atk_stat = "str"
    elif "DEX" in primary and "STR" not in primary:
        atk_stat = "dex"
    else:
        atk_stat = "dex" if mods.get("dex", 0) >= mods.get("str", 0) else "str"

    ab_mod      = mods.get(atk_stat, 0)
    p_roll      = random.randint(1, 20)
    p_total     = p_roll + ab_mod + prof
    p_crit      = p_roll == 20
    p_fumble    = p_roll == 1
    p_hit       = p_crit or (not p_fumble and p_total >= monster["ac"])

    p_dmg, p_dmg_str = 0, ""
    if p_hit:
        num_dice = 2 if p_crit else 1
        p_dmg    = max(0, _roll_ndm(num_dice, 8) + ab_mod)
        m_hp     = max(0, m_hp - p_dmg)
        with _enc_lock:
            _encounters[nick_l]["monster_hp"] = m_hp
        suffix   = " \x02(CRIT!)\x02" if p_crit else ""
        p_dmg_str = f"\x02{p_dmg} dmg\x02{suffix}"
    else:
        p_dmg_str = "\x02FUMBLE!\x02" if p_fumble else "MISS"

    nat_p = " \u2605 NAT 20!" if p_crit else (" nat 1" if p_fumble else "")
    bot.send_privmsg(target,
        f"\x02{char['name']}\x02 \u2694 \x02{m_name}\x02: "
        f"d20({p_roll}){ab_mod:+d}+{prof}prof = {p_total} "
        f"vs AC {monster['ac']} \u2192 {p_dmg_str}{nat_p}")

    # ── Monster slain? ─────────────────────────────────────────────
    if m_hp <= 0:
        with _enc_lock:
            _encounters.pop(nick_l, None)
        xp = CR_XP.get(monster["cr"], 0)
        bot.send_privmsg(target,
            f"\x02{m_name}\x02 is slain! \u2620  "
            f"{char['name']} gains \x02{xp} XP\x02!")
        char["xp"] = char.get("xp", 0) + xp
        save_character(char)
        lvl_msg = _do_level_up(char)
        if lvl_msg:
            bot.send_privmsg(target, f"\x02{nick}\x02: {lvl_msg}")
        return

    # Show monster HP bar
    bar_m = _hp_bar(m_hp, m_max)
    bot.send_privmsg(target,
        f"\x02{m_name}\x02: [{bar_m}] {m_hp}/{m_max} HP")

    # ── Monster counterattacks ─────────────────────────────────────
    atk_b, nd, ds, dm = _parse_monster_attack(monster.get("attacks", ""))
    m_roll   = random.randint(1, 20)
    m_total  = m_roll + atk_b
    m_crit   = m_roll == 20
    m_fumble = m_roll == 1
    m_hit    = m_crit or (not m_fumble and m_total >= char.get("ac", 10))

    m_dmg, m_dmg_str = 0, ""
    if m_hit:
        num_dice = nd * 2 if m_crit else nd
        m_dmg    = max(0, _roll_ndm(num_dice, ds) + dm)
        suffix   = " \x02(CRIT!)\x02" if m_crit else ""
        m_dmg_str = f"\x02{m_dmg} dmg\x02{suffix}"
    else:
        m_dmg_str = "\x02FUMBLE!\x02" if m_fumble else "MISS"

    nat_m = " \u2605 NAT 20!" if m_crit else (" nat 1" if m_fumble else "")
    bot.send_privmsg(target,
        f"\x02{m_name}\x02 strikes \x02{char['name']}\x02: "
        f"d20({m_roll}){atk_b:+d} = {m_total} "
        f"vs AC {char.get('ac',10)} \u2192 {m_dmg_str}{nat_m}")

    if m_hit and m_dmg > 0:
        _apply_damage_to_player(
            char, m_dmg,
            m_name, f"{m_name} attack for {m_dmg} damage",
            bot, target
        )


# ----------------------------------------------------------------
# !dm ambush <nick> <monster>  — DM-initiated monster attack
# ----------------------------------------------------------------

def _dm_ambush(bot, nick, target, args):
    """DM command: have a monster make an unprovoked attack on a player."""
    if not _is_session_dm(target, nick):
        bot.send_privmsg(target, f"{nick}: only the DM can ambush players.")
        return
    parts = args.strip().split(None, 1)
    if len(parts) < 2:
        bot.send_privmsg(target,
            f"{nick}: !dm ambush <player_nick> <monster>  e.g. !dm ambush n01d goblin")
        return
    whom, monster_query = parts[0], parts[1]

    char = load_character(whom)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: {whom} has no 5e character.")
        return
    if is_dead(whom):
        bot.send_privmsg(target, f"{nick}: {whom}'s character is already dead.")
        return

    from monsters_data import find_monster
    key, monster = find_monster(monster_query)
    if key is None:
        bot.send_privmsg(target, f"{nick}: monster not found.")
        return

    m_name = monster["name"]
    atk_b, nd, ds, dm = _parse_monster_attack(monster.get("attacks", ""))
    roll   = random.randint(1, 20)
    total  = roll + atk_b
    crit   = roll == 20
    fumble = roll == 1
    hit    = crit or (not fumble and total >= char.get("ac", 10))

    if hit:
        num_dice = nd * 2 if crit else nd
        dmg      = max(0, _roll_ndm(num_dice, ds) + dm)
        suffix   = " \x02(CRIT!)\x02" if crit else ""
        bot.send_privmsg(target,
            f"\x02[AMBUSH]\x02 \x02{m_name}\x02 attacks \x02{whom}\x02: "
            f"d20({roll}){atk_b:+d} = {total} vs AC {char.get('ac',10)} "
            f"\u2192 \x02{dmg} dmg\x02{suffix}!")
        _apply_damage_to_player(
            char, dmg,
            m_name, f"{m_name} ambush for {dmg} damage",
            bot, target
        )
    else:
        miss = "\x02FUMBLE!\x02" if fumble else "MISS"
        bot.send_privmsg(target,
            f"\x02[AMBUSH]\x02 \x02{m_name}\x02 attacks \x02{whom}\x02: "
            f"d20({roll}){atk_b:+d} = {total} vs AC {char.get('ac',10)} \u2192 {miss}")


# ================================================================
# Loot Commands
# ================================================================

def cmd_loot(bot, nick, target, args):
    """`!loot [dead_nick]` — list or collect loot piles in the channel."""
    if not target.startswith("#"):
        bot.send_privmsg(nick, "Use !loot in a channel.")
        return

    query = args.strip().split()[0] if args.strip() else ""

    if not query:
        # List all piles in channel
        piles = _loot_mod.list_loot(target)
        if not piles:
            bot.send_privmsg(target, "\x02No loot on the battlefield.\x02  Slay monsters or wait for someone to fall.")
            return
        bot.send_privmsg(target, f"\x02\U0001F4B0 Uncollected loot in {target}:\x02")
        for p in piles:
            bot.send_privmsg(target,
                f"  \u2620 \x02{p['name']}\x02 ({p['nick']}) dropped "
                f"\x02{p['gold']} GP\x02 — !loot {p['nick']} to collect")
        return

    # Collect a specific pile
    # You can't loot your own gold (you're dead)
    if query.lower() == nick.lower():
        bot.send_privmsg(target, f"{nick}: you can't loot your own corpse.")
        return

    # Collector must be alive with a character
    collector = load_character(nick)
    if not collector or collector.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: you need a 5e character to loot. Use !newchar.")
        return
    if is_dead(nick) or collector.get("dead"):
        bot.send_privmsg(target, f"{nick}: the dead cannot loot.")
        return

    pile = _loot_mod.collect_loot(target, query)
    if pile is None:
        bot.send_privmsg(target,
            f"{nick}: no loot pile found for \x02{query}\x02. "
            f"Use \x02!loot\x02 to see what's on the battlefield.")
        return

    # Add gold to collector's bank
    bank  = load_bank()
    old   = get_balance(bank, nick)
    new   = old + pile["gold"]
    set_balance(bank, nick, new)
    save_bank(bank)

    bot.send_privmsg(target,
        f"\U0001F4B0 \x02{nick}\x02 loots the fallen \x02{pile['name']}\x02 "
        f"and finds \x02{pile['gold']} GP\x02!  "
        f"(Balance: {new} GP)")


def cmd_scavenge(bot, nick, target, args):
    """`!scavenge` — collect ALL loot piles in the channel at once."""
    if not target.startswith("#"):
        bot.send_privmsg(nick, "Use !scavenge in a channel.")
        return

    collector = load_character(nick)
    if not collector or collector.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: you need a 5e character to scavenge. Use !newchar.")
        return
    if is_dead(nick) or collector.get("dead"):
        bot.send_privmsg(target, f"{nick}: the dead cannot scavenge.")
        return

    piles = _loot_mod.collect_all(target)
    if not piles:
        bot.send_privmsg(target, f"{nick}: nothing to scavenge here.")
        return

    total = sum(p["gold"] for p in piles)
    bank  = load_bank()
    old   = get_balance(bank, nick)
    new   = old + total
    set_balance(bank, nick, new)
    save_bank(bank)

    names = ", ".join(f"{p['name']} ({p['gold']} GP)" for p in piles)
    bot.send_privmsg(target,
        f"\U0001F4B0 \x02{nick}\x02 scavenges the battlefield: {names}  "
        f"Total: \x02{total} GP\x02  (Balance: {new} GP)")


# ================================================================
# Graveyard Commands
# ================================================================

_GRAVEYARD_CAP = 4   # max rows in channel before overflow


def cmd_graveyard(bot, nick, target, args):
    """`!graveyard` — list fallen adventurers."""
    graves = list_graves()   # newest first
    reply  = target if target.startswith("#") else nick

    if not graves:
        bot.send_privmsg(reply, "\x02\u26b0 The graveyard is empty.\x02  No one has fallen yet.")
        return

    bot.send_privmsg(reply,
        f"\x02\u26b0 The Graveyard ({len(graves)} fallen) \u26b0\x02")

    shown = 0
    for grave_nick, entry in graves:
        ts   = entry.get("tombstone", {})
        name = ts.get("name", grave_nick)
        race = ts.get("race", "")
        cls  = ts.get("class", "")
        lv   = ts.get("level", 1)
        killer = entry.get("killer", "unknown")
        bot.send_privmsg(reply,
            f"  \u2020 \x02{name}\x02 ({grave_nick}) — "
            f"{race} {cls} Lv.{lv} — Slain by \x02{killer}\x02")
        shown += 1
        if shown >= _GRAVEYARD_CAP and len(graves) > _GRAVEYARD_CAP:
            remaining = len(graves) - shown
            bot.send_privmsg(reply,
                f"  …and {remaining} more. Use \x02!tombstone <nick>\x02 for details.")
            break


def cmd_tombstone(bot, nick, target, args):
    """`!tombstone <nick>` — view a fallen character's full record."""
    query = args.strip().split()[0] if args.strip() else nick
    entry = get_tombstone(query)

    if not entry:
        # Maybe they're still alive
        char = load_character(query)
        if char and char.get("system") == "dnd5e":
            bot.send_privmsg(target,
                f"{nick}: {query}'s character is still alive! "
                f"HP: {char.get('hp_current',0)}/{char.get('hp_max',0)}")
        else:
            bot.send_privmsg(target,
                f"{nick}: no tombstone found for '{query}'.")
        return

    ts     = entry.get("tombstone", {})
    killer = entry.get("killer", "unknown")
    blow   = entry.get("killing_blow", "")
    died   = _ts_str(entry.get("died_at", 0))
    name   = ts.get("name", query)

    if target.startswith("#"):
        bot.send_privmsg(target,
            f"\x02\u26b0 {name} ({query})\x02 — Slain by \x02{killer}\x02 on {died}. "
            f"Full record sent via PM.")

    ab = ts.get("abilities", {})
    mo = ts.get("modifiers", {})
    lines = [
        f"\x02\u26b0 === TOMBSTONE: {name} === \u26b0\x02",
        f"  {ts.get('race','')} {ts.get('class','')} Lv.{ts.get('level',1)}  |  "
        f"Background: {ts.get('background','')}  |  {ts.get('alignment','')}",
        f"  \x02SLAIN BY:\x02 {killer}",
        f"  \x02Killing blow:\x02 {blow}",
        f"  \x02Date of death:\x02 {died}",
        "  ---",
        f"  Final HP: 0/{ts.get('hp_max',0)}  |  AC: {ts.get('ac',0)}  |  "
        f"Level: {ts.get('level',1)}  |  XP: {ts.get('xp',0)}",
        f"  STR {ab.get('str',0)}({mo.get('str',0):+d})  "
        f"DEX {ab.get('dex',0)}({mo.get('dex',0):+d})  "
        f"CON {ab.get('con',0)}({mo.get('con',0):+d})  "
        f"INT {ab.get('int',0)}({mo.get('int',0):+d})  "
        f"WIS {ab.get('wis',0)}({mo.get('wis',0):+d})  "
        f"CHA {ab.get('cha',0)}({mo.get('cha',0):+d})",
        f"  Skills: {', '.join(ts.get('skill_proficiencies', [])) or 'None'}",
    ]
    if ts.get("personality"):
        lines.append(f"  Last words: \"{ts['personality']}\"")
    if ts.get("inventory"):
        lines.append(f"  Buried with: {', '.join(ts['inventory'])}")

    for line in lines:
        bot.send_privmsg(nick, line)


def cmd_rez(bot, nick, target, args):
    """`!rez <nick>` — admin/DM only: resurrect a fallen character with 1 HP."""
    if nick.lower() not in ADMINS and not (target.startswith("#") and is_op(target, nick)):
        bot.send_privmsg(target, f"{nick}: only admins or ops can resurrect characters.")
        return
    whom = args.strip().split()[0] if args.strip() else ""
    if not whom:
        bot.send_privmsg(target, f"{nick}: !rez <nick>")
        return
    if resurrect(whom):
        char = load_character(whom)
        name = char.get("name", whom) if char else whom
        bot.send_privmsg(target,
            f"\x02{name}\x02 ({whom}) has been resurrected with 1 HP! "
            f"Death is not the end — for today.")
    else:
        bot.send_privmsg(target,
            f"{nick}: {whom} is not in the graveyard.")
