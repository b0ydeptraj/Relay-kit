# privacy-compliance Battle-Calibrated Output

Request: review what personal data a feature collects, justify each field, and name the retention and deletion path

Recommended skill: `privacy-compliance` because the request matches `privacy-reviewer` work and has concrete repo anchors.

Read first:

- `src/models/user.py`
- `src/signup/form.py`
- `jobs/retention.py`

Evidence gathered:

- Confirmed `User` and its `PII classification` before recommending changes.
- Checked `lawful basis` against `src/signup/form.py` as the proof surface.
- Identified `retention window` as a required proof term before completion.

Answer:

Inspect the named paths, compare them against the expected privacy proof surface, and only then recommend a change. If an anchor is missing, ask one question that names the missing file, config, or policy.

Residual risk:

- `deletion path` remains unverified until the focused gate for this domain is captured.
