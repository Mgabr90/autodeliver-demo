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

    def _prune(self, key, now):
        """Keep only the key's counting failures; delete the key if none are left. Returns them."""
        recent = [t for t in self._failures.get(key, ()) if now - t < self.window_seconds]
        if recent:
            self._failures[key] = recent
        else:
            self._failures.pop(key, None)
        return recent

    def record_failure(self, key):
        now = self._clock()
        self._failures.setdefault(key, []).append(now)
        for k in list(self._failures):
            self._prune(k, now)

    def is_blocked(self, key):
        if key not in self._failures:
            return False
        return len(self._prune(key, self._clock())) >= self.max_failures
