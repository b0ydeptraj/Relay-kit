# process-injection-techniques Battle-Calibrated Output

Request: implement process injection techniques including DLL injection, process hollowing, APC injection, and thread hijacking

Recommended skill: `process-injection-techniques` because the request matches `injection-specialist` work and has concrete repo anchors.

Read first:

- `relay_kit_v3/registry/skills.py`

Evidence gathered:

- Confirmed `inject_dll` or nearby ownership before recommending changes.
- Checked `DLL injection` and `process hollowing` against the relevant source path.
- Identified `APC queue` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `thread context` remains unverified until the focused gate or benchmark hit is captured.
