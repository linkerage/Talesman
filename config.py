#!/usr/bin/env python3
"""
Talesman Configuration — Final Stable Version
"""

import os

# ------------------------------------------------------------
# IRC CONFIGURATION
# ------------------------------------------------------------

IRC_SERVER = "irc.libera.chat"
IRC_PORT = 6697

IRC_NICK = "Talesman"
IRC_USER = "Talesman"
IRC_REALNAME = "Talesman IRC Bot"

# Channels to join — all three run the same D&D 5e game system
IRC_CHANNELS = [
    "#gentoo-weed",
    "##?",
    "#jedi",
]

# Admin users who bypass cooldowns
ADMINS = {
    "n01d",
    "linkerage",
    "ph0bos",
    "n01"
}

# ------------------------------------------------------------
# CREDENTIAL LOADING
# ------------------------------------------------------------

def _read_credential(env_var: str) -> str:
    """
    Loads a credential from a systemd-provided file path.
    The environment variable contains *the path* to the secret.
    """
    path = os.getenv(env_var, "")
    if not path:
        return ""
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return ""

# NickServ + SASL
NICKSERV_PASSWORD = _read_credential("TALESMAN_PASS")
SASL_ENABLED = True

# Gemini API key (from systemd credential file)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gemini model
GEMINI_MODEL = "gemini-3.1-flash-lite"

# ------------------------------------------------------------
# FILE PATHS
# ------------------------------------------------------------

BASE_DIR = os.path.expanduser("~/Talesman")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Shared JSON files
BANK_FILE = os.path.join(DATA_DIR, "bank.json")
QUEST_FILE = os.path.join(DATA_DIR, "quests.json")

# Per-character directory (matches character.py)
CHAR_DIR = os.path.join(DATA_DIR, "characters")

# ------------------------------------------------------------
# GAME SETTINGS
# ------------------------------------------------------------

STARTING_GOLD = 100

# GM users (case-sensitive IRC nicks)
GM_USERS = {
    "n01d",
}

