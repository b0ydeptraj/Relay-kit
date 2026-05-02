# team-board

## Shared objective
Harden Relay-kit paid-support operations with a support soak command and stricter support bundle diagnostics.

## Active orchestrator
- workflow-router

## Lanes
| Lane | Owner skill | Current hub | Current artifact | Lock scope | Status | Handoff status | Notes |
|---|---|---|---|---|---|---|---|
| primary | developer | fix-hub | support_triage/support_bundle/support-sla/tests/state | support operations soak | ready for PR | verified | `support soak`, `support triage`, readiness full, doctor, runtime doctor live, and full pytest 160 pass locally. |
| lane-2 | unassigned | none | none | none | parked | none | No parallel work active. |
| lane-3 | unassigned | none | none | none | parked | none | No parallel work active. |

## Shared artifacts that must stay authoritative
- `.relay-kit/contracts/project-context.md`
- `.relay-kit/state/workflow-state.md`
- `.relay-kit/state/lane-registry.md`
- `.relay-kit/state/handoff-log.md`
- `.relay-kit/state/team-board.md`

## Merge order
Primary lane only. Parallel lanes are parked until explicitly routed.

## Merge prerequisites
Support triage and soak strict pass, root pytest passes, enterprise readiness passes, and remote CI must pass after merge.

## Conflict risks
Low to medium. This slice changes the public support CLI and support triage behavior; support and readiness tests cover the change.

## Decision log
- 2026-04-27: Refresh state artifacts instead of starting a new feature slice because project-context was empty and workflow-state still referenced completed branch work.
- 2026-04-30: Refresh state artifacts after PR #17 merged and main CI `25173791427` passed.
- 2026-04-30: Refresh state artifacts after PR #19 merged and main CI `25174419399` passed.
- 2026-05-01: Refresh state artifacts after PR #21 merged and main CI `25208682877` passed.
- 2026-05-01: Refresh state artifacts after PR #23 merged and main CI `25210492548` passed.
- 2026-05-01: Refresh state artifacts after PR #25 merged and main CI `25210793716` passed.
- 2026-05-01: Refresh state artifacts after PR #27 merged and main CI `25211668550` passed.
- 2026-05-01: Refresh state artifacts after PR #29 merged and main CI `25215207136` passed.
- 2026-05-01: Refresh state artifacts after PR #31 merged and main CI `25216356829` passed.
- 2026-05-01: Start workflow eval scenario expansion from 20 to 28 bundled scenarios on `codex/eval-scenario-expansion-v2`.
- 2026-05-01: Verify eval scenario expansion locally with root pytest, eval, doctor, runtime doctor, readiness, Pulse, and signal export.
- 2026-05-01: Refresh state artifacts after PR #33 merged and main CI `25224916323` passed.
- 2026-05-02: Start support operations soak on `codex/support-operations-soak`; local evidence includes support triage/soak strict, readiness enterprise full, doctor enterprise, runtime doctor live, and full pytest `160 passed`.
