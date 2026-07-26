---
name: container-kubernetes-ops
description: "Use when packaging services into containers or operating Kubernetes workloads, including Dockerfiles, image hygiene, manifests, resource limits, probes, rollouts, and cluster troubleshooting."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Ship containers and Kubernetes workloads that start predictably, fail visibly, and roll out without taking traffic down.

## Mandatory scope
1. Image hygiene: pinned base image, non-root user, minimal layers, no secrets baked in, a reproducible build.
2. Manifests: explicit resource requests and limits, liveness and readiness probes that reflect real health, and a restart policy.
3. Rollout: a strategy (rolling or blue-green) with surge/unavailable bounds and a defined rollback to the previous revision.
4. Config and secrets: config via ConfigMap/env, secrets via a secret store -- never in the image or manifest literal.
5. Troubleshooting: read events, logs, and probe status before mutating; name the failing signal, not a guess.

## Evidence contract
- base image pinned and container runs non-root
- resource requests/limits and both probes defined
- rollout strategy and rollback revision named
- secrets sourced from a store, not the manifest

## Failure modes to block
- Running as root or baking secrets into the image.
- Missing readiness probe, so a rollout sends traffic to a not-ready pod.
- No resource limits, so one workload starves the node.
- Restarting or deleting pods before reading events and logs.

## Handoff
- Hand infrastructure to `iac-cloud-provisioning`, secret material to `secrets-management`, and health signals to `observability-instrumentation`.

## Role
- platform-engineer

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the service to containerize or the workload to operate
- existing Dockerfile or manifests
- cluster and resource constraints

## Outputs
- Dockerfile or manifest changes
- rollout and probe configuration
- troubleshooting notes

## Reference skills and rules
- Open `references/container-kubernetes-ops-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/container-kubernetes-ops-good-output.md` and `examples/container-kubernetes-ops-bad-output.md` to calibrate output quality.
- Use `evals/container-kubernetes-ops-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/container-kubernetes-ops-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- iac-cloud-provisioning
- secrets-management
- observability-instrumentation
- review-hub
