# database-migration-safety Battle-Calibrated Output

Request: handle a database-migration-safety request, name files first, and identify the proof surface before editing

Recommended skill: `database-migration-safety` because the request matches `db-migration-specialist` work and has concrete repo anchors.

Read first:

- `migrations/0042_add_status.sql`
- `src/db/models.py`
- `src/db/backfill.py`

Evidence gathered:

- Confirmed `add_column` ownership before recommending changes.
- Checked `expand contract` and `blocking lock` against the relevant source path.
- Identified `backfill batch` as a required proof term before completion.

Answer:

The safe next move is to inspect the named path, compare it with the expected test, metric, config, or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `rollback` remains unverified until the focused gate or proof surface is captured.
