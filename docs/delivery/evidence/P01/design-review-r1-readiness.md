LENS: readiness · round 1 · docs/delivery/plans/P01-plan.md
VERDICT: FINDINGS

## Blocking
- (none)

## Should-fix
- Decisions R4 vs Design "is_blocked" — **The plan gives two different end times for a block.** R4 says "the block ends 15 minutes after the 5th recorded failure". The Design rule blocks while 5 or more failures fall inside the last `window_seconds`. Blocked calls record nothing, so under that rule the block ends `window_seconds` after the **1st** of the five failures, not the 5th. Example: failures spread over 10 minutes leave only a 5-minute block under the Design rule, but 15 minutes under R4. — Consequence: the builder has to choose which one to build, and T7 ("after the window passes") passes either way. The gate then can't tell whether the code matches the plan. — Resolve: choose one rule. Either reword R4 to "ends `window_seconds` after the oldest of the last `max_failures` failures", or change `is_blocked` to measure from the newest failure. Then add a test that pins it, for example failures at t=0,100,200,300,400, then check blocked at t=899, and not blocked at t=901 (Design rule) or at t=1301 (R4 rule).
- Design, FailedAttemptLimiter state / Risks "Memory growth" — **It is not decided whether `is_blocked` may create an entry for a key it has never seen.** It is also not decided whether a key whose list is pruned to empty is deleted or kept. The Risks section says a key with no recent failures "holds an empty list", which suggests keys are never removed. — Consequence: an obvious `defaultdict(list)` build that "touches" the key in `is_blocked` would add an entry for every sign-up, including successful ones. Memory then grows with every email ever seen, not just with failing ones, which contradicts the scope R3 accepted. — Resolve: state that `is_blocked` never inserts a key, and that a key whose list prunes to empty is deleted, or explicitly kept. Add a limiter test for the chosen behaviour.
- Test plan — **Several behaviours the plan decides have no test:**
  - R4: a blocked attempt does not add a failure.
  - Design step 4: a successful sign-up neither records a failure nor resets the key.
  - R6: `" ana@example.com "` and `"ana@example.com"` share one key, and every non-string email maps to the shared key `""`.
  - R5: a blocked call does no hashing. The plan has no way to observe this. A stub store or a counting store passed as `store=` would do it.

  — Consequence: each of these can regress, or be built wrong, while T1–T8 stay green. — Resolve: add named cases, T9 onward, for each.

## Nits
- Design — **The constructor signature is spread across sections.** The full signature, `FailedAttemptLimiter(max_failures=5, window_seconds=900, clock=time.monotonic)`, is never written out in one place, and it doesn't say whether the arguments are keyword-only. Writing it out once would remove guesswork when tests build a fake-clock limiter for T3 and T7.
- Design "inside the last `window_seconds`" — **Whether a failure exactly `window_seconds` old still counts is not stated** (`>` or `>=`). T3 avoids the edge by going "past" the window. Stating it is cheap.
- Task 3 — **Some HANDOFF end-of-phase steps are missing.** The task lists the simplify pass, SYSTEM.md, full proof, ledger and roadmap. It does not list the separate `refactor(simplify)` commit or the final whole-phase review that HANDOFF step 4 requires. Adding both would make the task self-contained.
- T5 — **The "valid password" for the sixth attempt should be named.** `signup/validator.py:25` uses `<=`, so an exactly 8-character password is currently rejected. A builder who picks an 8-character "valid" password would get a confusing failure. Using `"orange123x"`, like the existing tests, avoids this.

## Notes
- I read the plan, `.autodeliver/config.json`, HANDOFF, ROADMAP, SYSTEM, the P01 ledger, and every file under `signup/` and `tests/`.
- **File boundary:** the paths to change exist (`signup/service.py`, `tests/test_signup.py`). The new files sit in existing folders. `signup/__init__.py` is empty, so no export change is needed. SYSTEM.md, the ledger and the roadmap are exempt delivery files.
- **Key matching:** the R6 key (`email.strip()`) matches the store key produced by `validate_email` (`signup/validator.py:20`), so limiter keys and store keys line up.
- **Tests:** `UserStore.count()` exists for T5's "no user stored" check.
- **Out of scope for this lens:** I saw possible defects outside this lens: the password length off-by-one, `welcome_sent=True` being set even when the mailer is absent or fails (`signup/service.py:38`), and case-sensitive duplicate detection. These are scope and fail-safe questions for the critic and zoom-out lenses, so I did not raise them here.
- No summary of the planner's reasoning was included with the brief.
