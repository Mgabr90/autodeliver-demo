"""Input rules for sign-up: email shape and password strength."""

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


class ValidationError(ValueError):
    """Raised when sign-up input breaks a rule. `field` names the input."""

    def __init__(self, field, message):
        super().__init__(message)
        self.field = field


def normalize_email(value):
    """The canonical form of an email: surrounding spaces removed, lower case. Non-strings give ""."""
    return value.strip().lower() if isinstance(value, str) else ""


def validate_email(email):
    """Check the shape of the email and return its canonical form."""
    email = normalize_email(email)
    if not EMAIL_RE.match(email):
        raise ValidationError("email", "Enter a valid email address.")
    return email


def validate_password(password):
    """Passwords need at least MIN_PASSWORD_LENGTH characters, a letter and a digit."""
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            "password", f"Use at least {MIN_PASSWORD_LENGTH} characters."
        )
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        raise ValidationError("password", "Use at least one letter and one digit.")
    return password
