#!/usr/bin/env python3
"""
go_analyzer.py - Go binary analysis: extract symbols, strings, version, and goroutine info.

Usage:
    python scripts/go_analyzer.py --binary ./app --action symbols
    python scripts/go_analyzer.py --binary ./app --action version
    python scripts/go_analyzer.py --binary ./app --action strings --min-len 10
    python scripts/go_analyzer.py --binary ./app --action goroutines
    python scripts/go_analyzer.py --binary ./app --action full --output report.json
"""
import argparse
import json
import os
import re
import struct
import subprocess
import sys

GO_MAGIC = {
    b"\xfb\xff\xff\xff\x00\x00": "Go 1.2-1.15",
    b"\xfa\xff\xff\xff\x00\x00": "Go 1.16",
    b"\xf0\xff\xff\xff\x00\x00": "Go 1.18+",
    b"\xf1\xff\xff\xff\x00\x00": "Go 1.20+",
}

GOROUTINE_MARKERS = [b"runtime.goexit", b"runtime.main", b"runtime.newproc"]


def detect_go_version(binary_path: str) -> str:
    """Detect Go version from pclntab magic bytes."""
    with open(binary_path, "rb") as f:
        data = f.read(1024 * 1024)  # Read 1MB

    for magic, version in GO_MAGIC.items():
        if magic in data:
            return version

    # Try Go build info
    try:
        result = subprocess.run(["go", "version", "-m", binary_path],
                                capture_output=True, text=True)
        if "go" in result.stdout.lower():
            m = re.search(r"go(\d+\.\d+[.\d]*)", result.stdout)
            if m: return f"Go {m.group(1)}"
    except:
        pass

    # Try strings
    strings_result = extract_strings(binary_path, min_len=10)
    for s in strings_result[:200]:
        m = re.search(r"go(\d+\.\d+[.\d]*)", s)
        if m: return f"Go {m.group(1)}"

    return "Unknown Go version"


def extract_symbols(binary_path: str) -> list:
    """Extract Go symbols using nm, objdump, or GoReSym."""
    symbols = []

    # Try 'go tool nm'
    try:
        result = subprocess.run(["go", "tool", "nm", binary_path],
                                capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                parts = line.strip().split()
                if len(parts) >= 3:
                    symbols.append({"addr": parts[0], "type": parts[1], "name": parts[2]})
            return symbols
    except:
        pass

    # Try nm (Linux/Unix)
    try:
        result = subprocess.run(["nm", binary_path], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                parts = line.strip().split()
                if len(parts) >= 3:
                    symbols.append({"addr": parts[0], "type": parts[1], "name": parts[2]})
            return symbols
    except:
        pass

    # Try GoReSym if available
    try:
        result = subprocess.run(["GoReSym", binary_path], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for fn in data.get("UserFunctions", []):
                symbols.append({"addr": hex(fn.get("Start",0)), "type": "T", "name": fn.get("FullName","")})
            return symbols
    except:
        pass

    # Fallback: extract string patterns that look like Go symbols
    with open(binary_path, "rb") as f:
        content = f.read()
    pattern = rb"(?:main|runtime|sync|net|http|fmt|os|io)\.[A-Za-z][A-Za-z0-9_.]+"
    found = set(m.decode("utf-8", errors="ignore") for m in re.findall(pattern, content))
    return [{"name": s, "type": "T", "addr": "?"} for s in sorted(found)]


def extract_strings(binary_path: str, min_len: int = 8) -> list:
    """Extract strings from binary."""
    try:
        result = subprocess.run(["strings", f"-n{min_len}", binary_path],
                                capture_output=True, text=True, timeout=30)
        return result.stdout.split("\n") if result.returncode == 0 else []
    except:
        # Fallback: Python implementation
        with open(binary_path, "rb") as f:
            data = f.read()
        strings = re.findall(rb"[ -~]{" + str(min_len).encode() + rb",}", data)
        return [s.decode("utf-8", errors="ignore") for s in strings]


def find_goroutines(binary_path: str) -> dict:
    """Find goroutine-related patterns in binary."""
    with open(binary_path, "rb") as f:
        data = f.read()
    found = {}
    for marker in GOROUTINE_MARKERS:
        offsets = [i for i in range(len(data)) if data[i:i+len(marker)] == marker]
        if offsets:
            found[marker.decode()] = [hex(o) for o in offsets[:5]]
    return found


def analyze_full(binary_path: str) -> dict:
    print(f"[*] Analyzing: {binary_path} ({os.path.getsize(binary_path):,} bytes)")
    report = {
        "file": binary_path,
        "size_bytes": os.path.getsize(binary_path),
        "go_version": detect_go_version(binary_path),
        "symbols": extract_symbols(binary_path)[:100],
        "goroutine_markers": find_goroutines(binary_path),
        "interesting_strings": [],
    }
    all_strings = extract_strings(binary_path, 12)
    interesting = [s for s in all_strings if any(kw in s.lower() for kw in
                    ["password","secret","key","token","api","http","url","sql","admin","config"])]
    report["interesting_strings"] = interesting[:50]
    print(f"  Go version: {report['go_version']}")
    print(f"  Symbols: {len(report['symbols'])}")
    print(f"  Goroutine markers: {len(report['goroutine_markers'])}")
    print(f"  Interesting strings: {len(report['interesting_strings'])}")
    return report


def main():
    p = argparse.ArgumentParser(description="Go binary analyzer")
    p.add_argument("--binary", required=True)
    p.add_argument("--action", choices=["version","symbols","strings","goroutines","full"], default="full")
    p.add_argument("--min-len", type=int, default=8)
    p.add_argument("--output", help="Output JSON")
    args = p.parse_args()

    if not os.path.exists(args.binary):
        print(f"[-] Binary not found: {args.binary}"); sys.exit(1)

    if args.action == "version":
        v = detect_go_version(args.binary)
        print(f"[*] Version: {v}")
    elif args.action == "symbols":
        syms = extract_symbols(args.binary)
        print(f"[*] {len(syms)} symbols:")
        for s in syms[:30]:
            print(f"  {s['addr']:>18} {s['type']} {s['name']}")
    elif args.action == "strings":
        strings = extract_strings(args.binary, args.min_len)
        print(f"[*] {len(strings)} strings (>={args.min_len} chars):")
        for s in strings[:50]:
            print(f"  {s[:100]}")
    elif args.action == "goroutines":
        goroutines = find_goroutines(args.binary)
        print(f"[*] Goroutine markers: {json.dumps(goroutines, indent=2)}")
    elif args.action == "full":
        report = analyze_full(args.binary)
        if args.output:
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"[+] Saved: {args.output}")


if __name__ == "__main__":
    main()
