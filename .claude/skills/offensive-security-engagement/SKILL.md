---
name: offensive-security-engagement
description: Use when a request contains offensive, red-team, evasion, injection, stealth, C2, payload, syscall, hollowing, or bypass keywords, or when authorization_risk >= medium. Gate + context provider for all offensive lanes.
---

# Mission
Activate authorized offensive context, cache engagement proof, enforce OPSEC ordering, and map ATT&CK phase so offensive lanes have a clear authorization record before any specialist runs.

## Mandatory scope
1. Confirm engagement authorization: check workflow-state for engagement_proof; if missing, prompt for scope, target, and authorization before proceeding.
2. Cache engagement_proof with: authorized-by, scope, target, risk-tier (low/medium/high/critical), ATT&CK phase.
3. Set lane mode to offensive in workflow-state.
4. Enforce OPSEC ordering: recon -> initial-access -> execution -> persistence -> privesc -> lateral -> collection -> exfil -> cleanup.
5. After caching proof, return control to the calling hub or cook — do not own the lane.
6. Distinguish from policy-guard: policy-guard is fail-closed for secrets/shell/path. This skill is fail-open-for-authorized for offensive techniques. Run policy-guard AFTER execution as post-gate.

## Evidence contract
- engagement_proof written to workflow-state with all required fields
- risk-tier set explicitly before specialist is called
- ATT&CK phase mapped for current task

## Role
- engagement-gate

## Layer
- layer-3-utility-providers

## Inputs
- user request with offensive keywords
- workflow-state
- authorization scope if provided

## Outputs
- workflow-state.engagement_proof
- workflow-state.lane_mode = offensive
- risk-tier annotation

## Reference skills and rules
- Never proceed without engagement_proof — if authorization is missing, block and prompt.
- Do not own the lane; return control after caching proof.
- Distinguish fail-closed (policy-guard) from fail-open-for-authorized (this skill).
- ATT&CK mapping is required for every offensive lane.
- Open `references/offensive-security-engagement-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/offensive-security-engagement-good-output.md` and `examples/offensive-security-engagement-bad-output.md` to calibrate output quality.
- Use `evals/offensive-security-engagement-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/offensive-security-engagement-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- attack-chain-orchestration
- cpp-systems-engineering
- edr-evasion-tactics
- process-injection-techniques
- network-stealth-c2
- binary-stealth-obfuscation
- policy-guard
