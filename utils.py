#!/usr/bin/env python3
"""
Talesman Utility Functions — Clean Rebuild

Provides:
- Dice rolling
- Command parsing
"""

import random
from typing import Tuple
import re


# ------------------------------------------------------------
# DICE ROLLING
# ------------------------------------------------------------

def roll_dice(expr: str) -> str:
    """
    Roll dice expressions like:
      1d20
      2d6+3
      4d8-1

    Returns a human-readable result string.
    """
    expr = expr.lower().replace(" ", "")
    m = re.match(r"(\d*)d(\d+)([+-]\d+)?", expr)
    if not m:
        return f"Invalid dice expression: {expr}"

    n = int(m.group(1)) if m.group(1) else 1
    sides = int(m.group(2))
    mod = int(m.group(3)) if m.group(3) else 0

    rolls = [random.randint(1, sides) for _ in range(n)]
    total = sum(rolls) + mod

    detail = " + ".join(str(r) for r in rolls)
    if mod:
        detail += f" {mod:+d}"

    return f"{expr} = {total} ({detail})"


# ------------------------------------------------------------
# COMMAND PARSING
# ------------------------------------------------------------

def parse_command(message: str) -> Tuple[str, str]:
    """
    Parse commands of the form:
      !cmd args...
    Returns (cmd, rest)
    """
    if not message.startswith("!"):
        return "", ""

    parts = message[1:].split(" ", 1)
    cmd = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    return cmd, rest

