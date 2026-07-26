# secure-code-review Battle Contract

Primary role: security-reviewer
Layer: layer-3-utility-providers
Battle family: security-defense

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: web service repo with HTTP handlers, a database layer, auth middleware, and a dependency lockfile
- First files to inspect:
  - src/api/handlers.py
  - src/db/queries.py
  - src/auth/middleware.py
  - requirements.txt
- Symbols or named surfaces to confirm: build_query, require_auth, current_user
- Evidence terms that should appear in a strong answer: tainted input, injection sink, object-level authorization, severity

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Flagging on keyword match without tracing input to a real sink.
- Passing a review while a critical injection or broken-authz path is open.
- Missing object-level authorization because authentication was present.
- Ignoring known-vulnerable dependency versions in the lockfile.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
