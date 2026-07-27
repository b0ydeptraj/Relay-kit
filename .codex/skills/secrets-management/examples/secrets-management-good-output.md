# secrets-management Battle-Calibrated Output

Request: review how a credential is stored, injected, scoped, and rotated, and name the leak-response path

Recommended skill: `secrets-management` because the request matches `secrets-engineer` work and has concrete repo anchors.

Read first:

- `config/settings.py`
- `infra/secrets_client.py`
- `docs/secret-policy.md`

Evidence gathered:

- Confirmed `get_secret` and its `vaulted secret` before recommending changes.
- Checked `least privilege` against `infra/secrets_client.py` as the proof surface.
- Identified `rotation window` as a required proof term before completion.

Answer:

Inspect the named paths, compare them against the expected secrets proof surface, and only then recommend a change. If an anchor is missing, ask one question that names the missing file, config, or policy.

Residual risk:

- `leak response` remains unverified until the focused gate for this domain is captured.
