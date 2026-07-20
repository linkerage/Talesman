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
| `!dm damage <nick> <n>` | Deal damage; announces UNCONSCIOUS if HP reaches 0 |
| `!dm dmg <nick> <n>` | Shorthand for damage |

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

### Legacy System
The original modern-day RPG system (`!create`, `!sheet`, `!bio`, `!thesis`) is still available alongside the D&D 5e system. Old characters are stored in `data/characters.json` and are distinguished by the absence of a `"system": "dnd5e"` field.

---

## Planned Expansions

- Monster Manual data (encounter building, creature stats)
- Dungeon Master's Guide (magic items, loot tables)
- Spell lists and spell slot tracking
- Combat initiative tracker
- Quest log system

---

*Built on the [D&D 5e SRD 5.2 Creative Commons](https://www.dndbeyond.com/srd) ruleset.*
