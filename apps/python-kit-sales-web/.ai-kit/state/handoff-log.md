# handoff-log

## Handoff entries
| From | To | Lane | Trigger | Artifact touched | Evidence linked | Expected return condition |
|---|---|---|---|---|---|---|
| workflow-router | plan-hub | lane-2 | request scoped as medium-complexity product + implementation work | `product-brief`, `PRD` | `.ai-kit/contracts/product-brief.md` | build-ready scope |
| plan-hub | developer | primary | scope and pricing model stabilized | `architecture`, `epics`, `story-001` | `.ai-kit/contracts/architecture.md` | working app routes |
| developer | test-hub | lane-3 | landing, pricing, checkout, and success routes implemented | `qa-report`, smoke notes | `npm run lint`, `npm run typecheck`, `npm run build` | QA recommendation |
| review-hub | developer + ui-ux-pro-max | primary | first-pass UI looked obviously AI-generated | `architecture`, `qa-report`, `src/components/*`, `src/app/globals.css` | `.ai-kit/references/sales-home-review-v2.png` | stronger ref-driven pricing/checkout layout |
| test-hub | review-hub | primary | smoke and browser review evidence collected | `qa-report`, `workflow-state` | `.ai-kit/references/sales-home-review-v2.png`, Playwright snapshot, API smoke outputs | close or request follow-up |
| developer | review-hub | primary | pricing sheet + checkout procurement pass completed | `qa-report`, `workflow-state`, pricing/checkout screenshots | `.ai-kit/references/sales-pricing-review-v2.png`, `.ai-kit/references/sales-checkout-review-v2.png` | decide commit readiness |
| review-hub | workflow-state | primary | no functional blocker remained | `workflow-state`, `team-board`, `lane-registry` | `.ai-kit/state/*.md` | lane closed |

## Rules
- Every non-trivial handoff should update this log before the receiving skill starts work.
- Link to the authoritative artifact, not only a chat summary.
- If a handoff changes scope or ownership, update `workflow-state.md` and `lane-registry.md` in the same pass.
