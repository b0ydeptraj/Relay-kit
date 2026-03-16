---
name: ui-ux-pro-max
description: UX and layout utility for user-facing work. Use when a hub needs sharper information hierarchy, cleaner flows, stronger screen structure, less generic AI-looking UI, or concrete UX corrections tied to implementation reality.
---

# Mission
Raise the UX and layout quality of the current slice without taking ownership away from product or implementation lanes.

This skill exists to stop vague UX comments and generic "make it modern" output. It should turn weak layouts and shallow UI prompts into concrete structure, hierarchy, flow, and refinement decisions that a builder can actually ship.

## What this skill should improve
- page structure and reading order
- information hierarchy and CTA hierarchy
- spacing rhythm, density, and grouping
- component choice and layout composition
- copy clarity inside forms, cards, nav, empty states, and checkout flows
- responsive collapse behavior
- post-build UI critique with concrete fixes

## Default outputs
- UX/layout notes appended to `product-brief`, `PRD`, `architecture`, or `qa-report`
- a compact screen-by-screen critique
- a refinement checklist with concrete edits, not vague taste comments

## Typical tasks
- audit a landing page, dashboard, checkout, or settings flow
- call out where a page looks obviously AI-generated or visually average
- convert a rough brief into a stronger page structure
- tighten CTA hierarchy, card usage, navigation, and responsive behavior
- review a built screen and specify the next round of polish

## Anti-generic rules
Do not approve UI just because it is clean.

Flag and correct these patterns aggressively:
- oversized safe hero + generic supporting card column
- rounded cards everywhere with little hierarchy difference
- decorative gradients with no structural purpose
- repetitive feature-card grids that say little and look the same
- metric tiles or badges used as filler instead of narrative proof
- default icon sets, default chart shapes, default typography stacks
- layouts that look like "template SaaS marketing page #427"

If the screen looks like first-pass AI output, say so directly and recommend structural changes.

## Working method

### 1. Start from evidence, not taste words
Tie every UX recommendation to one of:
- a user goal
- a conversion goal
- a repo truth / proof requirement
- a specific screen or flow problem

### 2. Prefer reference-driven direction
If visual quality matters, do not let the model invent layout from scratch.

Use one of these anchors:
- a provided screenshot or visual reference
- an existing product/page pattern already in the codebase
- a component/library source ("menu UI") for charts, icons, nav, forms, or pricing structures

When no reference exists, define a concrete direction before recommending changes:
- page archetype
- layout ratio
- typography behavior
- component density
- motion budget

### 3. Judge every screen with this checklist
- What is the first thing the user sees?
- Is the reading order obvious in 3 seconds?
- Are primary and secondary CTAs clearly separated?
- Does the layout have one dominant idea, or too many equal-weight blocks?
- Are cards doing real information work, or just filling space?
- Do spacing and alignment create rhythm, or just uniform emptiness?
- Will the mobile collapse still make sense?

### 4. Convert critique into implementation-ready edits
Bad:
- "make it nicer"
- "improve visual hierarchy"
- "make it more premium"

Good:
- reduce hero width and move proof closer to the headline
- replace three identical pain cards with one narrative proof block + one supporting metric strip
- switch checkout from stacked text blocks to two-column summary/form with stronger plan selection state
- tighten radius system from large-soft to controlled-small to reduce template feel

### 5. Require one review pass after build
For meaningful UI work, this skill should recommend at least one screenshot-based or browser-based review after implementation. First-pass code is not final UX.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- screenshots, built UI, or concrete page description when available
- only the evidence relevant to this pass

## Outputs
- implementation-ready UX notes
- layout critique with concrete corrections
- anti-generic design checklist for the owning lane

## Reference skills and rules
- Use alongside `developer`, `review-hub`, `qa-governor`, `frontend-design`, and browser review utilities.
- Return guidance to the owning hub instead of rewriting the whole project plan.

## Likely next step
- plan-hub
- developer
- review-hub
- qa-governor
