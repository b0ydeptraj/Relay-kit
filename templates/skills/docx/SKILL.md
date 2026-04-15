---
name: docx
description: Use when work needs DOCX parsing, generation, or content updates with deterministic file handling.
version: 2.0.0
---

# DOCX

Use this skill to provide bounded, evidence-backed domain guidance to the current hub or specialist.

## When to Use

- The active task touches DOCX behavior or tooling.
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

- Prefer repository docs and nearby code as primary references.

## Scripts

- scripts/__init__.py
- scripts/document.py
- scripts/utilities.py

## Guardrails

- Keep scope narrow; do not create parallel architecture.
- Separate observed evidence from recommendation.
- Do not claim completion without lane-level verification evidence.
