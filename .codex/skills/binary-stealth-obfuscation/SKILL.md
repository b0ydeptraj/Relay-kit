---
name: binary-stealth-obfuscation
description: Use when a binary payload, shellcode, or PE needs to evade static analysis, signature detection, AV/EDR scanning, or YARA rules through obfuscation, packing, or mutation.
---

# Mission
Apply binary obfuscation techniques to reduce static signature surface while preserving correct runtime behavior.

## Mandatory scope
1. Engagement proof required: confirm offensive-security-engagement has cached engagement_proof.
2. Identify detection surface: YARA rules, PE header heuristics, import table, string patterns, entropy.
3. Choose obfuscation approach: encryption (XOR/AES), packing, polymorphism, import obfuscation, section renaming.
4. Verify runtime behavior preserved: test in isolated sandbox BEFORE claiming detection evasion.
5. Document entropy delta: high entropy is itself a detection signal — balance obfuscation with entropy control.
6. Cleanup gate: document how the obfuscated artifact is removed from target after use.

## Evidence contract
- engagement_proof confirmed
- detection surface identified (YARA rules, strings, imports)
- sandbox execution result (behavior unchanged)
- entropy delta documented
- cleanup path written

## Role
- obfuscation-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- binary/shellcode/PE artifact
- target AV/EDR product if known
- engagement_proof from offensive-security-engagement

## Outputs
- obfuscated binary
- detection surface analysis
- sandbox result

## Reference skills and rules
- Never claim evasion without sandbox execution evidence.
- Entropy above 7.5 is a detection signal — document entropy control strategy.
- Preserve original behavior exactly — functionality must be verified after obfuscation.
- engagement_proof required; block if missing.
- Open `references/binary-stealth-obfuscation-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/binary-stealth-obfuscation-good-output.md` and `examples/binary-stealth-obfuscation-bad-output.md` to calibrate output quality.
- Use `evals/binary-stealth-obfuscation-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/binary-stealth-obfuscation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- edr-evasion-tactics
- telemetry-blinding
- process-injection-techniques
- test-hub
- field-journal-evolution
