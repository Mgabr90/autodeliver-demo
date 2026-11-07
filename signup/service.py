"""Sign-up use case: validate, store, send the welcome email."""

import logging

from .store import DuplicateEmail, UserStore
from .validator import ValidationError, validate_email, validate_password

log = logging.getLogger(__name__)


class SignupResult:
    def __init__(self, ok, error_field=None, message=""):
        self.ok = ok
        self.error_field = error_field
        self.message = message


class SignupService:
    def __init__(self, store=None, mailer=None):
        self.store = store or UserStore()
        self.mailer = mailer  # callable(email) that sends the welcome email

    def signup(self, email, password):
        try:
            email = validate_email(email)
            password = validate_password(password)
        except ValidationError as e:
            return SignupResult(False, e.field, str(e))
        try:
            user = self.store.add(email, password)
        except DuplicateEmail:
            return SignupResult(False, "email", "Could not create the account.")
        try:
            if self.mailer:
                self.mailer(email)
        except Exception:  # the mail service is optional
            log.warning("welcome email failed for a new account")
        user["welcome_sent"] = True
        return SignupResult(True, message="Account created.")
