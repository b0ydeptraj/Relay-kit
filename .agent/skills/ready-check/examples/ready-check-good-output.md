# ready-check Battle-Calibrated Output

Request: make a real go or no-go readiness decision about code shipability

Recommended skill: `ready-check` because the request matches `specialist` work and has concrete repo anchors.

Read first:

- `relay_kit_v3/registry/skills.py`
- `relay_kit_public_cli.py`

Evidence gathered:

- Confirmed `qa_governor` or nearby ownership before recommending changes.
- Checked `go/no-go` and `readiness` against the relevant source path.
- Identified `acceptance criteria` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `verdict` remains unverified until the focused gate or benchmark hit is captured.
