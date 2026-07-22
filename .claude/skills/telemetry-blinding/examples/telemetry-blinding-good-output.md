# telemetry-blinding Battle-Calibrated Output

Request: blind or suppress host telemetry including ETW, Sysmon, AMSI, and Windows event logging

Recommended skill: `telemetry-blinding` because the request matches `telemetry-specialist` work and has concrete repo anchors.

Read first:

- `relay_kit_v3/registry/skills.py`

Evidence gathered:

- Confirmed `etw_patch` or nearby ownership before recommending changes.
- Checked `ETW provider` and `Sysmon filter` against the relevant source path.
- Identified `AMSI patch` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `event log` remains unverified until the focused gate or benchmark hit is captured.
