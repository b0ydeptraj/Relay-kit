---
name: binary-patcher
description: "Use when a lane needs binary patcher: Expert methodology for binary patching and bypass development. Focuses on Assembly modification (NOP, JMP, JE/JNE inversion) using debuggers like x64dbg. Includes automated patching scripts for applying modifications to binary files."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Expert methodology for binary patching and bypass development.

# Binary Patcher Skill

> Reverse engineer and patch binary applications to bypass license checks, enable premium features, or modify logic behavior.

> **Language rule**: All skill instructions use English.
> **Final summary presented to the user must be in Vietnamese.**

---

## Patching Methodology (The Laragon Strategy)

### 1. Identify the Branch (JE/JNE Bypass)
Most license checks involve a `CALL` to a validation function followed by a conditional jump (`JE`, `JNE`, `JZ`, `JNZ`).

- **Search**: Use "String References" in x64dbg to find error messages like `"License not valid"`.
- **Trace**: Follow the code execution upwards to find the branch that jumps to that error.
- **Patch**: Modify the branch to skip the error.

| Condition | Goal | Patch Strategy |
|-----------|------|----------------|
| `JE <Error>` | Skip error | Change to `NOP` (No Operation) |
| `JNE <Success>` | Force success | Change to `JMP <Success>` |
| `CALL <Check>` | Force true | Patch `EAX`/`RAX` to 1 after call |

---

### 2. Forced State (NOPing the "Kick-out")
If the app checks for "Commercial" or "Pro" status and kicks you to a different branch if failed:

- **Locate**: Find the jump that "kicks out" the Pro status.
- **Action**: Replace the jump with `NOP` (`0x90`). This ensures the code "falls through" to the Pro logic.

---

## Step 1 — Finding the Offset

In x64dbg, when you find a patch, look at the **File Offset** (not just the Virtual Address).
- **RVA to File Offset**: Right-click in x64dbg -> `Copy` -> `File Offset`.

---

## Step 2 — Automated Patching

Once you have identified the offsets and bytes, use `scripts/apply_patch.py` to create a permanent cracked binary.

```bash
# bash / WSL / Linux / macOS
python scripts/apply_patch.py target.exe \
  --patch <OFFSET> <ORIGINAL_HEX> <PATCH_HEX> \
  --out cracked.exe
```

```powershell
# Windows PowerShell (use backtick for line continuation)
python scripts\apply_patch.py target.exe `
  --patch <OFFSET> <ORIGINAL_HEX> <PATCH_HEX> `
  --out cracked.exe
```

**Example (based on Laragon guide):**
```bash
# Bypass Validation (JNE -> NOP) — bash
python scripts/apply_patch.py laragon.exe --patch 0x61C14 7505 9090 --out cracked.exe
```

```powershell
# Bypass Validation (JNE -> NOP) — PowerShell
python scripts\apply_patch.py laragon.exe --patch 0x61C14 7505 9090 --out cracked.exe
```

---

## Final Report to User (always in Vietnamese)

```
✅ Quy trình Patch Binary hoàn tất:

  📍 Địa chỉ tìm thấy  : <OFFSETS>
  🛠️ Lệnh đã vá       : <OPCODE_CHANGES> (e.g., JE -> NOP)
  📂 File đầu ra       : <CRACKED_BINARY>

▶  Hướng dẫn sử dụng:
   - Chạy file đã vá để kiểm tra tính năng Premium.
   - Nếu ứng dụng có cơ chế kiểm tra checksum, bạn cần vá thêm hàm xác thực file.
```

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Patch without verification | Always check the "Original Hex" matches before applying a patch |
| Modify sizes | Ensure `PATCH_HEX` is the same byte length as `ORIGINAL_HEX` (use `90` for padding) |
| Forget the File Offset | x64dbg shows memory addresses (VA); you need file offsets for permanent patching |

## Role
- reverse-engineering-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with binary-patcher findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside binary-patcher's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/binary-patcher-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/binary-patcher-good-output.md` and `examples/binary-patcher-bad-output.md` to calibrate output quality.
- Use `evals/binary-patcher-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/binary-patcher-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- binary-patcher
- reverse-hub
- workflow-router
