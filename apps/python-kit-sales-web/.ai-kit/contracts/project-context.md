# project-context

> Path: `.ai-kit/contracts/project-context.md`
> Purpose: Document current codebase patterns, constraints, and rules that every later step must respect.
> Used by: workflow-router, bootstrap, cook, analyst, pm, architect, scrum-master, developer, qa-governor, scout-hub

## Existing architecture
- Next.js 16 App Router app with routes under `src/app`.
- Marketing content is centralized in `src/content/site.ts`.
- Validation logic is centralized in `src/lib/checkout.ts`.
- Shared UI sections live in `src/components`.

## Coding conventions
- TypeScript strict mode.
- App Router pages are thin; reusable markup stays in components.
- Content strings and plan definitions stay out of page files.
- Styling is global CSS with named utility-ish classes, not inline style sprawl.

## Dependency and toolchain rules
- Dependencies stay minimal: `next`, `react`, `react-dom` plus default TypeScript/ESLint toolchain.
- Validation uses plain TypeScript functions instead of extra schema libraries.
- Quality gates: `npm run lint`, `npm run typecheck`, `npm run build`.

## Domain and compliance constraints
- This is a demo storefront only; no real billing, auth, or persistence.
- Claims must map to real repo evidence.
- The demo is aimed at technical buyers, not general consumers.

## Known sharp edges
- Detached Windows shell patterns using `cmd /c start` were noisy and produced popup errors during experimentation; verification should prefer direct foreground server commands plus browser tooling.
- Query params on `/checkout` and `/success` must be validated and normalized.

## Files or modules to mirror
- `src/content/site.ts`
- `src/lib/checkout.ts`
- `src/components/home-page.tsx`
- `src/components/pricing-table.tsx`
- `src/components/checkout-form.tsx`
