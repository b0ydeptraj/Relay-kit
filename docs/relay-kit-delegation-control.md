# Relay-kit Delegation Control

`delegation-control` prevents unnecessary subagent spawning and makes approved delegation quota-aware and evidence-driven.

## Defaults

- Normal reasoning tier: `medium`.
- Use `low` only for mechanical, unambiguous, low-risk work with known verification.
- Use `high` for architecture, security, migration, production, and root-cause work.
- Maximum concurrent subagents: `2`.
- Each delegated lane gets a task-specific context pack.
- Completed agents close only after handoff evidence is recorded.

## Commands

```powershell
relay-kit delegation plan . --task "implement a bounded change" --complexity L2 --independent --artifact src/module.py --lock-scope src/module.py --expected-return-condition "tests pass" --verification-command "python -m pytest tests/test_module.py -q" --apply --json
relay-kit delegation audit . --strict --json
relay-kit delegation close-completed . --json
relay-kit delegation capabilities . --adapter all --json
```

Adapter capability reports distinguish `advisory`, `enforced`, and `unsupported`. Relay-kit does not claim a cross-adapter spawn or close control when the active runtime does not expose one.
