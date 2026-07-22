---
name: telemetry-blinding
description: Use when operations need to suppress, redirect, or corrupt security telemetry: ETW providers, Sysmon, WEF, audit logs, or kernel callbacks.
---

# Mission
Suppress or redirect security telemetry channels so offensive operations produce minimal forensic footprint.

## Mandatory scope
1. Engagement proof required.
2. Map active telemetry channels: ETW providers, Sysmon config, WEF subscriptions, audit policy.
3. Choose blinding approach: ETW provider disable, Sysmon filter bypass, audit log suppression, kernel callback removal.
4. Verify blinding in controlled environment: confirm target events no longer appear in SIEM/log.
5. Document restoration path: how telemetry is re-enabled after operation.
6. Anti-forensics scope: document which artifacts are wiped (prefetch, event logs, MFT timestamps).

## Evidence contract
- engagement_proof confirmed
- telemetry channels mapped
- blinding verified (events absent in controlled log)
- restoration path documented
- anti-forensics scope listed

## Role
- telemetry-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target environment telemetry stack
- operation scope
- engagement_proof

## Outputs
- telemetry blinding implementation
- verification result
- restoration runbook

## Reference skills and rules
- Never delete logs without explicit engagement scope including log suppression.
- Document restoration path — cleanup is mandatory after authorized operations.
- Verify blinding with actual log monitoring, not assumption.
- engagement_proof required; block if missing.
- Open `references/telemetry-blinding-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/telemetry-blinding-good-output.md` and `examples/telemetry-blinding-bad-output.md` to calibrate output quality.
- Use `evals/telemetry-blinding-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/telemetry-blinding-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- edr-evasion-tactics
- binary-stealth-obfuscation
- process-injection-techniques
- network-stealth-c2
- test-hub
- field-journal-evolution
