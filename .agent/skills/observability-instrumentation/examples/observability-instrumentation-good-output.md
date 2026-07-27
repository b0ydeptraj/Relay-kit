# observability-instrumentation Battle-Calibrated Output

Request: handle a observability-instrumentation request, name files first, and identify the proof surface before editing

Recommended skill: `observability-instrumentation` because the request matches `observability-specialist` work and has concrete repo anchors.

Read first:

- `src/server/handlers.py`
- `src/telemetry/metrics.py`
- `config/logging.yaml`

Evidence gathered:

- Confirmed `request_id` ownership before recommending changes.
- Checked `RED metrics` and `correlation id` against the relevant source path.
- Identified `SLO` as a required proof term before completion.

Answer:

The safe next move is to inspect the named path, compare it with the expected test, metric, config, or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `burn rate` remains unverified until the focused gate or proof surface is captured.
