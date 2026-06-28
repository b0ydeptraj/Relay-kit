---
name: scout-hub
description: Use when the repo area is unfamiliar, stale, or likely to drift from existing assumptions. Reconnoiter the codebase and refresh living references before planning, debugging, or review work continues.
---

# Mission
Gather the minimum reliable context the next lane needs so nobody plans or fixes from a false mental model.

## Mandatory routing
1. Use `repo-map` for entrypoints, ownership, dependency direction, and read-first files.
2. Use `doc-pointers` for exact docs, anchors, and source fragments.
3. Use `memory-search` for prior decisions, handoff breadcrumbs, or stale state checks.
4. Use `project-architecture` when module boundaries or architecture drift matter.
5. Use `dependency-management` when tooling, lockfiles, or dependency risk affects the lane.
6. Offensive recon routing: when the codebase is binary, native, or mobile-focused, pull the matching analysis skill before planning:
   - Binary / PE / ELF / Mach-O -> `binary-reverse-methodology`
   - Malware samples / suspicious code -> `malware-analysis-workflows`
   - APK / IPA / mobile native -> `mobile-app-reverse`
   - C++ / Win32 / driver code -> `cpp-systems-engineering`, `windows-native-internals`
   - Web JS / WASM crypto -> `frontend-crypto-reverse`, `browser-fingerprint-engineering`
   - Network protocol unknown -> `protocol-fingerprint-spoofing`

## Evidence contract
- cite concrete paths, commands, modules, or docs instead of broad summaries
- mark freshness for every important source: current, stale, inferred, or missing
- record unknowns that still block planning or debugging
- start `investigation-notes.md` when the scout is attached to a failure

## Failure modes
Hold if the output is a tree dump without ownership, a generic architecture summary, or a plan that skips stale evidence.

## Output contract
Name what became clearer, what is still unknown, which sources may be stale, and which hub or specialist should use the refreshed context next.

## Role
- recon-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- repo tree and relevant files
- .relay-kit/contracts/project-context.md
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/project-context.md
- .relay-kit/references/*.md as needed
- .relay-kit/contracts/investigation-notes.md when the work starts from a failure

## Reference skills and rules
- Use project-architecture, dependency-management, api-integration, data-persistence, and testing-patterns as living references.
- Prefer concrete file paths, commands, and entrypoints over summaries.
- When the problem starts from a failure, capture findings in investigation-notes.
- Run a freshness pass first: stale assumptions or stale artifacts should be called out explicitly before planning.
- Open `references/scout-hub-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/scout-hub-good-output.md` and `examples/scout-hub-bad-output.md` to calibrate output quality.
- Use `evals/scout-hub-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/scout-hub-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- repo-map
- doc-pointers
- memory-search
- project-architecture
- dependency-management
- plan-hub
- debug-hub
- review-hub
- workflow-router
- binary-reverse-methodology
- malware-analysis-workflows
- mobile-app-reverse
- cpp-systems-engineering
- windows-native-internals
- frontend-crypto-reverse
- browser-fingerprint-engineering
- protocol-fingerprint-spoofing
