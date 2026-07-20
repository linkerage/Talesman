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


def send_typing_indicator(bot, target, nick):
    """
    Sends a temporary typing indicator to IRC.
    """
    bot.send_privmsg(target, f"{nick}: …thinking…")


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

            # Acknowledge queue
            bot.send_privmsg(target, f"{nick}: your question has been queued…")

            # Typing indicator
            send_typing_indicator(bot, target, nick)

            first_chunk = True

            # Simple rate limiting: max ~3 lines/sec
            LINE_DELAY = 0.3

            # STREAMING RESPONSE
            buffer = ""

            for chunk in stream_fn(prompt):
                if chunk is None:
                    continue

                buffer += chunk

                # On first real output, clear typing indicator with a header
                if first_chunk:
                    first_chunk = False
                    bot.send_privmsg(target, f"{nick}: answer:")

                # Convert accumulated markdown to IRC
                formatted = markdown_to_irc(buffer)
                buffer = ""  # reset after conversion

                for line in formatted.split("\n"):
                    if not line.strip():
                        continue
                    bot.send_privmsg(target, f"{nick}: {line}")
                    time.sleep(LINE_DELAY)

        except Exception as e:
            logging.error(f"Gemini worker error: {e}")
            time.sleep(1)

