#!/usr/bin/env python3
"""
protection_bypass.py - Detect and bypass binary protections (VMProtect, Themida, ASPack, UPX).
Identifies protection type, extracts OEP (Original Entry Point), and guides unpacking.

Usage:
    python scripts/protection_bypass.py --binary app.exe --detect
    python scripts/protection_bypass.py --binary app.exe --unpack --output unpacked.exe
    python scripts/protection_bypass.py --binary app.exe --generate-script
    python scripts/protection_bypass.py --binary app.exe --find-oep
"""
import argparse
import os
import re
import struct
import subprocess
import sys

PROTECTION_SIGNATURES = {
    "UPX": {
        "signatures": [b"UPX0", b"UPX1", b"UPX2", b"UPX!"],
        "tool": "upx -d {binary} -o {output}",
        "difficulty": "Easy",
        "auto_unpack": True,
    },
    "ASPack": {
        "signatures": [b"ASPack", b".aspack", b"ASPr"],
        "tool": "aspunpack / manual OEP tracing",
        "difficulty": "Medium",
        "auto_unpack": False,
    },
    "VMProtect": {
        "signatures": [b"VMProtect", b"vmp0", b"vmp1", b"vmp2", b".vmp0", b".vmp1"],
        "tool": "OllyDbg VMP unpacker / x64dbg + VMP plugin",
        "difficulty": "Hard",
        "auto_unpack": False,
    },
    "Themida/WinLicense": {
        "signatures": [b"Themida", b"WinLicense", b".themida", b"SecureEngine"],
        "tool": "Themida unpacker / Tuts4You unpackers",
        "difficulty": "Hard",
        "auto_unpack": False,
    },
    "Enigma": {
        "signatures": [b"Enigma Protector", b".enigma1", b".enigma2"],
        "tool": "Enigma unpacker script",
        "difficulty": "Hard",
        "auto_unpack": False,
    },
    "MPRESS": {
        "signatures": [b"MPRESS1", b"MPRESS2"],
        "tool": "mpressunpack",
        "difficulty": "Easy",
        "auto_unpack": True,
    },
    "PECompact": {
        "signatures": [b"PECompact", b"pec1", b"pec2"],
        "tool": "PECompact decompressor",
        "difficulty": "Medium",
        "auto_unpack": False,
    },
    "Obsidium": {
        "signatures": [b"Obsidium", b".obsidium"],
        "tool": "Obsidium unpacker / manual",
        "difficulty": "Hard",
        "auto_unpack": False,
    },
    "dotNET_Reactor": {
        "signatures": [b"de4dot", b".NETReactor", b"CliSecure"],
        "tool": "de4dot: de4dot.exe {binary} -o {output}",
        "difficulty": "Easy-Medium",
        "auto_unpack": True,
    },
    "ConfuserEx": {
        "signatures": [b"ConfuserEx", b"Confuser"],
        "tool": "de4dot or NoFuserEx",
        "difficulty": "Medium",
        "auto_unpack": True,
    },
    "SmartAssembly": {
        "signatures": [b"SmartAssembly", b"SA.Obfuscation"],
        "tool": "de4dot deobfuscation",
        "difficulty": "Medium",
        "auto_unpack": True,
    },
}

PE_SECTIONS_INDICATORS = {
    "packed": [".packed", ".bind", ".crypted", "rmnet", "petite"],
    "encrypted": [b"\x00" * 64],  # Large zero regions
}


def read_pe_sections(binary_path: str) -> list:
    """Parse PE section headers."""
    sections = []
    with open(binary_path, "rb") as f:
        data = f.read()

    # Find PE header
    if data[:2] != b"MZ":
        return []
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset:pe_offset+4] != b"PE\x00\x00":
        return []

    # Machine type
    machine = struct.unpack_from("<H", data, pe_offset + 4)[0]
    is_64bit = machine == 0x8664

    # Number of sections
    num_sections = struct.unpack_from("<H", data, pe_offset + 6)[0]
    opt_header_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
    section_table_offset = pe_offset + 24 + opt_header_size

    for i in range(min(num_sections, 96)):
        offset = section_table_offset + i * 40
        if offset + 40 > len(data):
            break
        name = data[offset:offset+8].rstrip(b"\x00").decode("ascii", errors="replace")
        vsize   = struct.unpack_from("<I", data, offset + 8)[0]
        vaddr   = struct.unpack_from("<I", data, offset + 12)[0]
        rawsize = struct.unpack_from("<I", data, offset + 16)[0]
        rawptr  = struct.unpack_from("<I", data, offset + 20)[0]
        chars   = struct.unpack_from("<I", data, offset + 36)[0]
        sections.append({
            "name": name, "vaddr": hex(vaddr), "vsize": vsize,
            "rawsize": rawsize, "rawptr": hex(rawptr),
            "exec": bool(chars & 0x20000000),
            "writable": bool(chars & 0x80000000),
        })
    return sections


def detect_protection(binary_path: str) -> list:
    """Scan binary for known protection signatures."""
    with open(binary_path, "rb") as f:
        data = f.read()

    detections = []
    for prot_name, info in PROTECTION_SIGNATURES.items():
        for sig in info["signatures"]:
            if sig in data:
                detections.append({
                    "protection": prot_name,
                    "difficulty": info["difficulty"],
                    "auto_unpack": info["auto_unpack"],
                    "recommended_tool": info["tool"],
                    "signature_found": sig.decode("utf-8", errors="replace"),
                })
                break  # One hit per protection

    # Check section names for packing indicators
    sections = read_pe_sections(binary_path)
    for sec in sections:
        for indicator in PE_SECTIONS_INDICATORS["packed"]:
            if indicator.lower() in sec["name"].lower():
                detections.append({
                    "protection": f"Unknown packer (section: {sec['name']})",
                    "difficulty": "Unknown", "auto_unpack": False,
                    "recommended_tool": "x64dbg OEP finder",
                    "signature_found": sec["name"],
                })

    # Suspicious: executable + writable sections
    exec_writable = [s for s in sections if s["exec"] and s["writable"]]
    if exec_writable and not detections:
        detections.append({
            "protection": "Self-modifying/packed code (exec+writable sections)",
            "difficulty": "Medium", "auto_unpack": False,
            "recommended_tool": "Dynamic analysis + dump on OEP",
            "signature_found": str([s["name"] for s in exec_writable]),
        })

    return detections


def try_unpack(binary_path: str, output_path: str, protection: str) -> bool:
    """Attempt automatic unpacking for supported protections."""
    prot_info = PROTECTION_SIGNATURES.get(protection, {})
    if not prot_info.get("auto_unpack"):
        print(f"[-] {protection} requires manual unpacking")
        return False

    tool_template = prot_info.get("tool", "")
    cmd_str = tool_template.format(binary=f'"{binary_path}"', output=f'"{output_path}"')

    try:
        tool_name = cmd_str.split()[0]
        result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"[+] Unpacked: {output_path}")
            return True
        else:
            print(f"[-] {tool_name} failed: {result.stderr[:100]}")
    except FileNotFoundError:
        print(f"[-] Tool not found: {cmd_str.split()[0]}")
    except Exception as e:
        print(f"[-] Unpack error: {e}")
    return False


def generate_oep_finding_script(binary_path: str, protection: str) -> str:
    """Generate x64dbg/OllyDbg script for finding OEP."""
    scripts = {
        "VMProtect": """
// VMProtect OEP Finding Script (x64dbg)
// 1. Set hardware BP on executable memory page
// 2. Run until VMP stub completes
// 3. When execution hits non-VMP code: that's OEP
bp $main  // Set BP on binary entry
run
// After VMP unpacks: check EIP/RIP
// Dump process with PE-bear or Scylla
""",
        "UPX": """
// UPX OEP Script - set BP on POPAD/JMP pattern
// Pattern: 61 (POPAD) followed by JMP OEP
bp kernel32.GetProcAddress
run
// When hit: check ESP for OEP hint
// Or: bp on pushad/popad pattern
""",
        "Themida/WinLicense": """
// Themida OEP: Use Themida-specific plugins
// 1. x64dbg + OllyDumpEx
// 2. BP on TLS callbacks first
// 3. Trace until IAT reconstruction
""",
    }
    return scripts.get(protection, f"""
// Generic OEP finder for: {protection}
// Method 1: Hardware BP on first byte of original code section
// Method 2: ESP trick (BP on stack after initial PUSH)
// Method 3: Memory BP on write to decode buffer
// Tool: x64dbg + Scylla for IAT reconstruction
""")


def main():
    p = argparse.ArgumentParser(description="Binary protection detector and bypass")
    p.add_argument("--binary", required=True)
    p.add_argument("--detect", action="store_true")
    p.add_argument("--unpack", action="store_true")
    p.add_argument("--output")
    p.add_argument("--generate-script", action="store_true")
    p.add_argument("--find-oep", action="store_true")
    args = p.parse_args()

    if not os.path.exists(args.binary):
        print(f"[-] File not found: {args.binary}"); sys.exit(1)

    size_kb = os.path.getsize(args.binary) // 1024
    print(f"[*] Analyzing: {args.binary} ({size_kb} KB)")

    sections = read_pe_sections(args.binary)
    if sections:
        print(f"[*] PE sections ({len(sections)}):")
        for s in sections:
            flags = ("X" if s["exec"] else "-") + ("W" if s["writable"] else "-")
            print(f"    {s['name']:<12} vaddr:{s['vaddr']}  size:{s['rawsize']:>8}  [{flags}]")

    detections = detect_protection(args.binary)
    if not detections:
        print("\n[*] No known protection detected (may be custom/unknown)")
    else:
        print(f"\n[*] Detected {len(detections)} protection(s):")
        for d in detections:
            print(f"\n  [{d['protection']}]")
            print(f"    Difficulty : {d['difficulty']}")
            print(f"    Auto-unpack: {'YES' if d['auto_unpack'] else 'NO (manual required)'}")
            print(f"    Tool       : {d['recommended_tool']}")

    if args.unpack and detections:
        out = args.output or args.binary.replace(".exe", "_unpacked.exe")
        for d in detections:
            if d["auto_unpack"]:
                print(f"\n[*] Attempting auto-unpack ({d['protection']})...")
                if try_unpack(args.binary, out, d["protection"]):
                    break

    if args.generate_script and detections:
        prot = detections[0]["protection"]
        script = generate_oep_finding_script(args.binary, prot)
        script_path = args.binary + "_oep_script.txt"
        with open(script_path, "w") as f:
            f.write(script)
        print(f"\n[+] OEP script: {script_path}")


if __name__ == "__main__":
    main()
