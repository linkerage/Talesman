"""
Talesman Command Parser — Unified Persistence + Gemini Integration
"""

import logging
import os

from gemini import enqueue_question
from character import (
    create_character,
    get_sheet,
    update_bio,
    update_thesis,
)
from utils import roll_dice
from config import ADMINS
from persistence import load_character, char_path
import game as _game
import gm_tools as _gm
import points as _pts


# ------------------------------------------------------------
# Command Implementations
# ------------------------------------------------------------

def cmd_help(bot, nick, target, args):
    lines = [
        "\x02Talesman D&D 5e\x02 — !newchar  !charsheet [nick]  !chardelete  !cancelchar",
        "\x02Gameplay:\x02  !dm <sub>  !session  !players  !roll <dice>  !ask <question>",
        "\x02Combat:\x02   !attack [target]  !skill <name>  !save <str|dex|con|int|wis|cha>",
        "\x02Gold/XP:\x02  !gold [nick]  !pay <nick> <n>  !cash  !xp [nick]  !hp [nick]",
        "\x02DM seat:\x02  !dm claim  start [title]  narrate <text>  award <nick> <n> [gp|xp]",
        "\x02Combat:\x02   !fight <monster>  (call again each round to continue)",
        "\x02Loot:\x02      !loot [nick]  !scavenge  (collect gold dropped on death)",
        "\x02Graveyard:\x02 !graveyard  !tombstone <nick>  !rez <nick> (admin/DM only)",
        "\x02420-pts:\x02   !pts [nick]  !ptsboard  !pts2gp [n]  !gp2pts [n]  !cash",
        "\x02MM/DMG:\x02   !monster <name>  !cr <cr>  !encounter <diff> <lvl>  !loot [cr]  !mitem [name]",
    ]
    for line in lines:
        bot.send_privmsg(target, line)


def cmd_create(bot, nick, target, args):
    if not args:
        bot.send_privmsg(target, f"{nick}: usage: !create <archetype>")
        return

    try:
        result = create_character(nick, args)
        bot.send_privmsg(target, f"{nick}: {result}")
    except Exception as e:
        logging.error(f"create_character error: {e}")
        bot.send_privmsg(target, f"{nick}: character creation failed.")


def cmd_sheet(bot, nick, target, args):
    try:
        sheet = get_sheet(nick)
        bot.send_privmsg(target, f"{nick}: {sheet}")
    except Exception as e:
        logging.error(f"get_sheet error: {e}")
        bot.send_privmsg(target, f"{nick}: no sheet available.")


def cmd_roll(bot, nick, target, args):
    if not args:
        bot.send_privmsg(target, f"{nick}: usage: !roll <dice>")
        return

    try:
        result = roll_dice(args)
        bot.send_privmsg(target, f"{nick}: {result}")
    except Exception as e:
        logging.error(f"roll_dice error: {e}")
        bot.send_privmsg(target, f"{nick}: invalid dice expression.")


def cmd_xp(bot, nick, target, args):
    _game.cmd_xp(bot, nick, target, args)


def cmd_item(bot, nick, target, args):
    _game.cmd_item(bot, nick, target, args)


def cmd_skill(bot, nick, target, args):
    _game.cmd_skill_check(bot, nick, target, args)


def cmd_bio(bot, nick, target, args):
    if not args:
        bot.send_privmsg(target, f"{nick}: usage: !bio <text>")
        return

    try:
        result = update_bio(nick, args)
        bot.send_privmsg(target, f"{nick}: {result}")
    except Exception as e:
        logging.error(f"update_bio error: {e}")
        bot.send_privmsg(target, f"{nick}: failed to update bio.")


def cmd_thesis(bot, nick, target, args):
    """
    Generates thesis using Gemini based on the character's bio.
    No args required.
    """
    try:
        result = update_thesis(nick)
        bot.send_privmsg(target, f"{nick}: {result}")
    except Exception as e:
        logging.error(f"update_thesis error: {e}")
        bot.send_privmsg(target, f"{nick}: failed to generate thesis.")


def cmd_ask(bot, nick, target, args):
    if not args:
        bot.send_privmsg(target, f"{nick}: usage: !ask <question>")
        return

    try:
        enqueue_question(bot, nick, target, args)
    except Exception as e:
        logging.error(f"enqueue_question error: {e}")
        bot.send_privmsg(target, f"{nick}: failed to enqueue question.")


def cmd_nickserv(bot, nick, target, args):
    status = "identified" if bot.nickserv_identified else "not identified"
    account = bot.nickserv_account or "unknown"
    last = bot.nickserv_last_event or "none"

    bot.send_privmsg(target,
        f"{nick}: NickServ status: {status}\n"
        f"{nick}: Account: {account}\n"
        f"{nick}: Last event: {last}"
    )


# ------------------------------------------------------------
# D&D 5e Character Commands
# ------------------------------------------------------------

def cmd_newchar(bot, nick, target, args):
    """Start D&D 5e character creation wizard via PM."""
    from charwizard import start_session, is_active, cancel_session as _cancel
    from graveyard import is_dead

    # Only one living character per nick — must die or !chardelete first
    char = load_character(nick)
    if char and char.get("system") == "dnd5e" and not is_dead(nick) and not char.get("dead"):
        bot.send_privmsg(nick,
            f"\x02You already have a living character: {char['name']}.\x02  "
            "Your character must die in battle or be deleted with "
            "\x02!chardelete\x02 before you can create a new one.")
        if target.startswith("#"):
            bot.send_privmsg(target,
                f"{nick}: one character at a time — "
                f"{char['name']} is still alive.")
        return

    if is_active(nick):
        _cancel(nick)
        bot.send_privmsg(nick, "Previous character creation cancelled. Starting fresh.")

    # If previous character is dead, note they can start over
    if char and char.get("system") == "dnd5e" and (is_dead(nick) or char.get("dead")):
        bot.send_privmsg(nick,
            f"Your previous character \x02{char['name']}\x02 has fallen. "
            "Creating your next adventurer…")

    start_session(bot, nick)

    if target.startswith("#"):
        bot.send_privmsg(target, f"{nick}: D&D 5e character creation started — check your PMs!")


def cmd_cancelchar(bot, nick, target, args):
    """Cancel in-progress character creation."""
    from charwizard import cancel_session

    if cancel_session(nick):
        bot.send_privmsg(nick, "Character creation cancelled.")
        if target.startswith("#"):
            bot.send_privmsg(target, f"{nick}: character creation cancelled.")
    else:
        bot.send_privmsg(nick, "No active character creation session to cancel.")


def cmd_charsheet(bot, nick, target, args):
    """Display a D&D 5e character sheet via PM."""
    lookup = args.strip().split()[0] if args.strip() else nick
    char = load_character(lookup)

    if not char:
        bot.send_privmsg(target, f"{nick}: No character found for {lookup}. Use !newchar to create one.")
        return

    if char.get("system") != "dnd5e":
        bot.send_privmsg(target,
            f"{nick}: {lookup} has a legacy-style character. Use !sheet for that.")
        return

    ab = char["abilities"]
    mo = char["modifiers"]
    sv = char["saving_throws"]
    sb = char.get("skill_bonuses", {})
    profs = char.get("skill_proficiencies", [])

    lines = [
        f"\x02=== {char['name']}'s D&D 5e Sheet ===\x02",
        f"Race: {char['race']}  |  Class: {char['class']} Lv.{char['level']}  |  "
        f"BG: {char['background']}  |  Align: {char['alignment']}",
        f"HP: {char['hp_current']}/{char['hp_max']}  |  AC: {char['ac']} (unarmored)  |  "
        f"Speed: {char['speed']} ft  |  Initiative: {char['initiative']:+d}  |  "
        f"Hit Die: {char['hit_die']}",
        f"Prof Bonus: +{char['proficiency_bonus']}  |  Passive Perception: {char['passive_perception']}  |  "
        f"Size: {char.get('size', 'Medium')}",
        "---",
        f"STR {ab['str']} ({mo['str']:+d})  DEX {ab['dex']} ({mo['dex']:+d})  "
        f"CON {ab['con']} ({mo['con']:+d})  INT {ab['int']} ({mo['int']:+d})  "
        f"WIS {ab['wis']} ({mo['wis']:+d})  CHA {ab['cha']} ({mo['cha']:+d})",
        f"Saves: STR {sv['str']:+d}  DEX {sv['dex']:+d}  CON {sv['con']:+d}  "
        f"INT {sv['int']:+d}  WIS {sv['wis']:+d}  CHA {sv['cha']:+d}",
        "---",
    ]

    # Proficient skills with their bonuses
    if profs:
        prof_display = ", ".join(
            f"{s} {sb[s]:+d}" for s in profs if s in sb
        )
        lines.append(f"Skill Profs: {prof_display}")
    else:
        lines.append("Skill Profs: None")

    lines.append("---")
    lines.append(f"Languages: {', '.join(char.get('languages', ['Common']))}")

    traits = char.get("racial_traits", [])
    if traits:
        lines.append(f"Racial Traits: {', '.join(traits)}")

    features = char.get("level1_features", [])
    if features:
        lines.append(f"Class Features: {', '.join(features)}")

    if char.get("dragonborn_ancestry"):
        lines.append(f"Draconic Ancestry: {char['dragonborn_ancestry']}")

    lines.append("---")
    lines.append(f"Armor: {char.get('armor_proficiencies', '-')}")
    lines.append(f"Weapons: {char.get('weapon_proficiencies', '-')}")
    lines.append(f"Equipment: {char.get('starting_equipment', '-')}")
    lines.append(f"BG Equipment: {char.get('background_equipment', '-')}")
    lines.append(f"BG Feature: {char.get('background_feature', '-')}")

    if char.get("spellcaster"):
        sc = char.get("spellcasting_ability", "").upper()
        lines.append(f"Spellcasting: {sc}  |  Save DC: {char.get('spell_save_dc', '?')}  |  "
                     f"Atk Bonus: {char.get('spell_attack_bonus', 0):+d}")

    lines.append("---")
    if char.get("personality"):
        lines.append(f"Personality: {char['personality']}")
    if char.get("ideal"):
        lines.append(f"Ideal: {char['ideal']}")
    if char.get("bond"):
        lines.append(f"Bond: {char['bond']}")
    if char.get("flaw"):
        lines.append(f"Flaw: {char['flaw']}")

    # Always send via PM (sheet is too long for channel)
    for line in lines:
        bot.send_privmsg(nick, line)

    if target.startswith("#"):
        bot.send_privmsg(target, f"{nick}: character sheet sent via PM.")


def cmd_chardelete(bot, nick, target, args):
    """Delete the user's D&D 5e character."""
    char = load_character(nick)
    if not char or char.get("system") != "dnd5e":
        bot.send_privmsg(target, f"{nick}: no 5e character found to delete.")
        return

    path = char_path(nick)
    try:
        os.remove(path)
        bot.send_privmsg(target, f"{nick}: character \x02{char['name']}\x02 deleted.")
    except Exception as e:
        logging.error(f"chardelete error for {nick}: {e}")
        bot.send_privmsg(target, f"{nick}: failed to delete character: {e}")


# ------------------------------------------------------------
# Dispatch Table
# ------------------------------------------------------------

COMMANDS = {
    "!help":       cmd_help,
    "!create":     cmd_create,
    "!sheet":      cmd_sheet,
    "!roll":       cmd_roll,
    "!xp":         cmd_xp,
    "!item":       cmd_item,
    "!skill":      cmd_skill,
    "!bio":        cmd_bio,
    "!thesis":     cmd_thesis,
    "!ask":        cmd_ask,
    "!nickserv":   cmd_nickserv,
    # D&D 5e — character creation
    "!newchar":    cmd_newchar,
    "!cancelchar": cmd_cancelchar,
    "!charsheet":  cmd_charsheet,
    "!chardelete": cmd_chardelete,
    # D&D 5e — gameplay (game.py)
    "!dm":         lambda bot, nick, target, args: _game.cmd_dm(bot, nick, target, args),
    "!gold":       lambda bot, nick, target, args: _game.cmd_gold(bot, nick, target, args),
    "!gp":         lambda bot, nick, target, args: _game.cmd_gold(bot, nick, target, args),
    "!pay":        lambda bot, nick, target, args: _game.cmd_pay(bot, nick, target, args),
    # !cash is handled by points.py (chr0n ledger) — removed from here
    "!hp":         lambda bot, nick, target, args: _game.cmd_hp(bot, nick, target, args),
    "!save":       lambda bot, nick, target, args: _game.cmd_save_roll(bot, nick, target, args),
    "!attack":     lambda bot, nick, target, args: _game.cmd_attack(bot, nick, target, args),
    "!inventory":  lambda bot, nick, target, args: _game.cmd_inventory(bot, nick, target, args),
    "!session":    lambda bot, nick, target, args: _game.cmd_session(bot, nick, target, args),
    "!players":    lambda bot, nick, target, args: _game.cmd_players(bot, nick, target, args),
    # Combat + loot + graveyard
    "!fight":      lambda bot, nick, target, args: _game.cmd_fight(bot, nick, target, args),
    "!loot":       lambda bot, nick, target, args: _game.cmd_loot(bot, nick, target, args),
    "!scavenge":   lambda bot, nick, target, args: _game.cmd_scavenge(bot, nick, target, args),
    "!graveyard":  lambda bot, nick, target, args: _game.cmd_graveyard(bot, nick, target, args),
    "!tombstone":  lambda bot, nick, target, args: _game.cmd_tombstone(bot, nick, target, args),
    "!rez":        lambda bot, nick, target, args: _game.cmd_rez(bot, nick, target, args),
    # 420-point economy (chr0n↔Talesman exchange)
    "!pts":       lambda bot, nick, target, args: _pts.cmd_pts(bot, nick, target, args),
    "!ptsboard":  lambda bot, nick, target, args: _pts.cmd_ptsboard(bot, nick, target, args),
    "!pts2gp":    lambda bot, nick, target, args: _pts.cmd_pts2gp(bot, nick, target, args),
    "!gp2pts":    lambda bot, nick, target, args: _pts.cmd_gp2pts(bot, nick, target, args),
    "!cash":      lambda bot, nick, target, args: _pts.cmd_cash(bot, nick, target, args),
    # Monster Manual + DMG reference
    "!monster":    lambda bot, nick, target, args: _gm.cmd_monster(bot, nick, target, args),
    "!cr":         lambda bot, nick, target, args: _gm.cmd_cr(bot, nick, target, args),
    "!encounter":  lambda bot, nick, target, args: _gm.cmd_encounter(bot, nick, target, args),
    "!loot":       lambda bot, nick, target, args: _gm.cmd_loot(bot, nick, target, args),
    "!mitem":      lambda bot, nick, target, args: _gm.cmd_mitem(bot, nick, target, args),
}


# ------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------

def handle_command(bot, nick, target, message):
    """
    Main command handler.
    Only responds to known commands.
    Unknown !commands are ignored.
    """

    if not message.startswith("!"):
        return

    parts = message.split(" ", 1)
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    handler = COMMANDS.get(command)
    if handler is None:
        return

    try:
        handler(bot, nick, target, args)
    except Exception as e:
        logging.error(f"Command error in {command}: {e}")
        bot.send_privmsg(target, f"{nick}: command error.")

