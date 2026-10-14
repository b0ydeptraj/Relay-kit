---
name: av-payload-builder
description: "Use when a red team payload needs to evade antivirus static detection. Apply encoding, encryption, obfuscation, and packing to raw shellcode or executables. Engagement proof and authorized red team scope required."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when a red team payload needs to evade antivirus static detection.

# AV Payload Builder

> Build AV-evading payload wrappers and loaders for authorized red team engagements.

## Mission
Transform raw shellcode or tools into AV-evading payloads using multiple evasion layers.

## Mandatory scope checks
1. Engagement proof required.
2. Identify target AV: Windows Defender / CrowdStrike / Sentinel / Symantec
3. Choose evasion layers (stack):
   - Layer 1: Shellcode encryption (XOR/AES/ChaCha20 with runtime key)
   - Layer 2: Anti-analysis (sandbox-evasion checks)
   - Layer 3: PE format manipulation (binary-stealth-obfuscation)
   - Layer 4: Execution method (process-injection-techniques)
4. Verify in AV-enabled sandbox: confirm detection rate
5. Document bypass method and AV version tested

## AV bypass by layer
| Layer | Technique | Tool/Method |
|---|---|---|
| Static signature | XOR encrypt shellcode | string_encrypt.py / custom |
| Heuristic | API obfuscation (GetProcAddress dynamic) | Custom loader |
| Memory scan | Reflective loading into RX memory | reflective-dll-loader.hpp |
| Behavioral | Sleep + user check before detonation | sandbox-evasion skill |

## Evidence contract
- engagement_proof confirmed
- target AV named and version noted
- evasion layers documented
- detection rate before/after (VirusTotal or local AV test)
- cleanup: payload deleted from target after test

## Role
- offensive-security-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with av-payload-builder findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside av-payload-builder's scope back through `offensive-security-engagement` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/av-payload-builder-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/av-payload-builder-good-output.md` and `examples/av-payload-builder-bad-output.md` to calibrate output quality.
- Use `evals/av-payload-builder-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/av-payload-builder-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- av-payload-builder
- offensive-security-engagement
- workflow-router
