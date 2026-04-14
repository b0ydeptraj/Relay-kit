---
name: multimodal-evidence
description: Extract structured evidence from media inputs (images, video, audio, and documents) and convert results into implementation-relevant findings.
version: 2.0.0
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# Multimodal Evidence

Use this skill when key facts are inside media artifacts rather than source code.

## When to Use

- Screenshot/UI image needs precise interpretation.
- Video timeline or frame evidence is required.
- Audio/transcript must be summarized or checked.
- PDF/document content needs structured extraction.

## Output Contract

Return:
- Media analyzed and method used.
- Structured findings.
- Confidence/ambiguity notes.
- Actionable implications for current task.

## Workflow

1. Identify exact media question to answer.
2. Choose the smallest processing path that answers it.
3. Extract structured signals (tables, timestamps, entities).
4. Tie findings back to code, tests, or UX decisions.

## Scripts

- `python scripts/gemini_batch_process.py`
- `python scripts/document_converter.py`
- `python scripts/media_optimizer.py`

If script dependencies are needed: `pip install -r scripts/requirements.txt`.

## References

- `references/vision-understanding.md`
- `references/video-analysis.md`
- `references/audio-processing.md`
- `references/image-generation.md`

## Guardrails

- Do not claim certainty when input quality is poor.
- Keep analysis scoped to the task question.
- Preserve privacy and avoid exposing sensitive media content.
