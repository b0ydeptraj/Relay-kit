# qa-report

> Path: `.ai-kit/contracts/qa-report.md`
> Purpose: Record acceptance coverage, risk review, regression impact, and remaining gaps before declaring work complete.
> Used by: qa-governor, developer, test-hub, review-hub

## Scope checked
- Next.js app scaffold at `apps/python-kit-sales-web`.
- Public routes: `/`, `/pricing`, `/checkout`, `/success`.
- API route: `/api/mock-checkout`.
- Content model in `src/content/site.ts`.
- Client validation and redirect flow in `src/components/checkout-form.tsx`.

## Acceptance coverage
- `npm run lint` -> pass.
- `npm run typecheck` -> pass.
- `npm run build` -> pass.
- Smoke HTTP checks -> `/`, `/pricing`, `/checkout?plan=team-workflow`, and `/success?plan=team-workflow&orderId=PK-DEMO-123` all returned `200`.
- Valid POST to `/api/mock-checkout` returned a mock order payload with `orderId`, `plan`, `tierName`, and `billingModel`.
- Invalid POST returned field-level validation errors for `name`, `email`, `team`, and `useCase`.
- Browser review of `/` succeeded via Playwright at desktop width (`1440px`) and mobile width (`390px`) with refreshed screenshots saved to `.ai-kit/references/sales-home-review-v5.png` and `.ai-kit/references/sales-home-mobile-v4.png`.
- Browser review of `/pricing` succeeded via Playwright with a refreshed desktop screenshot saved to `.ai-kit/references/sales-pricing-review-v6.png`.
- Browser review of `/checkout?plan=team-workflow` succeeded via Playwright with refreshed screenshot saved to `.ai-kit/references/sales-checkout-review-v4.png`.
- Interactive checkout verification succeeded: changing the selected tier updated the CTA and summary, and a valid submission redirected to `/success` with a generated mock order id.
- Mobile browser review succeeded after header/footer, typography polish, and the final theme pass; the current mobile evidence set is led by `.ai-kit/references/sales-home-mobile-v4.png`.

## Risk matrix
- Low: static marketing routes; low functional complexity.
- Medium: checkout relies on query params and client-side state; mitigated by shared validation helpers.
- Medium: the visual system is now much stronger, but the remaining risk is refinement rather than structure: future passes may still tune animation pacing, copy density, and section rhythm.
- Low: mobile review now covers the primary routes; remaining responsive risk is edge-case tuning on unusually short or unusually dense viewports.
- Low: no persistence or third-party payment integration in this batch.

## Regression surface
- `src/app/layout.tsx`
- `src/app/globals.css`
- `src/app/page.tsx`
- `src/app/pricing/page.tsx`
- `src/app/checkout/page.tsx`
- `src/app/success/page.tsx`
- `src/app/api/mock-checkout/route.ts`
- `src/components/*`
- `src/content/site.ts`
- `src/lib/checkout.ts`

## Evidence collected
- Build output from `next build` showing `/`, `/pricing`, `/checkout`, `/success`, and `/api/mock-checkout` compiled.
- Desktop width verification from Playwright:
  - `window.innerWidth` -> `1440`
  - `document.body.clientWidth` -> `1440`
  - `.page-shell` width -> `1440`
  - `.hero-stage__grid` width -> `1440`
- Smoke outputs:
  - `/` -> `200`
  - `/pricing` -> `200`
  - `/checkout?plan=team-workflow` -> `200`
  - `/success?plan=team-workflow&orderId=PK-DEMO-123` -> `200`
  - valid POST -> `{"orderId":"PK-TEAMWO-MMRL4J2P","plan":"team-workflow","tierName":"Team Workflow","billingModel":"one-time"}`
  - invalid POST -> validation errors JSON
- Visual evidence:
  - Playwright snapshot of the landing page.
  - Screenshot file `.ai-kit/references/sales-home-review-v5.png`.
  - Screenshot file `.ai-kit/references/sales-pricing-review-v6.png`.
  - Screenshot file `.ai-kit/references/sales-checkout-review-v4.png`.
  - Screenshot file `.ai-kit/references/sales-home-mobile-v4.png`.
  - Home now uses a light editorial upper stage and a dark operator stage below it, with command panels replacing generic feature-copy blocks.
  - Pricing now reads as a denser operational pricing sheet with staged section pacing instead of repetitive floating cards.
  - Checkout now reads as a procurement-style flow with stronger plan state, cleaner hierarchy, and a summary rail that behaves like real product UI.
  - Brand presentation now includes a custom mark, a more deliberate wordmark treatment, and a warmer palette anchored on ivory, copper, plum, and mint instead of generic blue/black SaaS colors.
  - Typography now uses `Fraunces` for display, `Manrope` for body copy, and `JetBrains Mono` for command surfaces.
  - Root-cause fix recorded: `src/app/globals.css` originally shipped with a UTF-8 BOM, which produced `:root` CSS variables that failed to bind in the built stylesheet. Stripping the BOM corrected the theme system, dark-stage contrast, and pricing-page rendering.

## Go / no-go recommendation
Go for demo use. The app now has verified desktop/mobile behavior, a stronger non-generic visual identity, corrected production theme binding, and browser evidence for the core routes rather than only HTTP smoke.
