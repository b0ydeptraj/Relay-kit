# team-board

## Shared objective
Ship a working, proof-backed sales demo for `python-kit` that demonstrates the active baseline and validates the workflow OS story with real artifacts.

## Active orchestrator
- team

## Lanes
| Lane | Owner skill | Current hub | Current artifact | Lock scope | Status | Handoff status | Notes |
|---|---|---|---|---|---|---|---|
| primary | developer | review-hub | `src/app/*`, `src/components/*`, `.ai-kit/contracts/*` | app implementation + evidence artifacts | done | closed | main build lane carried the demo through verification |
| lane-2 | analyst / pm | plan-hub | `product-brief`, `PRD`, `epics` | planning artifacts | done | merged | planning inputs were folded into final app copy |
| lane-3 | qa-governor | test-hub | `qa-report`, smoke evidence, browser review | verification artifacts | done | merged | QA lane closed after build/smoke/visual checks |

## Shared artifacts that must stay authoritative
- `.ai-kit/state/workflow-state.md`
- `.ai-kit/state/lane-registry.md`
- `.ai-kit/state/handoff-log.md`
- `.ai-kit/contracts/project-context.md`
- `.ai-kit/contracts/PRD.md`
- `.ai-kit/contracts/architecture.md`

## Merge order
Planning artifacts -> app implementation -> QA report -> workflow-state closeout.

## Merge prerequisites
- Verified product claims against repo evidence.
- Verified checkout route contract.
- Verified build and smoke gates.

## Conflict risks
- Copy drift between marketing messaging and repo truth.
- Verification commands on Windows shells using detached startup patterns.

## Decision log
- Use `baseline`, not `round4`, as the marketed bundle.
- Keep checkout fake but fully implemented.
- Treat Windows popup issue as tooling evidence, not an application failure.
