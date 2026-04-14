---
name: handoff-context
description: Build a compact handoff context package for the next hub or specialist. Use when work changes owner, lane, or thread and continuity quality matters.
version: 2.0.0
---

# Handoff Context

This skill creates high-signal context packs that minimize restart cost.

## When to Use

- Lane ownership changes.
- Work moves to another hub/specialist.
- A new thread must continue existing work.
- You need to compress context without losing decisions.

## Required Input

- Current objective.
- Done vs pending.
- Decisions and constraints.
- Evidence links (tests, logs, files).
- Next expected action.

## Output Contract

Produce a handoff block with:
- Scope and ownership.
- Current state summary.
- Decision register (why).
- Open risks/blockers.
- Immediate next step and acceptance check.

## Workflow

1. Collect authoritative artifacts first.
2. Remove stale or duplicate context.
3. Compress to the smallest useful package.
4. Verify the receiver can execute next step without backtracking.

## Scripts

- `python scripts/context_analyzer.py`
- `python scripts/compression_evaluator.py`

## References

- `references/context-fundamentals.md`
- `references/context-degradation.md`
- `references/context-optimization.md`
- `references/context-compression.md`
- `references/memory-systems.md`
- `references/multi-agent-patterns.md`
- `references/evaluation.md`
- `references/tool-design.md`
- `references/project-development.md`

## Guardrails

- Prefer artifact links over chat recap.
- Keep claims evidence-backed.
- If uncertainty remains, call it out explicitly.
