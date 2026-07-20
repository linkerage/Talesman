#!/usr/bin/env python3
"""
Talesman IRC Bot — Main Loop with SASL + NickServ Status
"""

import ssl
import socket
import time
import threading
import logging
import base64

from utils import parse_command
from commands import handle_command
import gemini
import game
from config import (
    IRC_SERVER, IRC_PORT,
    IRC_NICK, IRC_USER, IRC_REALNAME,
    IRC_CHANNELS, NICKSERV_PASSWORD,
    SASL_ENABLED,
)

START_TIME = time.time()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)


def nickserv_ghost(bot):
    if NICKSERV_PASSWORD:
        bot.send_privmsg("NickServ", f"GHOST {IRC_NICK} {NICKSERV_PASSWORD}")
        time.sleep(1)


def nickserv_identify(bot):
    if NICKSERV_PASSWORD:
        bot.send_privmsg("NickServ", f"IDENTIFY {NICKSERV_PASSWORD}")
        time.sleep(1)


# Minimum seconds between consecutive sends to the same context.
# Libera.chat uses a token-bucket; staying at 2 msg/sec keeps us
# well clear of the flood limit on channels, and 6-7 msg/sec is
# fine for PMs.
CHANNEL_SEND_DELAY = 0.50   # 2 msgs / sec — conservative for channels
PM_SEND_DELAY      = 0.15   # ~6 msgs / sec — fine for PMs / wizard
CTRL_SEND_DELAY    = 0.05   # PONG, JOIN, NICK, etc.


class TalesmanBot:
    def __init__(self):
        self.sock = None
        self.buffer = ""
        self.reconnect_delay = 10  # seconds

        # NickServ / SASL status
        self.nickserv_identified = False
        self.nickserv_account = None
        self.nickserv_last_event = None
        self.last_nickserv_check = 0

        # Rate limiter — shared across all threads
        self._send_lock      = threading.Lock()
        self._last_send_time = 0.0

    # ------------------------------------------------------------
    # IRC SEND HELPERS
    # ------------------------------------------------------------
    def _throttled_send(self, raw: str, delay: float):
        """Send one raw IRC line, sleeping enough to stay under flood limits."""
        with self._send_lock:
            elapsed = time.monotonic() - self._last_send_time
            if elapsed < delay:
                time.sleep(delay - elapsed)
            self.sock.send((raw + "\r\n").encode("utf-8", errors="replace"))
            self._last_send_time = time.monotonic()
        # Mask NickServ credential commands so passwords never appear in logs
        log_line = raw
        if "PRIVMSG NickServ" in raw and any(
            kw in raw.upper() for kw in ("IDENTIFY", "GHOST", "REGISTER", "SET PASSWORD")
        ):
            log_line = raw.split()[0:3]
            log_line = " ".join(log_line) + " <masked>"
        logging.info(f">>> {log_line}")

    def send_raw(self, msg: str):
        """Control messages (PONG, JOIN, NICK, CAP …) — light throttle."""
        self._throttled_send(msg, CTRL_SEND_DELAY)

    def send_privmsg(self, target: str, msg: str):
        """
        Send PRIVMSG lines with flood-safe pacing.
        Channel targets use CHANNEL_SEND_DELAY; PMs use PM_SEND_DELAY.
        Blank lines are skipped so they don't waste flood budget.
        """
        delay = CHANNEL_SEND_DELAY if target.startswith("#") else PM_SEND_DELAY
        for line in msg.split("\n"):
            if not line.strip():   # skip blank / whitespace-only lines
                continue
            self._throttled_send(f"PRIVMSG {target} :{line}", delay)

    def send_pm_bulk(self, nick: str, lines):
        """
        Send a large block of PM lines at CHANNEL_SEND_DELAY (0.5 s/line).
        Use this instead of send_privmsg for any bulk PM output (e.g. !readme)
        to stay safely under Libera's flood threshold regardless of length.
        Blank/whitespace-only lines are skipped.
        """
        for line in lines:
            if not str(line).strip():
                continue
            self._throttled_send(f"PRIVMSG {nick} :{line}", CHANNEL_SEND_DELAY)

    # ------------------------------------------------------------
    # SASL AUTH
    # ------------------------------------------------------------
    def sasl_auth(self):
        """Perform SASL PLAIN authentication (Libera-style)."""
        if not SASL_ENABLED or not NICKSERV_PASSWORD:
            return False

        logging.info("Starting SASL authentication…")

        # CAP LS / REQ sasl
        self.send_raw("CAP LS")
        self.send_raw("CAP REQ :sasl")

        # Wait for ACK
        while True:
            data = self.sock.recv(4096).decode("utf-8", errors="ignore")
            for line in data.split("\r\n"):
                if not line:
                    continue
                logging.info(f"<<< {line}")
                parts = line.split()
                if len(parts) >= 4 and parts[1] == "CAP" and "ACK" in line and "sasl" in line:
                    logging.info("CAP ACK sasl received.")
                    break
            else:
                continue
            break

        # Begin SASL PLAIN
        self.send_raw("AUTHENTICATE PLAIN")

        # Wait for server "+"
        while True:
            data = self.sock.recv(4096).decode("utf-8", errors="ignore")
            for line in data.split("\r\n"):
                if not line:
                    continue
                logging.info(f"<<< {line}")
                if line.startswith("AUTHENTICATE +"):
                    logging.info("AUTHENTICATE + received.")
                    break
            else:
                continue
            break

        # Build payload: nick\0nick\0password
        payload = f"{IRC_NICK}\0{IRC_NICK}\0{NICKSERV_PASSWORD}"
        encoded = base64.b64encode(payload.encode()).decode()

        # Send encoded credentials
        self.send_raw(f"AUTHENTICATE {encoded}")

        # Wait for success/failure
        success = False
        while True:
            data = self.sock.recv(4096).decode("utf-8", errors="ignore")
            for line in data.split("\r\n"):
                if not line:
                    continue
                logging.info(f"<<< {line}")
                parts = line.split()
                if len(parts) >= 2:
                    cmd = parts[1]
                    if cmd == "903":  # SASL success
                        success = True
                        self.nickserv_identified = True
                        self.nickserv_last_event = "SASL success"
                        logging.info("SASL authentication successful.")
                        break
                    if cmd in ("904", "905"):  # SASL failure
                        self.nickserv_identified = False
                        self.nickserv_last_event = "SASL failure"
                        logging.error("SASL authentication failed.")
                        break
            else:
                continue
            break

        # End CAP
        self.send_raw("CAP END")
        return success

    # ------------------------------------------------------------
    # IRC CONNECTION
    # ------------------------------------------------------------
    def connect(self):
        logging.info("Connecting to IRC…")

        ctx = ssl.create_default_context()
        raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = ctx.wrap_socket(raw, server_hostname=IRC_SERVER)
        self.sock.connect((IRC_SERVER, IRC_PORT))

        # Ghost stale sessions
        nickserv_ghost(self)

        # SASL before NICK/USER if enabled
        if SASL_ENABLED:
            if not self.sasl_auth():
                logging.warning("SASL failed or disabled, falling back to NickServ IDENTIFY.")
        else:
            logging.info("SASL disabled; using NickServ IDENTIFY only.")

        # Register
        self.send_raw(f"NICK {IRC_NICK}")
        self.send_raw(f"USER {IRC_USER} 0 * :{IRC_REALNAME}")

        # If SASL didn't mark us identified, fallback to NickServ IDENTIFY
        if not self.nickserv_identified:
            nickserv_identify(self)

        # Join channels
        for ch in IRC_CHANNELS:
            self.send_raw(f"JOIN {ch}")

        logging.info("Connected and joined channels.")

        # Start Gemini worker
        threading.Thread(
            target=gemini.ask_worker,
            args=(self,),
            daemon=True
        ).start()
        logging.info("Gemini worker thread started.")

    # ------------------------------------------------------------
    # NickServ STATUS polling
    # ------------------------------------------------------------
    def check_nickserv(self):
        self.send_privmsg("NickServ", f"STATUS {IRC_NICK}")

    # ------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------
    def loop(self):
        while True:
            try:
                data = self.sock.recv(4096).decode("utf-8", errors="ignore")
                if not data:
                    raise Exception("Disconnected")

                self.buffer += data

                # Periodic NickServ STATUS check
                now = time.time()
                if now - self.last_nickserv_check > 60:
                    self.check_nickserv()
                    self.last_nickserv_check = now

                while "\r\n" in self.buffer:
                    line, self.buffer = self.buffer.split("\r\n", 1)
                    if not line:
                        continue
                    logging.info(f"<<< {line}")
                    self.handle_line(line)

            except Exception as e:
                logging.error(f"Connection lost: {e}")
                time.sleep(self.reconnect_delay)
                self.connect()

    # ------------------------------------------------------------
    # IRC LINE HANDLING
    # ------------------------------------------------------------
    def parse_prefix(self, prefix: str) -> str:
        if "!" in prefix:
            return prefix.split("!", 1)[0][1:]
        return prefix[1:]

    def handle_line(self, line: str):
        if line.startswith("PING"):
            self.send_raw(f"PONG {line.split()[1]}")
            return

        parts = line.split(" ")
        if len(parts) < 2:
            return

        prefix = parts[0]
        cmd    = parts[1]

        # Nick already in use (433)
        if cmd == "433":
            logging.warning("Nick already in use. Attempting ghost + retry.")
            if NICKSERV_PASSWORD:
                nickserv_ghost(self)
                time.sleep(2)
                self.send_raw(f"NICK {IRC_NICK}")
            return

        # 353 NAMES — build initial channel ops set
        if cmd == "353" and len(parts) >= 5:
            # :server 353 Talesman = #channel :@nick1 nick2 ...
            channel   = parts[4]
            raw_nicks = " ".join(parts[5:])
            if raw_nicks.startswith(":"):
                raw_nicks = raw_nicks[1:]
            game.set_names(channel, raw_nicks)
            return

        # MODE — track +o / -o in all channels
        if cmd == "MODE" and len(parts) >= 4:
            channel = parts[2]
            if channel.startswith("#"):
                modestr = parts[3]
                targets = parts[4:]
                grant   = True
                t_idx   = 0
                for ch in modestr:
                    if ch == '+':
                        grant = True
                    elif ch == '-':
                        grant = False
                    elif ch == 'o' and t_idx < len(targets):
                        game.update_op(channel, targets[t_idx], grant)
                        t_idx += 1
            return

        # PART — remove departing nick from ops tracking
        if cmd == "PART" and len(parts) >= 3:
            channel = parts[2]
            game.remove_nick(channel, self.parse_prefix(prefix))
            return

        # QUIT — remove from all channels
        if cmd == "QUIT":
            quit_nick = self.parse_prefix(prefix)
            for ch in IRC_CHANNELS:
                game.remove_nick(ch, quit_nick)
            return

        # PRIVMSG / NOTICE handling
        if cmd in ("PRIVMSG", "NOTICE"):
            prefix = parts[0]
            target = parts[2]
            msg    = " ".join(parts[3:])[1:] if parts[3].startswith(":") else " ".join(parts[3:])
            nick   = self.parse_prefix(prefix)

            # NickServ STATUS response
            if nick.lower() == "nickserv" and msg.startswith("STATUS"):
                try:
                    _, _, code = msg.split()
                    code = int(code)
                    self.nickserv_last_event = f"NickServ STATUS {code}"
                    if code == 3:
                        self.nickserv_identified = True
                        logging.info("NickServ STATUS: identified.")
                    else:
                        self.nickserv_identified = False
                        logging.warning(f"NickServ STATUS: not identified (code {code}).")
                except Exception as e:
                    logging.error(f"Failed to parse NickServ STATUS: {e}")
                return

            # Normal PRIVMSG command handling
            if cmd == "PRIVMSG":
                self.handle_privmsg(nick, target, msg)
            return

    # ------------------------------------------------------------
    # PRIVMSG COMMAND HANDLER
    # ------------------------------------------------------------
    def handle_privmsg(self, nick: str, target: str, msg: str):
        is_pm = not target.startswith("#")

        # Route non-command PMs to the D&D 5e character creation wizard
        if is_pm and not msg.startswith("!"):
            try:
                from charwizard import is_active, handle_input
                if is_active(nick):
                    handle_input(self, nick, msg)
                    return
            except Exception as e:
                logging.error(f"charwizard routing error for {nick}: {e}")

        # Only handle !commands
        if not msg.startswith("!"):
            return

        # Route to command handler — pass msg intact so handle_command
        # can do its own parsing (parse_command strips the '!' which
        # breaks the COMMANDS dispatch table lookup).
        handle_command(self, nick, target, msg)


# ------------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------------

def main():
    logging.info("Talesman starting...")
    bot = TalesmanBot()

    while True:
        try:
            bot.connect()
            bot.loop()
        except Exception as e:
            logging.error(f"Talesman crashed: {e}")
            logging.info("Restarting in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()

