---
name: sandbox-evasion
description: "Use when a payload or malware sample needs to evade automated sandbox analysis (Any.run, Cuckoo, VirusTotal Sandbox, Joe Sandbox, Hybrid Analysis). Implement sandbox detection checks, delayed execution, user interaction requirements, and environment fingerprinting to prevent detonation in sandboxes."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

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
- sandbox-evasion-specialist

## Layer
- layer-4-specialists-and-standalones

## Likely next step
- edr-evasion-tactics
- binary-stealth-obfuscation
- anti-debugging-techniques
- binary-protection-bypass
