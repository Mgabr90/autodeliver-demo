LENS: readiness · round 2 · docs/delivery/plans/P01-plan.md
VERDICT: CLEAR

## Blocking
- (none)

## Should-fix
- (none)

## Nits
- **Design, FailedAttemptLimiter state / Test plan L1, L5, S10:** the plan doesn't name the attribute that holds the limiter's map. L1 ("adds no entry"), L5 ("deleted from the map") and the second half of S10 ("the count is unchanged") all have to read it directly. The builder writes both the code and the tests, so this can't fail, but naming it (for example `_failures`) would settle one small choice. S10's second half could instead check behaviour: one more failure for that email gives a block.
- **Design, SignupService:** the plan says `limiter` is an optional argument but not where it goes. Writing the signature, `__init__(self, store=None, mailer=None, limiter=None)`, would keep existing callers that pass `store`/`mailer` by position working without the builder having to think about it.
- **Design step 5 / S9:** "if it raises" could say "raises an `Exception`", which matches the existing `except Exception` at `signup/service.py:36`, so nobody widens it to `BaseException`.
- **Task 4:** the list leaves out "commit the evidence under `docs/delivery/evidence/P01/`" (HANDOFF step 6) and doesn't say whether staging applies. HANDOFF already covers both, so this is only about the plan being complete on its own.

## Notes
- **Round 1 Should-fix 1 (two different block end times):** resolved. Design now says "Block length (sliding window)". R4 no longer gives a conflicting time. L3 pins the rule: blocked at t=899, not blocked at t=900 with a strict `<`. S3 covers the same thing at service level.
- **Round 1 Should-fix 2 (does `is_blocked` add keys; are empty keys removed):** resolved. `is_blocked` never inserts a key, and keys left empty after pruning are deleted. L1 and L5 test this. The Risks section no longer says empty lists are kept.
- **Round 1 Should-fix 3 (untested behaviours):** resolved.
  - A blocked attempt records nothing: S3.
  - A success neither records a failure nor resets the key: S10.
  - Case variants and padded variants share one key: S5, S6 and V1.
  - Non-string input: V3. It is now rejected at validation, because `""` fails `EMAIL_RE`.
  - A blocked call doesn't touch the store: S1 (`store.count() == 0`). `UserStore.count()` exists (`signup/store.py:34`).
- **Round 1 nits:** all addressed. The signature is written out with keyword-only arguments. The boundary rule for exactly `window_seconds` is stated. The `refactor(simplify)` commit and the final gate are in Task 4. The valid password is named (`"orange123x"`).
- **New in revision 2:** checked against the code.
  - R8 (`<=` to `<`) matches `signup/validator.py:25`.
  - R9 matches the defect at `signup/service.py:38`.
  - R6 keeps the existing test `test_valid_signup_creates_account_and_sends_welcome` passing, since its input is already lower case.
  - `signup/validator.py` was added to the boundary by ruling, as HANDOFF line 117 requires.
  - The boundary paths exist, or their folders do (`signup/`, `tests/`).
  - The task order stays buildable: limiter, then validator, then wiring.
- **Files read:** the plan, the round 1 readiness findings, HANDOFF (searched for end-of-phase and boundary rules), and every file under `signup/` and `tests/`. No summary of the planner's reasoning came with the brief.
