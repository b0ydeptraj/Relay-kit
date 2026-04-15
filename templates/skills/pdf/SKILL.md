---
name: pdf
description: Use when work needs PDF extraction, transformation, validation, or rendering-focused troubleshooting.
version: 2.0.0
---

# PDF

Use this skill to provide bounded, evidence-backed domain guidance to the current hub or specialist.

## When to Use

- The active task touches PDF behavior or tooling.
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

- scripts/check_bounding_boxes.py
- scripts/check_bounding_boxes_test.py
- scripts/check_fillable_fields.py
- scripts/convert_pdf_to_images.py
- scripts/create_validation_image.py
- scripts/extract_form_field_info.py
- scripts/fill_fillable_fields.py
- scripts/fill_pdf_form_with_annotations.py

## Guardrails

- Keep scope narrow; do not create parallel architecture.
- Separate observed evidence from recommendation.
- Do not claim completion without lane-level verification evidence.
