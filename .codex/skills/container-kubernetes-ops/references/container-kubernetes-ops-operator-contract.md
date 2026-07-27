# container-kubernetes-ops Battle Contract

Primary role: platform-engineer
Battle family: platform

Anchor every container-kubernetes-ops answer to a real artifact, repo area, or explicit missing-context question. The goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state -- not to sound like an expert.

## Concrete Battle Profile

- Repo profile: a service repo with a Dockerfile, Kubernetes manifests, a deployment with probes, and a rollout config
- First files to inspect: Dockerfile, k8s/deployment.yaml, k8s/service.yaml, k8s/configmap.yaml
- Symbols or named surfaces to confirm: readinessProbe, resources.limits, RollingUpdate
- Evidence terms that should appear in a strong answer: image hygiene, readiness probe, resource limits, rollout rollback

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Inspect at least one source file and one proof surface for this domain.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff.

## Failure Modes To Block

- Running as root or baking secrets into the image.
- Missing readiness probe, so a rollout serves not-ready pods.
- Treating a checklist as proof.
- Claiming the change is ready before the domain evidence was inspected.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite the image hygiene or readiness probe surface that proves the claim.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
