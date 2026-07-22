# protocol-fingerprint-spoofing Battle-Calibrated Output

Request: spoof TLS/HTTP protocol fingerprints to match specific clients and evade JA3/JA4/HTTP2 fingerprinting

Recommended skill: `protocol-fingerprint-spoofing` because the request matches `protocol-spoofer` work and has concrete repo anchors.

Read first:

- `relay_kit_v3/registry/skills.py`

Evidence gathered:

- Confirmed `ja3_hash` or nearby ownership before recommending changes.
- Checked `JA3 fingerprint` and `JA4` against the relevant source path.
- Identified `cipher suite order` as a required proof term before completion.

Answer:

The safe next move is to inspect the named file path, compare it with the expected test or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `HTTP/2 settings` remains unverified until the focused gate or benchmark hit is captured.
