from signup.ratelimit import FailedAttemptLimiter


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t


def make(clock=None, **kw):
    return FailedAttemptLimiter(clock=clock or FakeClock(), **kw)


def test_l1_new_key_not_blocked_and_no_entry_added():
    lim = make()
    assert not lim.is_blocked("a@example.com")
    assert "a@example.com" not in lim._failures


def test_l2_blocked_on_fifth_failure():
    lim = make()
    for _ in range(4):
        lim.record_failure("a@example.com")
    assert not lim.is_blocked("a@example.com")
    lim.record_failure("a@example.com")
    assert lim.is_blocked("a@example.com")


def test_l3_sliding_window_exact_edges():
    clock = FakeClock()
    lim = make(clock)
    for t in (0, 100, 200, 300, 400):
        clock.t = t
        lim.record_failure("a@example.com")
    clock.t = 899
    assert lim.is_blocked("a@example.com")
    clock.t = 900  # the failure at t=0 is exactly window_seconds old: no longer counts
    assert not lim.is_blocked("a@example.com")


def test_l4_keys_are_independent():
    lim = make()
    for _ in range(5):
        lim.record_failure("a@example.com")
    assert lim.is_blocked("a@example.com")
    assert not lim.is_blocked("b@example.com")


def test_l5_expired_key_deleted_on_next_record_for_any_key():
    clock = FakeClock()
    lim = make(clock)
    lim.record_failure("old@example.com")
    clock.t = 1000
    lim.record_failure("new@example.com")
    assert "old@example.com" not in lim._failures
    assert "new@example.com" in lim._failures


def test_l6_defaults():
    lim = FailedAttemptLimiter()
    assert lim.max_failures == 5
    assert lim.window_seconds == 900


def test_l7_limiters_do_not_share_state():
    a, b = make(), make()
    for _ in range(5):
        a.record_failure("x@example.com")
    assert a.is_blocked("x@example.com")
    assert not b.is_blocked("x@example.com")
