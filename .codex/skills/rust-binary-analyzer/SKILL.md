---
name: rust-binary-analyzer
description: "Use when a lane needs rust binary analyzer: Analyze Rust native binaries — demangle symbols, extract panic paths to reconstruct module map, detect frameworks (Tauri/Actix/Rocket/Axum), locate license validation logic."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Analyze Rust native binaries — demangle symbols, extract panic paths to reconstruct module map, detect frameworks (Tauri/Actix/Rocket/Axum), locate license validation logic.

# Rust Binary Analyzer

## Purpose

Rust compiles to native code with no bytecode/IL to decompile, but leaves rich
metadata in the binary: mangled symbol names, panic strings with source paths,
and framework-specific signatures.  This skill extracts and organises that
metadata to give the reverse engineer a high-level map of the application
*before* opening IDA or Ghidra.

## Workflow

```
┌────────────┐     ┌──────────────┐     ┌───────────────────┐
│ target.exe │────▶│ analyze_rust │────▶│ rust_analysis.json │
└────────────┘     └──────────────┘     └───────────────────┘
                         │
                         ├─ Demangle symbols (_RN… / _ZN…)
                         ├─ Extract panic paths → module tree
                         ├─ Detect framework (Tauri, Actix, …)
                         ├─ Find license-related functions
                         └─ Identify linked crates
```

## Usage

```bash
python rust-binary-analyzer/scripts/analyze_rust.py target.exe --out output/rust-analysis
python rust-binary-analyzer/scripts/analyze_rust.py target.exe --json output/rust_info.json
```

## Role
- reverse-engineering-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with rust-binary-analyzer findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside rust-binary-analyzer's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/rust-binary-analyzer-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/rust-binary-analyzer-good-output.md` and `examples/rust-binary-analyzer-bad-output.md` to calibrate output quality.
- Use `evals/rust-binary-analyzer-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/rust-binary-analyzer-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- rust-binary-analyzer
- reverse-hub
- workflow-router
