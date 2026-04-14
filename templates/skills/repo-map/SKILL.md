---
name: repo-map
description: Build a concise repository map and impact surface before planning, debugging, or review. Use when codebase shape is unclear or change risk must be estimated.
version: 2.0.0
---

# Repo Map

Use this skill to convert large repos into actionable structure summaries.

## When to Use

- Entering an unfamiliar repository area.
- Estimating blast radius for a change.
- Locating ownership boundaries and entrypoints.
- Preparing evidence for planning or review hubs.

## Output Contract

Return:
- Entrypoints and critical modules.
- Dependency/ownership map relevant to request.
- Impact surface (upstream/downstream/tests).
- Recommended next inspection targets.

## Workflow

1. Scope the question and target folders.
2. Build a focused map (not full-dump output).
3. Identify likely touched files and test surfaces.
4. Hand off concise findings with file pointers.

## Scripts

- `python scripts/repomix_batch.py --help`

See usage patterns in `scripts/README.md` and `references/usage-patterns.md`.

## References

- `references/configuration.md`
- `references/usage-patterns.md`

## Guardrails

- Prefer narrow maps over whole-repo snapshots.
- Keep outputs tied to the active task.
- Mark assumptions when module ownership is unclear.
