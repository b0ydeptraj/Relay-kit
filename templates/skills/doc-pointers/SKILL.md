---
name: doc-pointers
description: Retrieve exact documentation pointers and short excerpts from authoritative sources. Use when a hub needs citations or precise API behavior before deciding.
version: 2.0.0
---

# Doc Pointers

Use this skill for fast, source-grounded documentation retrieval.

## When to Use

- API behavior is unclear.
- Version-specific syntax matters.
- A fix must cite official docs.
- A planning decision depends on exact constraints.

## Output Contract

Return:
- Source links.
- Exact section names.
- Short relevant excerpts or paraphrases.
- Impact on the current task.

## Retrieval Order

1. Official product/library documentation.
2. Official repository docs (`README`, `docs/`, release notes).
3. Standards/specs when relevant.
4. Community sources only if primary docs are missing.

## Workflow

1. Normalize target library/framework and version.
2. Locate the narrowest relevant sections.
3. Capture only the lines needed for the current decision.
4. Map findings to concrete implementation guidance.

## References

- `references/documentation-sources.md`
- `references/tool-selection.md`
- `references/best-practices.md`
- `references/error-handling.md`
- `references/limitations.md`
- `references/performance.md`

## Guardrails

- Do not cite secondary summaries over primary docs.
- Avoid long dumps; keep pointers actionable.
- Mark assumptions when docs are ambiguous.
