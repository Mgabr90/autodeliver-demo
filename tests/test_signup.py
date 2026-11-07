from signup.service import SignupService
from signup.validator import ValidationError, validate_email, validate_password

import pytest


def test_valid_signup_creates_account_and_sends_welcome():
    sent = []
    svc = SignupService(mailer=sent.append)
    result = svc.signup("ana@example.com", "orange123x")
    assert result.ok
    assert sent == ["ana@example.com"]
    assert svc.store.get("ana@example.com")["welcome_sent"] is True


def test_bad_email_is_rejected():
    with pytest.raises(ValidationError):
        validate_email("not-an-email")


def test_password_needs_a_digit():
    with pytest.raises(ValidationError):
        validate_password("onlyletterslong")


def test_same_email_twice_is_refused():
    svc = SignupService()
    assert svc.signup("bo@example.com", "orange123x").ok
    second = svc.signup("bo@example.com", "orange123x")
    assert not second.ok
    assert second.error_field == "email"


# --- P01 validator (V1-V3)

from signup.validator import normalize_email


def test_v1_email_is_canonical():
    assert validate_email("  Ana@Example.COM ") == "ana@example.com"


def test_v2_password_minimum_is_inclusive():
    assert validate_password("abcdef12") == "abcdef12"
    with pytest.raises(ValidationError):
        validate_password("abcde12")


def test_v3_normalize_non_string():
    assert normalize_email(None) == ""


# --- P01 service (S1-S10)

from signup.ratelimit import FailedAttemptLimiter

GOOD = "orange123x"
SHORT = "abc1"
BLOCKED = "Too many attempts. Try again later."


class FakeClock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t


def service(clock=None, **kw):
    clock = clock or FakeClock()
    return SignupService(limiter=FailedAttemptLimiter(clock=clock), **kw), clock


def fail_at(svc, clock, email, times):
    for t in times:
        clock.t = t
        assert not svc.signup(email, SHORT).ok


def test_s1_sixth_attempt_blocked_and_nothing_stored():
    svc, clock = service()
    fail_at(svc, clock, "dee@example.com", [0, 1, 2, 3, 4])
    r = svc.signup("dee@example.com", GOOD)
    assert (r.ok, r.error_field, r.message) == (False, "email", BLOCKED)
    assert svc.store.count() == 0


def test_s2_duplicates_count_as_failures():
    svc, _ = service()
    assert svc.signup("eve@example.com", GOOD).ok
    for _ in range(5):
        assert svc.signup("eve@example.com", GOOD).message == "Could not create the account."
    assert svc.signup("eve@example.com", GOOD).message == BLOCKED


def test_s3_blocked_attempts_record_nothing():
    svc, clock = service()
    fail_at(svc, clock, "fay@example.com", [0, 100, 200, 300, 400])
    for t in (500, 600):
        clock.t = t
        assert svc.signup("fay@example.com", SHORT).message == BLOCKED
    clock.t = 900
    assert not svc.limiter.is_blocked("fay@example.com")


def test_s4_after_expiry_signup_succeeds():
    svc, clock = service()
    fail_at(svc, clock, "gus@example.com", [0, 100, 200, 300, 400])
    clock.t = 900
    assert svc.signup("gus@example.com", GOOD).ok


def test_s5_case_variant_is_a_duplicate():
    svc, _ = service()
    assert svc.signup("Bo@Example.com", GOOD).ok
    r = svc.signup("bo@example.com", GOOD)
    assert (r.ok, r.error_field, r.message) == (False, "email", "Could not create the account.")
    assert svc.store.count() == 1


def test_s6_case_variants_share_one_limiter_key():
    svc, clock = service()
    fail_at(svc, clock, "Cy@Example.com", [0, 1, 2])
    fail_at(svc, clock, "cy@example.com", [3, 4])
    assert svc.signup("CY@EXAMPLE.COM", GOOD).message == BLOCKED


def test_s7_malformed_email_records_nothing():
    svc, _ = service()
    for _ in range(6):
        assert svc.signup("not-an-email", GOOD).error_field == "email"
    assert svc.limiter._failures == {}
    assert svc.signup("hal@example.com", GOOD).ok


def test_s8_no_mailer_means_welcome_not_sent():
    svc, _ = service()
    assert svc.signup("ida@example.com", GOOD).ok
    assert svc.store.get("ida@example.com")["welcome_sent"] is False


def test_s9_mailer_failure_is_not_recorded_as_sent():
    def broken(email):
        raise RuntimeError("smtp down")

    svc, _ = service(mailer=broken)
    r = svc.signup("jo@example.com", GOOD)
    assert r.ok
    assert svc.store.get("jo@example.com")["welcome_sent"] is False


def test_s10_success_neither_records_nor_resets():
    svc, clock = service()
    fail_at(svc, clock, "kim@example.com", [0, 1, 2, 3])
    assert svc.signup("lou@example.com", GOOD).ok
    fail_at(svc, clock, "kim@example.com", [5])
    assert svc.signup("kim@example.com", GOOD).message == BLOCKED

    svc, clock = service()
    fail_at(svc, clock, "max@example.com", [0, 1, 2, 3])
    assert svc.signup("max@example.com", GOOD).ok
    fail_at(svc, clock, "max@example.com", [5])
    assert svc.limiter.is_blocked("max@example.com")
