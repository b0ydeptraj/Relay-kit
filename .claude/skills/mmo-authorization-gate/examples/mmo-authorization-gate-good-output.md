# mmo-authorization-gate Battle-Calibrated Output

Request: gate an MMO lane by confirming account ownership and operator authorization before any high-risk action

Recommended skill: `mmo-authorization-gate` because the request matches `utility-provider` work and has concrete repo anchors.

Read first:

- `accounts/inventory.json`
- `policy/authorization-ledger.json`
- `policy/risk-tiers.json`

Evidence gathered:

- Confirmed `account_owner` and its `account ownership` before recommending changes.
- Checked `operator authorization` against `policy/authorization-ledger.json` as the proof surface.
- Identified `platform terms` as a required proof term before completion.

Answer:

Inspect the named paths, compare them against the expected mmo-authorization proof surface, and only then recommend a change. If an anchor is missing, ask one question that names the missing file, config, or policy.

Residual risk:

- `risk tier` remains unverified until the focused gate for this domain is captured.
