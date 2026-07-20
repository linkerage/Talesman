#!/usr/bin/env python3
"""
Tests for character death and loot collection mechanics.

Run from the Talesman directory:
    .venv/bin/python3 -m pytest tests/test_death_and_loot.py -v
or:
    .venv/bin/python3 tests/test_death_and_loot.py

Tests cover:
  1. One-character-per-nick enforcement in !newchar
  2. Death strips GP from bank and creates a loot pile
  3. !loot (list) — show uncollected piles in channel
  4. !loot <nick> — collect a specific pile
  5. !scavenge — collect all piles at once
  6. Edge cases: no GP on death, dead collectors, wrong channel
"""

import os
import sys
import json
import unittest

# Make sure we can import from the parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import loot as loot_mod
import game
from commands import cmd_newchar
from charwizard import is_active as wizard_active
from graveyard import is_dead, resurrect
from persistence import (
    save_character, load_character, char_path,
    load_bank, save_bank, get_balance, set_balance,
)


# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────

def make_bot():
    """Return a mock bot that captures all send_privmsg calls."""
    sent = []

    class MockBot:
        def send_privmsg(self, target, msg):
            for line in msg.split("\n"):
                if line.strip():
                    sent.append((target, line))

        def flush(self):
            captured = list(sent)
            sent.clear()
            return captured

        @property
        def msgs(self):
            return [m for _, m in sent]

        @property
        def channel_msgs(self):
            return [m for t, m in sent if t.startswith("#")]

        @property
        def pm_msgs(self):
            return [m for t, m in sent if not t.startswith("#")]

    b = MockBot()
    b._sent = sent
    return b


def make_char(nick, hp=12, gold=0):
    """Create and save a minimal living 5e character, optionally seed gold."""
    char = {
        "nick": nick.lower(), "system": "dnd5e", "name": f"{nick.title()}Hero",
        "race": "Human", "class": "Fighter", "background": "Soldier",
        "alignment": "True Neutral", "level": 1, "xp": 0,
        "proficiency_bonus": 2,
        "abilities": {"str": 15, "dex": 12, "con": 14,
                      "int": 10, "wis": 10, "cha": 9},
        "modifiers": {"str": 2, "dex": 1, "con": 2,
                      "int": 0, "wis": 0, "cha": -1},
        "saving_throws": {"str": 4, "dex": 1, "con": 4,
                          "int": 0, "wis": 0, "cha": -1},
        "hp_max": hp, "hp_current": hp, "ac": 16,
        "initiative": 1, "speed": 30, "hit_die": "1d10",
        "skill_proficiencies": ["Athletics", "Intimidation"],
        "skill_bonuses": {"Athletics": 4, "Intimidation": 1},
        "inventory": [], "languages": ["Common"],
    }
    save_character(char)
    # Always write the bank balance explicitly so the STARTING_GOLD default
    # (100) doesn't silently give 100 GP to a "0 GP" test character.
    bank = load_bank()
    set_balance(bank, nick, gold)
    save_bank(bank)
    return char


def cleanup(*nicks):
    """Remove test character files and bank/loot entries."""
    bank = load_bank()
    for nick in nicks:
        p = char_path(nick)
        if os.path.exists(p):
            os.remove(p)
        # Remove from bank
        nl = nick.lower()
        to_del = [k for k in bank if k.lower() == nl]
        for k in to_del:
            del bank[k]
        # Remove from graveyard if present
        resurrect(nick)
    save_bank(bank)
    # Clear any loot piles these nicks left
    for ch in ("#gentoo-weed", "##?", "#jedi"):
        for n in nicks:
            loot_mod.collect_loot(ch, n)


# ────────────────────────────────────────────────────────────────
# 1.  One character per nick
# ────────────────────────────────────────────────────────────────

class TestOneCharPerNick(unittest.TestCase):

    def setUp(self):
        self.bot  = make_bot()
        self.CHAN = "#gentoo-weed"
        self.nick = "_oc_test_"
        cleanup(self.nick)

    def tearDown(self):
        cleanup(self.nick)

    def test_no_char_allows_newchar(self):
        """With no existing character, !newchar starts the wizard."""
        cmd_newchar(self.bot, self.nick, self.CHAN, "")
        self.assertTrue(wizard_active(self.nick),
                        "Wizard should start when no character exists")
        from charwizard import cancel_session
        cancel_session(self.nick)

    def test_living_char_blocks_newchar(self):
        """!newchar is blocked while the player has a living character."""
        make_char(self.nick)
        cmd_newchar(self.bot, self.nick, self.CHAN, "")
        self.assertFalse(wizard_active(self.nick),
                         "Wizard must NOT start for a living character")
        block_msgs = [m for m in self.bot.msgs
                      if "still alive" in m or "already have a living" in m]
        self.assertTrue(block_msgs, "Should send a 'still alive' message")

    def test_dead_char_allows_newchar(self):
        """After a character dies, !newchar is allowed again."""
        char = make_char(self.nick)
        # Kill the character
        game._kill_character(char, "Test Dragon",
                             "fire breath", self.bot, self.CHAN)
        self.bot._sent.clear()

        # Now !newchar should work
        cmd_newchar(self.bot, self.nick, self.CHAN, "")
        self.assertTrue(wizard_active(self.nick),
                        "Wizard should start for a dead character")
        from charwizard import cancel_session
        cancel_session(self.nick)

    def test_newchar_after_death_says_fallen(self):
        """!newchar after death acknowledges the previous character."""
        char = make_char(self.nick)
        game._kill_character(char, "Goblin", "Scimitar hit", self.bot, self.CHAN)
        self.bot._sent.clear()

        cmd_newchar(self.bot, self.nick, self.CHAN, "")
        fallen_msgs = [m for m in self.bot.pm_msgs if "fallen" in m.lower()]
        self.assertTrue(fallen_msgs,
                        "Should mention previous character has fallen")
        from charwizard import cancel_session
        cancel_session(self.nick)


# ────────────────────────────────────────────────────────────────
# 2.  Death strips gold
# ────────────────────────────────────────────────────────────────

class TestDeathStripsGold(unittest.TestCase):

    def setUp(self):
        self.bot  = make_bot()
        self.CHAN = "#gentoo-weed"
        self.nick = "_dsg_test_"
        cleanup(self.nick)

    def tearDown(self):
        cleanup(self.nick)
        loot_mod.collect_loot(self.CHAN, self.nick)  # clean any leftover pile

    def test_gold_zeroed_on_death(self):
        """Player's bank balance is zeroed when they die."""
        char = make_char(self.nick, gold=200)
        self.assertEqual(get_balance(load_bank(), self.nick), 200)

        game._kill_character(char, "Lich", "death touch", self.bot, self.CHAN)
        self.assertEqual(get_balance(load_bank(), self.nick), 0,
                         "Bank should be zeroed after death")

    def test_loot_pile_created_with_correct_amount(self):
        """Loot pile in channel equals the dead character's gold."""
        char = make_char(self.nick, gold=150)
        game._kill_character(char, "Vampire", "Bite", self.bot, self.CHAN)

        piles = loot_mod.list_loot(self.CHAN)
        nick_piles = [p for p in piles if p["nick"] == self.nick.lower()]
        self.assertEqual(len(nick_piles), 1)
        self.assertEqual(nick_piles[0]["gold"], 150)

    def test_no_pile_when_gold_is_zero(self):
        """No loot pile created if the character had 0 GP."""
        char = make_char(self.nick, gold=0)
        before_count = len(loot_mod.list_loot(self.CHAN))

        game._kill_character(char, "Wolf", "Bite", self.bot, self.CHAN)
        after_count = len(loot_mod.list_loot(self.CHAN))
        self.assertEqual(before_count, after_count,
                         "No pile should appear for a penniless death")

    def test_death_announcement_mentions_loot(self):
        """Death message includes the GP amount when gold > 0."""
        char = make_char(self.nick, gold=75)
        self.bot._sent.clear()
        game._kill_character(char, "Goblin", "Scimitar", self.bot, self.CHAN)

        death_msgs = [m for _, m in self.bot._sent
                      if "fallen" in m and self.CHAN in _]
        self.assertTrue(any("75" in m for m in death_msgs),
                        "Death announcement should mention the GP amount")

    def test_death_announcement_no_loot_line_when_broke(self):
        """Death message omits loot hint when character had no gold."""
        char = make_char(self.nick, gold=0)
        self.bot._sent.clear()
        game._kill_character(char, "Rat", "Bite", self.bot, self.CHAN)

        death_msgs = self.bot.channel_msgs
        self.assertFalse(any("!loot" in m for m in death_msgs),
                         "Should not mention !loot when no gold was dropped")


# ────────────────────────────────────────────────────────────────
# 3.  !loot (list piles)
# ────────────────────────────────────────────────────────────────

class TestLootList(unittest.TestCase):

    def setUp(self):
        self.bot  = make_bot()
        self.CHAN = "#gentoo-weed"
        self.dead = "_ll_dead_"
        cleanup(self.dead)

    def tearDown(self):
        cleanup(self.dead)
        loot_mod.collect_all(self.CHAN)

    def test_empty_channel_says_no_loot(self):
        """!loot with no piles reports nothing on battlefield."""
        loot_mod.collect_all(self.CHAN)   # ensure clean slate
        self.bot._sent.clear()
        game.cmd_loot(self.bot, "n01d", self.CHAN, "")
        self.assertTrue(
            any("No loot" in m or "nothing" in m.lower()
                for m in self.bot.channel_msgs),
            "Should report empty battlefield")

    def test_list_shows_pile_name_and_gold(self):
        """!loot lists the fallen character's name and gold amount."""
        char = make_char(self.dead, gold=300)
        game._kill_character(char, "Zombie", "Slam", self.bot, self.CHAN)
        self.bot._sent.clear()

        game.cmd_loot(self.bot, "n01d", self.CHAN, "")
        msgs = self.bot.channel_msgs
        self.assertTrue(any("300" in m for m in msgs),
                        "Should show 300 GP in listing")
        char_name = load_character(self.dead)
        if char_name:
            self.assertTrue(any(char_name.get("name", self.dead) in m
                                for m in msgs),
                            "Should show the character's name")

    def test_multiple_piles_all_listed(self):
        """!loot lists every pile, not just the first."""
        dead2 = "_ll_dead2_"
        try:
            char1 = make_char(self.dead, gold=100)
            char2 = make_char(dead2, gold=200)
            game._kill_character(char1, "Goblin", "hit", self.bot, self.CHAN)
            game._kill_character(char2, "Orc", "hit", self.bot, self.CHAN)
            self.bot._sent.clear()

            game.cmd_loot(self.bot, "n01d", self.CHAN, "")
            msgs = self.bot.channel_msgs
            self.assertTrue(any("100" in m for m in msgs))
            self.assertTrue(any("200" in m for m in msgs))
        finally:
            cleanup(dead2)
            loot_mod.collect_all(self.CHAN)


# ────────────────────────────────────────────────────────────────
# 4.  !loot <nick> (collect specific pile)
# ────────────────────────────────────────────────────────────────

class TestLootCollect(unittest.TestCase):

    CHAN = "#gentoo-weed"

    def setUp(self):
        self.bot       = make_bot()
        self.dead_nick = "_lc_dead_"
        self.live_nick = "_lc_live_"
        cleanup(self.dead_nick, self.live_nick)

    def tearDown(self):
        cleanup(self.dead_nick, self.live_nick)
        loot_mod.collect_all(self.CHAN)

    def _kill_with_gold(self, nick, gold):
        char = make_char(nick, gold=gold)
        game._kill_character(char, "Monster", "hit", self.bot, self.CHAN)
        self.bot._sent.clear()
        return char

    def test_collector_receives_gold(self):
        """Collecting a pile adds the gold to the collector's bank."""
        self._kill_with_gold(self.dead_nick, 120)
        make_char(self.live_nick)

        bank_before = get_balance(load_bank(), self.live_nick)
        game.cmd_loot(self.bot, self.live_nick, self.CHAN, self.dead_nick)
        bank_after  = get_balance(load_bank(), self.live_nick)

        self.assertEqual(bank_after - bank_before, 120,
                         "Collector should gain exactly 120 GP")

    def test_pile_removed_after_collection(self):
        """Loot pile disappears once collected."""
        self._kill_with_gold(self.dead_nick, 50)
        make_char(self.live_nick)

        game.cmd_loot(self.bot, self.live_nick, self.CHAN, self.dead_nick)
        piles = loot_mod.list_loot(self.CHAN)
        self.assertFalse(
            any(p["nick"] == self.dead_nick.lower() for p in piles),
            "Pile should be gone after collection")

    def test_cannot_loot_own_corpse(self):
        """A player cannot collect their own loot pile."""
        self._kill_with_gold(self.dead_nick, 80)
        # Even if we could call this — dead players are blocked earlier
        # Test the nick-equality guard
        game.cmd_loot(self.bot, self.dead_nick, self.CHAN, self.dead_nick)
        self.assertTrue(
            any("corpse" in m.lower() or "own" in m.lower()
                for m in self.bot.channel_msgs),
            "Should refuse self-looting")

    def test_dead_collector_cannot_loot(self):
        """A dead character cannot collect loot."""
        self._kill_with_gold(self.dead_nick, 100)
        dead_collector_nick = "_lc_deadcol_"
        try:
            dead_col_char = make_char(dead_collector_nick, gold=0)
            game._kill_character(dead_col_char, "Troll", "Claw",
                                 self.bot, self.CHAN)
            self.bot._sent.clear()

            game.cmd_loot(self.bot, dead_collector_nick,
                          self.CHAN, self.dead_nick)
            self.assertTrue(
                any("dead" in m.lower() or "cannot" in m.lower()
                    for m in self.bot.channel_msgs),
                "Dead collector should be refused")
            # Original pile untouched
            piles = loot_mod.list_loot(self.CHAN)
            self.assertTrue(
                any(p["nick"] == self.dead_nick.lower() for p in piles),
                "Pile should still exist after failed collection attempt")
        finally:
            cleanup(dead_collector_nick)

    def test_nonexistent_pile_returns_error(self):
        """Collecting from a nick with no pile gives an error."""
        make_char(self.live_nick)
        game.cmd_loot(self.bot, self.live_nick, self.CHAN, "ghostnick")
        self.assertTrue(
            any("not found" in m.lower() or "no loot" in m.lower()
                for m in self.bot.channel_msgs),
            "Should report pile not found")

    def test_collection_success_announcement(self):
        """Successful collection is announced in channel with amount."""
        self._kill_with_gold(self.dead_nick, 99)
        make_char(self.live_nick)

        game.cmd_loot(self.bot, self.live_nick, self.CHAN, self.dead_nick)
        self.assertTrue(
            any("99 GP" in m for m in self.bot.channel_msgs),
            "Announcement should include GP amount")

    def test_no_character_cannot_loot(self):
        """A player without a 5e character cannot collect loot."""
        self._kill_with_gold(self.dead_nick, 60)
        # "nobody" has no character on file
        game.cmd_loot(self.bot, "_nobody_at_all_", self.CHAN, self.dead_nick)
        self.assertTrue(
            any("need a 5e character" in m.lower() or "newchar" in m.lower()
                for m in self.bot.channel_msgs))


# ────────────────────────────────────────────────────────────────
# 5.  !scavenge (collect all piles at once)
# ────────────────────────────────────────────────────────────────

class TestScavenge(unittest.TestCase):

    CHAN = "#gentoo-weed"

    def setUp(self):
        self.bot      = make_bot()
        self.scav     = "_scav_live_"
        self.dead1    = "_scav_d1_"
        self.dead2    = "_scav_d2_"
        cleanup(self.scav, self.dead1, self.dead2)
        loot_mod.collect_all(self.CHAN)

    def tearDown(self):
        cleanup(self.scav, self.dead1, self.dead2)
        loot_mod.collect_all(self.CHAN)

    def _drop(self, nick, gold):
        char = make_char(nick, gold=gold)
        game._kill_character(char, "Wolf", "Bite", self.bot, self.CHAN)
        self.bot._sent.clear()

    def test_scavenge_collects_all_piles(self):
        """!scavenge picks up every pile in the channel."""
        self._drop(self.dead1, 40)
        self._drop(self.dead2, 60)
        make_char(self.scav)

        bank_before = get_balance(load_bank(), self.scav)
        game.cmd_scavenge(self.bot, self.scav, self.CHAN, "")
        bank_after  = get_balance(load_bank(), self.scav)

        self.assertEqual(bank_after - bank_before, 100,
                         "Scavenger should gain 40 + 60 = 100 GP")
        self.assertEqual(loot_mod.list_loot(self.CHAN), [],
                         "All piles should be cleared")

    def test_scavenge_empty_channel(self):
        """!scavenge on an empty channel gives an appropriate message."""
        make_char(self.scav)
        game.cmd_scavenge(self.bot, self.scav, self.CHAN, "")
        self.assertTrue(
            any("nothing" in m.lower() for m in self.bot.channel_msgs),
            "Should report nothing to scavenge")

    def test_dead_cannot_scavenge(self):
        """Dead players cannot scavenge."""
        self._drop(self.dead1, 50)
        dead_scav = "_scav_dead_"
        try:
            dead_char = make_char(dead_scav)
            game._kill_character(dead_char, "Orc", "Axe",
                                 self.bot, self.CHAN)
            self.bot._sent.clear()

            game.cmd_scavenge(self.bot, dead_scav, self.CHAN, "")
            self.assertTrue(
                any("dead" in m.lower() or "cannot" in m.lower()
                    for m in self.bot.channel_msgs))
            # Pile still there
            self.assertTrue(loot_mod.list_loot(self.CHAN))
        finally:
            cleanup(dead_scav)


# ────────────────────────────────────────────────────────────────
# 6.  Cross-channel isolation
# ────────────────────────────────────────────────────────────────

class TestCrossChannelIsolation(unittest.TestCase):

    def setUp(self):
        self.bot  = make_bot()
        self.nick = "_xch_dead_"
        self.CHAN_A = "#gentoo-weed"
        self.CHAN_B = "##?"
        cleanup(self.nick)
        loot_mod.collect_all(self.CHAN_A)
        loot_mod.collect_all(self.CHAN_B)

    def tearDown(self):
        cleanup(self.nick)
        loot_mod.collect_all(self.CHAN_A)
        loot_mod.collect_all(self.CHAN_B)

    def test_loot_stays_in_death_channel(self):
        """Loot dropped in channel A does not appear in channel B."""
        char = make_char(self.nick, gold=50)
        game._kill_character(char, "Spider", "Bite", self.bot, self.CHAN_A)

        piles_a = loot_mod.list_loot(self.CHAN_A)
        piles_b = loot_mod.list_loot(self.CHAN_B)
        self.assertTrue(
            any(p["nick"] == self.nick.lower() for p in piles_a),
            "Pile should exist in channel A")
        self.assertFalse(
            any(p["nick"] == self.nick.lower() for p in piles_b),
            "Pile must NOT appear in channel B")

    def test_loot_in_channel_b_invisible_from_a(self):
        """Collecting in channel B cannot grab a pile from channel A."""
        char = make_char(self.nick, gold=80)
        game._kill_character(char, "Goblin", "Stab", self.bot, self.CHAN_A)

        live = "_xch_live_"
        try:
            make_char(live)
            game.cmd_loot(self.bot, live, self.CHAN_B, self.nick)
            self.assertTrue(
                any("not found" in m.lower() or "no loot" in m.lower()
                    for m in self.bot.channel_msgs),
                "Should not find pile from a different channel")
        finally:
            cleanup(live)


# ────────────────────────────────────────────────────────────────
# 7.  Loot persistence (simulate restart)
# ────────────────────────────────────────────────────────────────

class TestLootPersistence(unittest.TestCase):

    CHAN = "#gentoo-weed"

    def setUp(self):
        self.bot  = make_bot()
        self.nick = "_lp_dead_"
        cleanup(self.nick)
        loot_mod.collect_all(self.CHAN)

    def tearDown(self):
        cleanup(self.nick)
        loot_mod.collect_all(self.CHAN)

    def test_piles_survive_reload(self):
        """Loot piles persist across a module reload (restart simulation)."""
        char = make_char(self.nick, gold=250)
        game._kill_character(char, "Dragon", "Fire breath", self.bot, self.CHAN)

        # Simulate restart: re-call _load() directly
        loot_mod._load()
        piles = loot_mod.list_loot(self.CHAN)
        nick_piles = [p for p in piles if p["nick"] == self.nick.lower()]
        self.assertEqual(len(nick_piles), 1)
        self.assertEqual(nick_piles[0]["gold"], 250,
                         "Loot pile should survive a restart")

    def test_uncollected_loot_stays_forever(self):
        """Uncollected loot is not auto-expired."""
        char = make_char(self.nick, gold=42)
        game._kill_character(char, "Bat", "Bite", self.bot, self.CHAN)

        # Re-load twice
        loot_mod._load()
        loot_mod._load()
        piles = loot_mod.list_loot(self.CHAN)
        self.assertTrue(
            any(p["nick"] == self.nick.lower() for p in piles),
            "Uncollected loot should persist indefinitely")


# ────────────────────────────────────────────────────────────────
# Run
# ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
