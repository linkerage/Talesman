#!/usr/bin/env python3
"""
Talesman GM Tools — Monster Manual & DMG Reference Commands

Commands:
  !monster <name>          — full stat block (channel summary + PM details)
  !cr <cr>                 — list monsters at a given challenge rating
  !encounter <diff> <lvl> [size] — XP budget for an encounter
  !loot [cr]               — roll random treasure for a given CR
  !mitem [name|rarity]     — look up or randomly generate a magic item
"""

from monsters_data import (
    MONSTERS, find_monster, monsters_at_cr, parse_cr, cr_str,
    CR_XP, mod_str,
)
from dmg_data import (
    MAGIC_ITEMS, find_item, random_item, items_by_rarity,
    roll_individual_treasure, roll_hoard, encounter_xp_budget,
    ITEM_RARITIES, cr_bucket,
)


# ----------------------------------------------------------------
# !monster <name>
# ----------------------------------------------------------------

def cmd_monster(bot, nick, target, args):
    """`!monster <name>` — channel summary + full PM stat block."""
    query = args.strip()
    if not query:
        bot.send_privmsg(target,
            f"{nick}: !monster <name>  e.g. !monster goblin  |  !monster ancient red dragon")
        return

    key, data = find_monster(query)
    if key is None:
        if isinstance(data, list):
            names = ", ".join(d.title() for d in data[:8])
            extra = f" (+{len(data)-8} more)" if len(data) > 8 else ""
            bot.send_privmsg(target, f"{nick}: ambiguous — did you mean: {names}{extra}?")
        else:
            bot.send_privmsg(target,
                f"{nick}: monster not found. Try !cr <number> for a list by challenge rating.")
        return

    m   = data
    cr  = cr_str(m["cr"])
    xp  = CR_XP.get(m["cr"], "?")
    att = (f"Attuned" if m.get("attunement") else "")

    # ── Channel: 2-line summary ───────────────────────────────────
    bot.send_privmsg(target,
        f"\x02{m['name']}\x02  CR {cr} ({xp} XP)  |  {m['type']}  |  "
        f"HP {m['hp']}  AC {m['ac']}  Speed {m['speed']}")
    bot.send_privmsg(target,
        f"STR {m['str']}({mod_str(m['str'])}) "
        f"DEX {m['dex']}({mod_str(m['dex'])}) "
        f"CON {m['con']}({mod_str(m['con'])}) "
        f"INT {m['int']}({mod_str(m['int'])}) "
        f"WIS {m['wis']}({mod_str(m['wis'])}) "
        f"CHA {m['cha']}({mod_str(m['cha'])})  |  "
        f"Align: {m.get('alignment','—')}")

    # ── PM: full stat block ────────────────────────────────────────
    lines = [
        f"\x02=== {m['name']} ===\x02  CR {cr} ({xp} XP)",
        f"{m['type']}  |  HP {m['hp']}  |  AC {m['ac']}  |  Speed {m['speed']}",
    ]
    if m.get("saves"):
        lines.append(f"Saves: {m['saves']}")
    if m.get("skills"):
        lines.append(f"Skills: {m['skills']}")
    if m.get("resist"):
        lines.append(f"Resistances: {m['resist']}")
    if m.get("immunities"):
        lines.append(f"Immunities: {m['immunities']}")
    if m.get("vuln"):
        lines.append(f"Vulnerabilities: {m['vuln']}")
    lines.append(f"Senses: {m.get('senses','—')}  |  Languages: {m.get('languages','—')}")
    lines.append("---")
    lines.append(f"Attacks: {m.get('attacks','—')}")
    if m.get("traits"):
        lines.append(f"Traits: {m['traits']}")
    lines.append(f"Alignment: {m.get('alignment','—')}")

    for line in lines:
        bot.send_privmsg(nick, line)

    if target.startswith("#"):
        bot.send_privmsg(target, f"{nick}: full stat block sent via PM.")


# ----------------------------------------------------------------
# !cr <cr>
# ----------------------------------------------------------------

def cmd_cr(bot, nick, target, args):
    """`!cr <cr>` — list all monsters at a given challenge rating."""
    query = args.strip()
    if not query:
        available = sorted(set(cr_str(v["cr"]) for v in MONSTERS.values()))
        bot.send_privmsg(target,
            f"{nick}: !cr <challenge rating>  —  available CRs: {', '.join(available)}")
        return

    try:
        cr_val = parse_cr(query)
    except (ValueError, ZeroDivisionError):
        bot.send_privmsg(target, f"{nick}: invalid CR. Use 0, 1/8, 1/4, 1/2, 1, 2 … 30")
        return

    names = monsters_at_cr(cr_val)
    if not names:
        bot.send_privmsg(target,
            f"{nick}: no monsters in database at CR {cr_str(cr_val)}.")
        return

    xp = CR_XP.get(cr_val, "?")
    bot.send_privmsg(target,
        f"\x02CR {cr_str(cr_val)}\x02 ({xp} XP each) — {len(names)} in database: "
        f"{', '.join(sorted(names))}")


# ----------------------------------------------------------------
# !encounter <difficulty> <party_level> [party_size]
# ----------------------------------------------------------------

def cmd_encounter(bot, nick, target, args):
    """`!encounter <easy|medium|hard|deadly> <level> [party_size=4]`"""
    parts = args.strip().split()
    if len(parts) < 2:
        bot.send_privmsg(target,
            f"{nick}: !encounter <easy|medium|hard|deadly> <level> [party_size]  "
            f"e.g. !encounter hard 5 4")
        return

    difficulty = parts[0].lower()
    if difficulty not in ("easy", "medium", "hard", "deadly"):
        bot.send_privmsg(target,
            f"{nick}: difficulty must be easy / medium / hard / deadly")
        return

    try:
        level = int(parts[1])
        size  = int(parts[2]) if len(parts) > 2 else 4
    except ValueError:
        bot.send_privmsg(target, f"{nick}: level and party size must be numbers.")
        return

    level = max(1, min(20, level))
    size  = max(1, min(20, size))

    budget = encounter_xp_budget(level, size, difficulty)
    bot.send_privmsg(target,
        f"\x02{difficulty.title()}\x02 encounter — Level {level} party of {size}: "
        f"\x02{budget:,} XP budget\x02")
    bot.send_privmsg(target,
        f"Tip: Use !cr <n> to find monsters by XP. Multiply monster XP by encounter "
        f"multiplier (×1.5 for 3-6, ×2 for 7-10 monsters).")


# ----------------------------------------------------------------
# !loot [cr]
# ----------------------------------------------------------------

def cmd_loot(bot, nick, target, args):
    """`!loot [cr]` — generate random treasure. DM gets hoard details via PM."""
    parts = args.strip().split()
    cr_val = 1.0
    if parts:
        try:
            cr_val = parse_cr(parts[0])
        except (ValueError, ZeroDivisionError):
            bot.send_privmsg(target, f"{nick}: !loot [cr]  e.g. !loot 5  or  !loot 1/4")
            return

    bucket = cr_bucket(cr_val)

    # Individual drop
    individual = roll_individual_treasure(cr_val)

    # Hoard (PM to channel — send to channel briefly, full to DM)
    coins_str, magic_items = roll_hoard(cr_val)

    bot.send_privmsg(target,
        f"\x02Treasure (CR {cr_str(cr_val)})\x02  Individual drop: {individual}  |  "
        f"Hoard coins: {coins_str}")

    if magic_items:
        bot.send_privmsg(target,
            f"Hoard magic items ({len(magic_items)}): {', '.join(magic_items)}")

    if target.startswith("#"):
        bot.send_privmsg(nick,
            f"[Loot roll — CR {cr_str(cr_val)}]  Coins: {coins_str}  "
            f"Magic: {', '.join(magic_items) or 'none'}")


# ----------------------------------------------------------------
# !mitem [name|rarity]
# ----------------------------------------------------------------

def cmd_mitem(bot, nick, target, args):
    """`!mitem [name|rarity]` — look up a magic item or get a random one."""
    query = args.strip()

    if not query:
        # Show rarity distribution
        for r in ITEM_RARITIES:
            names = items_by_rarity(r)
            if names:
                bot.send_privmsg(target,
                    f"\x02{r.title()}\x02 ({len(names)}): {', '.join(sorted(names)[:6])}"
                    + (f" …+{len(names)-6} more" if len(names) > 6 else ""))
        return

    # Check if it's a rarity keyword
    if query.lower() in ITEM_RARITIES or query.lower().replace(" ", "") in [
        r.replace(" ", "") for r in ITEM_RARITIES
    ]:
        # Random item of that rarity
        rarity = query.lower()
        item = random_item(rarity)
        if item:
            _send_item(bot, nick, target, item)
        else:
            bot.send_privmsg(target, f"{nick}: no items of rarity '{rarity}' in database.")
        return

    # Try name lookup
    key, data = find_item(query)
    if key is None:
        if isinstance(data, list):
            # Ambiguous
            names = ", ".join(d for d in sorted(data)[:6])
            extra = f" (+{len(data)-6} more)" if len(data) > 6 else ""
            bot.send_privmsg(target, f"{nick}: did you mean: {names}{extra}?")
        else:
            # No match — random item
            item = random_item()
            bot.send_privmsg(target, f"{nick}: not found — random item instead:")
            _send_item(bot, nick, target, item)
        return

    _send_item(bot, nick, target, data)


def _send_item(bot, nick, target, item: dict):
    """Send a magic item summary to channel (2 lines max)."""
    attune = " (requires attunement)" if item.get("attunement") else ""
    bot.send_privmsg(target,
        f"\x02{item['name']}\x02  {item['rarity'].title()} {item['type']}{attune}")
    # Truncate desc to ~400 chars for channel
    desc = item["desc"]
    if len(desc) > 380:
        desc = desc[:377] + "…"
    bot.send_privmsg(target, desc)
