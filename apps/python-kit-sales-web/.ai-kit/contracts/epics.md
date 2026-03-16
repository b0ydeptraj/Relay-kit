# epics

> Path: `.ai-kit/contracts/epics.md`
> Purpose: Break work into coherent slices and define sequencing before story creation.
> Used by: pm, scrum-master, plan-hub

## Epic overview
Three epics carried the demo:
1. Baseline workspace setup inside the app.
2. Public product surface (landing, pricing, proof sections).
3. Commerce simulation and verification.

## Per-epic goals
- Epic 1: Generate `baseline` plus contracts/docs/references into the app workspace and establish the artifact surface.
- Epic 2: Build a differentiated marketing UI with proof-backed copy and centralized content.
- Epic 3: Implement a fake checkout route, validate the flow, and record QA evidence back into `.ai-kit` artifacts.

## Dependencies
- Epic 2 depends on Epic 1 because the proof sections reference generated workspace artifacts.
- Epic 3 depends on Epic 2 because pricing and CTA routing feed the checkout flow.
- QA/reporting depends on all prior epics completing.

## Definition of done
- Code exists for all public routes and the mock API.
- Content only uses auditable repo claims.
- Lint, typecheck, and build pass.
- Smoke checks and one browser review are documented.

## Suggested order
1. Workspace generation.
2. Content + design system.
3. Route implementation.
4. Checkout/API.
5. QA and artifact updates.
