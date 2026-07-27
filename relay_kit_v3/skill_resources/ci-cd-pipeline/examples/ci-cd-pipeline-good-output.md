# ci-cd-pipeline Battle-Calibrated Output

Request: handle a ci-cd-pipeline request, name files first, and identify the proof surface before editing

Recommended skill: `ci-cd-pipeline` because the request matches `cicd-specialist` work and has concrete repo anchors.

Read first:

- `.github/workflows/ci.yml`
- `scripts/deploy.sh`
- `package-lock.json`

Evidence gathered:

- Confirmed `build` ownership before recommending changes.
- Checked `blocking gate` and `cache key` against the relevant source path.
- Identified `artifact promotion` as a required proof term before completion.

Answer:

The safe next move is to inspect the named path, compare it with the expected test, metric, config, or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `rollback trigger` remains unverified until the focused gate or proof surface is captured.
