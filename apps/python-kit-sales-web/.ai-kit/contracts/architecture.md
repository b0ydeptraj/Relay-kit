# architecture

> Path: `.ai-kit/contracts/architecture.md`
> Purpose: Translate the PRD into concrete technical structure, data flow, interfaces, and implementation constraints.
> Used by: architect, scrum-master, qa-governor, plan-hub, review-hub

## Current-system constraints
- The app must stay inside the `python-kit` monorepo as `apps/python-kit-sales-web`.
- The workspace already contains generated baseline artifacts under `.ai-kit/` and runtime skills under `.claude/skills`, `.agent/skills`, and `.codex/skills`.
- The app uses Next.js 16 App Router with strict TypeScript and no external backend.

## Proposed design
Use a content-driven Next.js marketing app with a small design system in global CSS, thin pages under `src/app`, and reusable components under `src/components`. The fake commerce flow is a client form posting to a server route handler that returns structured JSON. Proof sections are backed by content arrays that point to concrete repo evidence.

### Visual-system direction
- The top half of the site is intentionally light and editorial: warm ivory surfaces, restrained gradients, and more whitespace for the initial value proposition.
- The lower half of the site transitions into a dark operator stage so the product can shift from sales language into system proof, command surfaces, pricing logic, and checkout seriousness.
- Core explainer content now prefers command-style panels and proof boards over generic feature paragraphs.
- Brand expression is built from a custom inline SVG mark, a split wordmark treatment, and a warmer palette (`ivory`, `copper`, `plum`, `mint`) rather than default blue/black SaaS styling.
- Typography is deliberately mixed:
  - `Fraunces` for display hierarchy
  - `Manrope` for body/UI copy
  - `JetBrains Mono` for command and proof surfaces

### Reference anchors
- Landing/home structural direction now follows a ref-driven approach based primarily on [Linear](https://linear.app/) for editorial rhythm, asymmetry, and product-proof storytelling.
- Pricing direction is now anchored to [Resend pricing](https://resend.com/pricing) for denser, more credible developer-tool plan presentation and a pricing-sheet structure rather than three floating marketing cards.
- Checkout direction now uses a procurement-style two-column form + summary layout so the conversion flow reads like a real technical product checkout instead of a dead demo form.

## Module boundaries
- `src/content/site.ts`: authoritative content and pricing data.
- `src/lib/checkout.ts`: checkout payload validation and response shaping.
- `src/components/*`: reusable UI sections (`site-header`, `site-footer`, `workflow-diagram`, `pricing-table`, `checkout-form`, `home-page`).
- `src/app/*`: route entrypoints for `/`, `/pricing`, `/checkout`, `/success`, and `/api/mock-checkout`.
- `.ai-kit/contracts/*` and `.ai-kit/state/*`: workflow artifacts and verification evidence for this app workspace.

## Data flow and integrations
- Public route flow: `/` and `/pricing` link into `/checkout?plan=<tier>`.
- Checkout flow: `CheckoutForm` performs local validation, posts JSON to `/api/mock-checkout`, receives `{ orderId, plan, tierName, billingModel }`, then redirects to `/success`.
- There are no external APIs, databases, or payment providers in this batch.

## Operational concerns
- Security: only minimal validation is required because no persistence or real billing exists, but the API still rejects malformed payloads.
- Performance: pages are mostly static content; only checkout and success use query-driven server rendering.
- Reliability: smoke-tested via HTTP responses and mock API round-trip.
- Failure handling: invalid requests return 422 with field-level errors; invalid query params fall back to the recommended tier.
- Browser behavior: desktop and mobile are explicitly checked after build. The responsive contract is validated at desktop width (`1440px`) and mobile width (`390px`) instead of relying on screenshots alone.

## Trade-offs and ADR notes
- Chosen: global CSS with explicit design tokens. Rejected: default create-next-app styles because they would look generic.
- Chosen: rebuild the home page around editorial structure and a control-board panel. Rejected: oversized hero + floating support cards because the result looked obviously AI-generated.
- Chosen: rebuild pricing as a denser sheet with packaging logic and a technical comparison table. Rejected: repeated plan cards with equal visual weight because they looked interchangeable and marketing-generic.
- Chosen: add a final pricing narrative layer with a commercial-stance rail, a decision guide, a capability-matrix preface, and a closing CTA. Rejected: leaving pricing as a single uninterrupted sheet because the pacing still felt AI-generated even after the structural rebuild.
- Chosen: rebuild checkout as a procurement flow with stronger plan-selection state and a fixed summary rail. Rejected: soft stacked cards because they made the flow feel like a fake demo.
- Chosen: use a staged light-to-dark theme transition to separate brand introduction from proof-heavy operator sections. Rejected: a single uniform dark page because it kept reading like generic AI-generated SaaS.
- Chosen: use command panels as the primary explainer component. Rejected: plain text feature grids because they did not communicate the actual product behavior strongly enough.
- Chosen: keep reveal animations on scroll so command/proof panels enter as the user reaches them. Rejected: always-on motion or decorative animation with no structural purpose.
- Chosen: repo-backed proof claims only. Rejected: invented marketing metrics or testimonials.
- Chosen: fake checkout with real validation and navigation. Rejected: dead CTA or alert-based checkout because it would not prove implementation quality.
- Chosen: keep `round4` as compatibility context while selling `baseline` as the official bundle.
- Root-cause note: `src/app/globals.css` had to be rewritten without a UTF-8 BOM. The BOM caused the built stylesheet to emit a broken `:root` token, which prevented custom properties from binding and made dark-stage sections render with incorrect contrast.

## Implementation readiness verdict
Ready and implemented. The code paths, routes, and evidence artifacts are in place, and the app has passed lint, typecheck, build, smoke, and browser review.
