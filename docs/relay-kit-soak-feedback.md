# Relay-kit soak feedback tool

Use this tool during the soak cycle to capture real usage issues and summarize what should be improved next.

Script path:
- `scripts/soak_feedback.py`

Data store:
- `.ai-kit/state/soak-feedback.jsonl`

## Add one feedback item

```bash
python scripts/soak_feedback.py add . --source user --area runtime --severity p1 --summary "antigravity install path failed on clean machine" --evidence "run-relay-kit-phase2-gate.cmd output"
```

## Update status after triage or fix

```bash
python scripts/soak_feedback.py update . --id fb-20260401103000-abc123 --status resolved --commit 1a2b3c4 --note "fixed in public cli parser"
```

## Summary for daily review

```bash
python scripts/soak_feedback.py summary . --status all --limit 10
```

JSON output:

```bash
python scripts/soak_feedback.py summary . --status open --json
```
