---
name: ui-styling
description: Use when a lane needs styling system decisions, component theming, responsive polish, or design token consistency. UI styling utility.
---

# Mission
Stabilize UI styling decisions so implementation stays cohesive across screens and adapters.

## Default outputs
- styling-system recommendations appended to tech-spec, qa-report, or workflow-state
- component-level styling guardrails for consistency and accessibility

## Typical tasks
- Define typography, spacing, color, and motion constraints for the active surface.
- Review component states for contrast, focus behavior, and responsive integrity.
- Recommend targeted style adjustments tied to concrete product states.

## Working rules
- Do not approve styling that hides weak hierarchy behind decorative gradients.
- Keep motion performance-safe and respect reduced-motion requirements.
- Tie every styling recommendation to a specific screen or component state.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- styling-system recommendations appended to tech-spec, qa-report, or workflow-state
- component-level styling guardrails for consistency and accessibility

## Reference skills and rules
- Style decisions should reinforce hierarchy and usability.
- Prefer consistent tokens over ad-hoc utility-class sprawl.

## Likely next step
- frontend-design
- fix-hub
- test-hub
- review-hub
