#!/usr/bin/env python3
"""
flutter_reverser.py - Flutter/Dart app analysis tool.
Extracts Flutter version, identifies Dart snapshot type, and prepares for blutter analysis.

Usage:
    python scripts/flutter_reverser.py --apk app.apk --output ./flutter_out
    python scripts/flutter_reverser.py --libapp ./libapp.so --action analyze
    python scripts/flutter_reverser.py --apk app.apk --action extract-libapp
    python scripts/flutter_reverser.py --libapp ./libapp.so --action blutter
"""
import argparse
import json
import os
import re
import struct
import subprocess
import sys
import zipfile

FLUTTER_MARKERS = [
    b"io.flutter",
    b"dart:core",
    b"dart:async",
    b"flutter/src",
    b"Dart_Initialize",
]

SNAPSHOT_TYPES = {
    b"\xdc\xdc\xdc\xdc": "JIT snapshot (debug/profile)",
    b"\xdd\xdd\xdd\xdd": "AOT snapshot (release)",
    b"\xde\xde\xde\xde": "AppJIT snapshot",
}


def detect_flutter_version(binary_data: bytes) -> str:
    """Detect Flutter SDK version from binary."""
    patterns = [
        rb"(\d+\.\d+\.\d+)\s+\(stable\)",
        rb"Flutter\s+(\d+\.\d+\.\d+)",
        rb"flutter_version[\"']:\s*[\"'](\d+\.\d+\.\d+)",
    ]
    for pat in patterns:
        m = re.search(pat, binary_data)
        if m:
            return m.group(1).decode("utf-8", errors="ignore")

    # Check pubspec from assets
    marker = b"flutter:"
    idx = binary_data.find(marker)
    if idx != -1:
        snippet = binary_data[idx:idx+200].decode("utf-8", errors="ignore")
        m = re.search(r"sdk:\s*flutter\s+>=(\d+\.\d+)", snippet)
        if m: return f">={m.group(1)}"

    return "Unknown"


def detect_snapshot_type(binary_data: bytes) -> str:
    for magic, desc in SNAPSHOT_TYPES.items():
        if binary_data[:4] == magic or magic in binary_data[:8]:
            return desc
    if b"_kDartVmSnapshotData" in binary_data:
        return "Separate VM+Isolate snapshot (older Flutter)"
    return "Unknown snapshot type"


def extract_libapp_from_apk(apk_path: str, output_dir: str) -> dict:
    """Extract libapp.so and libflutter.so from APK."""
    os.makedirs(output_dir, exist_ok=True)
    extracted = {}
    with zipfile.ZipFile(apk_path, "r") as z:
        for name in z.namelist():
            if "libapp.so" in name or "libflutter.so" in name:
                arch = name.split("/")[-2] if "/" in name else "unknown"
                out_path = os.path.join(output_dir, f"{arch}_{os.path.basename(name)}")
                with z.open(name) as src, open(out_path, "wb") as dst:
                    dst.write(src.read())
                extracted[name] = out_path
                print(f"  Extracted: {name} -> {out_path} ({os.path.getsize(out_path):,} bytes)")
    return extracted


def is_flutter_app(binary_path: str) -> bool:
    """Check if binary is a Flutter app."""
    with open(binary_path, "rb") as f:
        data = f.read(1024 * 1024)
    return any(marker in data for marker in FLUTTER_MARKERS)


def analyze_libapp(binary_path: str) -> dict:
    """Analyze libapp.so or App framework binary."""
    print(f"[*] Analyzing: {binary_path}")
    size_mb = os.path.getsize(binary_path) / 1024 / 1024
    print(f"    Size: {size_mb:.1f} MB")

    with open(binary_path, "rb") as f:
        data = f.read()

    is_flutter = is_flutter_app(binary_path)
    flutter_ver = detect_flutter_version(data)
    snapshot_type = detect_snapshot_type(data)

    # Count approximate method/class count from pool pointers
    dart_class_pattern = rb"(?:dart:|package:)[A-Za-z][A-Za-z0-9_/.]+"
    dart_refs = list(set(m.decode("utf-8", errors="ignore")
                         for m in re.findall(dart_class_pattern, data)))

    # Extract strings
    string_pattern = rb"[ -~]{12,}"
    strings = [s.decode("utf-8", errors="ignore") for s in re.findall(string_pattern, data)]

    # Find API endpoints / URLs
    url_pattern = rb"https?://[^\s\x00-\x1f\"'<>]{10,}"
    urls = list(set(m.decode("utf-8", errors="ignore") for m in re.findall(url_pattern, data)))

    print(f"  Is Flutter : {is_flutter}")
    print(f"  Flutter ver: {flutter_ver}")
    print(f"  Snapshot   : {snapshot_type}")
    print(f"  Dart refs  : {len(dart_refs)}")
    print(f"  URLs found : {len(urls)}")

    if urls:
        print(f"\n  Extracted URLs:")
        for url in urls[:20]:
            print(f"    {url}")

    return {
        "binary": binary_path,
        "size_mb": round(size_mb, 1),
        "is_flutter": is_flutter,
        "flutter_version": flutter_ver,
        "snapshot_type": snapshot_type,
        "dart_references": dart_refs[:50],
        "embedded_urls": urls[:30],
        "total_strings": len(strings),
    }


def run_blutter(libapp_path: str, output_dir: str) -> bool:
    """Run blutter tool on libapp.so."""
    os.makedirs(output_dir, exist_ok=True)
    try:
        result = subprocess.run(["blutter", libapp_path, output_dir],
                                capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"[+] blutter completed. Output in: {output_dir}")
            for f in os.listdir(output_dir):
                print(f"  {f}: {os.path.getsize(os.path.join(output_dir, f)):,} bytes")
            return True
        else:
            print(f"[-] blutter failed: {result.stderr[:200]}")
            return False
    except FileNotFoundError:
        print("[-] blutter not found.")
        print("    Install: git clone https://github.com/worawit/blutter && cd blutter && python3 setup.py")
        return False
    except Exception as e:
        print(f"[-] blutter error: {e}")
        return False


def main():
    p = argparse.ArgumentParser(description="Flutter app reverse engineering tool")
    p.add_argument("--apk", help="APK file")
    p.add_argument("--libapp", help="libapp.so or App framework binary")
    p.add_argument("--action", choices=["analyze","extract-libapp","blutter","full"], default="full")
    p.add_argument("--output", default="./flutter_out")
    args = p.parse_args()

    if args.apk and args.action == "extract-libapp":
        extracted = extract_libapp_from_apk(args.apk, args.output)
        print(f"\n[+] Extracted {len(extracted)} files to {args.output}")
        return

    if args.apk:
        print(f"[*] Extracting libapp.so from APK...")
        extracted = extract_libapp_from_apk(args.apk, args.output)
        # Find arm64 version preferably
        libapp = next((v for k, v in extracted.items() if "arm64" in k and "libapp" in k),
                      next(iter(extracted.values()), None))
        if libapp:
            args.libapp = libapp

    if not args.libapp:
        print("[-] --apk or --libapp required"); sys.exit(1)

    report = analyze_libapp(args.libapp)

    if args.action == "blutter" or args.action == "full":
        print(f"\n[*] Running blutter...")
        run_blutter(args.libapp, os.path.join(args.output, "blutter"))

    out = os.path.join(args.output, "flutter_analysis.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[+] Analysis saved: {out}")


if __name__ == "__main__":
    main()
