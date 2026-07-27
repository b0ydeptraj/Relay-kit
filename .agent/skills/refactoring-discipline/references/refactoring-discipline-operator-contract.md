# refactoring-discipline Battle Contract

Primary role: refactor-discipline
Layer: layer-4-specialists-and-standalones
Battle family: engineering

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: repo with a tangled module, a passing unit suite, and duplicated logic across files
- First files to inspect:
  - src/orders/service.py
  - src/orders/legacy.py
  - tests/orders/test_service.py
- Symbols or named surfaces to confirm: OrderService, calculate_total, apply_discount
- Evidence terms that should appear in a strong answer: green test net, characterization test, behavior preserved, atomic commit

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Refactoring against a red or absent test suite.
- Mixing a behavior change into a refactor commit.
- Running tests only at the end and losing the failing step.
- Silently altering the public contract.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
