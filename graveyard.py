#!/usr/bin/env python3
"""
Talesman Graveyard — Persistent storage for fallen characters.

When a character's HP reaches 0 they are buried here with a full snapshot
of their stats, cause of death, and timestamp. The tombstone record is
permanent; the character cannot be revived except by an admin using !rez.
"""

import os
import time
import threading
from typing import Dict, Any, Optional

from config import DATA_DIR
from persistence import atomic_load, atomic_save, save_character

GRAVEYARD_FILE = os.path.join(DATA_DIR, "graveyard.json")

_lock = threading.Lock()
_graveyard: Dict[str, Dict[str, Any]] = {}


def _load():
    global _graveyard
    _graveyard = atomic_load(GRAVEYARD_FILE, {})


_load()


# ----------------------------------------------------------------
# Public API
# ----------------------------------------------------------------

def is_dead(nick: str) -> bool:
    """True if nick's character is in the graveyard."""
    with _lock:
        return nick.lower() in _graveyard


def bury_character(char: dict, killer: str, killing_blow: str):
    """
    Move a character to the graveyard.
    Saves a full snapshot of the character at the moment of death,
    then marks the live character record as dead.
    """
    nick = char["nick"].lower()
    entry = {
        "tombstone":    dict(char),       # full snapshot
        "died_at":      time.time(),
        "killer":       killer,
        "killing_blow": killing_blow,
    }
    with _lock:
        _graveyard[nick] = entry
        snapshot = dict(_graveyard)
    atomic_save(GRAVEYARD_FILE, snapshot)

    # Mark the live character record dead (so loadouts show it correctly)
    char["dead"]       = True
    char["hp_current"] = 0
    char["killer"]     = killer
    save_character(char)


def get_tombstone(nick: str) -> Optional[Dict[str, Any]]:
    """Return the full graveyard entry for nick, or None."""
    with _lock:
        return dict(_graveyard.get(nick.lower(), {})) or None


def list_graves() -> list:
    """Return list of (nick, entry) tuples sorted by death time (newest first)."""
    with _lock:
        items = list(_graveyard.items())
    return sorted(items, key=lambda x: x[1].get("died_at", 0), reverse=True)


def resurrect(nick: str) -> bool:
    """
    Remove a character from the graveyard (admin/DM use only).
    Clears the dead flag on the live character and restores 1 HP.
    Returns True if the character was in the graveyard.
    """
    nick_lower = nick.lower()
    with _lock:
        if nick_lower not in _graveyard:
            return False
        del _graveyard[nick_lower]
        snapshot = dict(_graveyard)
    atomic_save(GRAVEYARD_FILE, snapshot)

    # Restore the character
    from persistence import load_character
    char = load_character(nick_lower)
    if char:
        char.pop("dead",   None)
        char.pop("killer", None)
        char["hp_current"] = 1
        save_character(char)
    return True


def _ts_str(ts: float) -> str:
    """Human-readable timestamp."""
    import datetime
    dt = datetime.datetime.utcfromtimestamp(ts)
    return dt.strftime("%Y-%m-%d %H:%M UTC")
