#!/usr/bin/env python3
"""
D&D 5e Character Creation Wizard for Talesman IRC Bot

Guides a user step-by-step through 5e character creation
entirely via IRC private messages.  Start with start_session(),
then route every incoming PM to handle_input().
"""
import logging
import random
import threading
from typing import Dict, Any, Optional

from dnd5e_data import (
    RACES, CLASSES, BACKGROUNDS, ALIGNMENTS,
    STANDARD_ARRAY, ALL_SKILLS, SKILL_ABILITY,
    STAT_ORDER, STAT_NAMES, DRAGON_ANCESTRIES,
)
from persistence import save_character

# ----------------------------------------------------------------
# Thread-safe session store
# ----------------------------------------------------------------
_lock = threading.Lock()
_sessions: Dict[str, Dict[str, Any]] = {}

RACE_LIST  = list(RACES.keys())
CLASS_LIST = list(CLASSES.keys())
BG_LIST    = list(BACKGROUNDS.keys())


# ----------------------------------------------------------------
# Public API
# ----------------------------------------------------------------

def is_active(nick: str) -> bool:
    with _lock:
        return nick.lower() in _sessions


def cancel_session(nick: str) -> bool:
    with _lock:
        key = nick.lower()
        if key in _sessions:
            del _sessions[key]
            return True
        return False


def start_session(bot, nick: str):
    """Begin a new character creation wizard for nick."""
    key = nick.lower()
    with _lock:
        _sessions[key] = _new_session()

    _pm(bot, nick, "\x02=== D&D 5e Character Creation Wizard ===\x02")
    _pm(bot, nick, "I'll guide you through 5e character creation step by step.")
    _pm(bot, nick, "Reply with the NUMBER of your choice at each step.")
    _pm(bot, nick, "Type \x02!cancelchar\x02 at any time to quit.")
    _pm(bot, nick, " ")
    _ask_name(bot, nick)


def handle_input(bot, nick: str, text: str):
    """Route a PM reply into the active wizard session for nick."""
    key = nick.lower()
    with _lock:
        if key not in _sessions:
            return
        session = _sessions[key]   # reference — mutations are in-place

    text = text.strip()
    if not text:
        return

    step = session["step"]
    dispatch = {
        "name":            _step_name,
        "race":            _step_race,
        "half_elf_bonus":  _step_half_elf_bonus,
        "dragonborn":      _step_dragonborn,
        "class":           _step_class,
        "background":      _step_background,
        "alignment":       _step_alignment,
        "ability_method":  _step_ability_method,
        "ability_assign":  _step_ability_assign,
        "class_skills":    _step_class_skills,
        "half_elf_skills": _step_half_elf_skills,
        "personality":     _step_personality,
        "ideal":           _step_ideal,
        "bond":            _step_bond,
        "flaw":            _step_flaw,
    }
    handler = dispatch.get(step)
    if handler:
        try:
            handler(bot, nick, session, text)
        except Exception as e:
            logging.error(f"charwizard step '{step}' error for {nick}: {e}")
            _pm(bot, nick, f"Something went wrong: {e}. Type !cancelchar to reset.")


# ----------------------------------------------------------------
# Session initialiser
# ----------------------------------------------------------------

def _new_session() -> Dict[str, Any]:
    return {
        "step":                     "name",
        "char_name":                "",
        "race":                     "",
        "class_name":               "",
        "background":               "",
        "alignment":                "",
        "ability_method":           "",
        "available_scores":         [],
        "abilities":                {s: 0 for s in STAT_ORDER},
        "assign_index":             0,       # which stat we're assigning next
        "class_skills_available":   [],
        "class_skills_count":       0,
        "class_skills_picked":      0,
        "chosen_skills":            [],
        "bg_skills":                [],
        "half_elf_bonus_chosen":    [],
        "half_elf_bonus_remaining": 0,
        "half_elf_skills_avail":    [],
        "half_elf_skills_remain":   0,
        "dragonborn_ancestry":      "",
    }


# ----------------------------------------------------------------
# Helper: private message
# ----------------------------------------------------------------

def _pm(bot, nick: str, msg: str):
    for line in msg.split("\n"):
        if line.strip():
            bot.send_privmsg(nick, line)


def _numbered_list(items) -> str:
    lines = []
    for i, item in enumerate(items):
        lines.append(f"  {i + 1}. {item}")
    return "\n".join(lines)


def _parse_choice(text: str, count: int) -> Optional[int]:
    """Return 0-based index from a 1-based user choice, or None on error."""
    try:
        n = int(text.strip())
        if 1 <= n <= count:
            return n - 1
    except (ValueError, TypeError):
        pass
    return None


# ----------------------------------------------------------------
# Step: Character name
# ----------------------------------------------------------------

def _ask_name(bot, nick):
    _pm(bot, nick, "\x02Step 1 — Character Name\x02")
    _pm(bot, nick, "What is your character's name?")
    _pm(bot, nick, "(Type any name and press Enter)")


def _step_name(bot, nick, session, text):
    if len(text) > 40:
        _pm(bot, nick, "Name must be 40 characters or fewer. Try again:")
        return
    session["char_name"] = text
    _pm(bot, nick, f"Name set: \x02{text}\x02")
    _ask_race(bot, nick, session)


# ----------------------------------------------------------------
# Step: Race
# ----------------------------------------------------------------

def _ask_race(bot, nick, session):
    session["step"] = "race"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Step 2 — Race\x02")
    _pm(bot, nick, _numbered_list(RACE_LIST))
    _pm(bot, nick, "Enter the number of your race:")


def _step_race(bot, nick, session, text):
    idx = _parse_choice(text, len(RACE_LIST))
    if idx is None:
        _pm(bot, nick, f"Please enter a number from 1 to {len(RACE_LIST)}.")
        return
    race = RACE_LIST[idx]
    session["race"] = race
    race_data = RACES[race]

    # Show race summary
    bonuses = ", ".join(
        f"{STAT_NAMES[s]} +{v}" for s, v in race_data["ability_bonus"].items()
    )
    _pm(bot, nick, f"Race: \x02{race}\x02 — Ability bonuses: {bonuses}")
    _pm(bot, nick, f"Speed: {race_data['speed']} ft | Size: {race_data['size']}")
    traits_str = ", ".join(race_data["traits"][:4])   # show first 4 to keep it short
    if len(race_data["traits"]) > 4:
        traits_str += f" (+{len(race_data['traits']) - 4} more)"
    _pm(bot, nick, f"Traits: {traits_str}")

    # Branch for special races
    if race == "Half-Elf":
        session["half_elf_bonus_remaining"] = 2
        session["half_elf_bonus_chosen"] = []
        session["step"] = "half_elf_bonus"
        valid = [s for s in STAT_ORDER if s != "cha"]
        _pm(bot, nick, " ")
        _pm(bot, nick, "Half-Elves get +2 CHA plus +1 to \x02two\x02 other ability scores.")
        _pm(bot, nick, "Choose your first +1 bonus (pick 1 of 2):")
        _pm(bot, nick, _numbered_list([STAT_NAMES[s] for s in valid]))
    elif race == "Dragonborn":
        session["step"] = "dragonborn"
        _pm(bot, nick, " ")
        _pm(bot, nick, "Choose your \x02Draconic Ancestry\x02 (determines breath weapon & resistance):")
        _pm(bot, nick, _numbered_list(DRAGON_ANCESTRIES))
    else:
        _ask_class(bot, nick, session)


# ----------------------------------------------------------------
# Step: Half-Elf bonus ability choice
# ----------------------------------------------------------------

def _step_half_elf_bonus(bot, nick, session, text):
    remaining_stats = [s for s in STAT_ORDER if s != "cha"
                       and s not in session["half_elf_bonus_chosen"]]
    idx = _parse_choice(text, len(remaining_stats))
    if idx is None:
        _pm(bot, nick, f"Please enter a number from 1 to {len(remaining_stats)}.")
        return

    chosen_stat = remaining_stats[idx]
    session["half_elf_bonus_chosen"].append(chosen_stat)
    session["half_elf_bonus_remaining"] -= 1
    _pm(bot, nick, f"+1 bonus: \x02{STAT_NAMES[chosen_stat]}\x02")

    if session["half_elf_bonus_remaining"] > 0:
        remaining_stats2 = [s for s in STAT_ORDER if s != "cha"
                            and s not in session["half_elf_bonus_chosen"]]
        _pm(bot, nick, "Choose your second +1 bonus:")
        _pm(bot, nick, _numbered_list([STAT_NAMES[s] for s in remaining_stats2]))
    else:
        _ask_class(bot, nick, session)


# ----------------------------------------------------------------
# Step: Dragonborn ancestry
# ----------------------------------------------------------------

def _step_dragonborn(bot, nick, session, text):
    idx = _parse_choice(text, len(DRAGON_ANCESTRIES))
    if idx is None:
        _pm(bot, nick, f"Please enter a number from 1 to {len(DRAGON_ANCESTRIES)}.")
        return
    session["dragonborn_ancestry"] = DRAGON_ANCESTRIES[idx]
    _pm(bot, nick, f"Draconic Ancestry: \x02{DRAGON_ANCESTRIES[idx]}\x02")
    _ask_class(bot, nick, session)


# ----------------------------------------------------------------
# Step: Class
# ----------------------------------------------------------------

def _ask_class(bot, nick, session):
    session["step"] = "class"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Step 3 — Class\x02")
    lines = []
    for i, name in enumerate(CLASS_LIST):
        cd = CLASSES[name]
        lines.append(f"  {i + 1}. {name} (d{cd['hit_die']}, {cd['primary_ability']}, "
                     f"picks {cd['skill_count']} skill{'s' if cd['skill_count'] != 1 else ''})")
    _pm(bot, nick, "\n".join(lines))
    _pm(bot, nick, "Enter the number of your class:")


def _step_class(bot, nick, session, text):
    idx = _parse_choice(text, len(CLASS_LIST))
    if idx is None:
        _pm(bot, nick, f"Please enter a number from 1 to {len(CLASS_LIST)}.")
        return
    cls = CLASS_LIST[idx]
    session["class_name"] = cls
    cd = CLASSES[cls]
    _pm(bot, nick, f"Class: \x02{cls}\x02 — Hit Die: d{cd['hit_die']}")
    _pm(bot, nick, f"Level 1 features: {', '.join(cd['level1_features'])}")
    _ask_background(bot, nick, session)


# ----------------------------------------------------------------
# Step: Background
# ----------------------------------------------------------------

def _ask_background(bot, nick, session):
    session["step"] = "background"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Step 4 — Background\x02")
    lines = []
    for i, name in enumerate(BG_LIST):
        bd = BACKGROUNDS[name]
        lines.append(f"  {i + 1}. {name} — Skills: {', '.join(bd['skills'])}")
    _pm(bot, nick, "\n".join(lines))
    _pm(bot, nick, "Enter the number of your background:")


def _step_background(bot, nick, session, text):
    idx = _parse_choice(text, len(BG_LIST))
    if idx is None:
        _pm(bot, nick, f"Please enter a number from 1 to {len(BG_LIST)}.")
        return
    bg = BG_LIST[idx]
    session["background"] = bg
    bd = BACKGROUNDS[bg]
    session["bg_skills"] = list(bd["skills"])
    _pm(bot, nick, f"Background: \x02{bg}\x02")
    _pm(bot, nick, f"Skills granted: {', '.join(bd['skills'])}")
    _pm(bot, nick, f"Feature: {bd['feature']}")
    _ask_alignment(bot, nick, session)


# ----------------------------------------------------------------
# Step: Alignment
# ----------------------------------------------------------------

def _ask_alignment(bot, nick, session):
    session["step"] = "alignment"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Step 5 — Alignment\x02")
    _pm(bot, nick, _numbered_list(ALIGNMENTS))
    _pm(bot, nick, "Enter the number of your alignment:")


def _step_alignment(bot, nick, session, text):
    idx = _parse_choice(text, len(ALIGNMENTS))
    if idx is None:
        _pm(bot, nick, f"Please enter a number from 1 to {len(ALIGNMENTS)}.")
        return
    session["alignment"] = ALIGNMENTS[idx]
    _pm(bot, nick, f"Alignment: \x02{ALIGNMENTS[idx]}\x02")
    _ask_ability_method(bot, nick, session)


# ----------------------------------------------------------------
# Step: Ability score method
# ----------------------------------------------------------------

def _ask_ability_method(bot, nick, session):
    session["step"] = "ability_method"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Step 6 — Ability Scores\x02")
    _pm(bot, nick, "How would you like to determine your ability scores?")
    _pm(bot, nick, "  1. Standard Array  (15, 14, 13, 12, 10, 8)")
    _pm(bot, nick, "  2. Roll dice       (4d6 drop lowest, rolled for each score)")


def _step_ability_method(bot, nick, session, text):
    idx = _parse_choice(text, 2)
    if idx is None:
        _pm(bot, nick, "Please enter 1 (Standard Array) or 2 (Roll).")
        return
    if idx == 0:
        session["available_scores"] = list(STANDARD_ARRAY)
        session["ability_method"] = "standard"
        _pm(bot, nick, "Using Standard Array: \x0215, 14, 13, 12, 10, 8\x02")
    else:
        rolled = sorted([_roll_4d6_drop_lowest() for _ in range(6)], reverse=True)
        session["available_scores"] = rolled
        session["ability_method"] = "rolled"
        _pm(bot, nick, f"You rolled: \x02{', '.join(str(s) for s in rolled)}\x02")
    session["assign_index"] = 0
    session["step"] = "ability_assign"
    _prompt_ability_assign(bot, nick, session)


def _roll_4d6_drop_lowest() -> int:
    rolls = sorted([random.randint(1, 6) for _ in range(4)])
    return sum(rolls[1:])   # drop lowest


# ----------------------------------------------------------------
# Step: Assign ability scores one stat at a time
# ----------------------------------------------------------------

def _prompt_ability_assign(bot, nick, session):
    stat = STAT_ORDER[session["assign_index"]]
    avail = session["available_scores"]
    _pm(bot, nick, " ")
    _pm(bot, nick, f"\x02Assign a score to {STAT_NAMES[stat]}\x02  "
                   f"(remaining: {', '.join(str(s) for s in avail)})")
    for i, score in enumerate(avail):
        _pm(bot, nick, f"  {i + 1}. {score}")


def _step_ability_assign(bot, nick, session, text):
    avail = session["available_scores"]
    idx = _parse_choice(text, len(avail))
    if idx is None:
        _pm(bot, nick, f"Please enter a number from 1 to {len(avail)}.")
        return

    score = avail[idx]
    stat  = STAT_ORDER[session["assign_index"]]
    session["abilities"][stat] = score
    session["available_scores"] = [s for i, s in enumerate(avail) if i != idx]
    _pm(bot, nick, f"\x02{STAT_NAMES[stat]}\x02 = {score}  (modifier: {_mod_str(score)})")

    session["assign_index"] += 1
    if session["assign_index"] < 6:
        _prompt_ability_assign(bot, nick, session)
    else:
        _ask_class_skills(bot, nick, session)


def _mod_str(score: int) -> str:
    m = (score - 10) // 2
    return f"{m:+d}"


# ----------------------------------------------------------------
# Step: Class skill selection
# ----------------------------------------------------------------

def _ask_class_skills(bot, nick, session):
    cls  = session["class_name"]
    cd   = CLASSES[cls]
    bg_skills = set(session["bg_skills"])

    # Exclude skills already granted by background
    available = [s for s in cd["skill_options"] if s not in bg_skills]
    count = cd["skill_count"]

    session["class_skills_available"] = available
    session["class_skills_count"]     = count
    session["class_skills_picked"]    = 0
    session["step"] = "class_skills"

    _pm(bot, nick, " ")
    _pm(bot, nick, f"\x02Step 7 — {cls} Skills\x02  (choose {count}):")
    _pm(bot, nick, _numbered_list(available))
    _pm(bot, nick, f"Pick skill 1 of {count}:")


def _step_class_skills(bot, nick, session, text):
    available = session["class_skills_available"]
    idx = _parse_choice(text, len(available))
    if idx is None:
        _pm(bot, nick, f"Please enter a number from 1 to {len(available)}.")
        return

    skill = available[idx]
    session["chosen_skills"].append(skill)
    session["class_skills_picked"] += 1
    session["class_skills_available"] = [s for s in available if s != skill]
    _pm(bot, nick, f"Skill chosen: \x02{skill}\x02")

    remaining = session["class_skills_count"] - session["class_skills_picked"]
    if remaining > 0:
        _pm(bot, nick, f"Pick skill {session['class_skills_picked'] + 1} of "
                       f"{session['class_skills_count']}:")
        _pm(bot, nick, _numbered_list(session["class_skills_available"]))
    elif session["race"] == "Half-Elf":
        _ask_half_elf_skills(bot, nick, session)
    else:
        _ask_personality(bot, nick, session)


# ----------------------------------------------------------------
# Step: Half-Elf bonus skill selection (Skill Versatility — 2 any)
# ----------------------------------------------------------------

def _ask_half_elf_skills(bot, nick, session):
    all_avail = [s for s in ALL_SKILLS
                 if s not in session["chosen_skills"]
                 and s not in session["bg_skills"]]
    session["half_elf_skills_avail"]  = all_avail
    session["half_elf_skills_remain"] = 2
    session["step"] = "half_elf_skills"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Half-Elf Skill Versatility\x02 — choose 2 additional skills from any list:")
    _pm(bot, nick, _numbered_list(all_avail))
    _pm(bot, nick, "Pick bonus skill 1 of 2:")


def _step_half_elf_skills(bot, nick, session, text):
    available = session["half_elf_skills_avail"]
    idx = _parse_choice(text, len(available))
    if idx is None:
        _pm(bot, nick, f"Please enter a number from 1 to {len(available)}.")
        return

    skill = available[idx]
    session["chosen_skills"].append(skill)
    session["half_elf_skills_remain"] -= 1
    session["half_elf_skills_avail"] = [s for s in available if s != skill]
    _pm(bot, nick, f"Bonus skill: \x02{skill}\x02")

    if session["half_elf_skills_remain"] > 0:
        _pm(bot, nick, "Pick bonus skill 2 of 2:")
        _pm(bot, nick, _numbered_list(session["half_elf_skills_avail"]))
    else:
        _ask_personality(bot, nick, session)


# ----------------------------------------------------------------
# Steps: Personality, Ideal, Bond, Flaw (free text)
# ----------------------------------------------------------------

def _ask_personality(bot, nick, session):
    session["step"] = "personality"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Step 8 — Personality Trait\x02")
    _pm(bot, nick, "Describe your character's personality (1–2 sentences):")


def _step_personality(bot, nick, session, text):
    session["personality"] = text[:300]
    session["step"] = "ideal"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Step 9 — Ideal\x02")
    _pm(bot, nick, "What is your character's ideal? (e.g. Justice, Freedom, Greater Good):")


def _step_ideal(bot, nick, session, text):
    session["ideal"] = text[:200]
    session["step"] = "bond"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Step 10 — Bond\x02")
    _pm(bot, nick, "What is your character's bond? (a person, place, or purpose they're devoted to):")


def _step_bond(bot, nick, session, text):
    session["bond"] = text[:200]
    session["step"] = "flaw"
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02Step 11 — Flaw\x02")
    _pm(bot, nick, "What is your character's flaw? (a weakness or vice):")


def _step_flaw(bot, nick, session, text):
    session["flaw"] = text[:200]
    _finalize(bot, nick, session)


# ----------------------------------------------------------------
# Finalize — compute all derived stats and save
# ----------------------------------------------------------------

def _finalize(bot, nick: str, session: dict):
    race  = session["race"]
    cls   = session["class_name"]
    bg    = session["background"]

    race_data = RACES[race]
    cls_data  = CLASSES[cls]
    bg_data   = BACKGROUNDS[bg]

    # --- Apply racial ability bonuses ---
    abilities = dict(session["abilities"])
    for stat, bonus in race_data["ability_bonus"].items():
        abilities[stat] = abilities.get(stat, 0) + bonus

    # Half-Elf extra +1s
    for stat in session.get("half_elf_bonus_chosen", []):
        abilities[stat] = abilities.get(stat, 0) + 1

    # Cap at 20
    for stat in STAT_ORDER:
        abilities[stat] = min(abilities[stat], 20)

    # --- Modifiers ---
    def _mod(score: int) -> int:
        return (score - 10) // 2

    mods = {s: _mod(v) for s, v in abilities.items()}

    # --- Proficiency bonus (always +2 at level 1) ---
    prof = 2

    # --- HP ---
    hp = cls_data["hit_die"] + mods["con"]
    hp = max(1, hp)
    # Hill Dwarf gets +1 HP per level
    if race == "Hill Dwarf":
        hp += 1

    # --- AC (unarmored base — actual AC depends on armor worn) ---
    formula = cls_data.get("unarmored_ac", "10+dex")
    if formula == "10+dex+con":
        ac = 10 + mods["dex"] + mods["con"]       # Barbarian
    elif formula == "10+dex+wis":
        ac = 10 + mods["dex"] + mods["wis"]       # Monk
    else:
        ac = 10 + mods["dex"]                     # everyone else (unarmored)

    # --- Skill proficiencies ---
    race_skill_bonus = race_data.get("skill_bonus", [])
    all_prof_skills = sorted(set(
        session["chosen_skills"] + session["bg_skills"] + race_skill_bonus
    ))

    # --- Skill bonuses ---
    skill_bonuses: Dict[str, int] = {}
    for skill in ALL_SKILLS:
        ability = SKILL_ABILITY[skill]
        base = mods[ability]
        skill_bonuses[skill] = base + prof if skill in all_prof_skills else base

    # --- Saving throws ---
    saves: Dict[str, int] = {}
    for stat in STAT_ORDER:
        saves[stat] = mods[stat] + (prof if stat in cls_data["saving_throws"] else 0)

    # --- Passive Perception ---
    passive_perception = 10 + skill_bonuses.get("Perception", mods["wis"])

    # --- Spellcasting DC / attack bonus ---
    sc_ability = cls_data.get("spellcasting_ability", "")
    spell_save_dc    = 8 + prof + mods[sc_ability] if sc_ability else None
    spell_atk_bonus  = prof + mods[sc_ability] if sc_ability else None

    # --- Build character dict ---
    char = {
        "nick":              nick.lower(),
        "system":            "dnd5e",
        "srd_version":       "5.2",
        "name":              session["char_name"],
        "race":              race,
        "dragonborn_ancestry": session.get("dragonborn_ancestry", ""),
        "class":             cls,
        "background":        bg,
        "alignment":         session["alignment"],
        "level":             1,
        "xp":                0,
        "proficiency_bonus": prof,
        "abilities":         abilities,
        "modifiers":         mods,
        "saving_throws":     saves,
        "hp_max":            hp,
        "hp_current":        hp,
        "ac":                ac,
        "initiative":        mods["dex"],
        "speed":             race_data["speed"],
        "size":              race_data["size"],
        "hit_die":           f"1d{cls_data['hit_die']}",
        "armor_proficiencies":  cls_data["armor_proficiencies"],
        "weapon_proficiencies": cls_data["weapon_proficiencies"],
        "skill_proficiencies":  all_prof_skills,
        "skill_bonuses":        skill_bonuses,
        "languages":            race_data.get("languages", ["Common"]),
        "racial_traits":        race_data.get("traits", []),
        "level1_features":      cls_data.get("level1_features", []),
        "starting_equipment":   cls_data["starting_equipment"],
        "background_equipment": bg_data["equipment"],
        "background_feature":   bg_data["feature"],
        "spellcaster":          cls_data.get("spellcaster", False),
        "spellcasting_ability": sc_ability,
        "spell_save_dc":        spell_save_dc,
        "spell_attack_bonus":   spell_atk_bonus,
        "passive_perception":   passive_perception,
        "personality":          session.get("personality", ""),
        "ideal":                session.get("ideal", ""),
        "bond":                 session.get("bond", ""),
        "flaw":                 session.get("flaw", ""),
        "death_saves_success":  0,
        "death_saves_failure":  0,
        "conditions":           [],
        "notes":                "",
    }

    # Save to disk
    try:
        save_character(char)
    except Exception as e:
        logging.error(f"charwizard save failed for {nick}: {e}")
        _pm(bot, nick, f"Error saving character: {e}")
        return

    # Remove session
    with _lock:
        _sessions.pop(nick.lower(), None)

    # --- Summary ---
    ab = abilities
    mo = mods
    _pm(bot, nick, " ")
    _pm(bot, nick, "\x02=== Character Creation Complete! ===\x02")
    _pm(bot, nick,
        f"\x02{char['name']}\x02  |  {race} {cls}  |  {bg}  |  {char['alignment']}")
    _pm(bot, nick,
        f"HP: {hp}  |  AC: {ac} (unarmored)  |  Speed: {race_data['speed']} ft  |  "
        f"Initiative: {mo['dex']:+d}  |  Proficiency: +{prof}")
    _pm(bot, nick,
        f"STR {ab['str']}({mo['str']:+d})  DEX {ab['dex']}({mo['dex']:+d})  "
        f"CON {ab['con']}({mo['con']:+d})  INT {ab['int']}({mo['int']:+d})  "
        f"WIS {ab['wis']}({mo['wis']:+d})  CHA {ab['cha']}({mo['cha']:+d})")
    _pm(bot, nick,
        f"Skills: {', '.join(all_prof_skills) or 'None'}")
    if cls_data.get("spellcaster") and sc_ability:
        _pm(bot, nick,
            f"Spellcasting: {sc_ability.upper()}  |  Save DC: {spell_save_dc}  |  "
            f"Attack: {spell_atk_bonus:+d}")
    _pm(bot, nick, "Character saved. Use \x02!charsheet\x02 to view your full sheet.")
