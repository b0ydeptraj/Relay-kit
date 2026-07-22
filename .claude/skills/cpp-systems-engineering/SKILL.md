---
name: cpp-systems-engineering
description: Use when implementing or debugging C++ systems code: Windows/Linux native, RAII, memory management, Win32 API, COM, WTL, STL, multithreading, performance-critical paths, or driver-adjacent code.
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Produce correct, memory-safe, idiomatic C++ systems code with explicit ownership, RAII discipline, and documented Win32/POSIX API usage.

## Mandatory scope
1. Declare ownership model before writing: raw pointer vs unique_ptr vs shared_ptr vs RAII wrapper.
2. Use RAII for all resource acquisition: handles, sockets, file descriptors, locks.
3. Name the Win32/POSIX API surface explicitly: function signatures, error codes, and cleanup paths.
4. Document any UB risk: pointer arithmetic, reinterpret_cast, uninitialized memory, data races.
5. For multithreaded code: identify shared state, synchronization primitive, and lock ordering.
6. Capture compile + link command with exact flags (-std=c++17, /W4, /analyze if MSVC).

## Evidence contract
- compiles cleanly with named flags
- RAII ownership documented for every resource
- UB risks explicitly called out or eliminated
- Win32 error handling shown (GetLastError / HRESULT checked)

## Role
- cpp-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- story or tech-spec
- target platform (Windows/Linux/cross)
- existing C++ codebase if present

## Outputs
- C++ implementation with documented ownership
- compile command
- test evidence

## Reference skills and rules
- Prefer RAII wrappers over manual new/delete.
- Never use raw C-style casts where static_cast/reinterpret_cast is more explicit.
- Document every Win32 API call with its error-check pattern.
- Use /analyze or clang-tidy as static analysis gate before claiming done.
- Open `references/cpp-systems-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/cpp-systems-engineering-good-output.md` and `examples/cpp-systems-engineering-bad-output.md` to calibrate output quality.
- Use `evals/cpp-systems-engineering-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/cpp-systems-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- windows-native-internals
- binary-stealth-obfuscation
- process-injection-techniques
- desktop-imgui-development
- test-hub
- field-journal-evolution
