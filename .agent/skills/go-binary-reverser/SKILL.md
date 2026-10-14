---
name: go-binary-reverser
description: "Use when reverse engineering Go (Golang) binaries. Recover function names, package structure, and logic from stripped Go executables using IDA Pro, Ghidra, or go-exploit tools. Supports Go 1.16+ symbol recovery, goroutine analysis, and Go runtime structure mapping."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

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
- go-reverse-engineer

## Layer
- layer-4-specialists-and-standalones

## Likely next step
- binary-identifier
- binary-protection-bypass
- binary-patcher
- ida-nuitka-reconstructor
