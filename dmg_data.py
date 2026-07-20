#!/usr/bin/env python3
"""
D&D 5e SRD 5.2 (Creative Commons) — Dungeon Master's Guide Data

Contains:
  - Magic item database (40+ items)
  - Treasure tables by CR range (individual and hoard)
  - Encounter XP thresholds by party level and difficulty
"""

import random

# ----------------------------------------------------------------
# Magic Items  (SRD 5.2 CC)
# ----------------------------------------------------------------

MAGIC_ITEMS = {
    # ── Common ───────────────────────────────────────────────────
    "bag of tricks": {
        "name": "Bag of Tricks", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": False,
        "desc": "Pull a random figurine from the bag (up to 3/day). It transforms into a beast for up to 1 minute or until reduced to 0 HP. Beasts: Weasel, Cat, Badger, Axe Beak, Owl, Flying Snake, etc.",
    },
    "bag of holding": {
        "name": "Bag of Holding", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": False,
        "desc": "Holds up to 500 lb / 64 cu ft inside. Weighs 15 lb regardless of contents. Retrieving an item is an action. Placing inside another extradimensional space destroys both.",
    },
    "cloak of protection": {
        "name": "Cloak of Protection", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": True,
        "desc": "+1 bonus to AC and saving throws while worn.",
    },
    "goggles of night": {
        "name": "Goggles of Night", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": False,
        "desc": "Darkvision 60 ft. while worn. If you already have darkvision, range extended by 60 ft.",
    },
    "hat of disguise": {
        "name": "Hat of Disguise", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": True,
        "desc": "Cast Disguise Self at will while wearing the hat.",
    },
    "rope of climbing": {
        "name": "Rope of Climbing", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": False,
        "desc": "60 ft. animated rope. Can animate on command, fasten to surfaces, knot/unknot, wrap around objects. Holds up to 3,000 lb.",
    },
    "immovable rod": {
        "name": "Immovable Rod", "rarity": "uncommon", "type": "Rod",
        "attunement": False,
        "desc": "Press the button to fix in place in space. Holds up to 8,000 lb before it deactivates. Strength (DC 30) to move 10 ft.",
    },
    "potion of healing": {
        "name": "Potion of Healing", "rarity": "common", "type": "Potion",
        "attunement": False,
        "desc": "Drink as an action: regain 2d4+2 HP.",
    },
    "potion of greater healing": {
        "name": "Potion of Greater Healing", "rarity": "uncommon", "type": "Potion",
        "attunement": False,
        "desc": "Drink as an action: regain 4d4+4 HP.",
    },
    "potion of superior healing": {
        "name": "Potion of Superior Healing", "rarity": "rare", "type": "Potion",
        "attunement": False,
        "desc": "Drink as an action: regain 8d4+8 HP.",
    },

    # ── Uncommon ──────────────────────────────────────────────────
    "bracers of archery": {
        "name": "Bracers of Archery", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": True,
        "desc": "+2 bonus to attack rolls with longbows and shortbows while wearing these bracers.",
    },
    "broom of flying": {
        "name": "Broom of Flying", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": False,
        "desc": "Command word: fly speed 50 ft. Carries up to 400 lb at 30 ft.; over 200 lb reduces speed to 30 ft. Returns to you if abandoned.",
    },
    "cape of the mountebank": {
        "name": "Cape of the Mountebank", "rarity": "rare", "type": "Wondrous item",
        "attunement": False,
        "desc": "Use action: cast Dimension Door. The cape can't be used this way again until the next dawn.",
    },
    "chime of opening": {
        "name": "Chime of Opening", "rarity": "rare", "type": "Wondrous item",
        "attunement": False,
        "desc": "10 charges. Ring it to open a door/chest/lock within 120 ft. (no action needed). One charge per use. Object must not be held shut by magic. Crumbles to dust when last charge used.",
    },
    "decanter of endless water": {
        "name": "Decanter of Endless Water", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": False,
        "desc": "Command words produce 1 gallon (Stream), 5 gallons (Fountain), or 30 gallons as a geyser (Geyser — 1d4 bludgeoning if aimed at creature, DC 13 STR or knocked prone). Each use can be done once per round.",
    },
    "gem of brightness": {
        "name": "Gem of Brightness", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": False,
        "desc": "50 charges. Shed dim light 30 ft. (0 charges), bright 30 ft. (1 charge/turn), or flash (5 charges, DC 15 CON or blinded for 1 min). Recharge: doesn't.",
    },
    "gloves of swimming and climbing": {
        "name": "Gloves of Swimming and Climbing", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": True,
        "desc": "While wearing: climbing and swimming don't cost extra movement. +5 bonus to Athletics checks involving climbing or swimming.",
    },
    "headband of intellect": {
        "name": "Headband of Intellect", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": True,
        "desc": "Your Intelligence score is 19 while you wear this headband. No effect if your Intelligence is already 19 or higher.",
    },
    "helm of comprehending languages": {
        "name": "Helm of Comprehending Languages", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": False,
        "desc": "While wearing this helm, you can cast Comprehend Languages as a ritual at will.",
    },
    "helm of telepathy": {
        "name": "Helm of Telepathy", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": True,
        "desc": "Cast Detect Thoughts at will (DC 13 WIS). While concentrating: communicate telepathically with the target within 120 ft.; implant a suggestion (DC 13 WIS).",
    },
    "lantern of revealing": {
        "name": "Lantern of Revealing", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": False,
        "desc": "Burns for 6 hrs on 1 pint of oil. Bright light 30 ft., dim 60 ft. Invisible creatures and objects visible in bright light. Works against illusions.",
    },

    # ── Rare ──────────────────────────────────────────────────────
    "+1 weapon": {
        "name": "+1 Weapon", "rarity": "uncommon", "type": "Weapon",
        "attunement": False,
        "desc": "+1 bonus to attack and damage rolls made with this magic weapon.",
    },
    "+2 weapon": {
        "name": "+2 Weapon", "rarity": "rare", "type": "Weapon",
        "attunement": False,
        "desc": "+2 bonus to attack and damage rolls made with this magic weapon.",
    },
    "+3 weapon": {
        "name": "+3 Weapon", "rarity": "very rare", "type": "Weapon",
        "attunement": False,
        "desc": "+3 bonus to attack and damage rolls made with this magic weapon.",
    },
    "belt of giant strength (hill)": {
        "name": "Belt of Hill Giant Strength", "rarity": "rare", "type": "Wondrous item",
        "attunement": True,
        "desc": "STR score becomes 21 while wearing. No effect if your STR is already that or higher.",
    },
    "belt of giant strength (fire)": {
        "name": "Belt of Fire Giant Strength", "rarity": "very rare", "type": "Wondrous item",
        "attunement": True,
        "desc": "STR score becomes 25 while wearing.",
    },
    "belt of giant strength (storm)": {
        "name": "Belt of Storm Giant Strength", "rarity": "legendary", "type": "Wondrous item",
        "attunement": True,
        "desc": "STR score becomes 29 while wearing.",
    },
    "boots of speed": {
        "name": "Boots of Speed", "rarity": "rare", "type": "Wondrous item",
        "attunement": True,
        "desc": "Bonus action: click heels to double walking speed and impose disadvantage on opportunity attacks against you. Lasts 10 min. Recharge at dawn.",
    },
    "bracers of defense": {
        "name": "Bracers of Defense", "rarity": "rare", "type": "Wondrous item",
        "attunement": True,
        "desc": "+2 bonus to AC while wearing and not using armor or a shield.",
    },
    "carpet of flying": {
        "name": "Carpet of Flying", "rarity": "very rare", "type": "Wondrous item",
        "attunement": False,
        "desc": "Sizes vary: 3×5 ft. (200 lb, 80 ft. speed), 4×6 ft. (400 lb, 60 ft. speed), 5×7 ft. (600 lb, 40 ft. speed), 6×9 ft. (800 lb, 30 ft. speed). Command word activates.",
    },
    "cloak of displacement": {
        "name": "Cloak of Displacement", "rarity": "rare", "type": "Wondrous item",
        "attunement": True,
        "desc": "Attackers have disadvantage on attack rolls against you. Effect ends until start of your next turn when you take damage. Dispelled by restraint/incapacitation.",
    },
    "cloak of elvenkind": {
        "name": "Cloak of Elvenkind", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": True,
        "desc": "Advantage on Stealth checks to hide. Disadvantage on Perception checks to find you.",
    },
    "cloak of the bat": {
        "name": "Cloak of the Bat", "rarity": "rare", "type": "Wondrous item",
        "attunement": True,
        "desc": "Advantage on Stealth in dim light or darkness. Fly speed 40 ft. in darkness (can't use in light). Polymorph into a bat and back (retaining mental ability scores).",
    },
    "flame tongue": {
        "name": "Flame Tongue", "rarity": "rare", "type": "Weapon (any sword)",
        "attunement": True,
        "desc": "Command word ignites the blade: +2d6 fire damage, bright light 40 ft., dim 40 ft. beyond. Extinguished if sheathed.",
    },
    "frost brand": {
        "name": "Frost Brand", "rarity": "very rare", "type": "Weapon (any sword)",
        "attunement": True,
        "desc": "+1d6 cold damage. Resistance to fire damage. In freezing temperatures, bright light 10 ft. When you take fire damage, 50% chance it automatically extinguishes nonmagical fires within 30 ft.",
    },
    "gauntlets of ogre power": {
        "name": "Gauntlets of Ogre Power", "rarity": "uncommon", "type": "Wondrous item",
        "attunement": True,
        "desc": "STR score becomes 19 while wearing. No effect if STR is 19+.",
    },
    "holy avenger": {
        "name": "Holy Avenger", "rarity": "legendary", "type": "Weapon (any sword)",
        "attunement": True,
        "desc": "Requires Paladin. +3 to attack and damage. +2d10 radiant to fiends and undead. Aura: allies within 10 ft. advantage on saves vs. spells and magical effects.",
    },
    "javelin of lightning": {
        "name": "Javelin of Lightning", "rarity": "uncommon", "type": "Weapon (javelin)",
        "attunement": False,
        "desc": "When thrown: 5 ft. wide lightning bolt to end of range (100/400 ft.). Creatures in path DC 13 DEX or 4d6 lightning (half on save). Reverts to mundane javelin after use.",
    },
    "necklace of fireballs": {
        "name": "Necklace of Fireballs", "rarity": "rare", "type": "Wondrous item",
        "attunement": False,
        "desc": "1-9 beads. Throw as an action (range 60 ft.): Fireball DC 15 DEX. 1 bead = 3d6; each additional bead adds 1d6 (up to 8 beads at once). If destroyed, all remaining beads detonate.",
    },
    "ring of protection": {
        "name": "Ring of Protection", "rarity": "rare", "type": "Ring",
        "attunement": True,
        "desc": "+1 bonus to AC and saving throws.",
    },
    "ring of invisibility": {
        "name": "Ring of Invisibility", "rarity": "legendary", "type": "Ring",
        "attunement": True,
        "desc": "Turn invisible as an action. Remain invisible until you attack, cast a spell, or remove the ring.",
    },
    "ring of spell storing": {
        "name": "Ring of Spell Storing", "rarity": "rare", "type": "Ring",
        "attunement": True,
        "desc": "Stores up to 5 levels of spells cast into it. Any creature attuned to it can cast stored spells using your spell save DC and attack bonus.",
    },
    "rod of lordly might": {
        "name": "Rod of Lordly Might", "rarity": "legendary", "type": "Rod",
        "attunement": True,
        "desc": "6 buttons: +3 flaming longsword; +4 battleaxe with DC 17 STR or arm paralyzed; +4 warhammer; drain life (DC 17 CON or 4d6 necrotic); holds target in place (DC 17 STR); ladder extending up to 50 ft.",
    },
    "staff of fire": {
        "name": "Staff of Fire", "rarity": "very rare", "type": "Staff",
        "attunement": True,
        "desc": "Requires Druid, Sorcerer, Warlock, or Wizard. 10 charges. Burning Hands (1), Fireball (3), or Wall of Fire (4). Regain 1d6+4 charges at dawn. Destroyed if last charge expended (5% chance).",
    },
    "staff of the magi": {
        "name": "Staff of the Magi", "rarity": "legendary", "type": "Staff",
        "attunement": True,
        "desc": "Requires Sorcerer, Warlock, or Wizard. 50 charges. Absorb spells. Many spells (1-7 charges). Retributive Strike: break the staff for massive area explosion.",
    },
    "vorpal sword": {
        "name": "Vorpal Sword", "rarity": "legendary", "type": "Weapon (any sword with slashing)",
        "attunement": True,
        "desc": "+3 to attack and damage. Score a 20: immediately sever the head (killing most creatures). Doesn't work if the creature doesn't have a head, has Legendary Resistance left, or is immune to slashing.",
    },
    "wand of fireballs": {
        "name": "Wand of Fireballs", "rarity": "rare", "type": "Wand",
        "attunement": True,
        "desc": "Requires Spellcaster. 7 charges. Expend 1-3 charges: Fireball DC 15 DEX (as 3rd+extra levels). Regain 1d6+1 charges at dawn. Destroyed if last charge expended (5% chance).",
    },
    "wand of magic missiles": {
        "name": "Wand of Magic Missiles", "rarity": "uncommon", "type": "Wand",
        "attunement": False,
        "desc": "7 charges. Expend 1-3 charges: Magic Missile (1st-3rd level, no roll required). Regain 1d6+1 charges at dawn. Destroyed if last charge expended (5% chance).",
    },

    # ── Armor ─────────────────────────────────────────────────────
    "+1 armor": {
        "name": "+1 Armor", "rarity": "rare", "type": "Armor",
        "attunement": False,
        "desc": "+1 bonus to AC in addition to the armor's normal bonus.",
    },
    "+2 armor": {
        "name": "+2 Armor", "rarity": "very rare", "type": "Armor",
        "attunement": False,
        "desc": "+2 bonus to AC in addition to the armor's normal bonus.",
    },
    "+3 armor": {
        "name": "+3 Armor", "rarity": "legendary", "type": "Armor",
        "attunement": False,
        "desc": "+3 bonus to AC in addition to the armor's normal bonus.",
    },
    "animated shield": {
        "name": "Animated Shield", "rarity": "very rare", "type": "Armor (shield)",
        "attunement": True,
        "desc": "Bonus action: animate the shield. It hovers protecting you as if you held it, but leaves your hands free. Lasts 1 min or until incapacitated. Recharge: 1d4 hours.",
    },
    "demon armor": {
        "name": "Demon Armor", "rarity": "very rare", "type": "Armor (plate)",
        "attunement": True,
        "desc": "AC 18. Unarmed strikes: +1 to hit and 1d8 slashing. Cursed: can't be removed without Remove Curse. Disadvantage on attacks against demons.",
    },
    "mithral armor": {
        "name": "Mithral Armor", "rarity": "uncommon", "type": "Armor (medium or heavy, not hide)",
        "attunement": False,
        "desc": "Made of mithral — lightweight. No disadvantage on Stealth. No Strength requirement.",
    },
    "adamantine armor": {
        "name": "Adamantine Armor", "rarity": "uncommon", "type": "Armor (medium or heavy, not hide)",
        "attunement": False,
        "desc": "Any critical hit against you becomes a normal hit.",
    },
}

ITEM_RARITIES = ["common", "uncommon", "rare", "very rare", "legendary"]

ITEM_LIST = sorted(MAGIC_ITEMS.keys())

def find_item(query: str):
    """Partial name match. Returns (key, data) or (None, candidates)."""
    q = query.lower().strip()
    if q in MAGIC_ITEMS:
        return q, MAGIC_ITEMS[q]
    matches = [k for k in MAGIC_ITEMS if q in k]
    if len(matches) == 1:
        return matches[0], MAGIC_ITEMS[matches[0]]
    if len(matches) > 1:
        return None, matches
    return None, None

def random_item(rarity: str = None):
    """Return a random magic item, optionally filtered by rarity."""
    pool = list(MAGIC_ITEMS.values())
    if rarity:
        r = rarity.lower().strip()
        pool = [v for v in pool if v["rarity"].lower() == r]
    return random.choice(pool) if pool else None

def items_by_rarity(rarity: str):
    """Return names of all items at a given rarity."""
    r = rarity.lower().strip()
    return [v["name"] for v in MAGIC_ITEMS.values() if v["rarity"].lower() == r]

# ----------------------------------------------------------------
# Treasure Tables  (SRD 5.2 — simplified)
# ----------------------------------------------------------------

# Individual treasure by CR range
# Each entry: (dice_expr, multiplier, coin_type)
INDIVIDUAL_TREASURE = {
    # CR 0-4
    "cr04": [
        (lambda: random.randint(1,6)*3,   "cp"),
        (lambda: random.randint(1,6),      "sp"),
        (lambda: random.randint(1,4)*3,   "cp"),
        (lambda: random.randint(1,4)*2,   "sp"),
        (lambda: random.randint(1,4),      "gp"),
    ],
    # CR 5-10
    "cr510": [
        (lambda: random.randint(4,24)*10,  "cp"),
        (lambda: random.randint(1,6)*100,  "sp"),
        (lambda: random.randint(1,6)*10,   "ep"),
        (lambda: random.randint(1,6)*25,   "gp"),
        (lambda: random.randint(1,4)*50,   "gp"),
    ],
    # CR 11-16
    "cr1116": [
        (lambda: random.randint(4,24)*100,  "sp"),
        (lambda: random.randint(1,4)*100,   "ep"),
        (lambda: random.randint(1,10)*25,   "gp"),
        (lambda: random.randint(2,12)*250,  "gp"),
        (lambda: random.randint(1,4)*250,   "pp"),
    ],
    # CR 17+
    "cr17": [
        (lambda: random.randint(2,12)*250,  "ep"),
        (lambda: random.randint(2,8)*750,   "gp"),
        (lambda: random.randint(3,18)*500,  "gp"),
        (lambda: random.randint(1,10)*1000, "pp"),
        (lambda: random.randint(1,6)*1000,  "pp"),
    ],
}

# Hoard treasure by CR range — gems/art/magic items
HOARD_MAGIC = {
    "cr04": [
        "Roll a Trinket (common item)",
        "+1 Weapon",
        "Potion of Healing",
        "Wand of Magic Missiles",
        "Cloak of Protection",
        "Bag of Holding",
        "Hat of Disguise",
        "Rope of Climbing",
    ],
    "cr510": [
        "+2 Weapon", "Bracers of Defense", "Cloak of Displacement",
        "Staff of Fire", "Ring of Spell Storing", "Cape of the Mountebank",
        "Boots of Speed", "Necklace of Fireballs", "Flame Tongue",
        "Wand of Fireballs",
    ],
    "cr1116": [
        "+3 Weapon", "Holy Avenger", "Vorpal Sword",
        "Ring of Invisibility", "Staff of the Magi", "Rod of Lordly Might",
        "Belt of Storm Giant Strength", "Ring of Protection",
    ],
    "cr17": [
        "Holy Avenger", "Vorpal Sword", "Staff of the Magi",
        "Ring of Invisibility", "Rod of Lordly Might",
        "Belt of Storm Giant Strength", "+3 Armor",
    ],
}

def cr_bucket(cr: float) -> str:
    if cr <= 4:   return "cr04"
    if cr <= 10:  return "cr510"
    if cr <= 16:  return "cr1116"
    return "cr17"

def roll_individual_treasure(cr: float) -> str:
    """Generate individual treasure for a single creature at given CR."""
    bucket = cr_bucket(cr)
    roll = random.randint(1, 5) - 1   # pick one of the 5 entries
    fn, coin = INDIVIDUAL_TREASURE[bucket][roll]
    amount = fn()
    return f"{amount:,} {coin}"

def roll_hoard(cr: float):
    """Generate a hoard for an encounter at given CR. Returns (coins_str, items_list)."""
    bucket = cr_bucket(cr)
    coins_parts = []
    for fn, coin in INDIVIDUAL_TREASURE[bucket]:
        amount = fn() * random.randint(2, 6)   # hoards are bigger
        coins_parts.append(f"{amount:,} {coin}")

    # 1-3 magic items from the hoard table
    hoard_pool = HOARD_MAGIC[bucket]
    n_items = random.randint(1, min(3, len(hoard_pool)))
    items = random.sample(hoard_pool, n_items)

    return ", ".join(coins_parts), items

# ----------------------------------------------------------------
# Encounter XP Thresholds  (5e SRD — per character, by level)
# ----------------------------------------------------------------
# Difficulty: Easy / Medium / Hard / Deadly
# Index = level - 1

ENCOUNTER_THRESHOLDS = {
    # level: (easy, medium, hard, deadly)
    1:  (25,    50,    75,    100),
    2:  (50,    100,   150,   200),
    3:  (75,    150,   225,   400),
    4:  (125,   250,   375,   500),
    5:  (250,   500,   750,   1100),
    6:  (300,   600,   900,   1400),
    7:  (350,   750,   1100,  1700),
    8:  (450,   900,   1400,  2100),
    9:  (550,   1100,  1600,  2400),
    10: (600,   1200,  1900,  2800),
    11: (800,   1600,  2400,  3600),
    12: (1000,  2000,  3000,  4500),
    13: (1100,  2200,  3400,  5100),
    14: (1250,  2500,  3800,  5700),
    15: (1400,  2800,  4300,  6400),
    16: (1600,  3200,  4800,  7200),
    17: (2000,  3900,  5900,  8800),
    18: (2100,  4200,  6300,  9500),
    19: (2400,  4900,  7300,  10900),
    20: (2800,  5700,  8500,  12700),
}

DIFFICULTY_INDEX = {"easy": 0, "medium": 1, "hard": 2, "deadly": 3}

def encounter_xp_budget(party_level: int, party_size: int, difficulty: str) -> int:
    """Total XP budget for an encounter."""
    level  = max(1, min(20, party_level))
    thresholds = ENCOUNTER_THRESHOLDS[level]
    idx    = DIFFICULTY_INDEX.get(difficulty.lower(), 1)
    return thresholds[idx] * party_size
