---
name: mermaid-diagrams
description: Use when architecture or flow decisions need concise Mermaid diagrams tied to implementation artifacts.
version: 2.0.0
---

# Mermaid Diagrams

Use this skill to provide bounded, evidence-backed domain guidance to the current hub or specialist.

## When to Use

- The active task touches Mermaid Diagrams behavior or tooling.
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

- references/cli-usage.md
- references/configuration.md
- references/diagram-types.md
- references/examples.md
- references/integration.md

## Scripts

- No bundled scripts required for this skill.

## Guardrails

- Keep scope narrow; do not create parallel architecture.
- Separate observed evidence from recommendation.
- Do not claim completion without lane-level verification evidence.
