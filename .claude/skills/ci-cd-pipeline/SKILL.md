---
name: ci-cd-pipeline
description: Use when designing or fixing build, test, and deploy automation: pipeline stages, caching, required gates, environment promotion, artifact versioning, and rollback triggers.
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Design a deterministic, fail-closed delivery pipeline where every merge is gated by reproducible checks and every deploy has a defined rollback.

## Mandatory scope
1. Map stages: build, unit, integration, security scan, package, deploy — and which are blocking gates.
2. Reproducibility: pinned toolchain, cached dependencies keyed by lockfile hash, deterministic build.
3. Required gates: no merge to protected branch without passing gates and required reviews.
4. Environment promotion: artifact built once, promoted across environments — never rebuilt per env.
5. Rollback: a defined trigger, a tested rollback path, and a versioned previous artifact.

## Evidence contract
- stage list with blocking vs non-blocking marked
- cache key and toolchain pin declared
- protected-branch gate rules stated
- rollback trigger and path written

## Role
- cicd-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- existing CI config
- build and test commands
- deploy target and environments

## Outputs
- .relay-kit/references/ci-cd.md
- pipeline config changes
- rollback runbook

## Reference skills and rules
- Fail closed — a missing or errored gate blocks, it does not warn-and-pass.
- Build the artifact once and promote it; do not rebuild per environment.
- Every deploy path must have a tested rollback.
- Pin the toolchain; floating versions break reproducibility.
- Open `references/ci-cd-pipeline-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/ci-cd-pipeline-good-output.md` and `examples/ci-cd-pipeline-bad-output.md` to calibrate output quality.
- Use `evals/ci-cd-pipeline-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/ci-cd-pipeline-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- release-readiness
- dependency-management
- secure-code-review
- incident-response
