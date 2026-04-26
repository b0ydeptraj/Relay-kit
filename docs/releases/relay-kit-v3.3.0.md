# Relay-kit v3.3.0 Release Evidence

Date: 2026-04-26
Commit: d717898ed216bdb0c0655f68478c02557b169a3f
PR: https://github.com/b0ydeptraj/Relay-kit/pull/1
GitHub Actions: https://github.com/b0ydeptraj/Relay-kit/actions/runs/24953893415

## Verdict

Local release lane: pass.
Enterprise readiness: commercial-ready-candidate.
GitHub Actions Validate Runtime: success.

## Major Changes

- Real root pytest/runtime proof and CI expansion.
- Clean ai-kit to relay-kit namespace cutover with compatibility shim.
- Semantic skill gauntlet and workflow eval expanded to 20 scenarios.
- Policy guard, SRS opt-in guard, strict release/a11y evidence gates.
- Evidence ledger, Pulse report/history, and signal export.
- Readiness check requires signal export and release-lane gates.
- Support bundle includes signal export and release-lane diagnostics.
- Release-lane verification, wheel build smoke, and package install smoke.
- Contract export/import, support/SLA docs, trusted manifest, and upgrade CLI.

## Evidence Commands

- `python -m pytest -q --basetemp=.tmp\pytest-release-v3-3-0` -> 123 passed.
- `python scripts\validate_runtime.py` -> pass.
- `python scripts\migration_guard.py . --strict` -> findings: 0.
- `python scripts\package_smoke.py . --json` -> pass.
- `python relay_kit_public_cli.py release verify . --require-clean --json` -> pass.
- `python relay_kit_public_cli.py readiness check . --profile enterprise --json` -> commercial-ready-candidate.
- `python scripts\release_readiness.py . --phase pre --signals-file .tmp\release-v3.3.0-signals.json --strict --json` -> pass.
- GitHub Actions `Validate Runtime` run `24953893415` -> success.

## Residual Risks

- GitHub release is draft until explicitly published.
- Package upload or marketplace publication is not performed by this release note.
- Paid support operations are documented and diagnostically supported, but not a legal SLA.

## Rollback

- Do not publish the draft release if remote CI or local release gates fail.
- If a published release regresses, delete or supersede tag `v3.3.0`, restore main to prior stable commit `4fd2faa231709ab716f14c5505b84a9a8e904ace`, and rerun `relay-kit release verify`.
