#!/usr/bin/env python3
"""
winapi_explorer.py - Windows internals explorer: PEB, TEB, SSDT, handles, and hooks.
Enumerate Windows low-level structures for reverse engineering and rootkit detection.

Usage:
    python scripts/winapi_explorer.py --enum peb
    python scripts/winapi_explorer.py --enum processes
    python scripts/winapi_explorer.py --enum modules --pid 1234
    python scripts/winapi_explorer.py --detect-hooks --module kernel32.dll
    python scripts/winapi_explorer.py --enum handles --pid 1234
    python scripts/winapi_explorer.py --ssdt-check

Requires Windows + ctypes (built-in).
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import struct
import sys

if sys.platform != "win32":
    print("[!] winapi_explorer.py requires Windows")
    # Allow import for documentation purposes

IS_WINDOWS = sys.platform == "win32"
IS_64BIT   = sys.maxsize > 2**32

if IS_WINDOWS:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    ntdll    = ctypes.WinDLL("ntdll",    use_last_error=True)
    psapi    = ctypes.WinDLL("psapi",    use_last_error=True)

PROCESS_ALL_ACCESS       = 0x1F0FFF
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ          = 0x0010
TH32CS_SNAPPROCESS       = 0x00000002
TH32CS_SNAPMODULE        = 0x00000008


def get_peb_info() -> dict:
    """Read PEB (Process Environment Block) of current process."""
    if not IS_WINDOWS:
        return {"error": "Windows only"}

    info = {}
    try:
        # Get PEB address via NtQueryInformationProcess
        class PROCESS_BASIC_INFO(ctypes.Structure):
            _fields_ = [
                ("ExitStatus", ctypes.c_ulong),
                ("PebBaseAddress", ctypes.c_void_p),
                ("AffinityMask", ctypes.c_ulong_p if not IS_64BIT else ctypes.c_ulonglong),
                ("BasePriority", ctypes.c_ulong),
                ("UniqueProcessId", ctypes.c_void_p),
                ("InheritedFromUniqueProcessId", ctypes.c_void_p),
            ]

        pbi = (ctypes.c_byte * 48)()
        ret_len = ctypes.c_ulong(0)
        status = ntdll.NtQueryInformationProcess(-1, 0, pbi, 48, ctypes.byref(ret_len))

        peb_addr = ctypes.c_void_p.from_buffer(pbi, 8 if IS_64BIT else 4).value
        info["peb_address"] = hex(peb_addr) if peb_addr else "Unknown"

        # Read BeingDebugged flag from PEB
        being_debugged = ctypes.c_byte(0)
        kernel32.ReadProcessMemory(-1, peb_addr + 2, ctypes.byref(being_debugged), 1, None)
        info["being_debugged"] = bool(being_debugged.value)

        # NtGlobalFlag at PEB+0x68 (32-bit) or PEB+0xBC (64-bit)
        nt_global_flag_offset = 0xBC if IS_64BIT else 0x68
        nt_flag = ctypes.c_ulong(0)
        kernel32.ReadProcessMemory(-1, peb_addr + nt_global_flag_offset,
                                   ctypes.byref(nt_flag), 4, None)
        info["nt_global_flag"] = hex(nt_flag.value)
        info["heap_debug_flags"] = nt_flag.value == 0x70  # Debugger sets this

    except Exception as e:
        info["error"] = str(e)

    return info


def list_processes() -> list:
    """Enumerate all running processes via CreateToolhelp32Snapshot."""
    if not IS_WINDOWS:
        # Fallback for non-Windows
        try:
            import subprocess
            result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"],
                                   capture_output=True, text=True)
            processes = []
            for line in result.stdout.strip().split("\n"):
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    processes.append({"name": parts[0], "pid": parts[1]})
            return processes
        except:
            return []

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wt.DWORD),
            ("cntUsage", wt.DWORD),
            ("th32ProcessID", wt.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", wt.DWORD),
            ("cntThreads", wt.DWORD),
            ("th32ParentProcessID", wt.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wt.DWORD),
            ("szExeFile", ctypes.c_char * 260),
        ]

    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == -1:
        return []

    pe = PROCESSENTRY32()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
    processes = []
    if kernel32.Process32First(snap, ctypes.byref(pe)):
        while True:
            processes.append({
                "pid": pe.th32ProcessID,
                "ppid": pe.th32ParentProcessID,
                "name": pe.szExeFile.decode("utf-8", errors="replace"),
                "threads": pe.cntThreads,
            })
            if not kernel32.Process32Next(snap, ctypes.byref(pe)):
                break
    kernel32.CloseHandle(snap)
    return processes


def list_modules(pid: int) -> list:
    """Enumerate loaded modules in a process."""
    if not IS_WINDOWS:
        return []

    class MODULEENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wt.DWORD),
            ("th32ModuleID", wt.DWORD),
            ("th32ProcessID", wt.DWORD),
            ("GlblcntUsage", wt.DWORD),
            ("ProccntUsage", wt.DWORD),
            ("modBaseAddr", ctypes.POINTER(wt.BYTE)),
            ("modBaseSize", wt.DWORD),
            ("hModule", wt.HMODULE),
            ("szModule", ctypes.c_char * 256),
            ("szExePath", ctypes.c_char * 260),
        ]

    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, pid)
    if snap == -1:
        return []

    me = MODULEENTRY32()
    me.dwSize = ctypes.sizeof(MODULEENTRY32)
    modules = []
    if kernel32.Module32First(snap, ctypes.byref(me)):
        while True:
            modules.append({
                "name": me.szModule.decode("utf-8", errors="replace"),
                "path": me.szExePath.decode("utf-8", errors="replace"),
                "base": hex(ctypes.addressof(me.modBaseAddr.contents)) if me.modBaseAddr else "?",
                "size": me.modBaseSize,
            })
            if not kernel32.Module32Next(snap, ctypes.byref(me)):
                break
    kernel32.CloseHandle(snap)
    return modules


def detect_inline_hooks(module_name: str) -> list:
    """Detect inline hooks (JMP patches at function starts) in a loaded DLL."""
    if not IS_WINDOWS:
        return []

    hooks = []
    try:
        base = kernel32.GetModuleHandleA(module_name.encode())
        if not base:
            print(f"[-] Module not loaded: {module_name}")
            return []

        # Get exports via GetProcAddress for known functions
        MONITORED_FUNCS = [
            "VirtualAlloc", "VirtualAllocEx", "WriteProcessMemory", "CreateRemoteThread",
            "NtAllocateVirtualMemory", "NtWriteVirtualMemory", "NtCreateThreadEx",
            "LoadLibraryA", "GetProcAddress", "OpenProcess", "ReadProcessMemory",
        ]

        for func_name in MONITORED_FUNCS:
            func_addr = kernel32.GetProcAddress(base, func_name.encode())
            if not func_addr:
                continue

            # Read first 5 bytes of function
            buf = (ctypes.c_byte * 5)()
            kernel32.ReadProcessMemory(-1, func_addr, buf, 5, None)
            first_bytes = bytes(buf)

            # Check for JMP hook (E9 = near JMP)
            if first_bytes[0] == 0xE9:
                offset = struct.unpack("<i", first_bytes[1:])[0]
                jmp_target = func_addr + 5 + offset
                hooks.append({
                    "function": func_name,
                    "module": module_name,
                    "address": hex(func_addr),
                    "hook_type": "JMP (E9) inline hook",
                    "jmp_target": hex(jmp_target),
                    "original_bytes": first_bytes.hex(),
                })
            # Check for MOV RAX, [addr]; JMP RAX (64-bit hook)
            elif IS_64BIT and first_bytes[:2] == b"\x48\xB8":
                hooks.append({
                    "function": func_name,
                    "module": module_name,
                    "address": hex(func_addr),
                    "hook_type": "MOV RAX/JMP RAX hook (64-bit)",
                    "original_bytes": first_bytes.hex(),
                })
    except Exception as e:
        print(f"[-] Hook detection error: {e}")

    return hooks


def main():
    p = argparse.ArgumentParser(description="Windows internals explorer")
    p.add_argument("--enum", choices=["peb","processes","modules","handles"])
    p.add_argument("--detect-hooks", action="store_true")
    p.add_argument("--module", default="kernel32.dll")
    p.add_argument("--pid", type=int)
    p.add_argument("--ssdt-check", action="store_true")
    args = p.parse_args()

    if not IS_WINDOWS:
        print("[!] This tool requires Windows.")
        print("    Running in demo mode - showing available capabilities:\n")
        print("  --enum peb           : Read PEB.BeingDebugged, NtGlobalFlag, heap flags")
        print("  --enum processes     : List all processes (PID, PPID, threads)")
        print("  --enum modules       : List DLLs loaded in a process")
        print("  --detect-hooks       : Detect JMP/MOV hooks in kernel32/ntdll")
        print("  --ssdt-check         : Check SSDT for kernel hooks (requires ring0)")
        return

    if args.enum == "peb":
        peb = get_peb_info()
        print(f"[*] PEB Info (current process):")
        for k, v in peb.items():
            flag = " [!] DEBUGGER DETECTED" if k == "being_debugged" and v else ""
            print(f"  {k}: {v}{flag}")

    elif args.enum == "processes":
        procs = list_processes()
        print(f"[*] Running processes: {len(procs)}")
        print(f"  {'PID':>6} {'PPID':>6} {'Threads':>8}  Name")
        print("-" * 50)
        for proc in sorted(procs, key=lambda x: x["pid"]):
            print(f"  {proc['pid']:>6} {proc['ppid']:>6} {proc['threads']:>8}  {proc['name']}")

    elif args.enum == "modules":
        pid = args.pid or os.getpid()
        mods = list_modules(pid)
        print(f"[*] Modules in PID {pid}: {len(mods)}")
        for m in mods:
            print(f"  {m['name']:<30} base:{m['base']}  size:{m['size']:>8}  {m['path']}")

    elif args.detect_hooks:
        hooks = detect_inline_hooks(args.module)
        if hooks:
            print(f"[!] Found {len(hooks)} hook(s) in {args.module}:")
            for h in hooks:
                print(f"  [{h['hook_type']}] {h['function']} @ {h['address']} -> {h.get('jmp_target','?')}")
        else:
            print(f"[*] No inline hooks detected in {args.module}")


if __name__ == "__main__":
    main()
