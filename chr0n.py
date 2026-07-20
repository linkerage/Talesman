#!/usr/bin/env python3
"""
chr0n.py — Interface to chr0n's 420-point ledger.

File: /home/n01d/chr0n/420_points.json

This is the canonical source of truth for 420-points earned in
#gentoo-weed by toking at 4:20 AM/PM. Talesman reads and writes
this file directly to:
  - Show balances / leaderboard
  - Deduct pts when exchanging to D&D GP
  - Add pts when exchanging from D&D GP back
  - Deduct 420 pts when a player redeems for a gift card (!cash)

Writes are atomic (write to .tmp then rename) to avoid corruption.
"""

import json
import os
import time
import datetime
import threading
from typing import Optional, List, Tuple

CHR0N_FILE = "/home/n01d/chr0n/420_points.json"
CHR0N_LOCK = threading.Lock()   # file-level mutex for all reads/writes


# ----------------------------------------------------------------
# Low-level I/O
# ----------------------------------------------------------------

def _load() -> dict:
    try:
        with open(CHR0N_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict):
    tmp = CHR0N_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, CHR0N_FILE)


def _ts() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def _find_key(data: dict, nick: str) -> Optional[str]:
    """Case-insensitive nick lookup. Returns the actual key or None."""
    nick_lower = nick.lower()
    for k in data:
        if k.lower() == nick_lower:
            return k
    return None


# ----------------------------------------------------------------
# Public API
# ----------------------------------------------------------------

def get_balance(nick: str) -> int:
    """Return the current 420-pt balance for nick (0 if not found)."""
    with CHR0N_LOCK:
        data = _load()
        key = _find_key(data, nick)
        return int(data[key]["total"]) if key else 0


def list_balances() -> List[Tuple[str, int]]:
    """Return [(nick, total), …] sorted by balance descending."""
    with CHR0N_LOCK:
        data = _load()
    return sorted(
        ((k, int(v.get("total", 0))) for k, v in data.items()),
        key=lambda x: x[1], reverse=True
    )


def deduct(nick: str, amount: int, window: str) -> Tuple[bool, int]:
    """
    Deduct `amount` from nick's balance.
    Records a history entry with the given window label.
    Returns (success, new_balance).
    """
    with CHR0N_LOCK:
        data = _load()
        key = _find_key(data, nick)
        if key is None:
            return False, 0
        current = int(data[key].get("total", 0))
        if current < amount:
            return False, current
        new_total = current - amount
        data[key]["total"] = new_total
        data[key].setdefault("history", []).append({
            "window":  window,
            "time":    _ts(),
            "amount":  -amount,
        })
        _save(data)
        return True, new_total


def add(nick: str, amount: int, window: str) -> int:
    """
    Add `amount` to nick's balance (creates entry if nick is new).
    Returns the new balance.
    """
    with CHR0N_LOCK:
        data = _load()
        key = _find_key(data, nick)
        if key is None:
            key = nick
            data[key] = {"total": 0, "history": []}
        current = int(data[key].get("total", 0))
        new_total = current + amount
        data[key]["total"] = new_total
        data[key].setdefault("history", []).append({
            "window": window,
            "time":   _ts(),
            "amount": amount,
        })
        _save(data)
        return new_total


def cashout(nick: str) -> Tuple[bool, int]:
    """
    Redeem 420 pts for the gift card:
    deducts exactly 420 from chr0n's file.
    Returns (success, remaining_balance).
    """
    return deduct(nick, 420, f"cashout-gift-card-{datetime.date.today()}")
