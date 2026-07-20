# Talesman

An IRC bot for **irc.libera.chat** running a full **D&D 5e SRD 5.2** game system with Gemini AI integration, gold/points economy, and channel-based DM sessions.

Active in: `#gentoo-weed` · `##?` · `#jedi`

---

## Character Creation

Character creation happens entirely via **private message** — the bot won't flood the channel.

| Command | Description |
|---|---|
| `!newchar` | Start the 11-step D&D 5e character creation wizard (PM-based) |
| `!cancelchar` | Cancel an in-progress character creation |
| `!charsheet [nick]` | View your (or another player's) full 5e character sheet (sent via PM) |
| `!chardelete` | Permanently delete your 5e character |

### Wizard Steps
1. Character name
2. Race (14 options from SRD 5.2 — see below)
3. Class (12 options)
4. Background (12 options)
5. Alignment (9 options)
6. Ability scores — Standard Array `(15 14 13 12 10 8)` or roll `4d6 drop lowest`
7. Assign each score to STR / DEX / CON / INT / WIS / CHA
8. Class skill picks (automatically excludes background skills)
9. Half-Elf bonus skills if applicable
10–12. Personality · Ideal · Bond · Flaw (free text)

On completion the bot calculates and stores: HP, AC, initiative, proficiency bonus, all skill bonuses, saving throws, spell save DC, spell attack bonus, and passive Perception.

---

## Available Races (SRD 5.2)

Human · High Elf · Wood Elf · Hill Dwarf · Mountain Dwarf ·  
Lightfoot Halfling · Stout Halfling · Dragonborn · Forest Gnome ·  
Rock Gnome · Half-Elf · Half-Orc · Tiefling

Half-Elf gets an extra +1 to two ability scores of your choice and 2 bonus skills.  
Dragonborn picks their Draconic Ancestry (10 types, determines breath weapon and resistance).

---

## Available Classes (SRD 5.2)

Barbarian · Bard · Cleric · Druid · Fighter · Monk ·  
Paladin · Ranger · Rogue · Sorcerer · Warlock · Wizard

---

## Available Backgrounds (SRD 5.2)

Acolyte · Charlatan · Criminal · Entertainer · Folk Hero · Guild Artisan ·  
Hermit · Noble · Outlander · Sage · Sailor · Soldier

---

## Player Commands

### Character Status
| Command | Description |
|---|---|
| `!xp [nick]` | Show XP total, current level, and XP needed for next level |
| `!hp [nick]` | Show current / max HP with condition (Healthy / Wounded / Bloodied / Unconscious) |
| `!gold [nick]` / `!gp [nick]` | Check GP balance; alerts when eligible to `!cash` |
| `!inventory [nick]` | List inventory items |
| `!item drop <item>` | Drop an item from your inventory |

### Rolls
| Command | Description |
|---|---|
| `!roll <dice>` | Roll dice — e.g. `!roll 2d6+3` |
| `!skill <name>` | Roll a skill check using your character sheet (partial name match supported) |
| `!save <ability>` | Roll a saving throw — `str` `dex` `con` `int` `wis` `cha` |
| `!attack [target]` | Roll an attack using your class's primary ability + proficiency bonus |

### Gold Economy
| Command | Description |
|---|---|
| `!gold [nick]` | Check GP balance |
| `!pay <nick> <amount>` | Transfer GP to another player |
| `!cash` | Check gift card eligibility — 420 GP redeems for a $100 Visa gift card (PM n01d to arrange) |

> **chr0n** starts with **420 GP** already on account.  
> Every 1 GP earned in-game = 1 point toward the gift card.

---

## Session Commands

| Command | Description |
|---|---|
| `!session` | Show current DM, session title, scene, and duration |
| `!players` | Party roster — up to 4 rows in channel, full list sent to your PM if larger |
| `!ask <question>` | Ask Gemini AI anything |

---

## DM System

Anyone can claim the DM seat unless ops have locked it.  
DM commands are issued in the **channel** and apply to that channel's session.

### Claiming the Seat
| Command | Description |
|---|---|
| `!dm claim` | Take the DM seat (blocked if a DM is already active or seat is locked) |
| `!dm release` | Voluntarily give up the DM seat and end the session |

### Session Control
| Command | Description |
|---|---|
| `!dm start [title]` | Open a session with an optional title |
| `!dm end` | Close the active session |
| `!dm status` | Show session info (same as `!session`) |

### Narration
| Command | Description |
|---|---|
| `!dm narrate <text>` | Bold narration to the channel, surrounded by ✦ |
| `!dm n <text>` | Shorthand for narrate |
| `!dm scene <text>` | Set the current scene description (shown in `!session`) |
| `!dm roll <dice>` | Secret roll — result sent to DM via PM; channel sees "The DM rolls in secret…" |

### Awarding Players
| Command | Description |
|---|---|
| `!dm award <nick> <n> gp` | Award gold pieces to a player |
| `!dm award <nick> <n> xp` | Award XP; bot announces level-up automatically if threshold crossed |
| `!dm give <nick> <item>` | Place an item directly in a player's inventory |

### HP Management
| Command | Description |
|---|---|
| `!dm heal <nick> <n>` | Restore HP (capped at max) |
| `!dm damage <nick> <n>` | Deal damage — if HP reaches 0, character is killed and moved to the graveyard |
| `!dm dmg <nick> <n>` | Shorthand for damage |
| `!dm ambush <nick> <monster>` | DM-initiated monster attack — the named monster rolls against the player's AC and deals damage (or misses) |

---

## Combat

Players fight monsters from the SRD Monster Manual database. Combat is **one round per command call** — call `!fight` repeatedly to continue the encounter until one side is dead.

| Command | Description |
|---|---|
| `!fight <monster>` | Attack the named monster. Monster counterattacks. Repeat each round to continue. |

### How a round works
1. **Player attacks** — d20 + primary ability modifier + proficiency vs monster AC
2. **On hit** — 1d8 + ability mod damage (2d8 on a natural 20 critical)
3. **Monster HP bar** — shown after each hit if the monster survives
4. **Monster counterattacks** — uses the monster's actual attack bonus and damage from the stat block
5. **On a monster hit** — damage applied to player HP immediately

### Combat outcomes
- **Monster slain** — XP auto-awarded to the player; level-up announced if threshold crossed
- **Player killed** — character moved permanently to the **Graveyard** (see below)
- **Natural 20** — critical hit, damage dice doubled
- **Natural 1** — fumble, always a miss

> Each player tracks their own encounter. Monster HP persists between rounds until it dies or you switch to a different monster.

---

## Graveyard

Death is permanent. When a character's HP reaches 0 (from `!fight`, `!dm damage`, or `!dm ambush`), they are immediately buried with a full tombstone record. Dead characters **cannot** fight, use skills, or take any gameplay actions.

| Command | Description |
|---|---|
| `!graveyard` | List all fallen adventurers (name, nick, race/class/level, killer) |
| `!tombstone <nick>` | One-liner in channel + full record in PM: final stats, killer, killing blow, date of death, last words, items buried with them |
| `!rez <nick>` | **Admin/DM only** — resurrect a character with 1 HP, removing them from the graveyard |

### Tombstone contents
Every tombstone permanently records:
- Full character snapshot at time of death (race, class, level, all ability scores, skills, inventory)
- Cause of death and exact killing blow
- UTC timestamp
- Personality trait as "last words"
- Items they were carrying at death ("buried with")

---

## Ops-Only Commands

Channel operators (`@`) and bot admins bypass all cooldowns and have full control.

| Command | Description |
|---|---|
| `!dm set <nick>` | Appoint a specific player as DM, overriding whoever currently holds the seat |
| `!dm kick` | Remove the current DM and clear the session |
| `!dm lock <nick>` | Lock the DM seat so only `<nick>` can claim it |
| `!dm unlock` | Unlock the DM seat so anyone can claim it |

**Bot admins** (always treated as ops): `n01d` · `linkerage` · `ph0bos` · `n01`

---

## XP & Leveling

The bot uses official D&D 5e XP thresholds. When a DM awards XP that crosses a threshold, the bot automatically:
- Levels up the character
- Adds average HP per level (hit die average + CON modifier, min 1)
- Updates proficiency bonus at levels 5, 9, 13, 17
- Recalculates all proficient skill bonuses, saving throws, spell save DC, and spell attack bonus
- Announces the level-up in channel

| Level | XP Needed | Prof Bonus |
|---|---|---|
| 1 | 0 | +2 |
| 2 | 300 | +2 |
| 3 | 900 | +2 |
| 4 | 2,700 | +2 |
| 5 | 6,500 | +3 |
| 6 | 14,000 | +3 |
| 7 | 23,000 | +3 |
| 8 | 34,000 | +3 |
| 9 | 48,000 | +4 |
| 10 | 64,000 | +4 |
| 11–20 | … | +4 → +6 |

---

## Flood Protection

Talesman uses a per-message rate limiter to stay well under Libera.chat's flood threshold:

- **Channel messages** — 0.5 s per line (~2/sec)
- **Private messages** — 0.15 s per line (~6/sec)
- **Control messages** (PONG, JOIN, etc.) — 0.05 s

All channel commands are capped at **5 lines**. If a response would be longer (e.g. `!players` with a large party), the first chunk appears in channel and the full list is sent to the requester's PM.

---

## Technical Setup

### Requirements
- Python 3.14+
- `google-genai` (Gemini API)
- Systemd service recommended for auto-restart

### Configuration (`config.py`)
- `IRC_SERVER` / `IRC_PORT` — defaults to `irc.libera.chat:6697` (SSL)
- `IRC_CHANNELS` — `#gentoo-weed`, `##?`, `#jedi`
- `ADMINS` — set of nicks with ops-level bot access
- `SASL_ENABLED` — uses SASL PLAIN + NickServ fallback

### Credentials (environment / systemd)
- `TALESMAN_PASS` — NickServ password (path to credential file or raw value)
- `GEMINI_API_KEY` — Google Gemini API key

### Data Storage
All game state is stored as JSON in `data/`:
- `bank.json` — GP balances keyed by nick
- `characters/<nick>.json` — Individual 5e character sheets
- `sessions.json` — Active DM sessions per channel (survives restart)
- `dm_config.json` — Per-channel DM lock configuration
- `graveyard.json` — Permanent tombstone records for all fallen characters

### Legacy System
The original modern-day RPG system (`!create`, `!sheet`, `!bio`, `!thesis`) is still available alongside the D&D 5e system. Old characters are stored in `data/characters.json` and are distinguished by the absence of a `"system": "dnd5e"` field.

---

## Monster Manual & DMG Reference

The SRD 5.2 Monster Manual (50+ creatures) and Dungeon Master's Guide (55+ magic items, treasure tables, encounter budgets) are built into the bot as a DM reference tool.

### Monster lookups
| Command | Description |
|---|---|
| `!monster <name>` | 2-line stat summary in channel + full stat block (HP/AC/abilities/attacks/traits/immunities) sent via PM |
| `!cr <cr>` | List all monsters in the database at a given challenge rating (e.g. `!cr 5`, `!cr 1/4`) |

### Encounter building (DMG)
| Command | Description |
|---|---|
| `!encounter <difficulty> <level> [party_size]` | Calculate XP budget for an encounter — difficulty: `easy` `medium` `hard` `deadly`; default party size 4 |

Example: `!encounter hard 5 4` → **3,000 XP budget** for a hard encounter vs. a level-5 party of 4.

### Treasure (DMG)
| Command | Description |
|---|---|
| `!loot [cr]` | Roll random treasure for a creature of the given CR — individual drop + hoard coins + 1-3 magic items |
| `!mitem <name>` | Look up a specific magic item (Bag of Holding, Vorpal Sword, Flame Tongue, etc.) |
| `!mitem <rarity>` | Get a random magic item of that rarity (`common` `uncommon` `rare` `very rare` `legendary`) |
| `!mitem` | List all items by rarity |

### Available monsters (by CR)
Commoner (0) · Rat (0) · Bandit (1/8) · Kobold (1/8) · Skeleton (1/4) · Goblin (1/4) · Wolf (1/4) · Zombie (1/4) · Hobgoblin (1/2) · Orc (1/2) · Bugbear (1) · Giant Spider (1) · Ghoul (1) · Imp (1) · Ogre (2) · Gelatinous Cube (2) · Mimic (2) · Nothic (2) · Wererat (2) · Owlbear (3) · Wight (3) · Werewolf (3) · Manticore (3) · Ghost (4) · Succubus/Incubus (4) · Hill Giant (5) · Troll (5) · Flesh Golem (5) · Vampire Spawn (5) · Medusa (6) · Wyvern (6) · Mind Flayer (7) · Stone Giant (7) · Frost Giant (8) · Hydra (8) · Young Green Dragon (8) · Fire Giant (9) · Deva (10) · Stone Golem (10) · Young Red Dragon (10) · Remorhaz (11) · Archmage (12) · Iron Golem (16) · Vampire (13) · Purple Worm (15) · Death Knight (17) · Adult Red Dragon (17) · Ancient Red Dragon (24) · Lich (21) · Tarrasque (30)

---

## Planned Expansions

- Spell lists and spell slot tracking
- Combat initiative tracker (multi-player turn order)
- Quest log system
- Additional MM/DMG monsters and magic items

---

*Built on the [D&D 5e SRD 5.2 Creative Commons](https://www.dndbeyond.com/srd) ruleset.*
