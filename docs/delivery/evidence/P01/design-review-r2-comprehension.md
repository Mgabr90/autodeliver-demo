LENS: comprehension · round 2 · docs/delivery/plans/P01-plan.md
VERDICT: CLEAR

## Paraphrase
What this proposes: Emails get one canonical form: the address trimmed of spaces and lowercased. A new `normalize_email` helper in the validator produces it, and `validate_email` returns it, so both the store and a new limiter treat case variants as the same email. A new in-memory `FailedAttemptLimiter` in `signup/ratelimit.py` keeps failure timestamps for each canonical email. It blocks the email while 5 or more failures fall inside a sliding 15-minute window, and its clock can be injected for tests. `SignupService.signup` changes order: it validates the email shape first and records nothing if that fails. Next it checks the limiter and, if the email is blocked, returns "Too many attempts. Try again later." Then it checks the password and adds the user, recording a failure when the password is invalid or the email is a duplicate. The phase also fixes two defects. A password of exactly 8 characters is now accepted. `welcome_sent` is set only after the mailer returns without raising, and a mailer error logs a warning but still returns success.

How the existing system works, per this plan: `SignupService.signup` validates the input with `signup/validator.py`. It then adds the user to an in-memory `UserStore` (one per service instance), which is keyed by the exact email string and raises `DuplicateEmail` for an existing key. Finally it calls an optional mailer and returns `SignupResult(ok, error_field, message)`. Nothing limits attempts today. Emails are compared exactly as typed, so `Bo@Example.com` and `bo@example.com` become two accounts. An 8-character password is wrongly rejected, and `welcome_sent` is set even when no email went out. The code is single-threaded.

## Blocking
- (none)

## Should-fix
- (none)

Resolution of round-1 findings:
- **Block length mismatch:** resolved. Design states the sliding-window rule and when a block ends: `window_seconds` after the oldest of the last `max_failures` failures. Risks says "at most 15 minutes", and L3 and S3 give the exact fake-clock times (899 and 900).
- **Duplicate refusal "clear and reliable":** resolved. Goal and why names the actual defect (case variants become separate accounts). The fix is in the validator, which is inside the boundary, and the plan says `UserStore` is unchanged. R7 keeps the wording, and S5 pins the behaviour.
- **Round-1 nits:** all addressed. The plan now names `HANDOFF.md`, defines the case-folded key (R6, S6) and shows how tests inject the fake clock (Task 3).

## Nits
- **Test plan S10, second half:** "four failures, then a success for the same email: the count is unchanged". The plan doesn't say what "the count" is or how a test reads it, because the limiter exposes only `record_failure` and `is_blocked`. Fix: say "then one more failure for that email: blocked, and one fewer: not blocked", or name the internal map the test may inspect.
- **Test plan S4:** "fake clock past the window" doesn't give the time, unlike L3 and S3. Fix: give the failure times and the time the clock moves to (for example, t=900 after failures at 0 to 400).
- **Test plan S3:** "after the block starts at t=0 to 400 (one failure per 100 s)" reads awkwardly. Fix: "failures at t=0, 100, 200, 300, 400 block the email".
- **Design step 5:** the plan doesn't say which logger "log a warning" means. It's probably the standard `logging` module, given R1. Fix: name the logger.
- **Design step 1:** "return the validation result" relies on the existing mapping from `ValidationError(field, message)` to `SignupResult`, which the plan never states. It can be inferred from `SYSTEM.md`, but one clause would help.

## Notes
- I read only the plan and what it links (`HANDOFF.md`, `ROADMAP.md`, `SYSTEM.md`) plus my round-1 findings. As this lens requires, I did not search the code.
- There is no research brief (the plan says none is needed, citing R1). No reasoning summary came with the brief.
- I didn't open the ledger `docs/delivery/ledgers/P01.md`, which the plan cites for the round-1 resolutions. Every ruling the plan relies on (R1–R9) is restated in the plan itself.
