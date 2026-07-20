import time
import threading

class RateLimiter:
    def __init__(self, rate: float, per: float):
        """
        rate = number of tokens
        per  = seconds
        Example: RateLimiter(1, 1) → 1 request per second
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()
        self.lock = threading.Lock()

    def wait(self):
        """
        Blocking wait until a token is available.
        Safe for multi-threaded use.
        """
        sleep_time = 0

        with self.lock:
            now = time.time()
            elapsed = now - self.last_check
            self.last_check = now

            # refill tokens
            self.allowance += elapsed * (self.rate / self.per)
            if self.allowance > self.rate:
                self.allowance = self.rate

            # need to wait?
            if self.allowance < 1.0:
                sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
                self.allowance = 0
            else:
                self.allowance -= 1.0

        # sleep OUTSIDE the lock
        if sleep_time > 0:
            time.sleep(sleep_time)

    def remaining(self) -> float:
        """
        Non-blocking check:
        Returns 0 if allowed now,
        otherwise returns seconds remaining.
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_check

            projected = self.allowance + elapsed * (self.rate / self.per)
            if projected >= 1.0:
                return 0

            return (1.0 - projected) * (self.per / self.rate)

