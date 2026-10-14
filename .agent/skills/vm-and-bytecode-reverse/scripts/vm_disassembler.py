#!/usr/bin/env python3
"""
vm_disassembler.py - Custom VM opcode analyzer and disassembler.
Identifies VM handler tables, maps opcodes to operations, and lifts bytecode.

Usage:
    python scripts/vm_disassembler.py --binary app.exe --find-handlers
    python scripts/vm_disassembler.py --binary app.exe --bytecode-offset 0x1000 --bytecode-size 256
    python scripts/vm_disassembler.py --binary app.exe --auto-lift --output vm_listing.txt
    python scripts/vm_disassembler.py --bytecode-file vm.bin --opcode-map opcodes.json
"""
import argparse
import json
import os
import re
import struct
import sys

# Common VM patterns in malware/protectors
VM_PATTERNS = {
    "dispatch_loop": [
        b"\x8a\x06\x46",         # MOV AL,[ESI]; INC ESI (fetch opcode)
        b"\x8b\x07\x47",         # MOV EAX,[EDI]; INC EDI
        b"\x0f\xb6\x06\x46",     # MOVZX EAX,BYTE PTR [ESI]; INC ESI
        b"\xff\x24\x85",         # JMP [EAX*4+table] (dispatch table)
        b"\xff\x24\xc5",         # JMP [EAX*8+table]
    ],
    "stack_operations": [
        b"\x83\xc4\x04",         # ADD ESP,4 (pop-like)
        b"\x83\xec\x04",         # SUB ESP,4 (push-like)
        b"\x8f\x05",             # POP [addr]
    ],
    "handler_prologue": [
        b"\x55\x8b\xec",         # PUSH EBP; MOV EBP,ESP
        b"\x56\x57",             # PUSH ESI; PUSH EDI
    ],
}

# Generic opcode names for unknown VMs (educated guesses)
OPCODE_MNEMONICS = {
    0x00: "NOP",    0x01: "PUSH",   0x02: "POP",    0x03: "ADD",
    0x04: "SUB",    0x05: "MUL",    0x06: "DIV",    0x07: "MOD",
    0x08: "AND",    0x09: "OR",     0x0A: "XOR",    0x0B: "NOT",
    0x0C: "SHL",    0x0D: "SHR",   0x0E: "JMP",    0x0F: "JZ",
    0x10: "JNZ",    0x11: "CALL",  0x12: "RET",    0x13: "LOAD",
    0x14: "STORE",  0x15: "MOV",   0x16: "CMP",    0x17: "HALT",
    0x18: "PUSH_IMM", 0x19: "LOAD_LOCAL", 0x1A: "STORE_LOCAL",
    0x1B: "INVOKE", 0x1C: "NEW",   0x1D: "THROW",  0x1E: "CATCH",
}


def find_dispatch_tables(data: bytes) -> list:
    """Find potential VM dispatch tables (arrays of function pointers)."""
    tables = []
    # Look for sequences of 4-byte aligned pointers in typical code range
    base_heuristic = 0x400000  # Common PE base

    for i in range(0, len(data) - 256 * 4, 4):
        # Check for 32 consecutive valid-looking pointers
        ptrs = struct.unpack_from(f"<{32}I", data, i)
        valid = all(0x401000 <= p <= 0x800000 for p in ptrs)
        if valid:
            tables.append({
                "offset": hex(i),
                "entries": len(ptrs),
                "first_ptr": hex(ptrs[0]),
                "last_ptr": hex(ptrs[-1]),
                "span": hex(ptrs[-1] - ptrs[0]),
            })

    # Limit to most likely tables
    return tables[:10]


def find_vm_handlers(data: bytes) -> list:
    """Find VM handler prologues."""
    handlers = []
    for pattern_name, patterns in VM_PATTERNS.items():
        for pat in patterns:
            for i in range(len(data) - len(pat)):
                if data[i:i+len(pat)] == pat:
                    handlers.append({
                        "pattern": pattern_name,
                        "offset": hex(i),
                        "bytes": pat.hex(),
                        "context": data[i:i+16].hex(),
                    })
    return handlers[:50]


def disassemble_bytecode(bytecode: bytes, opcode_map: dict = None) -> list:
    """Simple linear sweep disassembler for bytecode."""
    mnemonics = opcode_map or OPCODE_MNEMONICS
    instructions = []
    i = 0
    while i < len(bytecode):
        op = bytecode[i]
        mnem = mnemonics.get(op, f"OP_{op:02X}")
        offset = i

        # Determine operand size based on mnemonic
        operand = None
        operand_size = 0

        if mnem in ("PUSH_IMM", "JMP", "JZ", "JNZ", "CALL", "LOAD", "STORE"):
            if i + 4 < len(bytecode):
                operand = struct.unpack_from("<I", bytecode, i + 1)[0]
                operand_size = 4
            elif i + 2 < len(bytecode):
                operand = struct.unpack_from("<H", bytecode, i + 1)[0]
                operand_size = 2
        elif mnem in ("LOAD_LOCAL", "STORE_LOCAL", "MOV"):
            if i + 1 < len(bytecode):
                operand = bytecode[i + 1]
                operand_size = 1

        instr = {"offset": offset, "opcode": op, "mnemonic": mnem}
        if operand is not None:
            instr["operand"] = operand
            instr["operand_str"] = hex(operand) if op not in (0x18,) else str(operand)
        instructions.append(instr)
        i += 1 + operand_size

    return instructions


def format_listing(instructions: list) -> str:
    """Format disassembled instructions as a listing."""
    lines = ["VM Bytecode Disassembly", "=" * 40]
    for ins in instructions:
        offset = f"  {ins['offset']:>6X}:"
        op = f"{ins['opcode']:02X}"
        mnem = f"{ins['mnemonic']:<15}"
        operand = ins.get("operand_str", "")
        lines.append(f"{offset}  {op}  {mnem} {operand}")
    return "\n".join(lines)


def analyze_bytecode_entropy(bytecode: bytes) -> dict:
    """Calculate byte frequency and entropy for bytecode."""
    from collections import Counter
    import math
    counts = Counter(bytecode)
    total = len(bytecode)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)
    most_common = counts.most_common(5)
    return {
        "length": total,
        "unique_opcodes": len(counts),
        "entropy": round(entropy, 2),
        "most_frequent": [(hex(b), count) for b, count in most_common],
        "likely_encrypted": entropy > 7.0,
    }


def main():
    p = argparse.ArgumentParser(description="VM opcode analyzer and bytecode disassembler")
    p.add_argument("--binary", help="PE binary to analyze")
    p.add_argument("--find-handlers", action="store_true")
    p.add_argument("--bytecode-offset", help="Bytecode section offset (hex)")
    p.add_argument("--bytecode-size", type=int, default=256)
    p.add_argument("--auto-lift", action="store_true")
    p.add_argument("--bytecode-file", help="Raw bytecode file")
    p.add_argument("--opcode-map", help="JSON file: {\"0\":\"NOP\", \"1\":\"PUSH\",...}")
    p.add_argument("--output")
    args = p.parse_args()

    opcode_map = None
    if args.opcode_map and os.path.exists(args.opcode_map):
        with open(args.opcode_map) as f:
            raw_map = json.load(f)
            opcode_map = {int(k, 16) if k.startswith("0x") else int(k): v
                          for k, v in raw_map.items()}

    # Process bytecode file directly
    if args.bytecode_file:
        with open(args.bytecode_file, "rb") as f:
            bytecode = f.read()
        print(f"[*] Bytecode: {len(bytecode)} bytes")
        entropy = analyze_bytecode_entropy(bytecode)
        print(f"[*] Entropy: {entropy['entropy']} | Unique opcodes: {entropy['unique_opcodes']}")
        if entropy["likely_encrypted"]:
            print(f"[!] High entropy ({entropy['entropy']}) - bytecode may be encrypted")
        else:
            instructions = disassemble_bytecode(bytecode, opcode_map)
            listing = format_listing(instructions)
            print(listing[:3000])
            if args.output:
                with open(args.output, "w") as f:
                    f.write(listing)
                print(f"\n[+] Saved: {args.output}")
        return

    # Process PE binary
    if not args.binary or not os.path.exists(args.binary):
        print("[-] --binary or --bytecode-file required"); sys.exit(1)

    with open(args.binary, "rb") as f:
        data = f.read()
    print(f"[*] Binary: {args.binary} ({len(data):,} bytes)")

    if args.find_handlers or args.auto_lift:
        handlers = find_vm_handlers(data)
        print(f"\n[*] VM patterns found: {len(handlers)}")
        for h in handlers[:10]:
            print(f"  [{h['pattern']}] offset:{h['offset']} | bytes: {h['bytes']}")

        tables = find_dispatch_tables(data)
        print(f"\n[*] Dispatch table candidates: {len(tables)}")
        for t in tables[:5]:
            print(f"  offset:{t['offset']} | entries:{t['entries']} | span:{t['span']}")

    if args.bytecode_offset:
        offset = int(args.bytecode_offset, 16)
        bytecode = data[offset:offset + args.bytecode_size]
        print(f"\n[*] Disassembling bytecode at {args.bytecode_offset}:")
        entropy = analyze_bytecode_entropy(bytecode)
        print(f"    Entropy: {entropy['entropy']} | Unique: {entropy['unique_opcodes']}")
        instructions = disassemble_bytecode(bytecode, opcode_map)
        listing = format_listing(instructions)
        print(listing)
        if args.output:
            with open(args.output, "w") as f:
                f.write(listing)
            print(f"[+] Saved: {args.output}")


if __name__ == "__main__":
    main()
