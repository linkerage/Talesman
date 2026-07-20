#!/usr/bin/env python3
"""
D&D 5e SRD 5.2 (Creative Commons) Data
Races, Classes, Backgrounds, Skills, Alignments, Standard Array
"""

# ----------------------------------------------------------------
# Skills
# ----------------------------------------------------------------

ALL_SKILLS = [
    "Acrobatics", "Animal Handling", "Arcana", "Athletics",
    "Deception", "History", "Insight", "Intimidation",
    "Investigation", "Medicine", "Nature", "Perception",
    "Performance", "Persuasion", "Religion", "Sleight of Hand",
    "Stealth", "Survival",
]

SKILL_ABILITY = {
    "Acrobatics":     "dex",
    "Animal Handling":"wis",
    "Arcana":         "int",
    "Athletics":      "str",
    "Deception":      "cha",
    "History":        "int",
    "Insight":        "wis",
    "Intimidation":   "cha",
    "Investigation":  "int",
    "Medicine":       "wis",
    "Nature":         "int",
    "Perception":     "wis",
    "Performance":    "cha",
    "Persuasion":     "cha",
    "Religion":       "int",
    "Sleight of Hand":"dex",
    "Stealth":        "dex",
    "Survival":       "wis",
}

STAT_ORDER = ["str", "dex", "con", "int", "wis", "cha"]
STAT_NAMES = {"str": "STR", "dex": "DEX", "con": "CON",
              "int": "INT", "wis": "WIS", "cha": "CHA"}

STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]

ALIGNMENTS = [
    "Lawful Good",   "Neutral Good",   "Chaotic Good",
    "Lawful Neutral","True Neutral",   "Chaotic Neutral",
    "Lawful Evil",   "Neutral Evil",   "Chaotic Evil",
]

# ----------------------------------------------------------------
# Dragonborn Ancestries
# ----------------------------------------------------------------

DRAGON_ANCESTRIES = [
    "Black (Acid)",     "Blue (Lightning)", "Brass (Fire)",
    "Bronze (Lightning)","Copper (Acid)",   "Gold (Fire)",
    "Green (Poison)",   "Red (Fire)",       "Silver (Cold)",
    "White (Cold)",
]

# ----------------------------------------------------------------
# Races  (SRD 5.2 — all subraces included as top-level entries)
# ----------------------------------------------------------------

RACES = {
    "Human": {
        "ability_bonus":  {"str":1,"dex":1,"con":1,"int":1,"wis":1,"cha":1},
        "speed": 30,
        "size":  "Medium",
        "darkvision": False,
        "traits": ["Extra Language"],
        "languages": ["Common", "(one extra of your choice)"],
    },
    "High Elf": {
        "ability_bonus":  {"dex":2,"int":1},
        "speed": 30,
        "size":  "Medium",
        "darkvision": True,
        "traits": ["Darkvision 60 ft", "Keen Senses (Perception)", "Fey Ancestry",
                   "Trance", "Elf Weapon Training", "Cantrip (Wizard list, INT)", "Extra Language"],
        "skill_bonus": ["Perception"],
        "languages": ["Common", "Elvish", "(one extra of your choice)"],
    },
    "Wood Elf": {
        "ability_bonus":  {"dex":2,"wis":1},
        "speed": 35,
        "size":  "Medium",
        "darkvision": True,
        "traits": ["Darkvision 60 ft", "Keen Senses (Perception)", "Fey Ancestry",
                   "Trance", "Elf Weapon Training", "Fleet of Foot", "Mask of the Wild"],
        "skill_bonus": ["Perception"],
        "languages": ["Common", "Elvish"],
    },
    "Hill Dwarf": {
        "ability_bonus":  {"con":2,"wis":1},
        "speed": 25,
        "size":  "Medium",
        "darkvision": True,
        "traits": ["Darkvision 60 ft", "Dwarven Resilience (poison adv.)",
                   "Dwarven Combat Training", "Tool Proficiency", "Stonecunning",
                   "Dwarven Toughness (+1 HP per level)"],
        "languages": ["Common", "Dwarvish"],
    },
    "Mountain Dwarf": {
        "ability_bonus":  {"str":2,"con":2},
        "speed": 25,
        "size":  "Medium",
        "darkvision": True,
        "traits": ["Darkvision 60 ft", "Dwarven Resilience (poison adv.)",
                   "Dwarven Combat Training", "Tool Proficiency", "Stonecunning",
                   "Dwarven Armor Training (light & medium)"],
        "languages": ["Common", "Dwarvish"],
    },
    "Lightfoot Halfling": {
        "ability_bonus":  {"dex":2,"cha":1},
        "speed": 25,
        "size":  "Small",
        "darkvision": False,
        "traits": ["Lucky (reroll 1s on d20)", "Brave (adv. vs. frightened)",
                   "Halfling Nimbleness (move through larger creatures)",
                   "Naturally Stealthy (hide behind bigger creatures)"],
        "languages": ["Common", "Halfling"],
    },
    "Stout Halfling": {
        "ability_bonus":  {"dex":2,"con":1},
        "speed": 25,
        "size":  "Small",
        "darkvision": False,
        "traits": ["Lucky (reroll 1s on d20)", "Brave (adv. vs. frightened)",
                   "Halfling Nimbleness", "Stout Resilience (poison adv. & resistance)"],
        "languages": ["Common", "Halfling"],
    },
    "Dragonborn": {
        "ability_bonus":  {"str":2,"cha":1},
        "speed": 30,
        "size":  "Medium",
        "darkvision": False,
        "traits": ["Draconic Ancestry (choose type)", "Breath Weapon (2d6 at lv.1)",
                   "Damage Resistance (matching ancestry)"],
        "languages": ["Common", "Draconic"],
        "needs_ancestry": True,
    },
    "Forest Gnome": {
        "ability_bonus":  {"int":2,"dex":1},
        "speed": 25,
        "size":  "Small",
        "darkvision": True,
        "traits": ["Darkvision 60 ft", "Gnome Cunning (adv. INT/WIS/CHA saves vs. magic)",
                   "Natural Illusionist (Minor Illusion cantrip)",
                   "Speak with Small Beasts"],
        "languages": ["Common", "Gnomish"],
    },
    "Rock Gnome": {
        "ability_bonus":  {"int":2,"con":1},
        "speed": 25,
        "size":  "Small",
        "darkvision": True,
        "traits": ["Darkvision 60 ft", "Gnome Cunning (adv. INT/WIS/CHA saves vs. magic)",
                   "Artificer's Lore (+2x prof on magical/alchemical/tech History checks)",
                   "Tinker (build tiny clockwork devices)"],
        "languages": ["Common", "Gnomish"],
    },
    "Half-Elf": {
        "ability_bonus":  {"cha":2},
        "ability_bonus_pick2": True,   # +1 to any 2 other abilities
        "speed": 30,
        "size":  "Medium",
        "darkvision": True,
        "traits": ["Darkvision 60 ft", "Fey Ancestry", "Skill Versatility (2 extra skills)"],
        "extra_skills": 2,
        "languages": ["Common", "Elvish", "(one extra of your choice)"],
    },
    "Half-Orc": {
        "ability_bonus":  {"str":2,"con":1},
        "speed": 30,
        "size":  "Medium",
        "darkvision": True,
        "traits": ["Darkvision 60 ft", "Menacing (Intimidation proficiency)",
                   "Relentless Endurance (drop to 1 HP instead of 0, 1/rest)",
                   "Savage Attacks (extra weapon die on critical hit)"],
        "skill_bonus": ["Intimidation"],
        "languages": ["Common", "Orc"],
    },
    "Tiefling": {
        "ability_bonus":  {"int":1,"cha":2},
        "speed": 30,
        "size":  "Medium",
        "darkvision": True,
        "traits": ["Darkvision 60 ft", "Hellish Resistance (fire damage resistance)",
                   "Infernal Legacy (Thaumaturgy / Hellish Rebuke / Darkness)"],
        "languages": ["Common", "Infernal"],
    },
}

# ----------------------------------------------------------------
# Classes  (SRD 5.2)
# ----------------------------------------------------------------

CLASSES = {
    "Barbarian": {
        "hit_die": 12,
        "primary_ability": "STR",
        "saving_throws": ["str", "con"],
        "armor_proficiencies": "Light armor, medium armor, shields",
        "weapon_proficiencies": "Simple weapons, martial weapons",
        "skill_count": 2,
        "skill_options": ["Animal Handling", "Athletics", "Intimidation",
                          "Nature", "Perception", "Survival"],
        "starting_equipment": ("Greataxe (or any martial melee), two handaxes "
                               "(or any simple weapon), explorer's pack, 4 javelins"),
        "spellcaster": False,
        "level1_features": ["Rage (2/rest, +2 dmg, adv. STR checks/saves, resistance)",
                            "Unarmored Defense (AC = 10 + DEX + CON while unarmored)"],
        "unarmored_ac": "10+dex+con",
    },
    "Bard": {
        "hit_die": 8,
        "primary_ability": "CHA",
        "saving_throws": ["dex", "cha"],
        "armor_proficiencies": "Light armor",
        "weapon_proficiencies": "Simple weapons, hand crossbows, longswords, rapiers, shortswords",
        "skill_count": 3,
        "skill_options": list(ALL_SKILLS),   # any 3 skills
        "starting_equipment": ("Rapier (or longsword or simple weapon), "
                               "diplomat's pack (or entertainer's pack), "
                               "lute (or musical instrument), leather armor, dagger"),
        "spellcaster": True,
        "spellcasting_ability": "cha",
        "level1_features": ["Bardic Inspiration (d6, CHA mod times/rest)",
                            "Spellcasting (CHA, cantrips + 1st-level spells)"],
        "unarmored_ac": "10+dex",
    },
    "Cleric": {
        "hit_die": 8,
        "primary_ability": "WIS",
        "saving_throws": ["wis", "cha"],
        "armor_proficiencies": "Light armor, medium armor, shields",
        "weapon_proficiencies": "Simple weapons",
        "skill_count": 2,
        "skill_options": ["History", "Insight", "Medicine", "Persuasion", "Religion"],
        "starting_equipment": ("Mace (or warhammer if proficient), scale mail "
                               "(or leather or chain mail), light crossbow + 20 bolts "
                               "(or simple weapon), priest's pack, shield, holy symbol"),
        "spellcaster": True,
        "spellcasting_ability": "wis",
        "level1_features": ["Spellcasting (WIS, domain spells + full cleric list)",
                            "Divine Domain (choose at level 1)"],
        "unarmored_ac": "10+dex",
    },
    "Druid": {
        "hit_die": 8,
        "primary_ability": "WIS",
        "saving_throws": ["int", "wis"],
        "armor_proficiencies": "Light armor, medium armor, shields (nonmetal only)",
        "weapon_proficiencies": "Clubs, daggers, darts, javelins, maces, quarterstaffs, scimitars, sickles, slings, spears",
        "skill_count": 2,
        "skill_options": ["Arcana", "Animal Handling", "Insight", "Medicine",
                          "Nature", "Perception", "Religion", "Survival"],
        "starting_equipment": ("Wooden shield (or simple weapon), scimitar "
                               "(or simple melee weapon), leather armor, "
                               "explorer's pack, druidic focus"),
        "spellcaster": True,
        "spellcasting_ability": "wis",
        "level1_features": ["Druidic (secret language)", "Spellcasting (WIS)"],
        "unarmored_ac": "10+dex",
    },
    "Fighter": {
        "hit_die": 10,
        "primary_ability": "STR or DEX",
        "saving_throws": ["str", "con"],
        "armor_proficiencies": "All armor, shields",
        "weapon_proficiencies": "Simple weapons, martial weapons",
        "skill_count": 2,
        "skill_options": ["Acrobatics", "Animal Handling", "Athletics", "History",
                          "Insight", "Intimidation", "Perception", "Survival"],
        "starting_equipment": ("Chain mail (or leather + longbow + 20 arrows), "
                               "martial weapon + shield (or two martial weapons), "
                               "light crossbow + 20 bolts (or two handaxes), "
                               "dungeoneer's pack (or explorer's pack)"),
        "spellcaster": False,
        "level1_features": ["Fighting Style (choose one)", "Second Wind (1d10+level HP, 1/rest)"],
        "unarmored_ac": "10+dex",
    },
    "Monk": {
        "hit_die": 8,
        "primary_ability": "DEX & WIS",
        "saving_throws": ["str", "dex"],
        "armor_proficiencies": "None",
        "weapon_proficiencies": "Simple weapons, shortswords",
        "skill_count": 2,
        "skill_options": ["Acrobatics", "Athletics", "History",
                          "Insight", "Religion", "Stealth"],
        "starting_equipment": ("Shortsword (or simple weapon), "
                               "dungeoneer's pack (or explorer's pack), 10 darts"),
        "spellcaster": False,
        "level1_features": ["Unarmored Defense (AC = 10 + DEX + WIS)",
                            "Martial Arts (unarmed d4, DEX for attacks)"],
        "unarmored_ac": "10+dex+wis",
    },
    "Paladin": {
        "hit_die": 10,
        "primary_ability": "STR & CHA",
        "saving_throws": ["wis", "cha"],
        "armor_proficiencies": "All armor, shields",
        "weapon_proficiencies": "Simple weapons, martial weapons",
        "skill_count": 2,
        "skill_options": ["Athletics", "Insight", "Intimidation",
                          "Medicine", "Persuasion", "Religion"],
        "starting_equipment": ("Martial weapon + shield (or two martial weapons), "
                               "five javelins (or simple melee weapon), "
                               "priest's pack (or explorer's pack), chain mail, holy symbol"),
        "spellcaster": True,
        "spellcasting_ability": "cha",
        "level1_features": ["Divine Sense (detect celestials/fiends/undead, CHA+1/rest)",
                            "Lay on Hands (HP pool = 5 × level)"],
        "unarmored_ac": "10+dex",
    },
    "Ranger": {
        "hit_die": 10,
        "primary_ability": "DEX & WIS",
        "saving_throws": ["str", "dex"],
        "armor_proficiencies": "Light armor, medium armor, shields",
        "weapon_proficiencies": "Simple weapons, martial weapons",
        "skill_count": 3,
        "skill_options": ["Animal Handling", "Athletics", "Insight", "Investigation",
                          "Nature", "Perception", "Stealth", "Survival"],
        "starting_equipment": ("Scale mail (or leather armor), two shortswords "
                               "(or two simple melee weapons), "
                               "dungeoneer's pack (or explorer's pack), "
                               "longbow + 20 arrows"),
        "spellcaster": True,
        "spellcasting_ability": "wis",
        "level1_features": ["Favored Enemy (choose creature type)", "Natural Explorer (choose terrain)"],
        "unarmored_ac": "10+dex",
    },
    "Rogue": {
        "hit_die": 8,
        "primary_ability": "DEX",
        "saving_throws": ["dex", "int"],
        "armor_proficiencies": "Light armor",
        "weapon_proficiencies": "Simple weapons, hand crossbows, longswords, rapiers, shortswords",
        "skill_count": 4,
        "skill_options": ["Acrobatics", "Athletics", "Deception", "Insight",
                          "Intimidation", "Investigation", "Perception",
                          "Performance", "Persuasion", "Sleight of Hand", "Stealth"],
        "starting_equipment": ("Rapier (or shortsword), shortbow + 20 arrows "
                               "(or shortsword), burglar's pack (or dungeoneer's or explorer's pack), "
                               "leather armor, two daggers, thieves' tools"),
        "spellcaster": False,
        "level1_features": ["Expertise (double prof on 2 skills)",
                            "Sneak Attack (1d6)",
                            "Thieves' Cant (secret rogue language)"],
        "unarmored_ac": "10+dex",
    },
    "Sorcerer": {
        "hit_die": 6,
        "primary_ability": "CHA",
        "saving_throws": ["con", "cha"],
        "armor_proficiencies": "None",
        "weapon_proficiencies": "Daggers, darts, slings, quarterstaffs, light crossbows",
        "skill_count": 2,
        "skill_options": ["Arcana", "Deception", "Insight",
                          "Intimidation", "Persuasion", "Religion"],
        "starting_equipment": ("Light crossbow + 20 bolts (or simple weapon), "
                               "component pouch (or arcane focus), "
                               "dungeoneer's pack (or explorer's pack), two daggers"),
        "spellcaster": True,
        "spellcasting_ability": "cha",
        "level1_features": ["Spellcasting (CHA)", "Sorcerous Origin (choose at level 1)"],
        "unarmored_ac": "10+dex",
    },
    "Warlock": {
        "hit_die": 8,
        "primary_ability": "CHA",
        "saving_throws": ["wis", "cha"],
        "armor_proficiencies": "Light armor",
        "weapon_proficiencies": "Simple weapons",
        "skill_count": 2,
        "skill_options": ["Arcana", "Deception", "History", "Intimidation",
                          "Investigation", "Nature", "Religion"],
        "starting_equipment": ("Light crossbow + 20 bolts (or simple weapon), "
                               "component pouch (or arcane focus), "
                               "scholar's pack (or dungeoneer's pack), "
                               "leather armor, simple weapon, two daggers"),
        "spellcaster": True,
        "spellcasting_ability": "cha",
        "level1_features": ["Otherworldly Patron (choose at level 1)",
                            "Pact Magic (short-rest spell slots, CHA)"],
        "unarmored_ac": "10+dex",
    },
    "Wizard": {
        "hit_die": 6,
        "primary_ability": "INT",
        "saving_throws": ["int", "wis"],
        "armor_proficiencies": "None",
        "weapon_proficiencies": "Daggers, darts, slings, quarterstaffs, light crossbows",
        "skill_count": 2,
        "skill_options": ["Arcana", "History", "Insight",
                          "Investigation", "Medicine", "Religion"],
        "starting_equipment": ("Quarterstaff (or dagger), component pouch "
                               "(or arcane focus), scholar's pack "
                               "(or explorer's pack), spellbook"),
        "spellcaster": True,
        "spellcasting_ability": "int",
        "level1_features": ["Spellcasting (INT, spellbook)",
                            "Arcane Recovery (regain spent slots on short rest, 1/day)"],
        "unarmored_ac": "10+dex",
    },
}

# ----------------------------------------------------------------
# Backgrounds  (SRD 5.2)
# ----------------------------------------------------------------

BACKGROUNDS = {
    "Acolyte": {
        "skills":            ["Insight", "Religion"],
        "tool_proficiencies": [],
        "languages": 2,
        "equipment": "Holy symbol, prayer book or prayer wheel, 5 sticks of incense, vestments, common clothes, 15 gp",
        "feature":   "Shelter of the Faithful",
        "description": "You've spent your life in service to a temple.",
    },
    "Charlatan": {
        "skills":            ["Deception", "Sleight of Hand"],
        "tool_proficiencies": ["Disguise kit", "Forgery kit"],
        "languages": 0,
        "equipment": "Disguise kit, forgery kit, 15 gp",
        "feature":   "False Identity",
        "description": "You've always had a way with people.",
    },
    "Criminal": {
        "skills":            ["Deception", "Stealth"],
        "tool_proficiencies": ["Thieves' tools", "Gaming set (one type)"],
        "languages": 0,
        "equipment": "Crowbar, dark common clothes with hood, 15 gp",
        "feature":   "Criminal Contact",
        "description": "You are an experienced criminal with a history of breaking the law.",
    },
    "Entertainer": {
        "skills":            ["Acrobatics", "Performance"],
        "tool_proficiencies": ["Disguise kit", "Musical instrument (one type)"],
        "languages": 0,
        "equipment": "Musical instrument, costume, 15 gp",
        "feature":   "By Popular Demand",
        "description": "You thrive in front of an audience.",
    },
    "Folk Hero": {
        "skills":            ["Animal Handling", "Survival"],
        "tool_proficiencies": ["Artisan's tools (one type)", "Vehicles (land)"],
        "languages": 0,
        "equipment": "Artisan's tools (one type), shovel, iron pot, common clothes, 10 gp",
        "feature":   "Rustic Hospitality",
        "description": "You come from a humble social rank but are destined for so much more.",
    },
    "Guild Artisan": {
        "skills":            ["Insight", "Persuasion"],
        "tool_proficiencies": ["Artisan's tools (one type)"],
        "languages": 1,
        "equipment": "Artisan's tools (one type), letter of introduction from guild, traveler's clothes, 15 gp",
        "feature":   "Guild Membership",
        "description": "You are a member of an artisan's guild.",
    },
    "Hermit": {
        "skills":            ["Medicine", "Religion"],
        "tool_proficiencies": ["Herbalism kit"],
        "languages": 1,
        "equipment": "Scroll case with notes, winter blanket, common clothes, herbalism kit, 5 gp",
        "feature":   "Discovery",
        "description": "You lived in seclusion for a formative part of your life.",
    },
    "Noble": {
        "skills":            ["History", "Persuasion"],
        "tool_proficiencies": ["Gaming set (one type)"],
        "languages": 1,
        "equipment": "Fine clothes, signet ring, scroll of pedigree, 25 gp",
        "feature":   "Position of Privilege",
        "description": "You understand wealth, power, and privilege.",
    },
    "Outlander": {
        "skills":            ["Athletics", "Survival"],
        "tool_proficiencies": ["Musical instrument (one type)"],
        "languages": 1,
        "equipment": "Staff, hunting trap, trophy from an animal, traveler's clothes, 10 gp",
        "feature":   "Wanderer",
        "description": "You grew up in the wilds far from civilization.",
    },
    "Sage": {
        "skills":            ["Arcana", "History"],
        "tool_proficiencies": [],
        "languages": 2,
        "equipment": "Bottle of black ink, quill, small knife, letter from dead colleague, common clothes, 10 gp",
        "feature":   "Researcher",
        "description": "You spent years learning the lore of the multiverse.",
    },
    "Sailor": {
        "skills":            ["Athletics", "Perception"],
        "tool_proficiencies": ["Navigator's tools", "Vehicles (water)"],
        "languages": 0,
        "equipment": "Belaying pin (club), silk rope (50 ft), lucky charm, common clothes, 10 gp",
        "feature":   "Ship's Passage",
        "description": "You sailed on a seagoing vessel for years.",
    },
    "Soldier": {
        "skills":            ["Athletics", "Intimidation"],
        "tool_proficiencies": ["Gaming set (one type)", "Vehicles (land)"],
        "languages": 0,
        "equipment": "Insignia of rank, trophy from a fallen enemy, gaming set, common clothes, 10 gp",
        "feature":   "Military Rank",
        "description": "War has been your life for as long as you care to remember.",
    },
}
