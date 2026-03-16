# story

> Path: `.ai-kit/contracts/stories/story-001.md`
> Purpose: Provide implementation-ready, focused context for a single vertical slice.
> Used by: scrum-master, developer, qa-governor, fix-hub, test-hub

## Story statement
As an AI builder evaluating `python-kit`, I need a working web demo that explains the baseline, shows proof-backed differentiation, and lets me step through a fake purchase flow so I can judge whether the system is credible.

## Acceptance criteria
- Landing page contains hero, pain/solution, 4-layer model, adapter parity, proof strip, workflow map, feature grid, and pricing preview.
- Pricing page shows the approved three-tier pricing model and FAQ.
- Checkout page preselects a plan from query params and posts a validated form to `/api/mock-checkout`.
- Success page renders the returned confirmation id and selected plan summary.
- All important claims are traceable to repo files.

## Implementation notes
- Use `src/content/site.ts` as the single source for pricing tiers, proof claims, workflow lanes, and messaging.
- Keep route files thin and push repeatable markup into `src/components`.
- Use global CSS tokens to achieve a control-room look without introducing a UI framework.

## Test notes
- `npm run lint`
- `npm run typecheck`
- `npm run build`
- HTTP smoke checks: `/`, `/pricing`, `/checkout?plan=team-workflow`, POST `/api/mock-checkout` valid + invalid payloads.
- Playwright browser review of `/` plus screenshot capture at `.ai-kit/references/sales-home-review.png`.

## Risks
- Overstating proof beyond what the repo can show.
- Checkout feeling fake if it does not round-trip through an API route.
- Windows shell quirks around detached processes during test automation.

## Done checklist
- [x] Public routes implemented.
- [x] Fake checkout route implemented.
- [x] Content centralized.
- [x] Styling differentiated from default scaffold.
- [x] Verification evidence captured.
