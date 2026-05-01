# team-board

## Shared objective
Expand Relay-kit workflow eval coverage and keep live state current for the active single-lane implementation slice.

## Active orchestrator
- workflow-router

## Lanes
| Lane | Owner skill | Current hub | Current artifact | Lock scope | Status | Handoff status | Notes |
|---|---|---|---|---|---|---|---|
| primary | developer | test-hub | workflow_scenarios/test_workflow_eval/upgrade-note/state | eval fixture and note files | ready for PR | verified locally | Default workflow eval coverage expanded from 20 to 28 scenarios; root pytest and enterprise gates pass. |
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
Runtime doctor live mode, enterprise doctor, root pytest, readiness, workflow eval, and remote CI must pass before merge.

## Conflict risks
Low. This slice edits state/context artifacts only.

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
