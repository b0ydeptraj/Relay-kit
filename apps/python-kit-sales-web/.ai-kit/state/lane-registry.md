# lane-registry

## Usage rules
- One lane owns one artifact lock at a time.
- Record the narrowest useful lock scope, not whole-repo ownership by default.
- Release or reassign the lock before a different lane edits the same artifact section.

## Active lanes
| Lane | Owner skill | Source orchestrator | Target hub | Primary artifact | Lock scope | Merge prerequisite | Status |
|---|---|---|---|---|---|---|---|
| primary | developer | workflow-router | review-hub | `src/app/*` and `src/components/*` | marketing UI + mock checkout flow | QA report complete | released |
| lane-2 | pm | team | plan-hub | `.ai-kit/contracts/PRD.md` | scope, requirements, pricing model | architecture aligned | released |
| lane-3 | qa-governor | team | test-hub | `.ai-kit/contracts/qa-report.md` | verification evidence and residual risk | smoke + browser review done | released |

## Released locks
| Lane | Artifact | Previous scope | Released because |
|---|---|---|---|
| lane-2 | `.ai-kit/contracts/*` | planning artifacts | implementation started against stable scope |
| primary | `src/content/site.ts` | proof claims and pricing copy | app pages finished and verified |
| lane-3 | `.ai-kit/contracts/qa-report.md` | QA evidence | recommendation recorded and no blocker remained |
