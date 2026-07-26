# Relay-kit skill upgrade — how to apply

This archive mirrors your relay-kit folder structure. It contains:
- `.claude/skills/...`  : 3 fixed benign skills (support files) + 8 NEW skills, each with SKILL.md + references/evals/examples/competencies
- 6 entrypoint `SKILL.md` with the UTF-8 BOM removed (build-it, debug-systematically, ready-check, review-pr, start-here, write-steps)
- `skills.manifest.yaml` : updated to register the new skills (already applied to your disk)
- `_apply_skill_upgrade.py` : the re-runnable generator (optional)

## Option A — extract (simplest)
Extract this zip INTO your relay-kit root:
  C:\Users\b0ydeptrai\Documents\relay-kit
Choose "replace files in destination" when Windows asks. Done.

## Option B — run the generator (if you have Python)
From the relay-kit root:
  python _apply_skill_upgrade.py .
It is idempotent: BOM fix + support files + manifest. Safe to re-run.

## New skills added
secure-code-review, observability-instrumentation, ci-cd-pipeline,
performance-optimization, technical-writing, refactoring-discipline,
database-migration-safety, incident-response
