# Deep checkpoint issue tracker (2026-04-18)

This note tracks weak points discovered during deep checkpoints and whether each item is fixed.

## Scope

- Runtime core / gating behavior
- SRS branch stress coverage
- Soak policy closure criteria
- Diagnostic signal quality (`runtime_doctor`)

## Status summary

- Runtime doctor false-positive: **fixed in code**
- SRS hard-mode coverage gap: **fixed in tests (sandbox lane)**
- 1-week soak governance closure: **closed early (override approved 2026-04-22)**

## Detail

1. `runtime_doctor --state-mode live` too strict for baseline projects
- Previous symptom: reported missing discipline skills (`srs-clarifier`, `test-first-development`) + `TBD` placeholders as hard findings.
- Fix applied:
  - bundle-aware expected skill surface (`--bundle auto` detection)
  - configurable live placeholder policy (`--state-placeholder-mode ignore|warn|strict`, default `warn`)
  - extra-skill policy separated from required-surface checks (`--disallow-extra-skills`)
- Current status: **resolved**
- Verification:
  - `tests/test_runtime_doctor.py`

2. `srs_guard` skipped in default policy (`enabled=false`, `gate=off`)
- Previous gap: no hard-mode stress for SRS branch in default gate run.
- Fix applied:
  - added sandbox hard-mode lane test (negative then positive) without changing production policy.
- Current status: **resolved for test coverage**
- Verification:
  - `tests/test_srs_guard_hard_mode.py`

3. P3-B asks for full 1-week soak window
- Previous state: deep checkpoints were green, but governance close criteria required a full 1-week window.
- Evidence at close time (2026-04-22): deep checkpoint `30/30` pass on `2026-04-19`, `2026-04-20`, `2026-04-21`, `2026-04-22`, and startup batch pass on `2026-04-21` and `2026-04-22`.
- Decision applied on `2026-04-22`: official **early-close override** with no further core-runtime changes required.
- Current status: **closed (governance override)**
- Re-open trigger:
  - any future deep checkpoint failure in `gate-suite`, `matrix`, `soak-real`, `public-cli`, or `context-continuity` flow.

## Evidence references

- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260418-103955.json`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260418-103955.md`
- `D:\relay-kit-checkpoint\logs\startup-deep-checkpoint-batch-20260418-104021.json`
- `D:\relay-kit-checkpoint\logs\startup-deep-checkpoint-batch-20260418-104021.md`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260418-140831.json`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260418-140831.md`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260419-081022.json`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260420-133038.json`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260421-125254.json`
- `D:\relay-kit-checkpoint\logs\deep-checkpoint-30-20260422-142257.json`
- `D:\relay-kit-checkpoint\logs\startup-deep-checkpoint-batch-20260421-125034.json`
- `D:\relay-kit-checkpoint\logs\startup-deep-checkpoint-batch-20260422-142256.json`
- `docs/release-gate-early-close-2026-04-22.md`
