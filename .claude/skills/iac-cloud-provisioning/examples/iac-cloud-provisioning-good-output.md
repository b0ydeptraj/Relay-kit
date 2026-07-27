# iac-cloud-provisioning Battle-Calibrated Output

Request: review an infrastructure change, read the plan diff, and flag any stateful replace before apply

Recommended skill: `iac-cloud-provisioning` because the request matches `infrastructure-engineer` work and has concrete repo anchors.

Read first:

- `main.tf`
- `modules/network/main.tf`
- `.github/workflows/plan.yml`

Evidence gathered:

- Confirmed `aws_db_instance` and its `plan diff` before recommending changes.
- Checked `state backend` against `modules/network/main.tf` as the proof surface.
- Identified `blast radius` as a required proof term before completion.

Answer:

Inspect the named paths, compare them against the expected infrastructure proof surface, and only then recommend a change. If an anchor is missing, ask one question that names the missing file, config, or policy.

Residual risk:

- `rollback path` remains unverified until the focused gate for this domain is captured.
