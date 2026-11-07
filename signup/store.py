"""A small in-memory user store."""

import hashlib
import os


class DuplicateEmail(Exception):
    pass


class UserStore:
    def __init__(self):
        self._users = {}

    def exists(self, email):
        return email in self._users

    def add(self, email, password):
        if self.exists(email):
            raise DuplicateEmail(email)
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        self._users[email] = {
            "email": email,
            "salt": salt,
            "hash": digest,
            "welcome_sent": False,
        }
        return self._users[email]

    def get(self, email):
        return self._users.get(email)

    def count(self):
        return len(self._users)
