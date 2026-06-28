---
name: fix-hub
description: Use when debug-hub has validated findings or when a change request is already sharply bounded. Turn those findings into a minimal implementation path and hand off to the developer loop.
---

# Mission
Convert a known problem into a bounded implementation path that can be executed safely.

## Mandatory routing
1. Use `project-architecture` when the fix touches boundaries, dependencies, or ownership.
2. Use `data-persistence` for schemas, migrations, transactions, caches, or backfills.
3. Use `dependency-management` for package, lockfile, toolchain, or environment fixes.
4. Use `go-service-engineering` or `next-product-frontend` for stack-specific implementation handoff.
5. Use `test-first-development` when behavior can be captured before the implementation pass.
6. Offensive fix handoff: when the fix involves native systems or security-sensitive code, route to the matching specialist:
   - C++ / Win32 / native code -> `cpp-systems-engineering`, `windows-native-internals`
   - Python scripting / automation -> `advanced-python-engineering`
   - Binary evasion / obfuscation -> `binary-stealth-obfuscation`
   - EDR / AV bypass -> `edr-evasion-tactics`, `telemetry-blinding`
   - Process injection / hollowing -> `process-injection-techniques`
   - C2 / network stealth -> `network-stealth-c2`
   - Antibot / fingerprint bypass -> `antibot-challenge-solving`, `protocol-fingerprint-spoofing`
   - Crypto reverse / signing -> `frontend-crypto-reverse`
   - Desktop ImGui UI -> `desktop-imgui-development`
   - Desktop Python UI -> `desktop-python-ui`
   - Terminal / CLI UI -> `terminal-operator-ui`

## Evidence contract
- update the active story or tech-spec with real files, boundaries, and verification steps
- name what must not change while fixing the issue
- include the failing signal, intended green signal, rollback note, and one edge case
- hand off to `developer` only after the implementation surface is bounded

## Failure modes
Hold when the fix expands architecture without plan review, hides data risk, or skips the first verification command.

## Role
- fix-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- tech-spec or story
- investigation-notes when debugging
- architecture and project-context when relevant

## Outputs
- refined tech-spec or story
- implementation handoff to developer
- updated workflow-state

## Reference skills and rules
- Keep the fix surface as small as possible.
- Use developer plus execution-loop for execution, not as a replacement for scoping.
- If the fix expands the contract or architecture, route back through workflow-router or plan-hub.
- Open `references/fix-hub-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/fix-hub-good-output.md` and `examples/fix-hub-bad-output.md` to calibrate output quality.
- Use `evals/fix-hub-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/fix-hub-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- developer
- go-service-engineering
- next-product-frontend
- project-architecture
- data-persistence
- dependency-management
- test-first-development
- test-hub
- review-hub
- workflow-router
- cpp-systems-engineering
- windows-native-internals
- advanced-python-engineering
- binary-stealth-obfuscation
- edr-evasion-tactics
- telemetry-blinding
- process-injection-techniques
- network-stealth-c2
- protocol-fingerprint-spoofing
- antibot-challenge-solving
- frontend-crypto-reverse
- desktop-imgui-development
- desktop-python-ui
- terminal-operator-ui
