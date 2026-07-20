import time
import threading
from config import ADMINS

class ChannelCooldowns:
    def __init__(self, seconds: float):
        self.seconds = seconds
        self.last = {}
        self.lock = threading.Lock()

    def check(self, channel: str, nick: str | None = None) -> float:
        """
        Returns:
            0  → allowed now
            >0 → seconds remaining
        Admins bypass channel cooldowns.
        """
        # Normalize channel name
        channel = channel.lower()

        # Admin bypass
        if nick and nick.lower() in ADMINS:
            return 0

        now = time.time()
        with self.lock:
            last_time = self.last.get(channel, 0)
            remaining = (last_time + self.seconds) - now

            if remaining <= 0:
                self.last[channel] = now
                return 0

            return remaining

    def reset(self):
        """Clear all channel cooldowns (useful on reconnect)."""
        with self.lock:
            self.last.clear()

