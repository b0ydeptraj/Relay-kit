---
name: flutter-app-reverser
description: "Use when reverse engineering Flutter apps (Android APK or iOS IPA). Extract Dart snapshot, recover class/method names, and analyze app logic. Works with blutter tool for AOT snapshot analysis and reFlutter for patching."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when reverse engineering Flutter apps (Android APK or iOS IPA).

# Flutter App Reverser

> Recover Flutter/Dart source structure from AOT-compiled snapshots.

## Mission  
Analyze Flutter apps to recover Dart class names, method names, field names, and app logic from AOT snapshots.

## Mandatory scope checks
1. Confirm authorization
2. Identify Flutter version from libapp.so or App.framework
3. Choose tool: blutter / reFlutter / jadx (for wrapper code)
4. Extract libapp.so (Android) or App.framework/App (iOS)

## Analysis workflow
```
Android:
  1. apktool d app.apk
  2. cd app/lib/arm64-v8a/
  3. blutter libapp.so ./output
  4. Analyze output/asm/ and output/pp.txt

iOS:
  1. unzip App.ipa
  2. Find App.framework/App binary  
  3. blutter App ./output (if ARM64)
```

## blutter output
- `asm/` - Disassembled Dart methods
- `pp.txt` - Pool pointer table (class names, fields)
- `ida_script.py` - IDA rename script

## Role
- reverse-engineering-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with flutter-app-reverser findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside flutter-app-reverser's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/flutter-app-reverser-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/flutter-app-reverser-good-output.md` and `examples/flutter-app-reverser-bad-output.md` to calibrate output quality.
- Use `evals/flutter-app-reverser-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/flutter-app-reverser-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- flutter-app-reverser
- reverse-hub
- workflow-router
