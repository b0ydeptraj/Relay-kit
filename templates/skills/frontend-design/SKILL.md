---
name: frontend-design
description: Use when the user asks to build web components, pages, or applications and visual quality matters. Create distinctive, production-grade frontend interfaces that avoid generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to structure, hierarchy, proportion, motion, and refinement.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Non-Negotiables

- Do not let the model invent the visual system from vague adjectives like "modern", "clean", or "minimal".
- If visual quality matters, anchor the work with one of:
  - screenshot references
  - an existing product/page pattern in the codebase
  - a strong component/library source ("menu UI") for charts, forms, nav, icons, or layouts
- Treat libraries and templates as raw material, not final design.
- If the first build looks obviously AI-generated, do not defend it. Diagnose it and change structure.

Flag these smells aggressively:
- giant safe hero + generic card column
- over-rounded cards everywhere
- purple/pink gradient filler
- evenly weighted sections with no focal point
- repetitive feature grids with interchangeable copy
- default icon packs and chart styles
- "clean SaaS" with no point of view

## Design Thinking

Before coding, understand the context and commit to a clear aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick a concrete direction with references, not a mood-board adjective salad. Examples: editorial dark tech, industrial dashboard, precise Swiss product page, tactile operator console, restrained brutalism, premium documentation UI.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this unforgettable? What is the one thing someone will remember?

The goal is not "more styling". The goal is a stronger structure and a more believable visual language.

## Taste controls
Before coding, set these three controls explicitly:
- **Design variance**: `low`, `medium`, or `high`
- **Motion intensity**: `low`, `medium`, or `high`
- **Visual density**: `low`, `medium`, or `high`

Do not leave these vague. A restrained docs surface and an operator dashboard should not use the same settings.

## State and layout requirements
For real product UI, require:
- a loading state
- an empty state
- an error state

These states must feel designed, not bolted on.

Prefer grid layout or deliberate asymmetry when hierarchy matters. Avoid using flexbox as a generic equal-card hack when a stronger grid would communicate better structure.

Keep motion performance-safe:
- prefer transform and opacity over layout-thrashing animation
- match motion intensity to the page purpose
- respect reduced-motion settings

If richer motion is needed, use `references/animejs.md` deliberately rather than inventing animation blindly.

## Reference-driven workflow

### 1. Lock a source of truth before styling
Use at least one of:
- screenshot references from real products
- UI libraries or component galleries
- chart libraries and icon systems
- a page archetype already validated in the project

When a reference exists, keep roughly 70-80% of its structural logic and spend the remaining 20-30% on adapting brand, copy, and product specifics.

### 2. Decompose the page before writing code
For every screen, define:
- primary focal point
- supporting proof block
- CTA hierarchy
- section rhythm
- mobile collapse behavior
- which blocks deserve contrast and which should recede

### 3. Source components intentionally
Do not ask the model to "make a beautiful chart" or "make a cool card". Pick or emulate a specific source, then adapt it.

### 4. Build, then critique like a designer
After the first pass, check:
- is the layout memorable?
- is there a dominant visual idea?
- are too many blocks competing equally?
- does the spacing feel intentional or merely padded?
- would another engineer instantly say "AI built this"?

If yes, revise structure before polishing details.

## Frontend aesthetics guidelines

Focus on:
- **Typography**: choose fonts with character; avoid lazy defaults like Arial, Inter, or generic system stacks unless the product truly calls for them
- **Color and theme**: use CSS variables and a deliberate contrast system; color should support hierarchy, not compensate for weak layout
- **Motion**: use animation to improve comprehension and delight, not to decorate weak structure
- **Spatial composition**: asymmetry, overlap, or density changes are useful only when reading order stays obvious
- **Backgrounds and detail**: create atmosphere with restraint; avoid filler gradients and texture spam

Never use generic AI-generated aesthetics like overused font families, cliched gradients, predictable equal-card layouts, or copy-paste SaaS sections with no point of view.

## Refinement checklist

Before calling a page done, verify:
- the hero is not just large text plus two buttons plus generic stats
- proof is visually closer to the core claim
- cards have different hierarchy roles, not one repeated component
- spacing changes by purpose, not just by a uniform gap scale
- icons, charts, and form states use deliberate systems
- mobile layout preserves priority and does not become a long stack of equal-weight cards

Strong frontend design comes from controlled references, sharper structure, and at least one serious review pass after implementation.
