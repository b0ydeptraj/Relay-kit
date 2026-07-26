# database-migration-safety Battle Contract

Primary role: db-migration-specialist
Layer: layer-4-specialists-and-standalones
Battle family: data

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: app repo with an ORM, a migrations directory, and a large hot table in production
- First files to inspect:
  - migrations/0042_add_status.sql
  - src/db/models.py
  - src/db/backfill.py
- Symbols or named surfaces to confirm: add_column, backfill_status, create_index_concurrently
- Evidence terms that should appear in a strong answer: expand contract, blocking lock, backfill batch, rollback

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Dropping or renaming a column before the new code path ships.
- Taking a blocking lock on a hot table during peak traffic.
- Running an unbatched backfill that saturates the database.
- Executing a destructive migration with no backup or rollback.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
