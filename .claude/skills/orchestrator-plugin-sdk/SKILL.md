---
name: orchestrator-plugin-sdk
description: "Use when a lane needs orchestrator plugin sdk: Scaffold and validate new toolkit skills with the standard file layout, metadata, output contract, and orchestrator registration checklist."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Scaffold and validate new toolkit skills with the standard file layout, metadata, output contract, and orchestrator registration checklist.

# Orchestrator Plugin SDK

## Purpose

Use this skill when adding a new local skill to the toolkit or validating that an existing skill can be chained from the master orchestrator.

## Workflow

1. Scaffold a skill with `python orchestrator-plugin-sdk/scripts/scaffold_skill.py <name> --description "<description>"`.
2. Implement scripts and tests inside the generated directories.
3. Validate the contract with `python orchestrator-plugin-sdk/scripts/validate_skill_contract.py <skill-dir>`.
4. Register the skill in `scripts/orchestrate.py` only after its CLI and tests are stable.

## Role
- builder-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with orchestrator-plugin-sdk findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside orchestrator-plugin-sdk's scope back through `workflow-router` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/orchestrator-plugin-sdk-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/orchestrator-plugin-sdk-good-output.md` and `examples/orchestrator-plugin-sdk-bad-output.md` to calibrate output quality.
- Use `evals/orchestrator-plugin-sdk-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/orchestrator-plugin-sdk-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- orchestrator-plugin-sdk
- workflow-router
