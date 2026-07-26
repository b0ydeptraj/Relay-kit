# incident-response Battle Contract

Primary role: incident-responder
Layer: layer-4-specialists-and-standalones
Battle family: reliability

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: production service with alerting, deploy history, and dashboards during an active latency/error spike
- First files to inspect:
  - ops/runbooks/latency.md
  - src/server/handlers.py
  - deploy/history.log
- Symbols or named surfaces to confirm: rollback, feature_flag, health_check
- Evidence terms that should appear in a strong answer: severity, mitigation, timeline, blameless postmortem

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Debugging root cause while users are still impacted instead of mitigating first.
- Communicating hypotheses as confirmed fact.
- Writing a postmortem that assigns blame instead of finding systemic factors.
- Producing action items with no owner or date.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
