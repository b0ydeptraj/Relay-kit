# secure-code-review Battle-Calibrated Output

Request: handle a secure-code-review request, name files first, and identify the proof surface before editing

Recommended skill: `secure-code-review` because the request matches `security-reviewer` work and has concrete repo anchors.

Read first:

- `src/api/handlers.py`
- `src/db/queries.py`
- `src/auth/middleware.py`
- `requirements.txt`

Evidence gathered:

- Confirmed `build_query` ownership before recommending changes.
- Checked `tainted input` and `injection sink` against the relevant source path.
- Identified `object-level authorization` as a required proof term before completion.

Answer:

The safe next move is to inspect the named path, compare it with the expected test, metric, config, or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `severity` remains unverified until the focused gate or proof surface is captured.
