---
name: skill-creator
description: Create or refactor Relay-kit skills with clear activation metadata, concise instructions, and maintainable bundled resources.
version: 2.0.0
---

# Skill Creator

Use this skill to build production-ready skills, not placeholders.

## When to Use

- Adding a new skill to runtime or templates.
- Refactoring an existing skill with drifted voice/scope.
- Splitting an oversized skill into focused references/scripts.
- Standardizing metadata for reliable activation.

## Output Contract

Return:
- Skill scope and activation intent.
- Final `SKILL.md` structure.
- Any bundled `references/` or `scripts/` added.
- Validation results and residual risks.

## Workflow

1. Define scope: one problem class per skill.
2. Write concise frontmatter (`name`, `description`).
3. Keep `SKILL.md` focused; move details to references/scripts.
4. Add tests/checks for deterministic scripts.
5. Verify integration with runtime gates.

## Scripts

- `python scripts/init_skill.py`
- `python scripts/quick_validate.py`
- `python scripts/package_skill.py`

## Guardrails

- Avoid broad "do everything" skill definitions.
- Prefer progressive disclosure over huge instruction blocks.
- Keep naming and voice aligned with Relay-kit runtime conventions.
