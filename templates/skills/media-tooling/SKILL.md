---
name: media-tooling
description: Use when assets or screenshots need conversion, optimization, or deterministic media preprocessing.
version: 2.0.0
---

# Media Tooling

Use this skill to provide bounded, evidence-backed domain guidance to the current hub or specialist.

## When to Use

- The active task touches Media Tooling behavior or tooling.
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

- references/ffmpeg-encoding.md
- references/ffmpeg-filters.md
- references/ffmpeg-streaming.md
- references/format-compatibility.md
- references/imagemagick-batch.md
- references/imagemagick-editing.md

## Scripts

- scripts/batch_resize.py
- scripts/media_convert.py
- scripts/requirements.txt
- scripts/video_optimize.py

## Guardrails

- Keep scope narrow; do not create parallel architecture.
- Separate observed evidence from recommendation.
- Do not claim completion without lane-level verification evidence.
