#!/usr/bin/env python3
"""
Loot pile system.

When a character dies their gold is stripped from the bank and dropped
as a loot pile in the channel where they fell.  Any other living player
can collect it with `!loot <nick>`.  If nobody picks it up, it stays
on the floor indefinitely — the battlefield holds its dead.

Storage: data/loot.json
  {
    "#gentoo-weed": [
      { "nick": "n01d", "name": "Sir Testington",
        "gold": 150, "died_at": 1721462400.0 }
    ]
  }
"""

import os
import threading
from typing import List, Dict, Any, Optional

from config import DATA_DIR
from persistence import atomic_load, atomic_save

LOOT_FILE = os.path.join(DATA_DIR, "loot.json")

_lock = threading.Lock()
_loot: Dict[str, List[Dict[str, Any]]] = {}


def _load():
    global _loot
    _loot = atomic_load(LOOT_FILE, {})


_load()


def _save():
    atomic_save(LOOT_FILE, _loot)


# ----------------------------------------------------------------
# Public API
# ----------------------------------------------------------------

def add_loot(channel: str, nick: str, name: str, gold: int):
    """Drop a loot pile in channel when a character dies."""
    if gold <= 0:
        return
    import time
    entry = {"nick": nick.lower(), "name": name, "gold": gold,
             "died_at": time.time()}
    with _lock:
        _loot.setdefault(channel, []).append(entry)
        _save()


def list_loot(channel: str) -> List[Dict[str, Any]]:
    """Return all uncollected loot piles in a channel."""
    with _lock:
        return list(_loot.get(channel, []))


def collect_loot(channel: str, dead_nick: str) -> Optional[Dict[str, Any]]:
    """
    Remove and return the loot pile for dead_nick in channel.
    Returns None if no pile exists.
    """
    target = dead_nick.lower()
    with _lock:
        piles = _loot.get(channel, [])
        for i, pile in enumerate(piles):
            if pile["nick"] == target:
                removed = piles.pop(i)
                if not piles:
                    _loot.pop(channel, None)
                _save()
                return removed
    return None


def collect_all(channel: str) -> List[Dict[str, Any]]:
    """Remove and return every loot pile in a channel (scavenge)."""
    with _lock:
        piles = _loot.pop(channel, [])
        if piles:
            _save()
        return piles


def has_loot(channel: str) -> bool:
    with _lock:
        return bool(_loot.get(channel))
