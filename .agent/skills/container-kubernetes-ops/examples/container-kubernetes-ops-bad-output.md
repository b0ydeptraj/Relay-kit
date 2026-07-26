# container-kubernetes-ops Weak Output Anti-Example

Request: review a container and Kubernetes change, check probes and limits, and name the rollback revision

Weak answer:

This looks like `container-kubernetes-ops`, so apply the standard fix and it should be fine.

Why this fails:

- No file path from `a service repo with a Dockerfile, Kubernetes manifests, a deployment with probes, and a rollout config` was inspected.
- No symbol such as `readinessProbe` was confirmed.
- No proof surface was named for `image hygiene`.
- It blurs verified evidence and inference, which is how overclaim slips back in.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
