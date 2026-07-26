# incident-response Battle-Calibrated Output

Request: handle a incident-response request, name files first, and identify the proof surface before editing

Recommended skill: `incident-response` because the request matches `incident-responder` work and has concrete repo anchors.

Read first:

- `ops/runbooks/latency.md`
- `src/server/handlers.py`
- `deploy/history.log`

Evidence gathered:

- Confirmed `rollback` ownership before recommending changes.
- Checked `severity` and `mitigation` against the relevant source path.
- Identified `timeline` as a required proof term before completion.

Answer:

The safe next move is to inspect the named path, compare it with the expected test, metric, config, or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `blameless postmortem` remains unverified until the focused gate or proof surface is captured.
