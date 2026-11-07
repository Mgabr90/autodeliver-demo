LENS: critic · round 2 · docs/delivery/plans/P01-plan.md
VERDICT: CLEAR

## Blocking
- (none)

## Should-fix
- (none)

## Nits
- Risks: "Memory" / R3: An attacker can still add one entry for each distinct well-formed email by sending a bad password, at no cost to them. Each entry lasts up to `window_seconds`, so memory is limited by request rate × 900 s, not by the number of keys ever seen. That is acceptable at demo scale. Saying "bounded by attempt rate over the window" would be more exact than "stale keys don't pile up".
- R6: `str.lower()` and `str.casefold()` give different results for some non-ASCII addresses, such as `ß`. This is irrelevant for the ASCII test cases. One sentence saying that `lower()` was chosen on purpose would head off a later question.

## Notes
- Round 1 findings all resolved:
  1. Case and whitespace normalization now goes through `normalize_email`, and the store and the limiter use the same key (R6). S5 and S6 test it, and `signup/validator.py` is in the boundary.
  2. The 8-character password defect is fixed by R8 and tested by V2. The lockout risk was rewritten to match.
  3. The mailer fail-safe is fixed by R9. S8 and S9 test it, and they match `signup/service.py:33-38`, which currently sets `welcome_sent = True` in every case.
  4. Malformed emails record nothing (R4, S7). Empty keys are deleted, and the whole map is pruned on each `record_failure` (L5).
- Round 1 nits resolved: the hashing and logging rationale is gone, the default limiter is built inside `__init__`, and the concurrency assumption is stated.
- Checked against the code: `signup/service.py`, `signup/validator.py` and `signup/store.py`. `store.count()` and `store.get()` exist, and the store starts users with `welcome_sent: False`, so the S8 and S9 expectations work. I also checked `tests/test_signup.py`: the existing mailer test still expects `True` when the mailer succeeds, which stays consistent with R9.
- Hard limits still hold by design: standard library only, in-memory, no secrets or outside services.
- No reasoning summary came with the brief.
