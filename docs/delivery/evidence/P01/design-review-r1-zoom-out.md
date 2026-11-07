LENS: zoom-out · round 1 · docs/delivery/plans/P01-plan.md
VERDICT: FINDINGS

## Blocking
- (none)

## Should-fix
- **Design step 1 and R6 (limiter key); "Goal and why" (duplicate refusal must be "clear and reliable").** The plan never fixes the main reason the duplicate-email refusal is unreliable. `validate_email` (`signup/validator.py:17-20`) only trims spaces. `UserStore` (`signup/store.py:19,23`) uses that trimmed string as its key, and so does the planned limiter. **Consequence:** `Bo@Example.com` and `bo@example.com` become two accounts, which breaks the HANDOFF goal of "one account per email". The limiter can also be bypassed by changing letter case: each case variant gets its own 5 failures. T8 only proves the refusal works when the input matches exactly, so the phase would pass while the root problem stays. **To resolve:** decide email normalization once, in the validator, so that `validate_email` returns a canonical form (at least a lowercase domain; a ruling on whether to casefold the whole address, with its cost if wrong). The store key and the limiter key should both use that form. Add a test where a duplicate differs only by case.
- **Design step 1: duplicated key logic (reuse).** The plan builds the key with its own rule ("surrounding spaces removed, non-strings use `""`"). This copies the normalization that `validate_email` already does (`isinstance(email, str)` and `.strip()`). **Consequence:** there would be two places that say what an email key is, and they will drift apart, e.g. when the case normalization above is added to the validator but not to the service. **To resolve:** put the normalization in one small helper in `signup/validator.py`, used by both `validate_email` and the service's limiter key, and add `signup/validator.py` to the file boundary. Alternatively, write a ruling explaining why a separate key rule is intended.
- **"Goal and why" (the stated reason for the limiter doesn't match the code).** The plan says repeated failed attempts "cost hashing work and fill logs". In the code, neither happens:
  - Validation failures return before the store is reached (`signup/service.py:24-28`).
  - `UserStore.add` raises `DuplicateEmail` before PBKDF2 runs (`signup/store.py:19-22`).
  - Failed sign-ups write no log; the only log call is the mailer warning (`signup/service.py:37`).

  R5's "a blocked call costs no hashing" rests on the same wrong premise. **Consequence:** the design is justified by costs that don't exist. The real benefit, slowing per-email probing and scripted retries, isn't stated, so reviewers can't judge whether a fixed window per email is the right tool. **To resolve:** restate the problem using the behaviour the code actually has (abuse and probing per email), and drop or correct the hashing and log claims in the Goal and in R5.

## Nits
- **Design (altitude):** the exact message strings and the numbered control flow inside `signup` are task-level detail. They already appear in R5 and the Tasks section, so the Design section could stay at the level of the component and its interface.
- **Risks, "Memory growth":** "a key with no failures in the window holds an empty list". This is simpler if the limiter deletes the key once its list is empty after pruning, so the leftover empty list doesn't need to be accepted as a risk.

## Notes
- **What I read:** the plan, HANDOFF.md, ROADMAP.md, SYSTEM.md, `.autodeliver/config.json`, `signup/service.py`, `signup/store.py`, `signup/validator.py` and `tests/test_signup.py`.
- **Reuse search:** I found no existing rate-limit, attempt-counter or clock helper in the repo, so adding `signup/ratelimit.py` as a new component is justified. Using only the standard library fits hard limit 4.
- **Rejected alternatives:** I agree with all of them (per-IP, exponential back-off, persisting attempts in `UserStore`, a third-party library). They are the simpler and correctly placed choices.
- **Outside this lens and the P01 roadmap scope, but against the HANDOFF goal.** These are for the drift check or roadmap follow-ups:
  - `validate_password` uses `<=` (`signup/validator.py:25`), so an 8-character password is rejected. SYSTEM.md says the minimum is 8.
  - `welcome_sent` is set to `True` even when the mailer is absent or raised an error (`signup/service.py:33-38`). This treats an unsent notice as sent, which goes against "no silent failures" and the fail-safe rule.
- **Ignored or unchecked:** no summary of the plan's reasoning was sent, so there was nothing to ignore. There is no research brief, which matches the plan's statement.
