# Relay-kit beta soak log

Track real-project soak checkpoints before broader rollout.

## Required run shape

- Run on at least 2 real target projects.
- Use canonical command path (`relay_kit.py` / public `relay-kit`).
- Keep the same baseline bundle across runs (`baseline`).
- Record pass/fail and missing output directories.

## Recommended command

```bash
python scripts/soak_beta.py /path/to/project-a /path/to/project-b --append-report --json
```

## Pass criteria for Beta gate

- 0 failed projects in a checkpoint run.
- Each project has all runtime outputs:
  - `.claude/skills`
  - `.agent/skills`
  - `.codex/skills`
  - `.relay-kit/contracts`
  - `.relay-kit/state`
  - `.relay-kit/docs`
  - `.relay-kit/references`
- `scripts/validate_runtime.py` still passes at repo root after soak.
