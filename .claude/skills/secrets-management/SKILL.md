---
name: secrets-management
description: "Use when handling secrets, API keys, tokens, or wallet keys across a fleet and you need vaulting, injection, rotation, scoping, and leak response instead of plaintext credentials."
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Mission
Keep every credential out of source and out of plaintext: vaulted at rest, injected at runtime, scoped to least privilege, and rotatable without downtime.

## Mandatory scope
1. Inventory: name each secret, where it lives now, and who reads it; flag any that sit in code, config, or logs.
2. Storage: move secrets to a vault or platform secret store; the app reads them at runtime, never from a committed file.
3. Scoping: grant each consumer the narrowest credential that works; no shared god-tokens across services.
4. Rotation: define a rotation interval and a zero-downtime rotation path (dual-key or overlap window).
5. Leak response: define detection, immediate revocation, rotation, and blast-radius assessment for an exposed secret.

## Evidence contract
- secret inventory with current storage location per item
- vault/store as the source of truth, injection path named
- least-privilege scoping stated per consumer
- rotation interval and zero-downtime rotation path
- leak-response steps: detect, revoke, rotate, assess

## Failure modes to block
- A secret left in source control, an env file, or a log line.
- One shared token used everywhere so revocation breaks everything.
- No rotation path, so a leak means a painful emergency.
- Handling the plaintext value directly instead of a reference.

## Handoff
- This skill never enters credential values itself; it hands entry to the operator. Hand consuming infra to `iac-cloud-provisioning` and `container-kubernetes-ops`, and code-path review to `secure-code-review`.

## Role
- secrets-engineer

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the secrets or credentials in play
- where they are currently stored and consumed
- rotation and scoping requirements

## Outputs
- a secret storage and injection plan
- rotation and scoping policy
- a leak-response runbook

## Reference skills and rules
- Open `references/secrets-management-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/secrets-management-good-output.md` and `examples/secrets-management-bad-output.md` to calibrate output quality.
- Use `evals/secrets-management-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/secrets-management-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- iac-cloud-provisioning
- container-kubernetes-ops
- secure-code-review
- review-hub
