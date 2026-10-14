---
name: tauri-unpacker
description: "Use when a lane needs tauri unpacker: Unpack Tauri desktop apps — extract embedded web assets (HTML/JS/CSS), Tauri config, IPC command map, and frontend license logic."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Unpack Tauri desktop apps — extract embedded web assets (HTML/JS/CSS), Tauri config, IPC command map, and frontend license logic.

# Tauri App Unpacker

## Purpose

Tauri apps embed a web frontend (HTML/JS/CSS) inside a native Rust binary.
The frontend often contains the license UI, API calls, and business logic
accessible without disassembly.  This skill extracts those embedded assets
and analyses the Tauri-specific IPC layer.

## Workflow

```
┌────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│ tauri-app.exe  │────▶│ unpack_tauri │────▶│ tauri-unpacked/     │
└────────────────┘     └──────────────┘     │  ├─ assets/         │
                                            │  │  ├─ index.html   │
                                            │  │  ├─ main.js      │
                                            │  │  └─ style.css    │
                                            │  └─ tauri_config.json│
                                            └─────────────────────┘
                              │
                              ▼
                       ┌───────────────┐     ┌───────────────────┐
                       │ analyze_tauri │────▶│ tauri_analysis.json│
                       └───────────────┘     └───────────────────┘
```

## Usage

```bash
# Extract assets
python tauri-unpacker/scripts/unpack_tauri.py app.exe --out output/tauri-unpacked

# Analyze extracted frontend
python tauri-unpacker/scripts/analyze_tauri.py output/tauri-unpacked --out output/tauri-analysis

# Full pipeline
python tauri-unpacker/scripts/unpack_tauri.py app.exe --out output/tauri-unpacked && \
python tauri-unpacker/scripts/analyze_tauri.py output/tauri-unpacked --out output/tauri-analysis
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
- .relay-kit/contracts/investigation-notes.md with tauri-unpacker findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside tauri-unpacker's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/tauri-unpacker-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/tauri-unpacker-good-output.md` and `examples/tauri-unpacker-bad-output.md` to calibrate output quality.
- Use `evals/tauri-unpacker-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/tauri-unpacker-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- tauri-unpacker
- reverse-hub
- workflow-router
