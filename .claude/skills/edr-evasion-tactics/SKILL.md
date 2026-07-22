---
name: edr-evasion-tactics
description: Use when a payload or tool needs to evade EDR runtime detection: hook bypass, AMSI bypass, ETW patching, direct syscall, or AV memory scanning evasion.
---

# Mission
Implement EDR/AV runtime evasion with explicit hook bypass, syscall strategy, and OPSEC discipline.

## Mandatory scope
1. Engagement proof required.
2. Identify EDR target: CrowdStrike / Defender / SentinelOne / Carbon Black — hook surface differs.
3. Choose syscall strategy: direct syscall (Syswhispers2/3), indirect syscall, or unhooking (overwrite ntdll from fresh copy).
4. Handle AMSI: patch AmsiScanBuffer / AmsiOpenSession in-process.
5. Handle ETW: patch EtwEventWrite / disable provider via NtTraceControl.
6. Verify no hook fires: use a controlled sandbox with ETW/kernel callback monitoring.

## Evidence contract
- engagement_proof confirmed
- EDR target named
- syscall strategy documented with method (direct/indirect/unhook)
- AMSI + ETW bypass verified in sandbox
- No hook fired in monitoring trace

## Role
- edr-evasion-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target EDR product
- payload or tool to protect
- engagement_proof

## Outputs
- hook-bypass implementation
- AMSI/ETW bypass
- sandbox evidence

## Reference skills and rules
- Never claim bypass without controlled sandbox monitoring evidence.
- Document which EDR version was tested — bypass techniques are version-specific.
- Unhooking must restore original bytes on cleanup.
- engagement_proof required; block if missing.
- Open `references/edr-evasion-tactics-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/edr-evasion-tactics-good-output.md` and `examples/edr-evasion-tactics-bad-output.md` to calibrate output quality.
- Use `evals/edr-evasion-tactics-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/edr-evasion-tactics-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- telemetry-blinding
- binary-stealth-obfuscation
- process-injection-techniques
- windows-native-internals
- test-hub
- field-journal-evolution
