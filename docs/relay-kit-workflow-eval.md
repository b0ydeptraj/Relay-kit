# Relay-kit Workflow Eval

`relay-kit eval run` turns bundled workflow scenarios into a machine-readable quality signal.

It is intentionally separate from `skill-gauntlet`:

- `skill-gauntlet --semantic` protects the runtime skill files from drift.
- `workflow eval` reports scenario pass rate, predicted skill, top routes, and missing evidence terms.

## Commands

```bash
relay-kit eval run /path/to/project --strict
relay-kit eval run /path/to/project --json --output-file workflow-eval.json
python scripts/eval_workflows.py . --strict
```

## Report Contract

The JSON report uses `schema_version=relay-kit.workflow-eval.v1` and includes:

- `status`
- `scenario_count`
- `passed`
- `failed`
- `pass_rate`
- `findings_count`
- per-scenario `expected_skill`
- per-scenario `predicted_skill`
- per-scenario `top_routes`
- per-scenario `missing_terms`

`--strict` returns exit code `2` when any scenario fails or the fixture file is missing/empty.

## Fixture Location

Bundled fixtures live at:

```text
relay_kit_v3/eval_fixtures/workflow_scenarios.json
```

Use `--scenario-fixtures <file>` to run a custom scenario suite.
