---
name: flutter-app-reverser
description: "Use when reverse engineering Flutter apps (Android APK or iOS IPA). Extract Dart snapshot, recover class/method names, and analyze app logic. Works with blutter tool for AOT snapshot analysis and reFlutter for patching."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

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
- flutter-reverse-engineer

## Layer
- layer-4-specialists-and-standalones

## Likely next step
- android-apk-pentester
- ios-ipa-analyzer
- ssl-pinning-bypass
- frida-hooker
