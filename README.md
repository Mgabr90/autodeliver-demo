# autodeliver demo: one phase, start to PASS

This repo is a small, real run of [autodeliver](https://github.com/Mgabr90/autonomous-delivery) 0.6.0 on a toy sign-up service (Python, pytest only). One phase, P01, goes through the whole loop: the plan is written as a design doc, four fresh "goldfish" reviewers check it before any code is written, the work is built test-first, and an independent gate reviews it, fails it until the findings are fixed, then passes it.

The starting code contains **planted defects**, so the reviewers have something real to catch. The list was committed only at the very end (`docs/delivery/evidence/P01/planted-defects.md`), after every review had run. Every design review and every gate verdict in `docs/delivery/evidence/P01/` is the verbatim reply of a separate, fresh Claude Code process (`claude -p`) that saw only the files, never the builder's reasoning. Nothing in them was hand-written or edited.

## How to read it

1. `git log --oneline`: the phase from the starting point to PASS, one commit per step.
2. `docs/delivery/plans/P01-plan.md`: the plan as a design doc (design, decisions, file boundary, test plan).
3. `docs/delivery/evidence/P01/design-review-*.md`: the four lenses (zoom-out, comprehension, critic, readiness), per round.
4. `docs/delivery/ledgers/P01.md`: what the builder did with each finding, and every ruling with its cost if wrong.
5. `docs/delivery/evidence/P01/review-r*.md`: the gate's verdicts, round by round.
6. `docs/delivery/evidence/P01/RESULTS.md`: which planted defects were caught, where, and what it cost.

Run the tests: `python -m pytest -q`.
