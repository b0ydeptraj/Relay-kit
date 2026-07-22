# cpp-systems-engineering Battle-Calibrated Output

Request: implement systems-level C++ for kernel drivers, DLL injection, memory manipulation, and Win32/NT API integration

Recommended skill: `cpp-systems-engineering` because the request matches `cpp-specialist` work and has concrete repo anchors.

Read first:

- `relay_kit_v3/registry/skills.py`

Evidence gathered:

- Confirmed `NtApi` or nearby ownership before recommending changes.
- Checked `Win32 API` and `NT internals` against the relevant source path.
- Identified `memory layout` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `calling convention` remains unverified until the focused gate or benchmark hit is captured.
