# technical-writing Battle Contract

Primary role: docs-author
Layer: layer-4-specialists-and-standalones
Battle family: docs

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: repo with a CLI or library, an outdated README, and example scripts
- First files to inspect:
  - README.md
  - src/cli.py
  - examples/quickstart.py
- Symbols or named surfaces to confirm: main, install, run
- Evidence terms that should appear in a strong answer: verified command, audience, quickstart, source of truth

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Documenting a flag or command that does not exist in the code.
- Blending audiences so no reader finds their task.
- Inventing behavior to fill a gap instead of labeling the unknown.
- Leaving no note on how the doc stays current.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
