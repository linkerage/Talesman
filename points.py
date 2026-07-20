#!/usr/bin/env python3
"""
Talesman 420-Point Exchange System

Two separate ledgers, bidirectional exchange:

  chr0n's file  /home/n01d/chr0n/420_points.json
  └─ Earned by toking at 4:20 AM/PM in #gentoo-weed
  └─ Commands: !pts [nick]  !ptsboard  !pts2gp [n]  !cash

  Talesman bank  ~/Talesman/data/bank.json
  └─ Earned through D&D gameplay (combat XP rewards, DM awards)
  └─ Commands: !gold [nick]  !gp  !gp2pts [n]  !pay

  Exchange (1 pt = 1 GP, always):
    !pts2gp [n]   — convert N 420-pts → N GP (leave chr0n, enter Talesman)
    !gp2pts [n]   — convert N GP → N 420-pts (leave Talesman, enter chr0n)

  Cash-in:
    !cash         — redeem 420 pts for a gift card
                    pts deducted from chr0n's file; PM n01d to arrange
"""

import datetime
import time
import threading
from typing import Dict, Tuple

import chr0n
from config import ADMINS
from persistence import load_bank, save_bank, get_balance, set_balance

CASH_THRESHOLD = 420
CASH_LABEL     = "a $100 Visa gift card"
CASH_CONTACT   = "n01d"
LEADERBOARD_CAP = 5


# ================================================================
# !pts [nick]  — show balance from chr0n's file
# ================================================================

def cmd_pts(bot, nick, target, args):
    """`!pts [nick]` — check 420-point balance from chr0n's ledger."""
    whom = args.strip().split()[0] if args.strip() else nick
    pts  = chr0n.get_balance(whom)
    gp   = get_balance(load_bank(), whom)
    eligible = "  \x02(420+ pts — eligible to !cash!)\x02" if pts >= CASH_THRESHOLD else ""
    bot.send_privmsg(target,
        f"🌿 \x02{whom}\x02: "
        f"\x02{pts} 420-pts\x02 (earned by toking at 4:20){eligible}  |  "
        f"{gp} GP (D&D gold)")


# ================================================================
# !ptsboard  — leaderboard from chr0n's file
# ================================================================

def cmd_ptsboard(bot, nick, target, args):
    """`!ptsboard` — 420-point leaderboard from chr0n's ledger."""
    balances = [(n, p) for n, p in chr0n.list_balances() if p > 0]
    in_channel = target.startswith("#")
    reply      = target if in_channel else nick

    if not balances:
        bot.send_privmsg(reply, "🌿 No 420-points on the board yet!")
        return

    medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]
    bot.send_privmsg(reply, "\x02🌿 420-Point Board (chr0n / #gentoo-weed) 🌿\x02")
    for i, (holder, pts) in enumerate(balances[:LEADERBOARD_CAP]):
        medal = medals[i] if i < len(medals) else " "
        bot.send_privmsg(reply,
            f"  {medal} \x02{holder}\x02: {pts} pts"
            + ("  ← eligible !cash" if pts >= CASH_THRESHOLD else ""))

    overflow = len(balances) - LEADERBOARD_CAP
    if overflow > 0 and in_channel:
        bot.send_privmsg(reply, f"  …and {overflow} more.")


# ================================================================
# !pts2gp [n]  — exchange N 420-pts from chr0n's file → Talesman GP
# ================================================================

def cmd_pts2gp(bot, nick, target, args):
    """`!pts2gp [n]` — convert N 420-pts to D&D GP (removes from chr0n, adds to Talesman)."""
    current_pts = chr0n.get_balance(nick)
    if current_pts <= 0:
        bot.send_privmsg(target,
            f"{nick}: you have 0 420-pts in chr0n's ledger. "
            f"Toke at 4:20 in #gentoo-weed to earn some! 🌿")
        return

    parts = args.strip().split()
    if parts:
        try:
            n = int(parts[0])
        except ValueError:
            bot.send_privmsg(target, f"{nick}: !pts2gp [n]  e.g. !pts2gp 10")
            return
    else:
        n = current_pts   # exchange everything

    if n <= 0:
        bot.send_privmsg(target, f"{nick}: amount must be positive.")
        return
    if n > current_pts:
        bot.send_privmsg(target,
            f"{nick}: you only have {current_pts} 420-pts (requested {n}).")
        return

    # Deduct from chr0n's file
    ok, new_pts = chr0n.deduct(nick, n,
        f"exchange-to-gp-{datetime.date.today()}")
    if not ok:
        bot.send_privmsg(target, f"{nick}: exchange failed — try again.")
        return

    # Add to Talesman bank
    bank   = load_bank()
    old_gp = get_balance(bank, nick)
    new_gp = old_gp + n
    set_balance(bank, nick, new_gp)
    save_bank(bank)

    bot.send_privmsg(target,
        f"🌿→💰 \x02{nick}\x02: "
        f"-{n} 420-pts (chr0n) → +{n} GP (Talesman)  "
        f"[420-pts: {new_pts}  |  GP: {new_gp}]")


# ================================================================
# !gp2pts [n]  — exchange N Talesman GP → 420-pts in chr0n's file
# ================================================================

def cmd_gp2pts(bot, nick, target, args):
    """`!gp2pts [n]` — convert N D&D GP back to 420-pts (removes from Talesman, adds to chr0n)."""
    bank       = load_bank()
    current_gp = get_balance(bank, nick)
    if current_gp <= 0:
        bot.send_privmsg(target,
            f"{nick}: you have 0 GP in Talesman. "
            f"Earn some by fighting monsters or getting DM awards!")
        return

    parts = args.strip().split()
    if parts:
        try:
            n = int(parts[0])
        except ValueError:
            bot.send_privmsg(target, f"{nick}: !gp2pts [n]  e.g. !gp2pts 10")
            return
    else:
        n = current_gp

    if n <= 0:
        bot.send_privmsg(target, f"{nick}: amount must be positive.")
        return
    if n > current_gp:
        bot.send_privmsg(target,
            f"{nick}: you only have {current_gp} GP (requested {n}).")
        return

    # Deduct from Talesman bank
    new_gp = current_gp - n
    set_balance(bank, nick, new_gp)
    save_bank(bank)

    # Add to chr0n's file
    new_pts = chr0n.add(nick, n,
        f"exchange-from-gp-{datetime.date.today()}")

    bot.send_privmsg(target,
        f"💰→🌿 \x02{nick}\x02: "
        f"-{n} GP (Talesman) → +{n} 420-pts (chr0n)  "
        f"[GP: {new_gp}  |  420-pts: {new_pts}]")


# ================================================================
# !cash  — redeem 420 pts from chr0n's file for the gift card
# ================================================================

def cmd_cash(bot, nick, target, args):
    """`!cash` — check eligibility or redeem 420 pts for a gift card."""
    pts = chr0n.get_balance(nick)
    gp  = get_balance(load_bank(), nick)

    if pts < CASH_THRESHOLD and gp < CASH_THRESHOLD:
        need_pts = CASH_THRESHOLD - pts
        need_gp  = CASH_THRESHOLD - gp
        bot.send_privmsg(target,
            f"{nick}: 🌿 {pts} 420-pts (need {need_pts} more)  |  "
            f"💰 {gp} GP (need {need_gp} more)  — keep toking and fighting!")
        return

    if pts >= CASH_THRESHOLD:
        bot.send_privmsg(target,
            f"\x02{nick}\x02: 🌿 You have \x02{pts} 420-pts\x02 — "
            f"enough to redeem for \x02{CASH_LABEL}\x02!")
    if gp >= CASH_THRESHOLD:
        bot.send_privmsg(target,
            f"\x02{nick}\x02: 💰 You also have \x02{gp} GP\x02 in Talesman. "
            f"Use \x02!gp2pts {CASH_THRESHOLD}\x02 to move them to 420-pts first.")

    bot.send_privmsg(target,
        f"PM \x02{CASH_CONTACT}\x02 to arrange your gift card redemption. "
        f"When confirmed, {CASH_THRESHOLD} pts will be deducted from chr0n's ledger.")
    bot.send_privmsg(nick,
        f"You are eligible to cash in {CASH_THRESHOLD} 420-pts for {CASH_LABEL}. "
        f"Contact {CASH_CONTACT} on IRC to arrange. "
        f"Your points will be deducted from chr0n's file when confirmed.")
