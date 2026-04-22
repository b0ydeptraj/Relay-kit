# Relay-kit release gate early close (2026-04-22)

## Decision

- Date: `2026-04-22` (Asia/Bangkok)
- Decision: close governance gate early on the same day.
- Scope: close remaining policy-only blocker in deep-checkpoint issue tracker.
- Core runtime impact: none (no additional runtime code changes required).

## Why early close is accepted

- Latest deep checkpoint run on `2026-04-22` passed `30/30`.
- Startup deep checkpoint batch on `2026-04-22` passed `1/1`.
- Prior daily evidence remained green across `2026-04-19`, `2026-04-20`, and `2026-04-21`.
- Current repo checks remain green (`scripts/validate_runtime.py`, `pytest -q tests`).

## Evidence bundle

- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260419-081022.json`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260420-133038.json`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260421-125254.json`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260422-142257.json`
- `D:\relay-kit-checkpoint\logs\startup-deep-checkpoint-batch-20260421-125034.json`
- `D:\relay-kit-checkpoint\logs\startup-deep-checkpoint-batch-20260422-142256.json`

## Residual risk and reopen policy

- This is a governance override, not a proof that regressions are impossible.
- Reopen immediately if any future deep-checkpoint run fails in:
  - `gate-suite`
  - `matrix`
  - `soak-real`
  - `public-cli`
  - `context-continuity`

## Follow-up

- Keep daily startup deep checkpoint automation enabled.
- Keep appending checkpoint evidence to `docs/relay-kit-beta-soak-log.md`.
