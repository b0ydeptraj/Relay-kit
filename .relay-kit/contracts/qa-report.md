# qa-report

> Path: `.relay-kit/contracts/qa-report.md`
> Purpose: Record acceptance coverage, risk review, regression impact, and remaining gaps before declaring work complete.
> Used by: qa-governor, developer, test-hub, review-hub

## Scope checked
Workflow focus dashboard branch `codex/dashboard-eval-polish`.

Changed surfaces:
- `scripts/eval_workflows.py`
- `relay_kit_v3/pulse.py`
- `relay_kit_v3/signal_export.py`
- `docs/relay-kit-pulse-report.md`
- `docs/relay-kit-signal-export.md`
- `tests/test_workflow_eval.py`
- `tests/test_pulse_report.py`
- `tests/test_signal_export.py`
- live state and upgrade backlog notes

## Acceptance coverage
- Workflow eval reports `quality.weak_routes`, `weak_route_count`, and `coverage_gaps`.
- Pulse JSON includes `workflow_focus` with weak routes, coverage gaps, and next actions.
- Pulse HTML renders a Workflow focus section before gate summary.
- Signal export emits `relay.workflow.weak_route_count` and `relay.workflow.coverage_gap_count`.

## Risk matrix
- Eval schema risk: medium. Adds fields under `quality` without removing existing keys.
- Pulse dashboard risk: low. Adds a new section and cards while preserving current gate summary and drilldowns.
- Signal metric risk: low. Adds metrics and keeps existing metric names stable.
- Commercial evidence risk: low locally. External SLA/legal/package-index proof remains outside repo gates.

## Regression surface
- Workflow eval, Pulse report JSON/HTML, signal export JSON/JSONL/OTLP, support bundle summaries that include workflow eval, readiness signal export gate.
- Generated Pulse and signal artifacts remain under ignored `.relay-kit/pulse/` and `.relay-kit/signals/` paths.

## Evidence collected
- `python -m pytest tests/test_workflow_eval.py tests/test_pulse_report.py tests/test_signal_export.py -q` passed: 25 passed.
- `python scripts\eval_workflows.py . --strict --json` passed and reports 28 scenarios, weak route count 2, and no missing eval layers.
- `python relay_kit_public_cli.py pulse build . --include-readiness --include-publication --include-support-request --no-history` passed and wrote Pulse JSON/HTML.
- `python relay_kit_public_cli.py signal export . --otlp --json` passed and emits `relay.workflow.weak_route_count` plus `relay.workflow.coverage_gap_count`.
- `python -m pytest tests -q` passed: 160 passed.
- `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise` passed.
- `python scripts\runtime_doctor.py . --strict --state-mode live` passed with findings 0.
- `python relay_kit_public_cli.py readiness check . --profile enterprise` passed with verdict `commercial-ready-candidate`.

## Go / no-go recommendation
Go for PR. Remote CI still needs to pass after push/PR.
