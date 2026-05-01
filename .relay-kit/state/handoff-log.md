# handoff-log

## Handoff entries
| From | To | Lane | Trigger | Artifact touched | Evidence linked | Expected return condition |
|---|---|---|---|---|---|---|
| workflow-router | bootstrap | primary | state/context drift after release and next-dev bump | project-context, workflow-state, team-board, lane-registry, handoff-log | GitHub PR #1/#2/#3, release `v3.3.0`, latest main CI `24956568795` | refreshed artifacts pass live runtime doctor, enterprise doctor, pytest, and CI |
| bootstrap | workflow-router | primary | bootstrap slice complete | project-context, workflow-state, team-board, lane-registry, handoff-log | runtime doctor live pass, enterprise doctor pass, pytest 125 pass; PR CI pending | next implementation slice selected |
| workflow-router | bootstrap | primary | state/context drift after PR #17 support request Pulse/signal merge | project-context, workflow-state, team-board, lane-registry, handoff-log | PR #17, main CI `25173791427`, readiness `commercial-ready-candidate`, pytest 146 pass | refreshed artifacts pass live runtime doctor, enterprise doctor, pytest, readiness, and CI |
| workflow-router | bootstrap | primary | state/context drift after PR #19 support bundle request-summary merge | project-context, workflow-state, team-board, lane-registry, handoff-log | PR #19, main CI `25174419399`, readiness `commercial-ready-candidate`, pytest 147 pass | refreshed artifacts pass live runtime doctor, enterprise doctor, pytest, readiness, and CI |
| workflow-router | bootstrap | primary | state/context drift after PR #21 workflow eval coverage merge | project-context, workflow-state, team-board, lane-registry, handoff-log | PR #21, main CI `25208682877`, readiness `commercial-ready-candidate`, pytest 147 pass | refreshed artifacts pass live runtime doctor, enterprise doctor, pytest, readiness, and CI |
| workflow-router | bootstrap | primary | state/context drift after PR #23 publication trail status merge | project-context, workflow-state, team-board, lane-registry, handoff-log | PR #23, main CI `25210492548`, readiness `commercial-ready-candidate`, pytest 150 pass | refreshed artifacts pass live runtime doctor, enterprise doctor, pytest, readiness, and CI |

## Rules
- Every non-trivial handoff should update this log before the receiving skill starts work.
- Link to the authoritative artifact, not only a chat summary.
- If a handoff changes scope or ownership, update `workflow-state.md` and `lane-registry.md` in the same pass.
