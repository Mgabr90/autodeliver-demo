LENS: comprehension · round 1 · docs/delivery/plans/P01-plan.md
VERDICT: FINDINGS

## Paraphrase
What this proposes: The plan adds a new in-memory `FailedAttemptLimiter` in `signup/ratelimit.py`. It records the times of failed sign-up attempts for each email key, and blocks a key once it has 5 failures inside a 15-minute sliding window. The clock can be injected so tests control time. `SignupService.signup` checks the limiter before doing anything else. If the key is blocked, it returns "Too many attempts. Try again later." on the `email` field. Otherwise it runs the normal flow and records a failure on a validation error or a duplicate-email refusal. Tests T1–T8 cover the limiter, the service wiring and the existing neutral duplicate-email refusal.

How the existing system works, per this plan: `SignupService.signup(email, password)` validates the input with `signup/validator.py`. It then adds the user to an in-memory `UserStore`, one per service instance, which refuses an existing email by raising `DuplicateEmail`. Finally it calls an optional mailer and returns `SignupResult(ok, error_field, message)`. Nothing limits attempts today, and a duplicate gets the neutral message "Could not create the account."

## Blocking
- (none)

## Should-fix
- **Decisions R4 vs Design (`is_blocked`), and Risks "the block is temporary (15 minutes)"**
  - Problem: the plan describes the length of a block in two ways that don't agree.
    - The Design defines a sliding window: a key is blocked while it has 5 or more failures in the last `window_seconds`.
    - R4 says "the block ends 15 minutes after the 5th recorded failure".
    - Under the sliding window, with failures at t0…t4, the failure at t0 drops out at t0+900. The count falls to 4 and the block ends 15 minutes after the *1st* failure in the window, not the 5th.
  - Consequence: a reader can't tell which behaviour is intended, and T7 ("after the window passes") doesn't say which window is meant. The builder has to choose, and the gate may then flag the result as a departure from R4.
  - What would resolve it:
    - Either restate R4 and the Risks section to match the sliding window ("unblocked once fewer than 5 failures remain in the last 15 minutes"),
    - or change the design to a lockout timed from the 5th failure.
    - Then make T7 name the exact time the fake clock is advanced to.

- **Goal and why ("the duplicate-email refusal also needs to stay clear and reliable") vs Design, File boundary and T8**
  - Problem: the roadmap row says "*make* the duplicate-email refusal clear and reliable". The plan's only work on this is test T8, and it never says whether the current behaviour already meets T8.
  - Consequence: if T8 fails against today's code, the builder has no design for the fix and no allowed file to change it in. `signup/store.py` is outside the boundary, and the Design doesn't mention any change to how `service.py` handles `DuplicateEmail`.
  - What would resolve it: state plainly that today's refusal already behaves as T8 describes and this phase only pins it with a test, or describe the change needed and add the affected file to the boundary.

## Nits
- **File boundary:** "as the charter says" doesn't name the file. Write `docs/delivery/HANDOFF.md`.
- **Design step 1:** the plan doesn't say whether the key is lowercased, or how it compares with the key `UserStore` uses after the validator trims the email. R6 settles the key, but one sentence on whether "A@x.com" and "a@x.com" share a limit would spare the reader from guessing.
- **Tasks 2/T7:** the tests have to inject the fake clock through `SignupService(limiter=FailedAttemptLimiter(clock=…))`. That can be inferred, but saying it would make T5–T8 easier to write.

## Notes
- I read only the plan and what it links (`HANDOFF.md`, `ROADMAP.md`, `SYSTEM.md`). As this lens requires, I did not search the code.
- There is no research brief (the plan says none is needed). No reasoning summary came with the brief.
- The ledger `docs/delivery/ledgers/P01.md` is named but not linked. I did not check that it exists.
