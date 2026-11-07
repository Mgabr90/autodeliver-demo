VERDICT: PASS
(round 1, full)

## Blocking
- none

## Should-fix
- none

## Nits
- `docs/delivery/SYSTEM.md` (Components table, "Tests" row): the row lists only `tests/test_signup.py`. The new `tests/test_ratelimit.py` is missing. Add it so the system doc matches the repo.
- `tests/test_signup.py:36,56`: imports sit in the middle of the module (`normalize_email`, `FailedAttemptLimiter`), and `FakeClock` is defined again here as well as in `tests/test_ratelimit.py`. Move the imports to the top and share the clock through a small `conftest.py` fixture. This is style only.

## Plan completeness
4 of 4 done. Missing: nothing.
- Task 1: L1 to L7 are present and passing.
- Task 2: V1 to V3 are present, and R6 and R8 are implemented in `signup/validator.py`.
- Task 3: S1 to S10 are present, and `signup/service.py` follows Design steps 1 to 6:
  - a malformed email returns before the limiter;
  - a blocked email returns before the password check and the store, with the R5 result;
  - a bad password or a duplicate records a failure;
  - `welcome_sent` is set only in the mailer's `else` branch;
  - no mailer means `welcome_sent` stays false;
  - a successful sign-up records nothing. S2 would catch a success that recorded a failure.
- Task 4:
  - The `refactor(simplify)` commit is `ddb38e4`.
  - `SYSTEM.md` is updated (canonical email, the limiter in the flow, R5, R9).
  - The ledger and roadmap are updated (P01 "in review").

The design review is recorded in `docs/delivery/ledgers/P01.md`: 2 rounds, 4 lenses, round 2 CLEAR on all lenses, rulings R1 to R9. All 8 design-review files are committed under `docs/delivery/evidence/P01/`. No visual or rendered claims needed further evidence.

Other checks:
- **File boundary:** every changed file is in the plan's boundary (`signup/ratelimit.py`, `signup/service.py`, `signup/validator.py`, `tests/test_ratelimit.py`, `tests/test_signup.py`) or is an exempt file under `docs/delivery/`.
- **Design conformance:** the code matches the plan. The constructor is keyword-only with defaults 5 and 900, the default limiter is built in `__init__`, and a failure counts while `now - t < window_seconds`. `is_blocked` never inserts a key, and `record_failure` prunes the whole map.
- **Dependencies:** standard library only.
- **Secrets and locales:** no secrets and no `TODO`. The mail warning log contains no personal data. All new user-facing text is in English, the only configured locale.
- **Fact-check:** not applicable (software profile, no external facts asserted).

## What I ran
- `python -m pytest -q`: 24 passed in 0.69s; re-run: 24 passed (flaky: none)
- Read `git diff a79314c..b88b9f2` (17 files), the plan, the ledger, the config and the current sources. The working tree is clean.
