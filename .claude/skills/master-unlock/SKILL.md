---
name: master-unlock
description: "Use when authorized RE extraction (source recovery, license-logic recovery, or keygen build) needs a disciplined loop controller because single-skill attempts have stalled. Orchestrates binary-identifier → unpacker/decompiler → memory-dumper → license-robustness-audit with iteration budget, progress check, and kill switch. Requires `offensive-domain-unlock` authorization already recorded."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob"]
---

# Mission
Drive an authorized RE extraction to completion by orchestrating existing leaf skills with a budget, a progress rule, and a kill switch. Not a capability grant.

## Scope boundary (do not violate)
- IN scope: scheduling the next leaf skill, scoring per-iteration progress, writing the iteration log, calling the kill switch.
- OUT of scope: doing the extraction yourself (decompile / dump / patch) — that belongs to the leaf skill called this iteration.
- OUT of scope: running without an authorization record. If `.relay-kit/state/offensive-authorization.md` does not exist for this lane, STOP and route to `offensive-domain-unlock`.
- OUT of scope: publishing a working bypass, keygen, or patched binary for third-party software. Output stays as research artifacts for the authorized owner.

## Pre-flight (refuse the loop if any missing)
1. Authorization record exists and names this target by path/hash.
2. Extraction GOAL is one concrete deliverable (not "crack the app").
3. Stall evidence: list of leaf skills already tried + why each stopped. Fresh lanes with no prior stall → go run the leaf skill directly, this loop is for stalled lanes.
4. Iteration budget (integer) and per-iteration time budget (minutes) set.
5. `binary-identifier` output exists OR is iteration 1.

## Loop contract
```
FOR i IN 1..budget:
    1. SELECT next leaf skill from the matrix below based on last iteration's verdict and binary-identifier fingerprint.
    2. INVOKE that leaf skill with its own contract. Record its evidence id (file paths it produced).
    3. SCORE progress:
       - progress     = new evidence id AND it unblocks the goal (source bytes, key candidate, logic branch)
       - no-progress  = leaf skill ran but produced no new usable evidence
       - blocked      = leaf skill refused (missing prereq, out of scope)
    4. APPEND iteration record to .relay-kit/contracts/extraction-loop.md
    5. KILL SWITCH: if 3 consecutive 'no-progress' OR any 'blocked' with no fallback leaf, STOP.
    6. If goal artifact exists, STOP with success.
```

## Leaf-skill routing matrix
| Binary-identifier says | Goal: source | Goal: license logic | Goal: keygen |
|---|---|---|---|
| PyInstaller | `pyinstaller-unpacker` → grep | `pyinstaller-unpacker` → `license-robustness-audit` | `memory-dumper` → `license-robustness-audit` |
| Nuitka | `nuitka-decryptor` | `nuitka-decryptor` → `license-robustness-audit` | `memory-dumper` + `frida-hooker` |
| .NET / IL | `dotnet-decompiler` | `dotnet-decompiler` → `license-robustness-audit` | `dotnet-keygen` |
| Electron | `electron-app-analyzer` + `javascript-deobfuscator` | `javascript-deobfuscator` → `license-robustness-audit` | `memory-dumper` |
| Native C/C++/Go/Rust | `binary-reverse-methodology` + `ghidra` externally | `binary-reverse-methodology` → `license-robustness-audit` | `memory-dumper` + `frida-hooker` |
| Java/APK | `java-decompiler` / `android-apk-pentester` | same + `license-robustness-audit` | `memory-dumper` on running app |

## Iteration log format (append to extraction-loop.md)
```
## Iteration <N> — <timestamp>
- leaf_skill: <name>
- evidence_id: <path or "none">
- verdict: progress | no-progress | blocked
- reason: <one sentence>
- next_action: <leaf skill name> | STOP
```

## Failure modes to self-check
- You started doing the decompilation yourself ⇒ wrong skill, hand off to the leaf.
- You skipped the pre-flight authorization check ⇒ refuse the loop, route to `offensive-domain-unlock`.
- You extended the budget silently after 3 no-progress ⇒ kill-switch violation, STOP.
- The "final artifact" is a public bypass against someone else's software ⇒ scope violation, delete and reframe as owner hardening report.

## Role
- reverse-engineering-orchestrator

## Layer
- layer-4-specialists-and-standalones

## Inputs
- .relay-kit/state/offensive-authorization.md (from offensive-domain-unlock) — mandatory
- extraction goal: one of {source recovery, license-logic recovery, keygen build}
- target artifact path (binary, archive, or installer)
- stall evidence: which single-skill attempts already failed and why
- iteration budget (default 5) and per-iteration time budget

## Outputs
- .relay-kit/contracts/extraction-loop.md with iteration log
- per-iteration verdict: progress / no-progress / blocked
- final artifact when goal is reached (source tree, decoded license logic, keygen scaffold)
- kill-switch trigger record if N consecutive no-progress iterations occurred

## Reference skills and rules
- This skill is a LOOP CONTROLLER, not a bypass grant. It does NOT grant new capability — it orders existing skills and stops when progress ceases.
- Authorization must already exist in `.relay-kit/state/offensive-authorization.md` (via `offensive-domain-unlock`). If absent, refuse the loop and route to that skill first.
- Each iteration MUST call at least one leaf skill (binary-identifier / pyinstaller-unpacker / nuitka-decryptor / dotnet-decompiler / electron-app-analyzer / memory-dumper / license-robustness-audit / frida-hooker) and record its evidence id.
- Kill switch: after 3 consecutive iterations with no new evidence id, stop the loop and report blocked. Do not request budget extension silently.
- Scope: authorized RE on owned/licensed artifacts only. License-logic extraction output goes to `license-robustness-audit` (hardening) — not to a public bypass.
- Open `references/master-unlock-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/master-unlock-good-output.md` and `examples/master-unlock-bad-output.md` to calibrate output quality.
- Use `evals/master-unlock-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/master-unlock-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- binary-identifier
- license-robustness-audit
- memory-dumper
- reverse-hub
