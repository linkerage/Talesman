#!/usr/bin/env python3
"""
Gemini worker thread for Talesman.
Thread-safe, rate-limited, admin-aware streaming.
"""

import logging
import time
import queue

from gemini_client import stream_gemini, stream_gemini_admin, markdown_to_irc
from config import ADMINS

# Bounded queue to avoid unbounded memory / API spam
ASK_QUEUE_MAXSIZE = 50
ask_queue = queue.Queue(maxsize=ASK_QUEUE_MAXSIZE)


def enqueue_question(bot, nick: str, target: str, prompt: str):
    """
    Called by commands.py when a user runs !ask.
    Enqueues a question for the worker thread.
    If the queue is full, politely reject.
    """
    try:
        ask_queue.put_nowait((nick, target, prompt))
    except queue.Full:
        bot.send_privmsg(target, f"{nick}: ask queue is full, try again later.")


MAX_ANSWER_LINES = 3   # max lines sent to channel per !ask response


def ask_worker(bot):
    logging.info("Gemini worker thread running.")

    while True:
        try:
            nick, target, prompt = ask_queue.get()
            logging.info(f"Gemini ask: nick={nick} target={target} prompt={prompt}")

            # Admin detection: prefer NickServ account if available
            account = bot.nickserv_account or nick
            is_admin = account in ADMINS

            stream_fn = stream_gemini_admin if is_admin else stream_gemini

            # Acknowledge queue (keep this one — it's the only pre-answer line)
            bot.send_privmsg(target, f"{nick}: your question has been queued…")

            # Collect the full streamed response before sending anything
            buffer = ""
            for chunk in stream_fn(prompt):
                if chunk is not None:
                    buffer += chunk

            # Convert markdown to plain IRC text, split into non-blank lines
            full_text = markdown_to_irc(buffer.strip())
            lines = [l for l in full_text.split("\n") if l.strip()]

            if len(lines) <= MAX_ANSWER_LINES:
                # Short answer — send entirely in channel
                for line in lines:
                    bot.send_privmsg(target, f"{nick}: {line}")
            else:
                # Long answer — send first 3 lines as summary to channel,
                # then full answer via PM
                for line in lines[:MAX_ANSWER_LINES]:
                    bot.send_privmsg(target, f"{nick}: {line}")
                bot.send_privmsg(target,
                    f"{nick}: … (full answer sent via PM)")
                # PM the complete response via flood-safe bulk sender
                pm_lines = [f"\x02[!ask] {prompt}\x02"] + \
                           [f"  {l}" for l in lines]
                bot.send_pm_bulk(nick, pm_lines)

        except Exception as e:
            logging.error(f"Gemini worker error: {e}")
            time.sleep(1)

