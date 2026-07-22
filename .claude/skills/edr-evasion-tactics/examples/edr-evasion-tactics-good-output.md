# edr-evasion-tactics Battle-Calibrated Output

Request: evade EDR detection through unhooking, direct syscalls, callback manipulation, and ETW blinding

Recommended skill: `edr-evasion-tactics` because the request matches `edr-evasion-specialist` work and has concrete repo anchors.

Read first:

- `relay_kit_v3/registry/skills.py`

Evidence gathered:

- Confirmed `syscall_stub` or nearby ownership before recommending changes.
- Checked `userland hook` and `direct syscall` against the relevant source path.
- Identified `ETW patch` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `callback removal` remains unverified until the focused gate or benchmark hit is captured.
