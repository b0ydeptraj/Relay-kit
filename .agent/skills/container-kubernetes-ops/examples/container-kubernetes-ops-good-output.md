# container-kubernetes-ops Battle-Calibrated Output

Request: review a container and Kubernetes change, check probes and limits, and name the rollback revision

Recommended skill: `container-kubernetes-ops` because the request matches `platform-engineer` work and has concrete repo anchors.

Read first:

- `Dockerfile`
- `k8s/deployment.yaml`
- `k8s/configmap.yaml`

Evidence gathered:

- Confirmed `readinessProbe` and its `image hygiene` before recommending changes.
- Checked `readiness probe` against `k8s/deployment.yaml` as the proof surface.
- Identified `resource limits` as a required proof term before completion.

Answer:

Inspect the named paths, compare them against the expected platform proof surface, and only then recommend a change. If an anchor is missing, ask one question that names the missing file, config, or policy.

Residual risk:

- `rollout rollback` remains unverified until the focused gate for this domain is captured.
