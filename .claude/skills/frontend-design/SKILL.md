---
name: frontend-design
description: Use when a lane needs to implement or refactor UI with clear visual direction and production-ready structure. Frontend design execution utility.
---

# Mission
Convert UI intent into implementation-ready structure that remains distinctive and maintainable.

## Default outputs
- implementation-ready UI structure guidance appended to the active artifact
- state coverage notes for loading, empty, and error scenarios

## Typical tasks
- Define composition, hierarchy, and responsive behavior before coding details.
- Ensure loading, empty, and error states are included for real product surfaces.
- Call out where implementation should use shared components versus custom layout work.

## Working rules
- Avoid template-like safe layouts when hierarchy demands stronger composition.
- Prefer explicit section roles (dominant/supporting/quiet) over equal-weight blocks.
- Route accessibility and verification concerns back through test-hub and qa-governor.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- implementation-ready UI structure guidance appended to the active artifact
- state coverage notes for loading, empty, and error scenarios

## Reference skills and rules
- Build from explicit design direction, not vague adjectives.
- Treat component libraries as ingredients, not final design.

## Likely next step
- ui-styling
- developer
- fix-hub
- test-hub
- review-hub
