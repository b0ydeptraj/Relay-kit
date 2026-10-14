---
name: sandbox-evasion
description: "Use when a payload or malware sample needs to evade automated sandbox analysis (Any.run, Cuckoo, VirusTotal Sandbox, Joe Sandbox, Hybrid Analysis). Implement sandbox detection checks, delayed execution, user interaction requirements, and environment fingerprinting to prevent detonation in sandboxes."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when a payload or malware sample needs to evade automated sandbox analysis (Any.

# Sandbox Evasion

> Detect and evade automated malware analysis sandboxes for authorized red team payloads.

## Mission
Ensure payload only executes in genuine target environments, not automated analysis systems.

## Mandatory scope checks
1. Engagement proof required.
2. Identify likely sandbox types: cloud AV sandbox / corporate EDR sandbox / DFIR sandbox
3. Choose detection techniques: timing, user artifacts, hardware fingerprinting, mouse/keyboard
4. Choose evasion technique: sleep, user interaction gate, env check, decoy behavior
5. Verify no false positives: test on clean genuine target environment

## Detection techniques
| Technique | What to check | Sandbox indicator |
|---|---|---|
| Timing | Sleep skipping | GetTickCount64 before/after sleep differs |
| User artifacts | Recent files | < 10 files in Recent, no browsing history |
| Hardware | CPU cores / RAM | < 2 cores or < 2GB RAM |
| Screen | Resolution | 800x600 or <1024px wide |
| Process | Known sandbox | VBoxService, vmwaretray, sandboxie, wireshark |
| Mouse | Movement | No mouse delta after 30s |
| Username | Generic | WIN-*, DESKTOP-* pattern |
| Disk | Total size | < 50GB total = likely VM |

## Evidence contract
- engagement_proof confirmed
- sandbox detection technique documented with detection logic
- evasion delay/gate design documented
- test result: executes on real target, skips on sandbox

## Role
- offensive-security-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with sandbox-evasion findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside sandbox-evasion's scope back through `offensive-security-engagement` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/sandbox-evasion-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/sandbox-evasion-good-output.md` and `examples/sandbox-evasion-bad-output.md` to calibrate output quality.
- Use `evals/sandbox-evasion-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/sandbox-evasion-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- sandbox-evasion
- offensive-security-engagement
- workflow-router
