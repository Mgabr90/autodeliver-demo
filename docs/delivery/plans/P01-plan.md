# P01 plan: sign-up hardening

Roadmap row: P01. Ledger: `docs/delivery/ledgers/P01.md`. Research brief: none (no external facts; standard library only, ruling R1). Revision 2, after design review round 1 (`docs/delivery/evidence/P01/design-review-r1-*.md`; resolutions in the ledger).

## Goal and why

Anyone can call `SignupService.signup` as often as they like. Nothing slows down repeated failed attempts for one email: probing whether an address has an account, scripted guessing, or a broken client in a retry loop. And "one account per email" (the goal in `docs/delivery/HANDOFF.md`) is not reliable today: the store compares emails exactly as typed, so `Bo@Example.com` and `bo@example.com` become two accounts.

Round 1 of the design review also found two defects in code this phase touches, which this phase fixes by ruling (R8, R9): an 8-character password is rejected although 8 is the documented minimum, and `welcome_sent` is set to `True` even when no welcome email was sent.

Done when:
- repeated failed sign-ups for one email are refused for a cool-down period with a clear message;
- one canonical form of an email is used for the store and the limiter, so case variants are duplicates;
- an 8-character password is accepted;
- `welcome_sent` is true only after the mailer returned successfully;
- the test plan below passes under the full proof (`python -m pytest -q`), and the gate PASSes.

## Context

From `docs/delivery/SYSTEM.md`: `SignupService.signup` validates input (`signup/validator.py`), adds the user to the in-memory `UserStore` (`signup/store.py`, keyed by the email string, refusing an existing key with `DuplicateEmail`), then calls the optional mailer. Results are `SignupResult(ok, error_field, message)`. There is no limit on attempts today, and the store is in memory, per service instance. The code is single-threaded; nothing here adds threads.

## Design

- **One canonical email (validator).** A helper `normalize_email(value)` in `signup/validator.py` returns `value.strip().lower()` for a string and `""` otherwise. `validate_email` checks the shape of the normalized value and returns it. The store therefore always receives the canonical form; `UserStore` itself is unchanged.
- **FailedAttemptLimiter** (new, `signup/ratelimit.py`): `FailedAttemptLimiter(*, max_failures=5, window_seconds=900, clock=time.monotonic)`, in-memory state `dict[str, list[float]]`.
  - A failure *counts* while `now - t < window_seconds`; a failure exactly `window_seconds` old no longer counts.
  - `record_failure(key)`: appends `clock()` for the key, then prunes every key in the map, deleting keys whose list is empty after pruning.
  - `is_blocked(key)`: true when the key has `max_failures` or more counting failures. It never inserts a key; it may prune and delete the key it reads.
  - **Block length (sliding window):** a key is unblocked as soon as fewer than `max_failures` of its failures still count, that is `window_seconds` after the oldest of its last `max_failures` failures. Blocked attempts record nothing.
- **SignupService** gets an optional `limiter` argument; when none is given, `__init__` builds a new `FailedAttemptLimiter()` (inside `__init__`, never as a default argument value, so instances don't share state). `signup(email, password)`:
  1. Validate the email shape (`validate_email`). On failure, return the validation result. Nothing is recorded (R4).
  2. `key` = the canonical email. If `limiter.is_blocked(key)`: return the blocked result (R5) without checking the password or touching the store.
  3. Validate the password. On failure, `record_failure(key)` and return the validation result.
  4. Add to the store. On `DuplicateEmail`, `record_failure(key)` and return the duplicate result (unchanged wording).
  5. Welcome email: if a mailer is configured, call it; set `welcome_sent = True` only if the call returned without raising. If it raises, log a warning, leave `welcome_sent` false, and still return success (the account exists). With no mailer, `welcome_sent` stays false.
  6. A successful sign-up records nothing and does not reset the key.

## Alternatives considered

- **Limit per client IP:** rejected. The service has no request context, and the abuse this phase targets is per email.
- **Exponential back-off, or a lockout timed from the last failure:** rejected (YAGNI). The sliding window is the simplest rule and is easy to test.
- **Persisting attempts in `UserStore`:** rejected. Failed attempts are not users, and mixing them couples two concerns.
- **A third-party rate-limit library:** rejected. The hard limits allow the standard library only (R1).
- **Normalizing inside `UserStore`:** rejected. The validator is the one place that defines a valid email, and the limiter needs the same key before the store is involved.

## Risks and fail-safe

- **Memory:** entries exist only for well-formed emails with a counting failure. Every `record_failure` prunes the whole map, so stale keys don't pile up. Each call costs O(number of tracked keys), which is acceptable at demo scale (R3).
- **Locking out a real user:** someone else can use up the limit for a victim's email. Accepted for this phase: the block lasts at most 15 minutes and the message says to retry later (R4). The password-length defect, which would have locked out honest users, is fixed here (R8).
- **Fail-safe mail:** an unsent welcome email is never recorded as sent (R9).
- **Clock:** `time.monotonic` can't go backwards.
- **Concurrency:** the check and the record are not atomic. That is fine here because the service is single-threaded, and is stated as an assumption.

## Decisions

- **R1:** standard library only; no new dependencies. Cost if wrong: none (hard limit).
- **R2:** defaults `max_failures=5`, `window_seconds=900`; keyword-only constructor arguments. Cost if wrong: low.
- **R3:** in-memory state per service instance; whole-map prune on each recorded failure. Cost if wrong: low at demo scale.
- **R4:** failures are password-validation errors and duplicate-email refusals for a well-formed email. Malformed emails and blocked attempts record nothing. Cost if wrong: medium (blocks could be shorter or longer than intended).
- **R5:** the blocked result is `SignupResult(False, "email", "Too many attempts. Try again later.")`, returned before the password check and before the store. Cost if wrong: low.
- **R6:** the canonical email is `strip().lower()` of the whole address, produced by `normalize_email` and used by both the store and the limiter. Cost if wrong: low. Mailbox local parts are case-sensitive in theory, but in practice providers treat them as case-insensitive, and two accounts for one inbox is the worse outcome.
- **R7:** the duplicate result stays `SignupResult(False, "email", "Could not create the account.")`, neutral on purpose.
- **R8 (boundary extended):** fix `validate_password` so that a password of exactly `MIN_PASSWORD_LENGTH` characters is accepted (`<` instead of `<=`). Cost if wrong: low.
- **R9 (boundary extended):** `welcome_sent` is true only after the mailer returns successfully; a mailer failure still returns success, with a warning log. Cost if wrong: medium (a later phase might want to report the mail failure to the caller).

## File boundary

- `signup/ratelimit.py` (new)
- `signup/service.py` (change)
- `signup/validator.py` (change: R6, R8)
- `tests/test_ratelimit.py` (new)
- `tests/test_signup.py` (change)

The delivery files under `docs/delivery/` are exempt, as `docs/delivery/HANDOFF.md` ("Review gate") says.

## Tasks

1. **Limiter.** Write `tests/test_ratelimit.py` first (L1 to L7), then `signup/ratelimit.py`. Done when: L1 to L7 pass.
2. **Validator.** Add V1 to V3 to `tests/test_signup.py` first, then change `signup/validator.py` (R6, R8). Done when: V1 to V3 and the existing tests pass.
3. **Service wiring and mail fail-safe.** Add S1 to S10 to `tests/test_signup.py` first, then change `signup/service.py` as in "Design". The tests build the service as `SignupService(limiter=FailedAttemptLimiter(clock=fake))`, where `fake` is a callable returning a number the test controls. Done when: all tests pass.
4. **End of phase:**
   - one simplify pass over the phase's files, as its own `refactor(simplify)` commit (or a ledger line saying nothing needed simplifying);
   - update `docs/delivery/SYSTEM.md` (canonical email, the limiter in the flow, R5, R9);
   - full proof, then the final whole-phase review (the gate);
   - ledger and roadmap update.

   Done when: `python -m pytest -q` is green and the ledger records it.

## Test plan

Limiter (`tests/test_ratelimit.py`, fake clock):
- **L1:** a new key is not blocked, and `is_blocked` adds no entry for it.
- **L2:** 4 failures: not blocked; the 5th: blocked.
- **L3:** sliding window exactness: failures at t=0, 100, 200, 300, 400. Blocked at t=899; not blocked at t=900, because the failure at t=0 is exactly `window_seconds` old and no longer counts.
- **L4:** keys are independent.
- **L5:** a key whose failures have all expired is deleted from the map on the next `record_failure` for any key.
- **L6:** default construction gives `max_failures=5` and `window_seconds=900`.
- **L7:** two limiters don't share state.

Validator (`tests/test_signup.py`):
- **V1:** `validate_email("  Ana@Example.COM ")` returns `"ana@example.com"`.
- **V2:** an 8-character password with a letter and a digit (`"abcdef12"`) is accepted; a 7-character one (`"abcde12"`) is rejected.
- **V3:** `normalize_email(None)` returns `""`.

Service (`tests/test_signup.py`, valid password `"orange123x"`):
- **S1:** five sign-ups for one email with a too-short password, then a sixth with a valid password: the sixth gets the R5 result and no user is stored (`store.count() == 0`).
- **S2:** duplicates count: one success, then five duplicate attempts, then a seventh attempt: blocked (R5).
- **S3:** a blocked attempt records nothing: after the block starts at t=0 to 400 (one failure per 100 s), extra attempts at t=500 and t=600 don't extend it; at t=900 the email is not blocked.
- **S4:** after expiry the email can sign up (fake clock past the window).
- **S5:** a case variant is a duplicate: `"Bo@Example.com"`, then `"bo@example.com"`: the second gets the R7 result, `store.count() == 1`.
- **S6:** case variants share one limiter key: failures under `"Cy@Example.com"` and `"cy@example.com"` add up to a block.
- **S7:** a malformed email records nothing (six malformed attempts, then a valid sign-up for a well-formed email succeeds).
- **S8:** no mailer: the account is created and `welcome_sent` is `False`.
- **S9:** a mailer that raises: the result is `ok`, the account exists, and `welcome_sent` is `False`. A mailer that succeeds: `welcome_sent` is `True` (the existing test).
- **S10:** a successful sign-up records no failure (four failures, one success for another email, then one more failure for the first email: blocked; four failures, then a success for the same email: the count is unchanged).
