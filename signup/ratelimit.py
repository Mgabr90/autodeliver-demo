"""Per-key limit on failed sign-up attempts, over a sliding time window."""

import time


class FailedAttemptLimiter:
    """Blocks a key while it has `max_failures` or more failures in the last `window_seconds`.

    A failure counts while `now - t < window_seconds`. State is in memory; not thread-safe.
    """

    def __init__(self, *, max_failures=5, window_seconds=900, clock=time.monotonic):
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self._clock = clock
        self._failures = {}

    def _recent(self, times, now):
        return [t for t in times if now - t < self.window_seconds]

    def record_failure(self, key):
        now = self._clock()
        self._failures.setdefault(key, []).append(now)
        for k in list(self._failures):
            recent = self._recent(self._failures[k], now)
            if recent:
                self._failures[k] = recent
            else:
                del self._failures[k]

    def is_blocked(self, key):
        times = self._failures.get(key)
        if times is None:
            return False
        recent = self._recent(times, self._clock())
        if recent:
            self._failures[key] = recent
        else:
            del self._failures[key]
        return len(recent) >= self.max_failures
