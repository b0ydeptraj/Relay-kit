---
name: java-decompiler
description: "Use when a lane needs java decompiler: Decompile Java applications (JAR/WAR/APK/class) — extract archives, detect obfuscators, decompile bytecode to source, analyse license logic and secrets."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Decompile Java applications (JAR/WAR/APK/class) — extract archives, detect obfuscators, decompile bytecode to source, analyse license logic and secrets.

# Java Decompiler

## Purpose

Java bytecode (.class) retains nearly all source-level information, making
decompilation highly effective.  This skill extracts, decompiles, and analyses
Java applications across all packaging formats: JAR, WAR, EAR, APK, and raw
class files.

## Workflow

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│ target.jar / .apk│────▶│ decompile_java   │────▶│ java-decompiled/     │
└──────────────────┘     └──────────────────┘     │  ├─ src/             │
                                │                  │  ├─ manifest.json    │
                                │                  │  └─ obfuscation.json │
                                ▼                  └──────────────────────┘
                         ┌──────────────────┐     ┌──────────────────────┐
                         │  analyze_java    │────▶│ java_analysis.json   │
                         └──────────────────┘     └──────────────────────┘
```

## Usage

```bash
# Decompile a JAR
python java-decompiler/scripts/decompile_java.py app.jar --out output/java-decompiled

# Decompile an Android APK
python java-decompiler/scripts/decompile_java.py app.apk --out output/java-decompiled

# Decompile with specific tool
python java-decompiler/scripts/decompile_java.py app.jar --out output/java-decompiled --decompiler cfr

# Analyse decompiled source
python java-decompiler/scripts/analyze_java.py output/java-decompiled --out output/java-analysis
```

## Decompiler Priority

| Tool | Best for | Install |
|------|----------|---------|
| **CFR** | General JAR/class (best output quality) | Download cfr.jar |
| **Procyon** | Complex generics, lambdas | Download procyon-decompiler.jar |
| **FernFlower** | IntelliJ-style output | Download fernflower.jar |
| **JADX** | Android APK (dex → java directly) | `pip install jadx` or download |
| **javap** | Fallback bytecode listing | Included with JDK |

## Role
- reverse-engineering-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with java-decompiler findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside java-decompiler's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/java-decompiler-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/java-decompiler-good-output.md` and `examples/java-decompiler-bad-output.md` to calibrate output quality.
- Use `evals/java-decompiler-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/java-decompiler-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- java-decompiler
- reverse-hub
- workflow-router
