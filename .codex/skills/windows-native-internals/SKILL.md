---
name: windows-native-internals
description: Use when work requires Windows-internal knowledge: NT APIs, PEB/TEB, kernel structures, SSDT, ETW, driver interaction, object manager, undocumented syscalls, or memory manager internals.
---

# Mission
Apply Windows NT internals knowledge to implement, debug, or bypass Windows-native subsystems safely and correctly.

## Mandatory scope
1. Identify the Windows version target: XP/7/10/11/Server — kernel structures change across versions.
2. Name the NT API or structure being used: NtAllocateVirtualMemory, PEB, LDR_DATA_TABLE_ENTRY, etc.
3. Declare whether the technique uses documented API, undocumented API, or direct syscall.
4. Document SSDT/ETW/Callback implications for any kernel-touching operation.
5. For usermode-kernel transitions: document syscall number, calling convention, and version dependency.
6. Include version-conditional code where kernel structures differ across Windows releases.

## Evidence contract
- Windows version target declared
- API tier declared (documented / undocumented / direct syscall)
- Structure offsets verified against target version
- SSDT/ETW impact documented

## Role
- windows-internals-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target Windows version
- NT API surface needed
- existing code context

## Outputs
- Windows-native implementation
- API documentation
- version-conditional guards

## Reference skills and rules
- Always declare which Windows version the code targets — offsets change.
- Never hardcode structure offsets without a version guard.
- Document whether ETW or PatchGuard is affected.
- Use ntdll imports or direct syscall — never assume high-level API availability in injected context.
- Open `references/windows-native-internals-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/windows-native-internals-good-output.md` and `examples/windows-native-internals-bad-output.md` to calibrate output quality.
- Use `evals/windows-native-internals-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/windows-native-internals-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- cpp-systems-engineering
- process-injection-techniques
- edr-evasion-tactics
- telemetry-blinding
- binary-stealth-obfuscation
- field-journal-evolution
