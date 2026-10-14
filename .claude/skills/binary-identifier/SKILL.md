---
name: binary-identifier
description: "Use when a lane needs binary identifier: Fingerprint binary executables to identify programming languages, compilers, packers, and obfuscators. Uses signature scanning (PE sections, strings, function names) to determine the technology stack."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Fingerprint binary executables to identify programming languages, compilers, packers, and obfuscators.

# Binary Identifier Skill

> Analyze any executable (.exe, .pyd, .dll) to determine how it was built and protected. Essential for choosing the right reverse engineering strategy.

> **Language rule**: All skill instructions use English.
> **Final summary presented to the user must be in Vietnamese.**

---

## Capabilities

This skill can detect:
- **Languages**: Python (Nuitka/PyInstaller), Go, Rust, C#, C++, Java, Delphi.
- **Packers**: UPX, VMProtect, Themida, Enigma.
- **Encryption**: Indicators of Fernet, AES, or custom XOR layers.

---

## Step 1 — Quick Identification

Run `scripts/identify_app.py`:

```bash
# bash / WSL / Linux / macOS
python scripts/identify_app.py path/to/target.exe
```

```powershell
# Windows PowerShell
python scripts\identify_app.py 'C:\Program Files\MyApp\target.exe'
```

**What it looks for:**
- **PE Sections**: Names like `.vmp0` (VMProtect), `UPX0` (UPX), `.rdata` (Nuitka constants).
- **Strings**: Magic constants like `Py_Initialize`, `go.itab.`, `rustc`.
- **Imports**: DLLs like `mscoree.dll` (.NET), `python3.dll`.

---

## Step 2 — Analysis Strategy Selection

Based on the identification results:

| Result | Strategy |
|--------|----------|
| **Python (Nuitka)** | Use `nuitka-decryptor` or `writerpro-pentest`. |
| **Python (PyInstaller)** | Use `pyinstxtractor` to recover source. |
| **C# / .NET** | Use `dnSpy` for near-perfect source code recovery. |
| **UPX** | Run `upx -d file.exe` to unpack. |
| **Go / Rust** | Use specialized IDA/Ghidra plugins for symbol recovery. |

---

## Final Report to User (always in Vietnamese)

```
🔍 Kết quả định danh ứng dụng:

  🌐 Ngôn ngữ/Trình biên dịch : <LANGUAGE>
  🛡️ Packer/Bảo mật           : <PACKER_TYPE>
  🔑 Dấu hiệu mã hóa          : <ENCRYPTION_HINTS>

▶  Khuyến nghị:
   - <Dựa trên kết quả, hãy sử dụng skill tương ứng hoặc công cụ phù hợp>
```

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Start decrypting without identifying the language | Different languages use different encryption libraries |
| Assume all Python apps use Nuitka | PyInstaller is equally common and requires different tools |
| Skip the identification step | Identifying a packer like UPX saves hours of reverse engineering |

## Role
- reverse-engineering-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with binary-identifier findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside binary-identifier's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/binary-identifier-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/binary-identifier-good-output.md` and `examples/binary-identifier-bad-output.md` to calibrate output quality.
- Use `evals/binary-identifier-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/binary-identifier-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- binary-identifier
- reverse-hub
- workflow-router
