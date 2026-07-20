#!/usr/bin/env python3
"""
Talesman Character System — Unified + Safe Version
"""

import os
import json
from gemini_client import build_thesis as gemini_build_thesis

CHAR_DIR = "characters"


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _char_path(nick: str) -> str:
    os.makedirs(CHAR_DIR, exist_ok=True)
    return os.path.join(CHAR_DIR, f"{nick.lower()}.json")


def _atomic_save(path: str, data: dict):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _default_character(nick: str, archetype: str) -> dict:
    return {
        "nick": nick,
        "archetype": archetype.title(),
        "bio": "",
        "thesis": "",
        "level": 1,
        "xp": 0,
        "inventory": [],
        "skills": [],
    }


def _validate_character(char: dict) -> dict:
    """Ensure required fields exist; repair missing ones."""
    defaults = _default_character(char.get("nick", "unknown"), char.get("archetype", "Unknown"))
    for key, val in defaults.items():
        char.setdefault(key, val)
    return char


# ------------------------------------------------------------
# Load / Save
# ------------------------------------------------------------

def load_character(nick: str) -> dict | None:
    path = _char_path(nick)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            char = json.load(f)
            return _validate_character(char)
    except Exception:
        return None


def save_character(char: dict):
    path = _char_path(char["nick"])
    try:
        _atomic_save(path, char)
    except Exception:
        pass


# ------------------------------------------------------------
# Character Creation
# ------------------------------------------------------------

def create_character(nick: str, archetype: str) -> str:
    """Create a new character; refuse overwrite."""
    if load_character(nick):
        return f"{nick}: character already exists."

    char = _default_character(nick, archetype)
    save_character(char)
    return f"Character created: {archetype.title()}"


# ------------------------------------------------------------
# Bio + Thesis
# ------------------------------------------------------------

def update_bio(nick: str, text: str) -> str:
    char = load_character(nick)
    if not char:
        return "No character found. Use !create first."

    char["bio"] = text
    save_character(char)
    return "Bio updated."


def update_thesis(nick: str) -> str:
    """
    Generate thesis using Gemini based on the character's bio.
    """
    char = load_character(nick)
    if not char:
        return "No character found. Use !create first."

    thesis = gemini_build_thesis(char["bio"])
    char["thesis"] = thesis
    save_character(char)
    return "Thesis generated."


# ------------------------------------------------------------
# Character Sheet
# ------------------------------------------------------------

def get_sheet(nick: str) -> str:
    char = load_character(nick)
    if not char:
        return "No character found. Use !create <archetype> first."

    lines = [
        f"=== {char['nick']}'s Character Sheet ===",
        f"Archetype: {char['archetype']}",
        f"Level: {char['level']}  XP: {char['xp']}",
        f"Inventory: {', '.join(char['inventory']) or 'None'}",
        f"Skills: {', '.join(char['skills']) or 'None'}",
    ]

    if char["bio"]:
        lines.append(f"Bio: {char['bio']}")

    if char["thesis"]:
        lines.append(f"Thesis: {char['thesis']}")

    return "\n".join(lines)

