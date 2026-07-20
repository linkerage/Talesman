#!/usr/bin/env python3
"""
D&D 5e SRD 5.2 (Creative Commons) Monster Database
60+ creatures spanning CR 0 through CR 30.

CR stored as float (0.125=1/8, 0.25=1/4, 0.5=1/2).
XP values are standard 5e XP per monster.
"""

# XP by CR
CR_XP = {
    0: 10, 0.125: 25, 0.25: 50, 0.5: 100,
    1: 200, 2: 450, 3: 700, 4: 1100, 5: 1800,
    6: 2300, 7: 2900, 8: 3900, 9: 5000, 10: 5900,
    11: 7200, 12: 8400, 13: 10000, 14: 11500, 15: 13000,
    16: 15000, 17: 18000, 18: 20000, 19: 22000, 20: 25000,
    21: 33000, 22: 41000, 23: 50000, 24: 62000,
    25: 75000, 30: 155000,
}

def cr_str(cr: float) -> str:
    """Return a human-readable CR string."""
    if cr == 0.125: return "1/8"
    if cr == 0.25:  return "1/4"
    if cr == 0.5:   return "1/2"
    if cr == int(cr): return str(int(cr))
    return str(cr)

def mod_str(score: int) -> str:
    m = (score - 10) // 2
    return f"{m:+d}"

# ----------------------------------------------------------------
# Monster Database
# ----------------------------------------------------------------

MONSTERS = {
    # ── CR 0 ──────────────────────────────────────────────────────
    "commoner": {
        "name": "Commoner", "cr": 0, "type": "Medium humanoid",
        "hp": 4, "ac": 10, "speed": "30 ft.",
        "str": 10, "dex": 10, "con": 10, "int": 10, "wis": 10, "cha": 10,
        "senses": "PP 10", "languages": "any one language",
        "attacks": "Club +2 1d4 bludgeoning",
        "traits": "",
        "alignment": "Any",
    },
    "rat": {
        "name": "Rat", "cr": 0, "type": "Tiny beast",
        "hp": 1, "ac": 10, "speed": "20 ft.",
        "str": 2, "dex": 11, "con": 9, "int": 2, "wis": 10, "cha": 4,
        "senses": "Darkvision 30 ft., PP 10", "languages": "—",
        "attacks": "Bite +0 1 piercing",
        "traits": "Keen Smell: Advantage on Perception (smell)",
        "alignment": "Unaligned",
    },

    # ── CR 1/8 ────────────────────────────────────────────────────
    "bandit": {
        "name": "Bandit", "cr": 0.125, "type": "Medium humanoid",
        "hp": 11, "ac": 12, "speed": "30 ft.",
        "str": 11, "dex": 12, "con": 12, "int": 10, "wis": 10, "cha": 10,
        "senses": "PP 10", "languages": "any one",
        "attacks": "Scimitar +3 1d6+1 slashing; Light crossbow +3 range 80/320 ft. 1d8+1 piercing",
        "traits": "",
        "alignment": "Any Non-Lawful",
    },
    "kobold": {
        "name": "Kobold", "cr": 0.125, "type": "Small humanoid",
        "hp": 5, "ac": 12, "speed": "30 ft.",
        "str": 7, "dex": 15, "con": 9, "int": 8, "wis": 7, "cha": 8,
        "skills": "Perception +1", "senses": "Darkvision 60 ft., PP 8", "languages": "Common, Draconic",
        "attacks": "Dagger +4 1d4+2 piercing; Sling +4 range 30/120 ft. 1d4+2 bludgeoning",
        "traits": "Sunlight Sensitivity: Disadvantage on attacks/Perception in sunlight. Pack Tactics: Advantage on attacks if ally adjacent to target.",
        "alignment": "Lawful Evil",
    },
    "skeleton": {
        "name": "Skeleton", "cr": 0.25, "type": "Medium undead",
        "hp": 13, "ac": 13, "speed": "30 ft.",
        "str": 10, "dex": 14, "con": 15, "int": 6, "wis": 8, "cha": 5,
        "vuln": "Bludgeoning", "immunities": "Poison, Exhaustion, Poisoned",
        "senses": "Darkvision 60 ft., PP 9", "languages": "understands languages it knew in life",
        "attacks": "Shortsword +4 1d6+2 piercing; Shortbow +4 range 80/320 ft. 1d6+2 piercing",
        "traits": "",
        "alignment": "Lawful Evil",
    },

    # ── CR 1/4 ────────────────────────────────────────────────────
    "goblin": {
        "name": "Goblin", "cr": 0.25, "type": "Small humanoid",
        "hp": 7, "ac": 15, "speed": "30 ft.",
        "str": 8, "dex": 14, "con": 10, "int": 10, "wis": 8, "cha": 8,
        "skills": "Stealth +6", "senses": "Darkvision 60 ft., PP 9", "languages": "Common, Goblin",
        "attacks": "Scimitar +4 1d6+2 slashing; Shortbow +4 range 80/320 ft. 1d6+2 piercing",
        "traits": "Nimble Escape: Disengage or Hide as bonus action.",
        "alignment": "Neutral Evil",
    },
    "wolf": {
        "name": "Wolf", "cr": 0.25, "type": "Medium beast",
        "hp": 11, "ac": 13, "speed": "40 ft.",
        "str": 12, "dex": 15, "con": 12, "int": 3, "wis": 12, "cha": 6,
        "skills": "Perception +3, Stealth +4", "senses": "PP 13", "languages": "—",
        "attacks": "Bite +4 2d4+2 piercing; target DC 11 STR save or knocked prone",
        "traits": "Keen Hearing and Smell: Advantage on Perception. Pack Tactics.",
        "alignment": "Unaligned",
    },

    # ── CR 1/2 ────────────────────────────────────────────────────
    "orc": {
        "name": "Orc", "cr": 0.5, "type": "Medium humanoid",
        "hp": 15, "ac": 13, "speed": "30 ft.",
        "str": 16, "dex": 12, "con": 16, "int": 7, "wis": 11, "cha": 10,
        "skills": "Intimidation +2", "senses": "Darkvision 60 ft., PP 10", "languages": "Common, Orc",
        "attacks": "Greataxe +5 1d12+3 slashing; Javelin +5 range 30/120 ft. 1d6+3 piercing",
        "traits": "Aggressive: Bonus action to move up to speed toward a hostile.",
        "alignment": "Chaotic Evil",
    },
    "ghoul": {
        "name": "Ghoul", "cr": 1, "type": "Medium undead",
        "hp": 22, "ac": 12, "speed": "30 ft.",
        "str": 13, "dex": 15, "con": 10, "int": 7, "wis": 10, "cha": 6,
        "immunities": "Poison, Charmed, Exhaustion, Poisoned",
        "senses": "Darkvision 60 ft., PP 10", "languages": "Common",
        "attacks": "Bite +2 2d6+2 piercing; Claws +4 2d4+2 slashing (DC 10 CON or Paralyzed 1 min)",
        "traits": "Paralysis: Claws paralyze non-elf targets on failed CON save.",
        "alignment": "Chaotic Evil",
    },
    "hobgoblin": {
        "name": "Hobgoblin", "cr": 0.5, "type": "Medium humanoid",
        "hp": 11, "ac": 18, "speed": "30 ft.",
        "str": 13, "dex": 12, "con": 12, "int": 10, "wis": 10, "cha": 9,
        "senses": "Darkvision 60 ft., PP 10", "languages": "Common, Goblin",
        "attacks": "Longsword +3 1d8+1 slashing; Longbow +3 range 150/600 ft. 1d8+1 piercing",
        "traits": "Martial Advantage: +2d6 damage if ally is adjacent to target.",
        "alignment": "Lawful Evil",
    },

    # ── CR 1 ──────────────────────────────────────────────────────
    "bugbear": {
        "name": "Bugbear", "cr": 1, "type": "Medium humanoid",
        "hp": 27, "ac": 16, "speed": "30 ft.",
        "str": 15, "dex": 14, "con": 13, "int": 8, "wis": 11, "cha": 9,
        "skills": "Stealth +6, Survival +2", "senses": "Darkvision 60 ft., PP 10", "languages": "Common, Goblin",
        "attacks": "Morningstar +4 2d8+2 piercing; Javelin +4 range 30/120 ft. 2d6+2 piercing",
        "traits": "Brute: +1 die to melee damage (included). Surprise Attack: +2d6 damage if target surprised.",
        "alignment": "Chaotic Evil",
    },
    "imp": {
        "name": "Imp", "cr": 1, "type": "Tiny fiend (devil)",
        "hp": 10, "ac": 13, "speed": "20 ft., fly 40 ft.",
        "str": 6, "dex": 17, "con": 13, "int": 11, "wis": 12, "cha": 14,
        "skills": "Deception +4, Insight +3, Persuasion +4, Stealth +5",
        "resist": "Cold; Bludgeoning/Piercing/Slashing from nonmagical weapons not silver",
        "immunities": "Fire, Poison, Poisoned", "senses": "Darkvision 120 ft., PP 11",
        "languages": "Infernal, Common",
        "attacks": "Sting +5 1d4+3 piercing + 3d4 poison (DC 11 CON halves)",
        "traits": "Shapechanger: Polymorph into raven/rat/spider. Devil's Sight: See through magical darkness. Magic Resistance: Advantage on saves vs. spells. Invisibility.",
        "alignment": "Lawful Evil",
    },
    "wererat": {
        "name": "Wererat", "cr": 2, "type": "Medium humanoid (shapechanger)",
        "hp": 33, "ac": 12, "speed": "30 ft.",
        "str": 10, "dex": 15, "con": 12, "int": 11, "wis": 10, "cha": 8,
        "skills": "Perception +2, Stealth +4",
        "immunities": "Bludgeoning/Piercing/Slashing from nonmagical non-silvered weapons",
        "senses": "Darkvision 60 ft. (rat form), PP 12", "languages": "Common (can't speak in rat form)",
        "attacks": "Multiattack (2): Bite +4 1d4+2 piercing (DC 11 CON or lycanthropy); Hand Crossbow +4 range 30/120 ft. 1d6+2 piercing",
        "traits": "Shapechanger: Polymorph into rat/hybrid. Keen Smell.",
        "alignment": "Lawful Evil",
    },

    # ── CR 2 ──────────────────────────────────────────────────────
    "ogre": {
        "name": "Ogre", "cr": 2, "type": "Large giant",
        "hp": 59, "ac": 11, "speed": "40 ft.",
        "str": 19, "dex": 8, "con": 16, "int": 5, "wis": 7, "cha": 7,
        "senses": "Darkvision 60 ft., PP 8", "languages": "Common, Giant",
        "attacks": "Greatclub +6 2d8+4 bludgeoning; Javelin +6 range 30/120 ft. 2d6+4 piercing",
        "traits": "",
        "alignment": "Chaotic Evil",
    },
    "gelatinous cube": {
        "name": "Gelatinous Cube", "cr": 2, "type": "Large ooze",
        "hp": 84, "ac": 6, "speed": "15 ft.",
        "str": 14, "dex": 3, "con": 20, "int": 1, "wis": 6, "cha": 1,
        "immunities": "Blinded, Charmed, Deafened, Exhaustion, Frightened, Prone",
        "senses": "Blindsight 60 ft., PP 8", "languages": "—",
        "attacks": "Pseudopod +4 3d6+2 acid; Engulf (DC 12 DEX or restrained, 6d6 acid/turn)",
        "traits": "Transparent: DC 15 Perception to see. Ooze Cube: Occupies full 10 ft. space.",
        "alignment": "Unaligned",
    },
    "owlbear": {
        "name": "Owlbear", "cr": 3, "type": "Large monstrosity",
        "hp": 59, "ac": 13, "speed": "40 ft.",
        "str": 20, "dex": 12, "con": 17, "int": 3, "wis": 12, "cha": 7,
        "skills": "Perception +3", "senses": "Darkvision 60 ft., PP 13", "languages": "—",
        "attacks": "Multiattack (2): Beak +7 1d10+5 piercing; Claws +7 2d8+5 slashing",
        "traits": "Keen Sight and Smell: Advantage on Perception.",
        "alignment": "Unaligned",
    },
    "mimic": {
        "name": "Mimic", "cr": 2, "type": "Medium monstrosity (shapechanger)",
        "hp": 58, "ac": 12, "speed": "15 ft.",
        "str": 17, "dex": 12, "con": 15, "int": 5, "wis": 13, "cha": 8,
        "skills": "Stealth +5",
        "immunities": "Acid, Prone",
        "senses": "Darkvision 60 ft., PP 11", "languages": "—",
        "attacks": "Pseudopod +5 1d8+3 bludgeoning + Adhesive; Bite +5 1d8+3 piercing",
        "traits": "Adhesive: Target grappled (escape DC 13). Shapechanger: Appear as any object. False Appearance: Indistinguishable when still.",
        "alignment": "Neutral",
    },
    "nothic": {
        "name": "Nothic", "cr": 2, "type": "Medium aberration",
        "hp": 45, "ac": 15, "speed": "30 ft.",
        "str": 14, "dex": 16, "con": 16, "int": 13, "wis": 10, "cha": 8,
        "skills": "Arcana +3, Insight +4, Perception +2, Stealth +5",
        "senses": "Truesight 120 ft., PP 12", "languages": "Undercommon",
        "attacks": "Multiattack (2): Claw +4 1d6+2 slashing; Rotting Gaze (60 ft. range, DC 12 CON or 3d6 necrotic)",
        "traits": "Weird Insight: Contested Insight vs. Deception — learn one secret about target.",
        "alignment": "Neutral Evil",
    },

    # ── CR 3 ──────────────────────────────────────────────────────
    "manticore": {
        "name": "Manticore", "cr": 3, "type": "Large monstrosity",
        "hp": 68, "ac": 14, "speed": "30 ft., fly 50 ft.",
        "str": 17, "dex": 16, "con": 17, "int": 7, "wis": 12, "cha": 8,
        "senses": "Darkvision 60 ft., PP 11", "languages": "Common",
        "attacks": "Multiattack (3): Bite +5 1d8+3 piercing; Claw +5 1d6+3 slashing; Tail Spike +5 range 100/200 ft. 1d8+3 piercing (24 spikes total)",
        "traits": "",
        "alignment": "Lawful Evil",
    },
    "wight": {
        "name": "Wight", "cr": 3, "type": "Medium undead",
        "hp": 45, "ac": 14, "speed": "30 ft.",
        "str": 15, "dex": 14, "con": 16, "int": 10, "wis": 13, "cha": 15,
        "skills": "Perception +3, Stealth +4",
        "resist": "Necrotic; Bludgeoning/Piercing/Slashing from nonmagical non-silvered weapons",
        "immunities": "Cold, Necrotic, Poison, Exhaustion, Poisoned",
        "senses": "Darkvision 60 ft., PP 13", "languages": "Languages known in life",
        "attacks": "Multiattack (2): Longsword +4 1d8+2 slashing; Life Drain +4 1d6+2 necrotic (DC 13 CON or HP max reduced)",
        "traits": "Life Drain: Reduces HP maximum. Sunlight Sensitivity.",
        "alignment": "Neutral Evil",
    },
    "werewolf": {
        "name": "Werewolf", "cr": 3, "type": "Medium humanoid (shapechanger)",
        "hp": 58, "ac": 11, "speed": "30 ft. (40 ft. wolf form)",
        "str": 15, "dex": 13, "con": 14, "int": 10, "wis": 11, "cha": 10,
        "skills": "Perception +4, Stealth +3",
        "immunities": "Bludgeoning/Piercing/Slashing from nonmagical non-silvered weapons",
        "senses": "PP 14", "languages": "Common (can't speak in wolf form)",
        "attacks": "Multiattack (2 in hybrid): Bite +4 2d6+2 piercing (DC 12 CON or lycanthropy); Claws +4 2d4+2 slashing",
        "traits": "Shapechanger: Polymorph into wolf/hybrid. Keen Hearing and Smell.",
        "alignment": "Chaotic Evil",
    },

    # ── CR 4 ──────────────────────────────────────────────────────
    "ghost": {
        "name": "Ghost", "cr": 4, "type": "Medium undead",
        "hp": 45, "ac": 11, "speed": "0 ft., fly 40 ft. (hover)",
        "str": 7, "dex": 13, "con": 10, "int": 10, "wis": 12, "cha": 17,
        "resist": "Acid, Fire, Lightning, Thunder; Bludgeoning/Piercing/Slashing from nonmagical weapons",
        "immunities": "Cold, Necrotic, Poison, Charmed, Exhaustion, Frightened, Grappled, Paralyzed, Petrified, Poisoned, Prone, Restrained",
        "senses": "Darkvision 60 ft., PP 11", "languages": "Languages known in life",
        "attacks": "Withering Touch +5 4d6+3 necrotic; Corrupting Touch (DC 13 CHA or Frightened 1 min)",
        "traits": "Ethereal Sight. Incorporeal Movement (pass through solid objects). Possession (recharge 6): DC 13 CHA or possessed. Horrifying Visage: DC 13 WIS or frightened 1 min.",
        "alignment": "Any",
    },
    "succubus": {
        "name": "Succubus/Incubus", "cr": 4, "type": "Medium fiend (shapechanger)",
        "hp": 66, "ac": 13, "speed": "30 ft., fly 60 ft.",
        "str": 8, "dex": 17, "con": 13, "int": 15, "wis": 12, "cha": 20,
        "skills": "Deception +9, Insight +5, Perception +5, Persuasion +9, Stealth +7",
        "resist": "Cold, Fire, Lightning, Poison; Bludgeoning/Piercing/Slashing from nonmagical weapons",
        "immunities": "Poison, Poisoned",
        "senses": "Darkvision 60 ft., PP 15", "languages": "Abyssal, Common, Infernal, telepathy 60 ft.",
        "attacks": "Claw (fiend form only) +5 1d6+3 slashing; Charm (DC 15 WIS or charmed 24h)",
        "traits": "Telepathic Bond. Shapechanger. Draining Kiss: 5d10+5 psychic, reduces HP max.",
        "alignment": "Neutral Evil",
    },

    # ── CR 5 ──────────────────────────────────────────────────────
    "troll": {
        "name": "Troll", "cr": 5, "type": "Large giant",
        "hp": 84, "ac": 15, "speed": "30 ft.",
        "str": 18, "dex": 13, "con": 20, "int": 7, "wis": 9, "cha": 7,
        "skills": "Perception +2", "senses": "Darkvision 60 ft., PP 12", "languages": "Giant",
        "attacks": "Multiattack (3): Bite +7 1d6+4 piercing; Claws +7 2d6+4 slashing",
        "traits": "Keen Smell. Regeneration: Regain 10 HP/turn unless took acid or fire damage this turn.",
        "alignment": "Chaotic Evil",
    },
    "hill giant": {
        "name": "Hill Giant", "cr": 5, "type": "Huge giant",
        "hp": 105, "ac": 13, "speed": "40 ft.",
        "str": 21, "dex": 8, "con": 19, "int": 5, "wis": 9, "cha": 6,
        "skills": "Perception +2", "senses": "PP 12", "languages": "Giant",
        "attacks": "Multiattack (2): Greatclub +8 3d8+5 bludgeoning; Rock +8 range 60/240 ft. 3d10+5 bludgeoning",
        "traits": "",
        "alignment": "Chaotic Evil",
    },
    "flesh golem": {
        "name": "Flesh Golem", "cr": 5, "type": "Medium construct",
        "hp": 93, "ac": 9, "speed": "30 ft.",
        "str": 19, "dex": 9, "con": 18, "int": 6, "wis": 10, "cha": 5,
        "immunities": "Lightning, Poison; Bludgeoning/Piercing/Slashing from nonmagical non-adamantine weapons; Charmed, Exhaustion, Frightened, Paralyzed, Petrified, Poisoned",
        "senses": "Darkvision 60 ft., PP 10", "languages": "understands creator's languages",
        "attacks": "Multiattack (2): Slam +7 2d8+4 bludgeoning",
        "traits": "Aversion to Fire: If takes fire damage, disadvantage on attacks/ability checks until next turn. Berserk: If ≤40 HP, may go berserk, attacking nearest creature. Immutable Form. Magic Resistance.",
        "alignment": "Neutral",
    },
    "vampire spawn": {
        "name": "Vampire Spawn", "cr": 5, "type": "Medium undead",
        "hp": 82, "ac": 15, "speed": "30 ft.",
        "str": 16, "dex": 16, "con": 16, "int": 11, "wis": 10, "cha": 12,
        "skills": "Perception +3, Stealth +6",
        "resist": "Necrotic; Bludgeoning/Piercing/Slashing from nonmagical weapons",
        "immunities": "Poison, Exhaustion, Poisoned",
        "senses": "Darkvision 60 ft., PP 13", "languages": "Languages known in life",
        "attacks": "Multiattack (2): Claws +6 2d4+3 slashing; Bite +6 1d6+3 piercing + 2d6 necrotic (DC 13 or max HP reduced)",
        "traits": "Regeneration 10 HP/turn (not in sunlight or running water). Spider Climb. Vampire Weaknesses (sunlight, running water, stake).",
        "alignment": "Neutral Evil",
    },

    # ── CR 6 ──────────────────────────────────────────────────────
    "medusa": {
        "name": "Medusa", "cr": 6, "type": "Medium monstrosity",
        "hp": 127, "ac": 15, "speed": "30 ft.",
        "str": 10, "dex": 15, "con": 16, "int": 12, "wis": 13, "cha": 15,
        "skills": "Deception +5, Insight +4, Perception +4, Stealth +5",
        "senses": "Darkvision 60 ft., PP 14", "languages": "Common",
        "attacks": "Multiattack (3): Snake Hair +5 1d4+2 piercing + 4d6 poison (DC 14 CON halves); Shortsword +5 1d6+2 piercing; Longbow +5 range 150/600 ft. 1d8+2 piercing",
        "traits": "Petrifying Gaze: DC 14 CON at start of turn or Petrified (via Restrained → Petrified progression). Averting gaze imposes disadvantage on attacks.",
        "alignment": "Lawful Evil",
    },
    "wyvern": {
        "name": "Wyvern", "cr": 6, "type": "Large dragon",
        "hp": 110, "ac": 13, "speed": "20 ft., fly 80 ft.",
        "str": 19, "dex": 10, "con": 16, "int": 5, "wis": 12, "cha": 6,
        "skills": "Perception +4", "senses": "Darkvision 60 ft., PP 14", "languages": "—",
        "attacks": "Multiattack (2): Bite +7 2d6+4 piercing; Stinger +7 2d6+4 piercing + 7d6 poison (DC 15 CON halves)",
        "traits": "",
        "alignment": "Unaligned",
    },

    # ── CR 7 ──────────────────────────────────────────────────────
    "stone giant": {
        "name": "Stone Giant", "cr": 7, "type": "Huge giant",
        "hp": 126, "ac": 17, "speed": "40 ft.",
        "str": 23, "dex": 15, "con": 20, "int": 10, "wis": 12, "cha": 9,
        "saves": "DEX +5, CON +8, WIS +4",
        "skills": "Athletics +12, Perception +4",
        "senses": "Darkvision 60 ft., PP 14", "languages": "Giant",
        "attacks": "Multiattack (2): Greatclub +9 3d8+6 bludgeoning; Rock +9 range 60/240 ft. 4d10+6 bludgeoning (DC 17 STR or knocked prone)",
        "traits": "Stone Camouflage: Advantage on Stealth in rocky terrain.",
        "alignment": "Neutral",
    },

    # ── CR 8 ──────────────────────────────────────────────────────
    "frost giant": {
        "name": "Frost Giant", "cr": 8, "type": "Huge giant",
        "hp": 138, "ac": 15, "speed": "40 ft.",
        "str": 23, "dex": 9, "con": 21, "int": 9, "wis": 10, "cha": 12,
        "saves": "CON +8, WIS +3, CHA +4",
        "skills": "Athletics +9, Perception +3",
        "immunities": "Cold",
        "senses": "PP 13", "languages": "Giant",
        "attacks": "Multiattack (2): Greataxe +9 3d12+6 slashing; Rock +9 range 60/240 ft. 4d10+6 bludgeoning",
        "traits": "",
        "alignment": "Neutral Evil",
    },
    "hydra": {
        "name": "Hydra", "cr": 8, "type": "Huge monstrosity",
        "hp": 172, "ac": 15, "speed": "30 ft., swim 30 ft.",
        "str": 20, "dex": 12, "con": 20, "int": 2, "wis": 10, "cha": 7,
        "skills": "Perception +6", "senses": "Darkvision 60 ft., PP 16", "languages": "—",
        "attacks": "Multiattack (starts 5 heads): Bite +8 per head 1d10+5 piercing",
        "traits": "Hold Breath 1 hour. Multiple Heads: Advantage on saves vs. Blinded/Charmed/Deafened/Frightened/Stunned/Unconscious. Reactive Heads: Extra reaction per extra head. Wakeful: One head always awake. Severed Heads grow back (2 per head removed unless fire damage used).",
        "alignment": "Unaligned",
    },

    # ── CR 9 ──────────────────────────────────────────────────────
    "fire giant": {
        "name": "Fire Giant", "cr": 9, "type": "Huge giant",
        "hp": 162, "ac": 18, "speed": "30 ft.",
        "str": 25, "dex": 9, "con": 23, "int": 10, "wis": 14, "cha": 13,
        "saves": "DEX +2, CON +9, CHA +4",
        "skills": "Athletics +10, Perception +5",
        "immunities": "Fire",
        "senses": "PP 15", "languages": "Giant",
        "attacks": "Multiattack (2): Greatsword +10 6d6+7 slashing; Rock +10 range 60/240 ft. 4d10+7 bludgeoning",
        "traits": "",
        "alignment": "Lawful Evil",
    },

    # ── CR 10 ─────────────────────────────────────────────────────
    "stone golem": {
        "name": "Stone Golem", "cr": 10, "type": "Large construct",
        "hp": 178, "ac": 17, "speed": "30 ft.",
        "str": 22, "dex": 9, "con": 20, "int": 3, "wis": 11, "cha": 1,
        "immunities": "Poison, Psychic; Bludgeoning/Piercing/Slashing from nonmagical non-adamantine weapons; Charmed, Exhaustion, Frightened, Paralyzed, Petrified, Poisoned",
        "senses": "Darkvision 120 ft., PP 10", "languages": "understands creator",
        "attacks": "Multiattack (2): Slam +10 3d8+6 bludgeoning",
        "traits": "Immutable Form. Magic Resistance. Magic Weapons. Slow (recharge 5-6): DC 17 WIS or speed halved and no bonus actions/reactions for 1 min.",
        "alignment": "Unaligned",
    },

    # ── CR 11 ─────────────────────────────────────────────────────
    "remorhaz": {
        "name": "Remorhaz", "cr": 11, "type": "Huge monstrosity",
        "hp": 195, "ac": 17, "speed": "30 ft., burrow 20 ft.",
        "str": 24, "dex": 13, "con": 21, "int": 4, "wis": 10, "cha": 5,
        "immunities": "Cold, Fire",
        "senses": "Darkvision 60 ft., Tremorsense 60 ft., PP 10", "languages": "—",
        "attacks": "Bite +11 6d10+7 piercing; Swallow (grappled target DC 17 STR or swallowed, 6d6 acid/turn)",
        "traits": "Heated Body: 3d6 fire to those grappling or in contact.",
        "alignment": "Unaligned",
    },

    # ── CR 12 ─────────────────────────────────────────────────────
    "archmage": {
        "name": "Archmage", "cr": 12, "type": "Medium humanoid",
        "hp": 99, "ac": 12, "speed": "30 ft.",
        "str": 10, "dex": 14, "con": 12, "int": 20, "wis": 15, "cha": 16,
        "saves": "INT +9, WIS +6",
        "skills": "Arcana +13, History +13",
        "resist": "Damage from spells; Bludgeoning/Piercing/Slashing from nonmagical weapons (stoneskin)",
        "senses": "PP 12", "languages": "Any six",
        "attacks": "Dagger +6 1d4+2 piercing. Spells: Fireball, Cone of Cold, Scrying, Time Stop, Wish (and many more)",
        "traits": "Magic Resistance. Spellcasting INT 20 DC 17 +9 to hit. 6th-level slots used for signature spells.",
        "alignment": "Any",
    },
    "iron golem": {
        "name": "Iron Golem", "cr": 16, "type": "Large construct",
        "hp": 210, "ac": 20, "speed": "30 ft.",
        "str": 24, "dex": 9, "con": 20, "int": 3, "wis": 11, "cha": 1,
        "immunities": "Fire, Poison, Psychic; Bludgeoning/Piercing/Slashing from nonmagical non-adamantine; Charmed, Exhaustion, Frightened, Paralyzed, Petrified, Poisoned",
        "senses": "Darkvision 120 ft., PP 10", "languages": "understands creator",
        "attacks": "Multiattack (2): Slam +13 3d10+7 bludgeoning; Sword +13 3d10+7 slashing; Poison Breath (recharge 6): 30 ft. cone, DC 19 CON or 10d8 poison (half on save)",
        "traits": "Fire Absorption: Fire heals it. Immutable Form. Magic Resistance. Magic Weapons.",
        "alignment": "Unaligned",
    },

    # ── CR 13 ─────────────────────────────────────────────────────
    "deva": {
        "name": "Deva", "cr": 10, "type": "Medium celestial",
        "hp": 136, "ac": 17, "speed": "30 ft., fly 90 ft.",
        "str": 18, "dex": 18, "con": 18, "int": 17, "wis": 20, "cha": 20,
        "saves": "WIS +9, CHA +9",
        "skills": "Insight +9, Perception +9",
        "resist": "Radiant; Bludgeoning/Piercing/Slashing from nonmagical weapons",
        "immunities": "Charmed, Exhaustion, Frightened",
        "senses": "Darkvision 120 ft., PP 19", "languages": "All, telepathy 120 ft.",
        "attacks": "Multiattack (2): Mace +8 1d6+4 bludgeoning + 4d8 radiant; Healing Touch (3/day): 20 HP + cure conditions",
        "traits": "Angelic Weapons (+4d8 radiant included). Divine Awareness: Knows if it hears a lie. Magic Resistance. Shapechanger. Spellcasting WIS DC 17.",
        "alignment": "Lawful Good",
    },

    # ── CR 15 ─────────────────────────────────────────────────────
    "purple worm": {
        "name": "Purple Worm", "cr": 15, "type": "Gargantuan monstrosity",
        "hp": 247, "ac": 18, "speed": "50 ft., burrow 30 ft.",
        "str": 28, "dex": 7, "con": 22, "int": 1, "wis": 8, "cha": 4,
        "saves": "CON +11, WIS +4",
        "immunities": "Poison, Poisoned",
        "senses": "Blindsight 30 ft., Tremorsense 60 ft., PP 9", "languages": "—",
        "attacks": "Multiattack (2): Bite +14 3d8+9 piercing; Tail Stinger +14 3d6+9 piercing + 7d6 poison (DC 19 CON halves); Swallow (DC 19 STR or swallowed, 6d6 acid/turn)",
        "traits": "Tunneler: Creates 10 ft. diameter tunnels.",
        "alignment": "Unaligned",
    },
    "vampire": {
        "name": "Vampire", "cr": 13, "type": "Medium undead (shapechanger)",
        "hp": 144, "ac": 16, "speed": "30 ft.",
        "str": 18, "dex": 18, "con": 18, "int": 17, "wis": 15, "cha": 18,
        "saves": "DEX +9, WIS +7, CHA +9",
        "skills": "Perception +7, Stealth +9",
        "resist": "Necrotic; Bludgeoning/Piercing/Slashing from nonmagical weapons",
        "immunities": "Poison, Exhaustion, Poisoned",
        "senses": "Darkvision 120 ft., PP 17", "languages": "Languages known in life",
        "attacks": "Multiattack (2): Unarmed Strike +9 1d8+4 bludgeoning; Bite +9 1d6+4 piercing + 3d6 necrotic (DC 15 or max HP reduced)",
        "traits": "Shapechanger (bat/mist). Legendary Resistance (3/day). Misty Escape. Regeneration 20/turn (not in sunlight/running water). Spider Climb. Vampire Weaknesses (sunlight, running water, stake).",
        "alignment": "Lawful Evil",
    },

    # ── CR 17 ─────────────────────────────────────────────────────
    "death knight": {
        "name": "Death Knight", "cr": 17, "type": "Medium undead",
        "hp": 180, "ac": 20, "speed": "30 ft.",
        "str": 20, "dex": 11, "con": 20, "int": 12, "wis": 16, "cha": 18,
        "saves": "DEX +6, WIS +9, CHA +10",
        "immunities": "Necrotic, Poison, Exhaustion, Frightened, Poisoned",
        "senses": "Darkvision 120 ft., PP 13", "languages": "Abyssal, Common",
        "attacks": "Multiattack (3): Longsword +11 1d8+5 slashing + 4d8 necrotic; Hellfire Orb (recharge 5-6): DC 18 DEX, 10d6 fire + 10d6 necrotic (half on save)",
        "traits": "Magic Resistance. Marshal Undead: Nearby undead have advantage on saves. Paladin Spellcasting DC 18. Legendary Resistance (3/day).",
        "alignment": "Chaotic Evil",
    },

    # ── CR 20+ ────────────────────────────────────────────────────
    "lich": {
        "name": "Lich", "cr": 21, "type": "Medium undead",
        "hp": 135, "ac": 17, "speed": "30 ft.",
        "str": 11, "dex": 16, "con": 16, "int": 20, "wis": 14, "cha": 16,
        "saves": "CON +10, INT +12, WIS +9",
        "skills": "Arcana +18, History +12, Insight +9, Perception +9",
        "resist": "Cold, Lightning, Necrotic; Bludgeoning/Piercing/Slashing from nonmagical weapons",
        "immunities": "Poison, Charmed, Exhaustion, Frightened, Paralyzed, Poisoned",
        "senses": "Truesight 120 ft., PP 19", "languages": "Common + up to 5 others",
        "attacks": "Paralyzing Touch +12 3d6 cold (DC 18 CON or Paralyzed for 1 min); Spells INT DC 20 +12 to hit",
        "traits": "Legendary Resistance (3/day). Rejuvenation (phylactery). Legendary Actions (3). Spellcasting: Finger of Death, Power Word Kill, Time Stop, Disintegrate, etc.",
        "alignment": "Any Evil",
    },
    "tarrasque": {
        "name": "Tarrasque", "cr": 30, "type": "Gargantuan monstrosity (titan)",
        "hp": 676, "ac": 25, "speed": "40 ft.",
        "str": 30, "dex": 11, "con": 30, "int": 3, "wis": 11, "cha": 11,
        "saves": "INT +5, WIS +9, CHA +9",
        "immunities": "Fire, Poison; Bludgeoning/Piercing/Slashing from nonmagical weapons; Charmed, Frightened, Paralyzed, Poisoned",
        "senses": "Blindsight 120 ft., PP 10", "languages": "—",
        "attacks": "Multiattack (5): Bite +19 4d12+10 piercing; Claw +19 4d8+10 slashing; Horn +19 4d6+10 piercing; Tail +19 4d8+10 bludgeoning; Swallow. Frightful Presence DC 17 WIS or Frightened.",
        "traits": "Legendary Resistance (3/day). Magic Resistance. Reflective Carapace: spells (cone/line/spell attack) have 1-in-6 chance of reflecting. Siege Monster: +3x damage vs structures. Legendary Actions (5). Regeneration 30 HP/turn.",
        "alignment": "Unaligned",
    },

    # ── Dragons ───────────────────────────────────────────────────
    "young red dragon": {
        "name": "Young Red Dragon", "cr": 10, "type": "Large dragon",
        "hp": 178, "ac": 18, "speed": "40 ft., climb 40 ft., fly 80 ft.",
        "str": 23, "dex": 10, "con": 21, "int": 14, "wis": 11, "cha": 19,
        "saves": "DEX +4, CON +9, WIS +4, CHA +8",
        "skills": "Perception +8, Stealth +4",
        "immunities": "Fire",
        "senses": "Blindsight 30 ft., Darkvision 120 ft., PP 18", "languages": "Common, Draconic",
        "attacks": "Multiattack (3): Bite +10 2d10+6 piercing; Claw +10 2d6+6 slashing; Fire Breath (recharge 5-6): 30 ft. cone, DC 17 DEX or 16d6 fire (half on save)",
        "traits": "",
        "alignment": "Chaotic Evil",
    },
    "adult red dragon": {
        "name": "Adult Red Dragon", "cr": 17, "type": "Huge dragon",
        "hp": 256, "ac": 19, "speed": "40 ft., climb 40 ft., fly 80 ft.",
        "str": 27, "dex": 10, "con": 25, "int": 16, "wis": 13, "cha": 21,
        "saves": "DEX +6, CON +13, WIS +7, CHA +11",
        "skills": "Perception +13, Stealth +6",
        "immunities": "Fire",
        "senses": "Blindsight 60 ft., Darkvision 120 ft., PP 23", "languages": "Common, Draconic",
        "attacks": "Multiattack (3 + Legendary): Bite +14 2d10+8; Claw +14 2d6+8; Tail +14 2d8+8. Fire Breath (recharge 5-6): 60 ft. cone DC 21 DEX 26d6 fire (half). Legendary Actions (3).",
        "traits": "Frightful Presence DC 19 WIS. Legendary Resistance (3/day). Magic Resistance.",
        "alignment": "Chaotic Evil",
    },
    "ancient red dragon": {
        "name": "Ancient Red Dragon", "cr": 24, "type": "Gargantuan dragon",
        "hp": 546, "ac": 22, "speed": "40 ft., climb 40 ft., fly 80 ft.",
        "str": 30, "dex": 10, "con": 29, "int": 18, "wis": 15, "cha": 23,
        "saves": "DEX +7, CON +16, WIS +9, CHA +13",
        "skills": "Perception +16, Stealth +7",
        "immunities": "Fire",
        "senses": "Blindsight 60 ft., Darkvision 120 ft., PP 26", "languages": "Common, Draconic",
        "attacks": "Multiattack (3 + Legendary): Bite +17 4d10+10; Claw +17 4d6+10; Tail +17 4d8+10. Fire Breath (recharge 5-6): 90 ft. cone DC 24 DEX 26d6 fire (half). Legendary Actions (3).",
        "traits": "Frightful Presence DC 21 WIS. Legendary Resistance (3/day). Tail Attack legendary action.",
        "alignment": "Chaotic Evil",
    },
    "young green dragon": {
        "name": "Young Green Dragon", "cr": 8, "type": "Large dragon",
        "hp": 136, "ac": 18, "speed": "40 ft., fly 80 ft., swim 40 ft.",
        "str": 19, "dex": 12, "con": 17, "int": 16, "wis": 13, "cha": 15,
        "saves": "DEX +4, CON +6, WIS +4, CHA +5",
        "skills": "Deception +5, Perception +7, Stealth +4",
        "immunities": "Poison, Poisoned",
        "senses": "Blindsight 30 ft., Darkvision 120 ft., PP 17", "languages": "Common, Draconic",
        "attacks": "Multiattack (3): Bite +7 2d10+4 piercing; Claw +7 2d6+4 slashing; Poison Breath (recharge 5-6): 30 ft. cone DC 14 CON 12d6 poison (half)",
        "traits": "Amphibious.",
        "alignment": "Lawful Evil",
    },

    # ── Undead ────────────────────────────────────────────────────
    "zombie": {
        "name": "Zombie", "cr": 0.25, "type": "Medium undead",
        "hp": 22, "ac": 8, "speed": "20 ft.",
        "str": 13, "dex": 6, "con": 16, "int": 3, "wis": 6, "cha": 5,
        "saves": "WIS +0",
        "immunities": "Poison, Exhaustion, Poisoned",
        "senses": "Darkvision 60 ft., PP 8", "languages": "understands languages in life",
        "attacks": "Slam +3 1d6+1 bludgeoning",
        "traits": "Undead Fortitude: DC 5+damage taken CON save to drop to 1 HP instead of 0.",
        "alignment": "Neutral Evil",
    },

    # ── Aberrations ───────────────────────────────────────────────
    "mind flayer": {
        "name": "Mind Flayer", "cr": 7, "type": "Medium aberration",
        "hp": 71, "ac": 15, "speed": "30 ft.",
        "str": 11, "dex": 12, "con": 12, "int": 19, "wis": 17, "cha": 17,
        "saves": "INT +7, WIS +6, CHA +6",
        "skills": "Arcana +7, Deception +6, Insight +6, Perception +6, Persuasion +6, Stealth +4",
        "resist": "Psychic",
        "senses": "Darkvision 120 ft., PP 16", "languages": "Deep Speech, Undercommon, telepathy 120 ft.",
        "attacks": "Tentacles +7 2d10+4 psychic (DC 15 INT or Stunned 1 min); Extract Brain (stunned target, DC 15 INT or die, 10d10 psychic). Mind Blast (recharge 5-6): 60 ft. cone DC 15 INT or Stunned 1 min",
        "traits": "Magic Resistance. Telepathic Bond.",
        "alignment": "Lawful Evil",
    },

    # ── Beasts ────────────────────────────────────────────────────
    "giant spider": {
        "name": "Giant Spider", "cr": 1, "type": "Large beast",
        "hp": 26, "ac": 14, "speed": "30 ft., climb 30 ft.",
        "str": 14, "dex": 16, "con": 12, "int": 2, "wis": 11, "cha": 4,
        "skills": "Stealth +7", "senses": "Blindsight 10 ft., Darkvision 60 ft., PP 10", "languages": "—",
        "attacks": "Bite +5 1d8+3 piercing + 2d8 poison (DC 11 CON, 0 on save); Web (recharge 5-6) +5 range 30/60 ft. Restrained (DC 12 STR to escape)",
        "traits": "Spider Climb. Web Sense (tremorsense in web). Web Walker (ignores web movement restrictions).",
        "alignment": "Unaligned",
    },
}

# Build a sorted list and name→key lookup
MONSTER_LIST = sorted(MONSTERS.keys())

def find_monster(query: str):
    """Find a monster by partial or full name match. Returns (key, data) or (None, None)."""
    q = query.lower().strip()
    # Exact match first
    if q in MONSTERS:
        return q, MONSTERS[q]
    # Prefix match
    matches = [k for k in MONSTERS if k.startswith(q)]
    if len(matches) == 1:
        return matches[0], MONSTERS[matches[0]]
    # Substring match
    matches = [k for k in MONSTERS if q in k]
    if len(matches) == 1:
        return matches[0], MONSTERS[matches[0]]
    if len(matches) > 1:
        return None, matches   # ambiguous — return list
    return None, None

def monsters_at_cr(cr_val: float):
    """Return list of monster names at a given CR."""
    return [v["name"] for v in MONSTERS.values() if v["cr"] == cr_val]

def parse_cr(s: str) -> float:
    """Parse a CR string like '1/4', '5', '1/2' into float."""
    s = s.strip()
    if "/" in s:
        num, den = s.split("/", 1)
        return int(num) / int(den)
    return float(s)
