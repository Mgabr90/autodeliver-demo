LENS: zoom-out · round 2 · docs/delivery/plans/P01-plan.md
VERDICT: CLEAR

## Blocking
- (none)

## Should-fix
- (none)

## Nits
- **Design section, altitude (repeated from round 1, not resolved):** the numbered control flow inside `SignupService.signup` (steps 1 to 6) is task-level detail. It's still in the Design section. That's acceptable, and the build doesn't wait on it.
- **Design, "One canonical email":** `normalize_email` returns `""` for a non-string, but the only caller is `validate_email`, and the service takes its key from `validate_email`'s return value (Design step 2). So the `""` branch only feeds the shape check, which then fails. Making `normalize_email` a private detail of `validate_email` would be slightly simpler. V3 tests the branch anyway, so this is a preference, not a gap.

## Notes
- **Round 1 Should-fix 1 (case-sensitive key): resolved.** R6 and the "One canonical email" design bullet make `validate_email` return `strip().lower()`. The store and the limiter both use that value, and V1, S5 and S6 test it. `signup/validator.py` is now in the file boundary.
- **Round 1 Should-fix 2 (duplicated key logic): resolved.** The plan has one helper in `signup/validator.py`. The service's limiter key is the canonical email that `validate_email` returns (Design step 2), so there is no second key rule.
- **Round 1 Should-fix 3 (wrong justification): resolved.** "Goal and why" now gives the real problems: unlimited attempts per email (probing, scripted guessing, retry loops) and duplicate accounts from case variants. The hashing and log claims are gone, both from the goal and from R5.
- **Round 1 Nit (empty lists in the map): resolved.** `record_failure` now deletes keys whose list is empty after pruning, and L5 tests this.
- **Scope:** the two out-of-lens items I raised in round 1 (the `<=` password check, and `welcome_sent` set to true without a sent email) are now in scope as R8 and R9. Each has a test (V2, S8 and S9) and the needed boundary entries. Both fixes are minimal and stay in the right place.
- **Checked against the code:** I re-read `signup/validator.py` and `signup/service.py`. They still match round 1's description, so the plan's "Context" section is accurate. I searched the repo for `validate_email`, `normalize` and `lower(`: there's no existing normalization helper to reuse. No summary of the plan's reasoning was sent, so there was nothing to ignore.
