---
name: attack-chain-orchestration
description: Use when planning or orchestrating a multi-phase authorized attack chain: from initial recon through execution, persistence, lateral movement, collection, and cleanup.
---

# Mission
Plan and sequence an authorized multi-phase attack chain with explicit path planning, OPSEC discipline, and mandatory cleanup gate.

## Mandatory scope
1. Engagement proof required.
2. Map 7-phase kill chain: Recon -> Initial Access -> Execution -> Persistence -> Privilege Escalation -> Lateral Movement -> Collection/Exfil -> Cleanup.
3. For each phase: current foothold + goal + constraints -> next 3 actions ranked by risk and detectability.
4. Per-phase technique selection: call appropriate Phase 2+ specialists for implementation.
5. Blocked-path replanning: if one path is blocked, automatically propose 2 alternatives.
6. Cleanup-mandatory gate: do not claim operation complete until cleanup is verified.

## Evidence contract
- engagement_proof confirmed
- kill chain phases mapped with ATT&CK technique IDs
- per-phase action ranking documented
- cleanup plan written
- blocked-path alternatives documented

## Role
- attack-chain-planner

## Layer
- layer-3-utility-providers

## Inputs
- engagement scope and objective
- current foothold and constraints
- engagement_proof

## Outputs
- attack chain plan (mermaid diagram)
- per-phase action list
- cleanup runbook

## Reference skills and rules
- Never claim operation complete without cleanup verification.
- Every phase must have an alternative path if primary is blocked.
- OPSEC risk tier must be documented per action.
- engagement_proof required; block if missing.
- Open `references/attack-chain-orchestration-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/attack-chain-orchestration-good-output.md` and `examples/attack-chain-orchestration-bad-output.md` to calibrate output quality.
- Use `evals/attack-chain-orchestration-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/attack-chain-orchestration-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- offensive-security-engagement
- edr-evasion-tactics
- process-injection-techniques
- network-stealth-c2
- telemetry-blinding
- test-hub
- field-journal-evolution
