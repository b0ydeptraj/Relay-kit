# Code Stubs Index — Relay-kit Offensive Reference

Kho code template production-ready cho mảng RE, bypass, inject, và MMO automation.
Mỗi stub là starting point đã tested về cấu trúc — mở rộng trực tiếp thay vì viết lại từ đầu.

## Index

| File | Kỹ thuật | Compat | Dùng khi |
|---|---|---|---|
| [`dynamic-syscall-stub.hpp`](code-stubs/dynamic-syscall-stub.hpp) | Indirect Syscall (SSN resolver + gadget finder) | Win10/11 19041→22631+ x64 | Tránh hook tại KiSystemCall64; bypass EDR user-mode hooks |
| [`reflective-dll-loader.hpp`](code-stubs/reflective-dll-loader.hpp) | Reflective DLL Loading (no LoadLibrary, no CRT) | Win10/11 x64 | Inject DLL vào process mà không cần disk-backed PE; memory-only delivery |
| [`threadless-injection.hpp`](code-stubs/threadless-injection.hpp) | EarlyBird APC + Fiber Execution | Win10/11 x64 | Tránh CreateRemoteThread telemetry; alertable wait shellcode delivery |
| [`bezier-mouse.py`](code-stubs/bezier-mouse.py) | Bezier + Fitts's Law mouse trajectory | Windows (SendInput) | MMO automation: bypass pixel-bot / behavioral mouse detection |

## Extension Points

### Syscall Stub → Production Path
1. Implement `DoIndirectSyscall` bằng MASM `.asm` file (link với MSVC hoặc LLVM-MinGW).
2. Hoặc dùng Syswhispers3 (`python syswhispers.py --preset all --output syscalls`) để auto-generate stub per-function.
3. Kết hợp với `reflective-dll-loader.hpp`: resolve tất cả imports qua SSN thay vì GetProcAddress.

### Reflective Loader → Production Path
1. Port `ReflectiveLoader` vào `.asm` trampoline để tránh frame setup bởi compiler.
2. Import resolution: implement hash-based lookup (DJB2 hoặc ROT13) qua PEB InMemoryOrderModuleList.
3. Mark loaded sections với đúng protection (RX cho .text, R cho .rdata, RW cho .data) sau khi map.

### Threadless Injection → Production Path
1. Thêm **Module Stomping variant**: `NtMapViewOfSection` over `xpsservices.dll` để tránh `VirtualAlloc` anomaly detection.
2. Thêm **Phantom DLL Hollowing**: map clean DLL, write shellcode, set entry point.

### Bezier Mouse → Production Path
1. Tune `steps_per_100px` và `jitter_px` theo profile game target (FPS vs MMORPG có pattern khác nhau).
2. Thêm random scroll wheel events và window focus checks giữa các move sequences.
3. Record real human sessions và fit Bezier parameters để match distribution.

## OPSEC Reminders
- Luôn xóa stub files khỏi disk sau khi compile/load (fileless execution).
- Compile với `/GS-` (no stack cookies) và `/GL-` (no LTCG) để dễ control code layout.
- Strip PDB và debug symbols trước khi deploy.
- Test syscall SSNs trên exact target Windows build — SSN thay đổi theo build.
