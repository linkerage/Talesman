import time
import threading
from config import ADMINS

class Cooldowns:
    def __init__(self, seconds: float):
        self.seconds = seconds
        self.last = {}
        self.lock = threading.Lock()

    def check(self, user: str) -> float:
        """
        Returns:
            0  → allowed now
            >0 → number of seconds remaining
        Admins bypass cooldowns.
        """
        user = user.lower()

        # Admin bypass
        if user in ADMINS:
            return 0

        now = time.time()
        with self.lock:
            last_time = self.last.get(user, 0)
            remaining = (last_time + self.seconds) - now

            if remaining <= 0:
                self.last[user] = now
                return 0

            return remaining

    def reset(self):
        """Clear all cooldowns (useful on reconnect)."""
        with self.lock:
            self.last.clear()

