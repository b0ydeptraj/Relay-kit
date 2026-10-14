---
name: mmo-anti-detection-browser
description: "Use when MMO operations need anti-detection browser management: GoLogin, Multilogin, AdsPower, Dolphin Anty, or custom Chrome profile isolation with fingerprint spoofing for multi-account automation without detection."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when MMO operations need anti-detection browser management: GoLogin, Multilogin, AdsPower, Dolphin Anty, or custom Chrome profile isolation with fingerprint spoofing for multi-account automation without detection.

# Anti-Detection Browser Fleet Management

> Manage multi-profile anti-detection browsers for MMO operations with full fingerprint isolation.

## Mission
Operate browser profiles with complete fingerprint isolation per account: unique canvas, WebGL, fonts, timezone, screen, UA, and proxy affinity.

## Mandatory scope checks
1. Choose browser engine: GoLogin / Multilogin / AdsPower / Dolphin Anty / DIY Chromium
2. Define fingerprint isolation: canvas noise, WebGL vendor, font list, screen resolution, timezone per profile
3. Define proxy affinity: 1 profile = 1 residential proxy (sticky session)
4. Define profile storage: local folder isolation vs cloud sync
5. Define session lifecycle: create → warm → operate → park → rotate

## Evidence contract
- profile_id and fingerprint_hash per session
- proxy health check before each launch
- canvas fingerprint test URL result
- IP-profile affinity table
- screenshot proof of platform login per profile

## Platform support matrix
| Browser | API | Free tier | Fingerprint depth |
|---|---|---|---|
| GoLogin | REST API ✅ | 3 profiles | Full (canvas, WebGL, fonts, audio) |
| AdsPower | REST API ✅ | 5 profiles | Full |
| Dolphin Anty | REST API ✅ | 10 profiles | Full |
| Multilogin | REST API ✅ | Paid only | Enterprise grade |
| DIY Chromium | No API | Unlimited | Manual via JS injection |

## Role
- mmo-automation-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with mmo-anti-detection-browser findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside mmo-anti-detection-browser's scope back through `mmo-authorization-gate` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/mmo-anti-detection-browser-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-anti-detection-browser-good-output.md` and `examples/mmo-anti-detection-browser-bad-output.md` to calibrate output quality.
- Use `evals/mmo-anti-detection-browser-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-anti-detection-browser-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-anti-detection-browser
- mmo-authorization-gate
- workflow-router
