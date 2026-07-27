# technical-writing Battle-Calibrated Output

Request: handle a technical-writing request, name files first, and identify the proof surface before editing

Recommended skill: `technical-writing` because the request matches `docs-author` work and has concrete repo anchors.

Read first:

- `README.md`
- `src/cli.py`
- `examples/quickstart.py`

Evidence gathered:

- Confirmed `main` ownership before recommending changes.
- Checked `verified command` and `audience` against the relevant source path.
- Identified `quickstart` as a required proof term before completion.

Answer:

The safe next move is to inspect the named path, compare it with the expected test, metric, config, or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `source of truth` remains unverified until the focused gate or proof surface is captured.
