# autodeliver demo: system (living doc)

What is built **now**, as it stands on `main`. It is not a plan and not a history: each phase that changes the shape of the system updates this file in the same change, and the drift check compares it with the code. New sessions and design reviewers read it to learn the system without reading every file.

## Purpose

A small, correct sign-up service (email and password) that is safe to abuse-test: valid input only, one account per email, and no silent failures. It exists to demonstrate the autodeliver loop on one real phase.

## Components

| Component | Where (paths) | Does | Talks to |
|---|---|---|---|
| Validator | `signup/validator.py` | `normalize_email` (the canonical email: trimmed, lower case; non-strings give `""`), `validate_email` (shape check, returns the canonical form) and `validate_password` (at least `MIN_PASSWORD_LENGTH` = 8 characters, inclusive, with a letter and a digit). Raises `ValidationError(field, message)`. | nothing |
| Failed-attempt limiter | `signup/ratelimit.py` | `FailedAttemptLimiter(*, max_failures=5, window_seconds=900, clock=time.monotonic)`: per-key failure times in memory (`_failures`). `record_failure(key)` adds one and prunes every key; `is_blocked(key)` is true with `max_failures` or more failures younger than `window_seconds` (sliding window), and never adds a key. Not thread-safe. | nothing |
| User store | `signup/store.py` | `UserStore`: in-memory dict keyed by the canonical email. `add` refuses an existing key with `DuplicateEmail`, stores a PBKDF2-SHA256 hash with a random salt, and `welcome_sent=False`. `exists`, `get`, `count`. | nothing |
| Sign-up service | `signup/service.py` | `SignupService(store=None, mailer=None, limiter=None)`. `signup(email, password)` → `SignupResult(ok, error_field, message)`: validate the email (malformed: return, nothing recorded); if the limiter blocks the canonical email, return "Too many attempts. Try again later."; validate the password and add to the store, recording a failure on a bad password or a duplicate; call the optional `mailer(email)` and set `welcome_sent` only if it returned without raising. | Validator, Limiter, User store, mailer |
| Tests | `tests/test_signup.py` | pytest suite; the proof is `python -m pytest -q`. | — |

## Data

One in-memory store and one in-memory limiter per `SignupService` instance (lost on restart). Each user record: `email` (canonical), `salt`, `hash`, `welcome_sent`. The limiter holds canonical emails with recent failures and their times. Personal data: the email address. Passwords are never stored in clear.

## Outside services

- **Mailer** (optional callable passed to `SignupService`): sends the welcome email. When it is absent, no email is sent and `welcome_sent` stays false. When it raises, a warning is logged, `welcome_sent` stays false, and the sign-up still succeeds (ruling P01 R9).

## Key decisions

- The duplicate-email refusal is worded neutrally ("Could not create the account."), with `error_field="email"` (P01 R7).
- One canonical email (trimmed, lower case) for the store and the limiter, so case variants are the same account (P01 R6).
- Failed attempts are bad passwords and duplicates for a well-formed email; 5 within 15 minutes block that email for the rest of the window (P01 R4, R5).

## Not built yet

- Nothing on the roadmap yet beyond the publishing gate.
