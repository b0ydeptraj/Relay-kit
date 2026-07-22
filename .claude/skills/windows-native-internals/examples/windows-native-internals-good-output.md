# windows-native-internals Battle-Calibrated Output

Request: work with Windows NT internals including undocumented APIs, PEB/TEB structures, kernel objects, and system information classes

Recommended skill: `windows-native-internals` because the request matches `windows-internals-specialist` work and has concrete repo anchors.

Read first:

- `relay_kit_v3/registry/skills.py`

Evidence gathered:

- Confirmed `PEB` or nearby ownership before recommending changes.
- Checked `PEB walk` and `TEB access` against the relevant source path.
- Identified `SYSTEM_INFORMATION_CLASS` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `kernel object` remains unverified until the focused gate or benchmark hit is captured.
