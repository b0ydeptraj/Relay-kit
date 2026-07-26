---
name: refactoring-discipline
description: Use when restructuring code without changing behavior: extract, rename, split, or de-duplicate under a green test suite with small reversible steps and a characterization safety net.
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Change structure while proving behavior is preserved: lean on a green test net, move in small reversible steps, and keep commits atomic.

## Mandatory scope
1. Confirm a passing test net covers the target; if coverage is thin, add characterization tests first.
2. Separate refactor commits from behavior-change commits — never mix them.
3. Move in small reversible steps; run tests after each step.
4. Preserve the public contract (signatures, outputs, side effects) unless the task is explicitly to change it.
5. State the risk if the safety net is incomplete, and what is unverified.

## Evidence contract
- test net status before and after (green -> green)
- characterization tests added when coverage was thin
- refactor and behavior changes kept in separate commits
- public contract confirmed unchanged (or the change called out)

## Role
- refactor-discipline

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target code / smell
- existing test suite
- behavior-preservation requirement

## Outputs
- refactored code
- added characterization tests if needed
- commit plan separating refactor from behavior

## Reference skills and rules
- No refactor without a green test net — add characterization tests first if needed.
- Never mix a refactor with a behavior change in one commit.
- Run the suite after each small step, not only at the end.
- If behavior must change, that is not a refactor — route to the developer loop.
- Open `references/refactoring-discipline-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/refactoring-discipline-good-output.md` and `examples/refactoring-discipline-bad-output.md` to calibrate output quality.
- Use `evals/refactoring-discipline-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/refactoring-discipline-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- test-first-development
- developer
- review-hub
- testing-patterns
