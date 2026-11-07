# autodeliver demo: roadmap

Phases run top to bottom. A session takes the first row that isn't done and whose dependencies are done. A **GATE** row waits for the owner; prepare it fully, then stop.

| Phase | Scope | Depends on | Done when | Status |
|---|---|---|---|---|
| P01 | Sign-up hardening: limit repeated failed sign-up attempts per email, and make the duplicate-email refusal clear and reliable | — | the plan's test plan passes under the full proof, and the gate PASSes | in review |
| GATE | Publishing the service publicly needs the owner's approval in chat (owner approval) | P01 | the evidence is linked in DECISIONS_LOG "Hard-limit gates" | waiting |

## Follow-ups

Findings routed here from reviews and security sweeps, each with the phase that will take it:

-
