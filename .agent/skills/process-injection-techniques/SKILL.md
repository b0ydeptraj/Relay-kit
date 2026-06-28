---
name: process-injection-techniques
description: Use when a payload needs to run in the context of another process: classic injection, reflective DLL, process hollowing, APC injection, thread hijacking, or shellcode runners.
---

# Mission
Implement process injection techniques with correct memory management, error handling, and cleanup discipline.

## Mandatory scope
1. Engagement proof required.
2. Choose injection method: CreateRemoteThread, APC queue, SetWindowsHookEx, reflective DLL, process hollowing, early-bird, thread hijacking.
3. Document memory allocation: VirtualAllocEx permissions (RWX -> RX after write), cleanup on failure.
4. Handle 32-bit / 64-bit mismatch: WOW64 constraints for cross-arch injection.
5. Verify target process selection: PPID spoofing if needed, handle privileges required.
6. Cleanup gate: document how the injected memory and handles are cleaned up after operation.

## Evidence contract
- engagement_proof confirmed
- injection method declared with rationale
- memory permissions and cleanup documented
- arch mismatch handled (WOW64 if applicable)
- PPID spoofing documented if used

## Role
- injection-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target process or criteria
- payload shellcode or DLL
- engagement_proof

## Outputs
- injection implementation
- memory management docs
- cleanup runbook

## Reference skills and rules
- Never leave RWX memory pages after payload execution — change to RX.
- Document cleanup: close handles, free memory, restore target thread state.
- Handle WOW64 explicitly when injecting cross-arch.
- engagement_proof required; block if missing.
- Open `references/process-injection-techniques-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/process-injection-techniques-good-output.md` and `examples/process-injection-techniques-bad-output.md` to calibrate output quality.
- Use `evals/process-injection-techniques-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/process-injection-techniques-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- edr-evasion-tactics
- telemetry-blinding
- windows-native-internals
- binary-stealth-obfuscation
- network-stealth-c2
- test-hub
- field-journal-evolution
