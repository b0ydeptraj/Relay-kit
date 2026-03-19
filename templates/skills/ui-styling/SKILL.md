---
name: ui-styling
description: Use when building user interfaces, implementing design systems, creating responsive layouts, adding accessible components (dialogs, dropdowns, forms, tables), customizing themes and colors, implementing dark mode, generating visual designs and posters, or establishing consistent styling patterns across applications. Create beautiful, accessible user interfaces with shadcn/ui components (built on Radix UI + Tailwind), Tailwind CSS utility-first styling, and canvas-based visual designs.
license: MIT
version: 1.0.0
---

# UI Styling Skill

Comprehensive skill for creating beautiful, accessible user interfaces combining shadcn/ui components, Tailwind CSS utility styling, and canvas-based visual design systems. Treat component libraries as raw material, not as finished design.

## Reference

- shadcn/ui: https://ui.shadcn.com/llms.txt
- Tailwind CSS: https://tailwindcss.com/docs

## When to Use This Skill

Use when:
- building UI with React-based frameworks (Next.js, Vite, Remix, Astro)
- implementing accessible components (dialogs, forms, tables, navigation)
- styling with utility-first CSS approach
- creating responsive, mobile-first layouts
- implementing dark mode and theme customization
- building design systems with consistent tokens
- generating visual designs, posters, or brand materials
- adding complex UI patterns (data tables, charts, command palettes)
- a page looks too generic, too template-like, or too obviously AI-generated

## Anti-generic rules

Do not ship the default look of a component library.

Reject and revise when the page depends on:
- default shadcn card styling with minimal customization
- equal-radius panels everywhere
- safe monochrome spacing with no emphasis hierarchy
- generic chart defaults
- placeholder icon choices
- utility-class accumulation without a clear design system

When styling a real product surface:
- choose a deliberate type system
- choose a deliberate corner system
- choose a deliberate contrast system
- define which blocks are dominant, supporting, and quiet
- customize borrowed components until they feel native to the product

## Taste controls
Set these three controls before building or restyling a surface:
- **Design variance**: `low`, `medium`, or `high`
- **Motion intensity**: `low`, `medium`, or `high`
- **Visual density**: `low`, `medium`, or `high`

These controls should change the result. A minimal marketing page should not look like a dense operations dashboard.

## State coverage requirements
When styling a real product surface, require explicit design for:
- loading state
- empty state
- error state

Do not leave these as unstyled placeholders. They are part of the product UI, not afterthoughts.

## Layout and motion rules
- Prefer grid layout or deliberate asymmetry when hierarchy matters; do not rely on flexbox as a generic equal-card hack.
- Avoid the default three-card horizontal block unless the content truly has equal priority.
- Avoid purple-blue gradient filler and other generic AI styling shortcuts.
- Keep motion performance-safe: prefer transform and opacity, use staggered reveals intentionally, and respect reduced-motion settings.

## Menu UI principle

When a screen needs strong visual quality, source patterns intentionally instead of asking the model to invent them.

Examples:
- use a chart library for chart structure and tune it
- use a specific icon system and keep it consistent
- use trusted component galleries for nav, pricing, or form patterns
- use screenshot references to anchor layout before styling

The goal is not to paste a library verbatim. The goal is to start from a stronger source and then adapt it convincingly.

## Core stack

### Component layer: shadcn/ui
- Pre-built accessible components via Radix UI primitives
- Copy-paste distribution model (components live in your codebase)
- TypeScript-first with full type safety
- Composable primitives for complex UIs

### Styling layer: Tailwind CSS
- Utility-first CSS framework
- Build-time processing with zero runtime overhead
- Mobile-first responsive design
- Consistent design tokens
- Automatic dead code elimination

### Visual design layer: Canvas
- Museum-quality visual compositions
- Sophisticated visual communication
- Minimal text, maximum visual impact
- Systematic patterns and refined aesthetics

## Use the bundled references

Reach for these files instead of bloating `SKILL.md` with details:
- `references/shadcn-components.md`
- `references/shadcn-theming.md`
- `references/shadcn-accessibility.md`
- `references/tailwind-utilities.md`
- `references/tailwind-responsive.md`
- `references/tailwind-customization.md`
- `references/canvas-design-system.md`

Use scripts when deterministic setup helps:
- `scripts/shadcn_add.py`
- `scripts/tailwind_config_gen.py`

## Working method

1. Decide whether the surface needs a design-system pass, a layout pass, or both.
2. Pick taste controls before touching classes or tokens.
3. Choose a source pattern for charts, icons, nav, forms, or tables.
4. Adapt spacing, type, contrast, and states until the borrowed components feel native.
5. Review the screen for hierarchy, accessibility, and generic-AI smells before calling it done.

## Final check

Before shipping, verify:
- components no longer look like untouched library defaults
- hierarchy is visible without relying on color alone
- loading, empty, and error states feel designed
- motion is subtle, useful, and performance-safe
- the page looks product-specific rather than template-generated
