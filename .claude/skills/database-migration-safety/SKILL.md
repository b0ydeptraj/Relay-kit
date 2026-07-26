---
name: database-migration-safety
description: Use when a schema or data migration touches a live database: expand/contract sequencing, backfills, index builds, lock analysis, and a tested rollback for zero-downtime changes.
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Ship schema and data changes without downtime or data loss by sequencing expand-before-contract, analyzing locks, and proving a rollback.

## Mandatory scope
1. Classify the change: additive (safe), rewriting (locking), or destructive (irreversible) — and treat each accordingly.
2. Sequence expand/contract: add new columns/tables and dual-write before removing old ones across separate deploys.
3. Analyze locking: check whether the migration takes a blocking lock on a hot table and prefer concurrent/online paths.
4. Backfill safely: batch large backfills, throttle, and make them resumable and idempotent.
5. Provide a tested rollback or forward-fix, and confirm a backup/point-in-time exists before destructive steps.

## Evidence contract
- change classified (additive/rewriting/destructive)
- expand-contract sequencing described across deploys
- lock impact on hot tables assessed
- rollback/forward-fix and backup confirmation stated

## Role
- db-migration-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- migration script / schema diff
- table size and traffic profile
- deploy and rollback process

## Outputs
- .relay-kit/references/db-migration.md
- sequenced migration plan
- rollback and backfill runbook

## Reference skills and rules
- Never drop or rewrite before the new path is deployed and dual-writing.
- Avoid blocking locks on hot tables — use concurrent/online migration paths.
- Backfills must be batched, throttled, resumable, and idempotent.
- No destructive step without a confirmed backup and a rollback plan.
- Open `references/database-migration-safety-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/database-migration-safety-good-output.md` and `examples/database-migration-safety-bad-output.md` to calibrate output quality.
- Use `evals/database-migration-safety-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/database-migration-safety-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- data-persistence
- release-readiness
- ci-cd-pipeline
- incident-response
