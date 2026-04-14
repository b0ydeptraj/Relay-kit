---
name: ux-structure
description: Improve information hierarchy, flow clarity, and interaction quality in user-facing interfaces. Use when a hub needs concrete UX corrections tied to implementation reality.
version: 2.0.0
---

# UX Structure

Use this skill for practical UX correction, not style catalog dumping.

## When to Use

- Screen structure is confusing or inconsistent.
- User flow has friction or dead ends.
- Layout works visually but fails task clarity.
- UI review needs prioritized UX fixes.

## Output Contract

Return:
- Current UX issues by severity.
- Proposed structural changes.
- Accessibility and responsiveness checks.
- Implementation notes by file/component.

## Workflow

1. Identify user goal on the screen.
2. Check hierarchy, navigation, and action clarity.
3. Propose minimal structural edits first.
4. Validate with accessibility and responsive constraints.

## Scripts

- `python scripts/search.py --help`
- `python scripts/core.py --help`
- `python scripts/design_system.py --help`

## Guardrails

- Prioritize usability over visual novelty.
- Avoid generic card-heavy rewrites by default.
- Tie each UX recommendation to user impact.
