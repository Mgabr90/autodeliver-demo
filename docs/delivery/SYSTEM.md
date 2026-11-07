# autodeliver demo: system (living doc)

What is built **now**, as it stands on `main`. It is not a plan and not a history: each phase that changes the shape of the system updates this file in the same change, and the drift check compares it with the code. New sessions and design reviewers read it to learn the system without reading every file.

## Purpose

A small, correct sign-up service (email and password) that is safe to abuse-test: valid input only, one account per email, and no silent failures. It exists to demonstrate the autodeliver loop on one real phase.

## Components

| Component | Where (paths) | Does | Talks to |
|---|---|---|---|
| Validator | `signup/validator.py` | `validate_email` (shape check, trims spaces) and `validate_password` (minimum length `MIN_PASSWORD_LENGTH` = 8, at least one letter and one digit). Raises `ValidationError(field, message)`. | nothing |
| User store | `signup/store.py` | `UserStore`: in-memory dict keyed by email. `add` refuses an existing key with `DuplicateEmail`, stores a PBKDF2-SHA256 hash with a random salt, and `welcome_sent=False`. `exists`, `get`, `count`. | nothing |
| Sign-up service | `signup/service.py` | `SignupService.signup(email, password)` → `SignupResult(ok, error_field, message)`: validate, add to the store, call the optional `mailer(email)`, then set `welcome_sent`. | Validator, User store, mailer |
| Tests | `tests/test_signup.py` | pytest suite; the proof is `python -m pytest -q`. | — |

## Data

One in-memory store per `SignupService` instance (lost on restart). Each user record: `email`, `salt`, `hash`, `welcome_sent`. Personal data: the email address. Passwords are never stored in clear.

## Outside services

- **Mailer** (optional callable passed to `SignupService`): sends the welcome email. When it is absent, no email is sent.

## Key decisions

- The duplicate-email refusal is worded neutrally ("Could not create the account."), with `error_field="email"`.

## Not built yet

- P01: limiting repeated failed sign-up attempts per email (`docs/delivery/ROADMAP.md`).
