---
name: backend-development
description: Use when the request requires focused Backend Development implementation, debugging, or review guidance in the active lane.
version: 2.0.0
---

# Backend Development

Use this skill to provide bounded, evidence-backed domain guidance to the current hub or specialist.

## When to Use

- The active task touches Backend Development behavior or tooling.
- A decision needs domain constraints before coding.
- A fix or review needs focused checks for this domain.

## Output Contract

- Key findings tied to affected files or artifacts.
- Recommended next action and verification notes.
- Risks or unknowns that still block safe completion.

## Workflow

1. Confirm scope and acceptance signal with the owning hub.
2. Gather only domain evidence needed for this pass.
3. Propose the smallest safe implementation or review path.
4. Hand results back to the owning lane with a concrete next step.

## References

- references/backend-api-design.md
- references/backend-architecture.md
- references/backend-authentication.md
- references/backend-code-quality.md
- references/backend-debugging.md
- references/backend-devops.md
- references/backend-mindset.md
- references/backend-performance.md
- references/backend-security.md
- references/backend-technologies.md
- references/backend-testing.md

## Scripts

- No bundled scripts required for this skill.

## Guardrails

- Keep scope narrow; do not create parallel architecture.
- Separate observed evidence from recommendation.
- Do not claim completion without lane-level verification evidence.
