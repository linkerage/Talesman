#!/usr/bin/env python3
"""
Talesman Persistence Layer — Unified Storage

- Characters stored as individual JSON files
- Bank + Quests stored as shared JSON
- Atomic writes
- Lowercase nick normalization
"""

import json
import os
from typing import Dict, Any

from config import (
    DATA_DIR,
    CHAR_DIR,
    BANK_FILE,
    QUEST_FILE,
    STARTING_GOLD,
)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CHAR_DIR, exist_ok=True)

def atomic_save(path: str, data: Any):
    ensure_dirs()
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    os.replace(tmp, path)

def atomic_load(path: str, default):
    ensure_dirs()
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

# ------------------------------------------------------------
# Character Storage (per-file)
# ------------------------------------------------------------

def char_path(nick: str) -> str:
    return os.path.join(CHAR_DIR, f"{nick.lower()}.json")

def load_character(nick: str) -> Dict[str, Any] | None:
    path = char_path(nick)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def save_character(char: Dict[str, Any]):
    atomic_save(char_path(char["nick"]), char)

def list_characters() -> Dict[str, Any]:
    """Return all characters as a dict keyed by nick."""
    ensure_dirs()
    chars = {}
    for fn in os.listdir(CHAR_DIR):
        if fn.endswith(".json"):
            nick = fn[:-5]
            data = load_character(nick)
            if data:
                chars[nick] = data
    return chars

# ------------------------------------------------------------
# Bank Storage
# ------------------------------------------------------------

def load_bank() -> Dict[str, int]:
    raw = atomic_load(BANK_FILE, {})
    return {k: int(v) for k, v in raw.items()}

def save_bank(bank: Dict[str, int]):
    atomic_save(BANK_FILE, bank)

def get_balance(bank: Dict[str, int], nick: str) -> int:
    return int(bank.get(nick.lower(), STARTING_GOLD))

def set_balance(bank: Dict[str, int], nick: str, amount: int):
    bank[nick.lower()] = int(amount)

# ------------------------------------------------------------
# Quest Storage
# ------------------------------------------------------------

def load_quests() -> Dict[str, Any]:
    return atomic_load(QUEST_FILE, {})

def save_quests(quests: Dict[str, Any]):
    atomic_save(QUEST_FILE, quests)

