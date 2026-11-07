# P01 plan: sign-up hardening

Roadmap row: P01. Ledger: `docs/delivery/ledgers/P01.md`. Research brief: none (no external facts; standard library only, ruling R1).

## Goal and why

Anyone can call `SignupService.signup` as often as they like. Repeated failed attempts for one email (guessing, scripted abuse, a broken client in a retry loop) cost hashing work and fill logs, and nothing slows them down. The duplicate-email refusal also needs to stay clear and reliable as the service grows.

Done when: repeated failed sign-ups for one email are refused for a cool-down period with a clear message; the duplicate-email refusal is covered by tests; the test plan below passes under the full proof (`python -m pytest -q`); and the gate PASSes.

## Context

From `docs/delivery/SYSTEM.md`: `SignupService.signup` validates input (`signup/validator.py`), adds the user to the in-memory `UserStore` (`signup/store.py`), which refuses an existing key with `DuplicateEmail`, then calls the optional mailer. Results are `SignupResult(ok, error_field, message)`. There is no limit on attempts today. The store is in memory, per service instance.

## Design

- A new component, **FailedAttemptLimiter** (`signup/ratelimit.py`), keeps, per key, the times of recent failed sign-up attempts in memory.
  - `record_failure(key)` adds the current time.
  - `is_blocked(key)` is true when the key has `max_failures` or more failures inside the last `window_seconds`. Entries older than the window are dropped when the key is touched.
  - The clock is injected (`clock`, default `time.monotonic`) so tests control time.
- **SignupService** takes an optional `limiter` (a default `FailedAttemptLimiter()` when none is given). In `signup`:
  1. Compute the key: the email argument as given, with surrounding spaces removed (non-strings use `""`).
  2. If `limiter.is_blocked(key)`: return `SignupResult(False, "email", "Too many attempts. Try again later.")` without validating, hashing or storing.
  3. Otherwise run today's flow. On a validation failure or a duplicate-email refusal, call `limiter.record_failure(key)` before returning the failure result.
  4. A successful sign-up does not record anything and does not reset the key.
- Data flow stays one-way: service → limiter, service → validator → store → mailer. The limiter knows nothing about users.

## Alternatives considered

- **Limit per client IP:** rejected. The service has no request context, and the abuse this phase targets is per email.
- **Exponential back-off instead of a fixed window:** rejected for now (YAGNI). A fixed window is simpler to reason about and test.
- **Persisting attempts in `UserStore`:** rejected. Failed attempts are not users, and mixing them would couple two concerns.
- **A third-party rate-limit library:** rejected. The hard limits allow the standard library only (ruling R1).

## Risks and fail-safe

- **Memory growth:** one entry per distinct key with recent failures. Old timestamps are pruned on touch; a key with no failures in the window holds an empty list. Acceptable for an in-memory demo service (ruling R3).
- **Locking out a real user:** someone else can burn the limit for a victim's email. Accepted for this phase: the block is temporary (15 minutes), and the message tells the user to retry later (ruling R4).
- **Clock:** `time.monotonic` cannot go backwards, so wall-clock changes can't extend or skip a block.
- **No new outside services.** The mailer path is unchanged by this phase.

## Decisions

- **R1:** standard library only; no new dependencies. Cost if wrong: none (the hard limits require it).
- **R2:** defaults `max_failures=5`, `window_seconds=900` (15 minutes), both constructor arguments. Cost if wrong: low; values are easy to change.
- **R3:** in-memory state only, per service instance, like `UserStore`. Cost if wrong: low for the demo; a shared store is a later phase if ever needed.
- **R4:** what counts as a failure: validation errors and duplicate-email refusals. A blocked attempt does not itself add a failure (the block ends 15 minutes after the 5th recorded failure). Cost if wrong: medium; legitimate users could be blocked longer or shorter than intended.
- **R5:** the blocked message is "Too many attempts. Try again later." with `error_field="email"`, and the result is returned before validation, so a blocked call costs no hashing. Cost if wrong: low.
- **R6:** the key is the email argument as given, with surrounding spaces removed. Cost if wrong: medium.

## File boundary

- `signup/ratelimit.py` (new)
- `signup/service.py` (change)
- `tests/test_ratelimit.py` (new)
- `tests/test_signup.py` (change)

Delivery files under `docs/delivery/` are exempt, as the charter says.

## Tasks

1. **Limiter.** Write `tests/test_ratelimit.py` first (cases T1 to T4), then `signup/ratelimit.py`. Done when: T1 to T4 pass.
2. **Service wiring.** Add cases T5 to T8 to `tests/test_signup.py` first, then change `signup/service.py` as in "Design". Done when: T5 to T8 and the existing tests pass.
3. **End of phase.** One simplify pass over the phase's files; update `docs/delivery/SYSTEM.md` (new component, the limiter in the service flow, the R5 message); full proof; ledger and roadmap update. Done when: `python -m pytest -q` is green and the ledger records it.

## Test plan

- **T1:** a new key is not blocked.
- **T2:** after 4 failures in the window the key is not blocked; after the 5th it is.
- **T3:** failures older than `window_seconds` don't count (advance the fake clock past the window: not blocked).
- **T4:** keys are independent (5 failures for one key don't block another).
- **T5:** five sign-ups with an invalid password for one email, then a sixth with a valid password: the sixth is refused with "Too many attempts. Try again later." and `error_field == "email"`, and no user is stored.
- **T6:** a duplicate-email attempt counts as a failure (one success, then five duplicates, then the next attempt is blocked).
- **T7:** after the window passes (fake clock), the same email can sign up successfully.
- **T8:** the duplicate-email refusal returns `ok=False`, `error_field="email"` and the neutral message "Could not create the account.", and the store still holds one user.
