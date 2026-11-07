# P01 results

One phase, run with autodeliver 0.6.0 in local mode on 2026-11-07. Every reviewer was a separate, fresh `claude -p` process (Claude Opus 5.5). It was given only the reviewer instructions (`.claude/agents/design-reviewer.md` or `.claude/agents/delivery-reviewer.md`) and a short brief with file paths, never the builder's reasoning. Its reply is saved verbatim in this folder. The design reviewers could read files only; the gate could also run commands, to run the proof.

## The planted defects (see `planted-defects.md`)

| Defect | Caught? | Where | By |
|---|---|---|---|
| D1 case-sensitive duplicate email | **Yes** | Design review, round 1, before any code was written | critic (Should-fix), zoom-out (Should-fix); comprehension raised it as a question (Nit); readiness noted it as outside its lens |
| D2 8-character password rejected | **Yes** | Design review, round 1 | critic (Should-fix); zoom-out and readiness noted it as outside their lens |
| D3 `welcome_sent` true without a sent email | **Yes** | Design review, round 1 | critic (Should-fix); zoom-out and readiness noted it as outside their lens |

**All 3 were caught by the design review, before building.** The builder then fixed them by ruling (R6, R8, R9), test-first. **The gate caught none of them, because by the time it ran there was nothing left to catch.** It passed in round 1 and confirmed the fixes against the plan.

## The loop, round by round

| Step | Result |
|---|---|
| Design review round 1 (4 lenses in parallel) | 0 Blocking, 12 Should-fix, 12 Nits. Besides the 3 planted defects, the reviewers found real design problems in the plan: two contradictory definitions of how long a block lasts, unbounded memory from junk keys, decisions with no test, a key rule that duplicated the validator, and a goal justified by costs the code doesn't have. |
| Plan revision 2 | Every Should-fix resolved by a plan change or a ruling; file boundary extended by ruling for D2 and D3 |
| Design review round 2 (all 4 lenses re-run) | **All CLEAR**: 0 Blocking, 0 Should-fix, 13 Nits (7 taken; the other 6 left, with reasons in the ledger) |
| Build | 3 tasks, test-first; 4 tests became 24 |
| Simplify pass | 1 commit (one prune helper instead of two copies) |
| Gate round 1 (full proof run by the reviewer, twice) | **PASS**: 0 Blocking, 0 Should-fix, 2 Nits (carried to the next phase), plan 4 of 4 done |

Rounds to PASS at the gate: **1**. Fix rounds: **0**. That means this run never exercised the gate's FAIL → fix → re-review path. The design review moved every finding before the build.

## Cost (reviewer processes only)

As reported by each `claude -p` run (`total_cost_usd`, Claude Opus 5.5):

| Reviewer | Runs | Output tokens | Cost (USD) |
|---|---|---|---|
| Design review round 1 | 4 | 16,729 | 1.03 |
| Design review round 2 | 4 | 9,249 | 0.78 |
| Gate round 1 | 1 | 3,310 | 0.41 |
| **Total** | **9** | **29,288** | **2.22** |

The builder's own tokens (the session that wrote the plan, the code and the ledger) were **not recorded**: the token-log hook wasn't installed in that session.

## Caveats

- **This is one small phase, not a benchmark.** It shows the loop working; it doesn't measure how often the design review catches defects in general.
- **The defects were planted by the builder, who knew them.** The builder left them out of plan revision 1 and changed the plan only after reviewers raised them. The fixes themselves were written by that same builder.
- **The reviewers read the starting code**, which is how they found defects the plan didn't mention. The critic and zoom-out lenses search the code by design.
