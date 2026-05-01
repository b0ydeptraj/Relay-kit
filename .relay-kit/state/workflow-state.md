# workflow-state

## Current request
Expand workflow eval scenario coverage from 20 to 28 production/team routes and refresh the upgrade note with the new progress position.

## Active lane
- Lane id: primary
- Mode: serial
- Lane owner: Codex

## Active orchestration
- Layer-1 orchestrator: workflow-router
- Layer-2 workflow hub: test-hub
- Active specialist: developer

## Active utility providers
- Primary utility provider: skill-gauntlet
- Additional utilities in play: evidence-before-completion

## Active standalone/domain skill
- Skill: developer
- Why selected: this is a bounded eval fixture, test expectation, and documentation update.

## Complexity level
- Level: L2
- Reasoning: this pass changes bundled eval fixtures and tests, then verifies routing quality through eval, doctor, readiness, and runtime gates.

## Chosen track
- Track: enterprise-flow
- Why this track fits: bundled eval coverage affects commercial readiness signals and should be verified with the same gates used for paid/team claims.

## Completed artifacts
- [ ] product-brief
- [ ] PRD
- [ ] architecture
- [ ] epics
- [ ] story
- [ ] tech-spec
- [ ] investigation-notes
- [x] project-context
- [x] qa-report
- [x] team-board
- [x] lane-registry
- [x] handoff-log

## Ownership locks
| Artifact | Owner lane | Lock scope | Status |
|---|---|---|---|
| none | none | none | none |

## Next skill
qa-governor

## Known blockers
Package upload, marketplace publication, and legal SLA commitments remain external release actions outside the local repo gates.

## Escalation triggers noticed
Future work that changes package metadata, release artifacts, trusted manifest data, readiness gates, CI gates, or support diagnostics should remain on an enterprise-flow path.

## Current source of truth
- Published release: https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0.
- Published tag commit: `d46f9c934805010cbf64fca00c28c6bc9dc233a9`.
- Current mainline package version: `3.4.0.dev0`.
- Latest confirmed main CI: https://github.com/b0ydeptraj/Relay-kit/actions/runs/25216531367, conclusion `success`.
- PR #1 merged release readiness and package smoke gates: https://github.com/b0ydeptraj/Relay-kit/pull/1.
- PR #2 merged Relay OTLP signal export: https://github.com/b0ydeptraj/Relay-kit/pull/2.
- PR #3 merged next-dev version hygiene: https://github.com/b0ydeptraj/Relay-kit/pull/3.
- PR #5 merged OTLP readiness/support evidence: https://github.com/b0ydeptraj/Relay-kit/pull/5.
- PR #6 merged CI action hardening: https://github.com/b0ydeptraj/Relay-kit/pull/6.
- PR #7 merged publication plan gate: https://github.com/b0ydeptraj/Relay-kit/pull/7.
- PR #8 merged backlog note hygiene: https://github.com/b0ydeptraj/Relay-kit/pull/8.
- PR #9 merged Pulse publication dashboard: https://github.com/b0ydeptraj/Relay-kit/pull/9.
- PR #10 merged post-dashboard state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/10.
- PR #11 merged publication execution evidence: https://github.com/b0ydeptraj/Relay-kit/pull/11.
- PR #12 merged post-publication-evidence state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/12.
- PR #13 merged publication trail hardening: https://github.com/b0ydeptraj/Relay-kit/pull/13.
- PR #15 merged support request intake: https://github.com/b0ydeptraj/Relay-kit/pull/15.
- PR #16 merged post-support-request state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/16.
- PR #17 merged support request Pulse/signal visibility: https://github.com/b0ydeptraj/Relay-kit/pull/17.
- PR #18 merged post-support-Pulse state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/18.
- PR #19 merged support bundle request-summary diagnostics: https://github.com/b0ydeptraj/Relay-kit/pull/19.
- PR #20 merged post-support-bundle state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/20.
- PR #21 merged workflow eval layer/role coverage signals: https://github.com/b0ydeptraj/Relay-kit/pull/21.
- PR #22 merged post-workflow-eval state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/22.
- PR #23 merged publication trail status: https://github.com/b0ydeptraj/Relay-kit/pull/23.
- PR #24 merged post-publication-status state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/24.
- PR #25 merged readiness pytest output hygiene: https://github.com/b0ydeptraj/Relay-kit/pull/25.
- PR #26 merged post-readiness-output state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/26.
- PR #27 merged support triage readiness gate: https://github.com/b0ydeptraj/Relay-kit/pull/27.
- PR #28 merged post-support-triage state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/28.
- PR #29 merged Pulse gate summary: https://github.com/b0ydeptraj/Relay-kit/pull/29.
- PR #30 merged post-Pulse-gate-summary state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/30.
- PR #31 merged Pulse gate drilldowns: https://github.com/b0ydeptraj/Relay-kit/pull/31.
- PR #32 merged post-Pulse-drilldowns state refresh: https://github.com/b0ydeptraj/Relay-kit/pull/32.
- PR #17 verification: `python -m pytest -q --basetemp=.tmp\pytest-support-request-pulse-full`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, `python scripts\runtime_doctor.py . --strict --state-mode live`, and `python relay_kit_public_cli.py readiness check . --profile enterprise --json` passed before merge.
- PR #19 verification: `python -m pytest -q --basetemp=.tmp\pytest-support-bundle-request-summary-full`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, `python scripts\runtime_doctor.py . --strict --state-mode live`, and `python relay_kit_public_cli.py readiness check . --profile enterprise --json` passed before merge.
- PR #21 verification: `python -m pytest -q --basetemp=.tmp\pytest-workflow-eval-coverage-full`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, `python scripts\runtime_doctor.py . --strict --state-mode live`, `python scripts\eval_workflows.py . --strict --json`, and `python relay_kit_public_cli.py readiness check . --profile enterprise --json` passed before merge.
- PR #23 verification: `python -m pytest -q --basetemp=.tmp\pytest-publication-status-full-2`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, `python scripts\runtime_doctor.py . --strict --state-mode live`, `python relay_kit_public_cli.py publish status . --json`, and `python relay_kit_public_cli.py readiness check . --profile enterprise --json` passed before merge.
- PR #25 verification: `python -m pytest -q --basetemp=.tmp\pytest-readiness-basetemp-full`, `python relay_kit_public_cli.py readiness check . --profile enterprise --json`, and `python scripts\runtime_doctor.py . --strict --state-mode live` passed before merge.
- PR #27 verification: `python -m pytest tests\test_support_triage.py tests\test_support_bundle.py tests\test_support_request.py -q --basetemp=.tmp\pytest-support-triage-green-3`, `python -m pytest -q --basetemp=.tmp\pytest-support-triage-full`, `python relay_kit_public_cli.py support triage . --json`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, `python scripts\runtime_doctor.py . --strict --state-mode live`, and `python relay_kit_public_cli.py readiness check . --profile enterprise --json` passed before merge.
- Pulse gate summary branch verification: `python -m pytest tests\test_pulse_report.py tests\test_signal_export.py -q --basetemp=.tmp\pytest-pulse-gate-summary-green`, `python -m pytest -q --basetemp=.tmp\pytest-pulse-gate-summary-full`, `python relay_kit_public_cli.py pulse build . --include-readiness --include-publication --include-support-request --json --no-history`, `python relay_kit_public_cli.py signal export . --otlp --json`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, `python scripts\runtime_doctor.py . --strict --state-mode live`, and `python relay_kit_public_cli.py readiness check . --profile enterprise --json` passed locally.
- PR #29 main CI: https://github.com/b0ydeptraj/Relay-kit/actions/runs/25215207136, conclusion `success`.
- Pulse gate drilldown branch verification: `python -m pytest tests\test_pulse_report.py tests\test_signal_export.py -q --basetemp=.tmp\pytest-pulse-drilldowns-green-2`, `python -m pytest -q --basetemp=.tmp\pytest-pulse-drilldowns-full-2`, `python relay_kit_public_cli.py pulse build . --include-readiness --include-publication --include-support-request --no-history`, `python relay_kit_public_cli.py signal export . --otlp --json`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, `python scripts\runtime_doctor.py . --strict --state-mode live`, and `python relay_kit_public_cli.py readiness check . --profile enterprise --json` passed locally.
- PR #31 main CI: https://github.com/b0ydeptraj/Relay-kit/actions/runs/25216356829, conclusion `success`.
- Eval scenario expansion branch verification: `python -m pytest tests\test_workflow_eval.py -q --tb=short -p no:cacheprovider`, `python scripts\eval_workflows.py . --strict --json`, `python -m pytest -q`, `python scripts\validate_runtime.py`, `python relay_kit_public_cli.py doctor . --skip-tests --policy-pack enterprise`, `python scripts\runtime_doctor.py . --strict --state-mode live`, `python relay_kit_public_cli.py readiness check . --profile enterprise --json`, `python relay_kit_public_cli.py pulse build . --include-readiness --include-publication --include-support-request --no-history`, and `python relay_kit_public_cli.py signal export . --otlp --json` passed locally; signal export reports `relay.workflow.scenario_count=28`.
- Current feature branch: `codex/eval-scenario-expansion-v2`.
- Current main baseline: `19f24493e300c42eefe8bc01e10aef8a8a755902`.

## Recommended next lane
Complete eval scenario expansion, then continue support operations soak and broader dashboard/eval polish.
