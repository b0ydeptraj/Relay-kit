# qa-report

> Path: `.relay-kit/contracts/qa-report.md`
> Purpose: Record acceptance coverage, risk review, regression impact, and remaining gaps before declaring work complete.
> Used by: qa-governor, developer, test-hub, review-hub

## Scope checked
Support operations soak branch `codex/support-operations-soak`.

Changed surfaces:
- `relay_kit_v3/support_triage.py`
- `relay_kit_v3/support_bundle.py`
- `relay_kit_public_cli.py`
- `docs/relay-kit-support-sla.md`
- `tests/test_support_triage.py`
- `tests/test_support_bundle.py`
- live state and upgrade backlog notes

## Acceptance coverage
- `relay-kit support soak` now runs P0/P1/P2 paid-support handoff fixtures.
- `relay-kit support triage` now fails degraded support bundle diagnostics instead of accepting schema-only bundles.
- Support bundle required command list includes `relay-kit support soak`.
- Support SLA docs name the soak command and escalation placement.

## Risk matrix
- Public CLI risk: low. New subcommand is additive under `relay-kit support soak`.
- Support triage/readiness strictness risk: medium. Triage and readiness now require manifest, policy, workflow eval, signal export, and release-lane diagnostics to be healthy in the bundle.
- Commercial evidence risk: low locally. External SLA/legal/package-index proof remains outside repo gates.

## Regression surface
- Support request, support bundle, support triage, readiness, Pulse, signal export, doctor, runtime doctor live mode.
- Generated support and signal artifacts remain under ignored `.relay-kit/support/` and `.relay-kit/signals/` paths.

## Evidence collected
- `python -m pytest tests/test_support_triage.py -q` passed: 6 passed.
- `python -m pytest tests/test_support_request.py tests/test_support_bundle.py tests/test_support_triage.py -q` passed: 17 passed.
- `python -m pytest tests/test_readiness_check.py tests/test_pulse_report.py tests/test_signal_export.py -q` passed: 24 passed before readiness support-bundle hardening.
- `python -m pytest tests/test_readiness_check.py tests/test_support_triage.py tests/test_support_bundle.py -q` passed: 20 passed after readiness support-bundle hardening.
- `python relay_kit_public_cli.py support bundle . --policy-pack enterprise` passed.
- `python relay_kit_public_cli.py support request . --severity P1 ... --strict` passed with status `ready`.
- `python relay_kit_public_cli.py support triage . --strict` passed with status `ready`.
- `python relay_kit_public_cli.py support soak . --strict` passed with P0/P1/P2 cases.
- `python -m pytest tests -q` passed: 160 passed.
- `python relay_kit_public_cli.py readiness check . --profile enterprise` passed with verdict `commercial-ready-candidate`.
- `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise` passed.
- `python scripts\runtime_doctor.py . --strict --state-mode live` passed with findings 0.

## Go / no-go recommendation
Go for PR. Remote CI still needs to pass after push/PR.
