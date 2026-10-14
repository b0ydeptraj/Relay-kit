---
name: go-binary-reverser
description: "Use when reverse engineering Go (Golang) binaries. Recover function names, package structure, and logic from stripped Go executables using IDA Pro, Ghidra, or go-exploit tools. Supports Go 1.16+ symbol recovery, goroutine analysis, and Go runtime structure mapping."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when reverse engineering Go (Golang) binaries.

# Go Binary Reverser

> Recover Go binary structure: packages, functions, goroutines, and embedded data.

## Mission
Analyze stripped Go binaries to recover meaningful function names, data structures, and business logic.

## Mandatory scope checks
1. Confirm authorized analysis
2. Identify Go version from binary (pclntab magic bytes)
3. Choose tool: GoReSym / IDA Go plugin / Ghidra + go-loader / radare2
4. Identify entry point and main.main
5. Map goroutine scheduler patterns

## Go binary features
| Feature | Location | Recovery tool |
|---|---|---|
| Function names | pclntab section | GoReSym, objdump |
| Package names | pclntab + moduledata | GoReSym |
| Type info | rodata section | IDA + go-type-parser |
| Strings | .data + .rodata | strings, GoReSym |
| Goroutines | runtime.goexit chain | manual trace |

## Quick analysis
```bash
gotools: go tool nm ./binary | grep -v "^U" | sort -k2
GoReSym: GoReSym.exe ./binary > symbols.json
Ghidra: load + go-loader script → auto-rename functions
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
- .relay-kit/contracts/investigation-notes.md with go-binary-reverser findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside go-binary-reverser's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/go-binary-reverser-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/go-binary-reverser-good-output.md` and `examples/go-binary-reverser-bad-output.md` to calibrate output quality.
- Use `evals/go-binary-reverser-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/go-binary-reverser-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- go-binary-reverser
- reverse-hub
- workflow-router
