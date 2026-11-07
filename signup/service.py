"""Sign-up use case: validate, limit failed attempts, store, send the welcome email."""

import logging

from .ratelimit import FailedAttemptLimiter
from .store import DuplicateEmail, UserStore
from .validator import ValidationError, validate_email, validate_password

log = logging.getLogger(__name__)

BLOCKED_MESSAGE = "Too many attempts. Try again later."
DUPLICATE_MESSAGE = "Could not create the account."


class SignupResult:
    def __init__(self, ok, error_field=None, message=""):
        self.ok = ok
        self.error_field = error_field
        self.message = message


class SignupService:
    def __init__(self, store=None, mailer=None, limiter=None):
        self.store = store or UserStore()
        self.mailer = mailer  # callable(email) that sends the welcome email
        self.limiter = limiter or FailedAttemptLimiter()

    def signup(self, email, password):
        try:
            email = validate_email(email)  # canonical form; malformed emails record nothing
        except ValidationError as e:
            return SignupResult(False, e.field, str(e))
        if self.limiter.is_blocked(email):
            return SignupResult(False, "email", BLOCKED_MESSAGE)
        try:
            password = validate_password(password)
        except ValidationError as e:
            self.limiter.record_failure(email)
            return SignupResult(False, e.field, str(e))
        try:
            user = self.store.add(email, password)
        except DuplicateEmail:
            self.limiter.record_failure(email)
            return SignupResult(False, "email", DUPLICATE_MESSAGE)
        if self.mailer:
            try:
                self.mailer(email)
            except Exception:
                log.warning("welcome email failed for a new account")
            else:
                user["welcome_sent"] = True
        return SignupResult(True, message="Account created.")
