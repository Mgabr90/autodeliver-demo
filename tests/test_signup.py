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
