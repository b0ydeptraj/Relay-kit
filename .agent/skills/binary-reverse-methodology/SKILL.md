---
name: binary-reverse-methodology
description: Use when reverse engineering a binary: PE/ELF/Mach-O analysis, disassembly, decompilation, protocol reconstruction, anti-analysis bypass, or understanding undocumented behavior.
---

# Mission
Systematically reverse engineer a binary to understand its behavior, protocol, or protection scheme.

## Mandatory scope
1. Tool selection: IDA Pro / Ghidra / Binary Ninja / radare2 — document which and why.
2. Entry point analysis: identify main, WinMain, TLS callbacks, anti-debug checks.
3. Anti-analysis handling: detect and bypass anti-debug (IsDebuggerPresent, timing checks, checksum), anti-vm, and packer.
4. Protocol reconstruction: if network binary, capture traffic and correlate with code paths.
5. Function naming: rename identified functions before documenting — avoid generic sub_XXXX in reports.
6. Document findings: algorithm identified, key material location, C2 protocol, persistence mechanism.

## Evidence contract
- tool documented
- entry point and anti-analysis techniques identified
- anti-debug bypassed or documented
- key findings renamed and documented
- protocol or algorithm reconstructed

## Role
- reverse-engineer

## Layer
- layer-4-specialists-and-standalones

## Inputs
- binary to analyze
- analysis goal (protocol / protection / behavior)
- engagement_proof if offensive sample

## Outputs
- reverse engineering report
- annotated binary/IDB
- protocol or algorithm doc

## Reference skills and rules
- Rename functions before writing the report — sub_XXXX references are not useful findings.
- Document anti-analysis techniques explicitly — they are often the most important finding.
- Protocol reconstruction requires both code analysis and traffic capture correlation.
- Decompiler output is pseudocode — verify against disassembly for critical paths.
- Open `references/binary-reverse-methodology-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/binary-reverse-methodology-good-output.md` and `examples/binary-reverse-methodology-bad-output.md` to calibrate output quality.
- Use `evals/binary-reverse-methodology-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/binary-reverse-methodology-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- malware-analysis-workflows
- binary-stealth-obfuscation
- frontend-crypto-reverse
- windows-native-internals
- test-hub
- field-journal-evolution
