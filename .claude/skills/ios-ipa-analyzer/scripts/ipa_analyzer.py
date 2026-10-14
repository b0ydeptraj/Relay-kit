#!/usr/bin/env python3
"""
ipa_analyzer.py - Static analysis tool for iOS IPA files.
Extracts structure, plists, entitlements, strings, and security info.

Usage:
    python scripts/ipa_analyzer.py --ipa MyApp.ipa
    python scripts/ipa_analyzer.py --ipa MyApp.ipa --output report.json
    python scripts/ipa_analyzer.py --ipa MyApp.ipa --extract-dir ./extracted
    python scripts/ipa_analyzer.py --ipa MyApp.ipa --search-strings --keywords "api,key,token,secret"
"""
import argparse
import json
import os
import plistlib
import re
import sys
import zipfile
import struct


def extract_ipa(ipa_path: str, dest: str) -> str:
    """Extract IPA to directory. Returns app bundle path."""
    os.makedirs(dest, exist_ok=True)
    with zipfile.ZipFile(ipa_path, "r") as z:
        z.extractall(dest)
    # Find .app bundle
    payload = os.path.join(dest, "Payload")
    if os.path.exists(payload):
        apps = [d for d in os.listdir(payload) if d.endswith(".app")]
        if apps:
            return os.path.join(payload, apps[0])
    return dest


def read_plist(path: str) -> dict:
    """Read a plist file (XML or binary format)."""
    try:
        with open(path, "rb") as f:
            return plistlib.load(f)
    except Exception as e:
        return {"error": str(e)}


def get_info_plist(app_path: str) -> dict:
    """Read Info.plist from app bundle."""
    plist_path = os.path.join(app_path, "Info.plist")
    if os.path.exists(plist_path):
        return read_plist(plist_path)
    return {}


def get_entitlements(binary_path: str) -> dict:
    """Extract entitlements embedded in Mach-O binary."""
    with open(binary_path, "rb") as f:
        data = f.read()
    # Find entitlements plist between markers
    start = data.find(b"<?xml version")
    if start == -1:
        start = data.find(b"<plist")
    end = data.find(b"</plist>", start)
    if start != -1 and end != -1:
        plist_data = data[start:end + 8]
        try:
            return plistlib.loads(plist_data)
        except:
            pass
    return {}


def list_frameworks(app_path: str) -> list:
    """List all frameworks and dylibs in the app."""
    frameworks = []
    for root, dirs, files in os.walk(app_path):
        for f in files:
            if f.endswith((".framework", ".dylib", ".tbd")):
                frameworks.append(os.path.join(root, f).replace(app_path + os.sep, ""))
    return frameworks


def extract_strings_from_binary(binary_path: str, min_len: int = 8) -> list:
    """Extract strings from Mach-O binary."""
    with open(binary_path, "rb") as f:
        data = f.read()
    pattern = rb"[ -~]{" + str(min_len).encode() + rb",}"
    strings = re.findall(pattern, data)
    return [s.decode("utf-8", errors="ignore") for s in strings]


def find_security_relevant(strings: list, keywords: list = None) -> dict:
    """Filter strings for security-relevant content."""
    if not keywords:
        keywords = ["api", "key", "token", "secret", "password", "auth", "bearer",
                    "http://", "https://", "amazonaws", "firebase", "mongodb", "sql",
                    "admin", "private", "certificate"]
    found = {}
    for kw in keywords:
        matches = [s for s in strings if kw.lower() in s.lower()]
        if matches:
            found[kw] = matches[:10]
    return found


def detect_ssl_pinning(binary_path: str, strings: list) -> list:
    """Detect SSL pinning implementations."""
    indicators = {
        "OkHttp CertificatePinner": "CertificatePinner",
        "TrustKit": "TrustKit",
        "AFNetworking": "AFSecurityPolicy",
        "NSURLSession pinning": "URLSession",
        "Custom SHA256": "sha256/",
        "Public key pinning": "HPKP",
        "commonName pinning": "commonName",
    }
    detected = []
    all_text = " ".join(strings)
    with open(binary_path, "rb") as f:
        binary_data = f.read()
    for name, pattern in indicators.items():
        if pattern in all_text or pattern.encode() in binary_data:
            detected.append(name)
    return detected


def detect_arch(binary_path: str) -> str:
    """Detect Mach-O architecture."""
    with open(binary_path, "rb") as f:
        magic = f.read(4)
    ARCHS = {
        b"\xce\xfa\xed\xfe": "x86 (32-bit)",
        b"\xcf\xfa\xed\xfe": "x86_64",
        b"\xfe\xed\xfa\xce": "ARM (32-bit, BE)",
        b"\xfe\xed\xfa\xcf": "ARM64 (BE)",
        b"\xca\xfe\xba\xbe": "FAT binary (multi-arch)",
    }
    return ARCHS.get(magic, f"Unknown ({magic.hex()})")


def analyze_ipa(ipa_path: str, extract_dir: str = None, search_keywords: list = None) -> dict:
    print(f"[*] Analyzing IPA: {ipa_path}")
    size_mb = os.path.getsize(ipa_path) / 1024 / 1024
    print(f"    Size: {size_mb:.1f} MB")

    dest = extract_dir or ipa_path.replace(".ipa", "_extracted")
    app_path = extract_ipa(ipa_path, dest)
    print(f"[*] Extracted to: {app_path}")

    # Info.plist
    info = get_info_plist(app_path)
    bundle_id = info.get("CFBundleIdentifier", "unknown")
    version   = info.get("CFBundleShortVersionString", "?")
    build     = info.get("CFBundleVersion", "?")
    min_ios   = info.get("MinimumOSVersion", "?")
    url_schemes = [s["CFBundleURLSchemes"] for s in info.get("CFBundleURLTypes", []) if "CFBundleURLSchemes" in s]

    print(f"[*] Bundle ID: {bundle_id} | v{version} ({build}) | iOS {min_ios}+")

    # Main binary
    binary_path = os.path.join(app_path, os.path.basename(app_path).replace(".app",""))
    if not os.path.exists(binary_path):
        # Try to find it
        for f in os.listdir(app_path):
            if os.path.isfile(os.path.join(app_path, f)) and not f.endswith((".plist",".png",".car",".strings")):
                binary_path = os.path.join(app_path, f)
                break

    arch = detect_arch(binary_path) if os.path.exists(binary_path) else "N/A"
    print(f"[*] Architecture: {arch}")

    # Entitlements
    entitlements = get_entitlements(binary_path) if os.path.exists(binary_path) else {}

    # Frameworks
    frameworks = list_frameworks(app_path)
    print(f"[*] Frameworks/dylibs: {len(frameworks)}")

    # Strings
    strings = extract_strings_from_binary(binary_path, 10) if os.path.exists(binary_path) else []
    print(f"[*] Strings extracted: {len(strings)}")

    # Security analysis
    ssl_pinning = detect_ssl_pinning(binary_path, strings) if os.path.exists(binary_path) else []
    security_strings = find_security_relevant(strings, search_keywords)

    print(f"[*] SSL pinning: {ssl_pinning if ssl_pinning else 'Not detected'}")
    if security_strings:
        print(f"[*] Security-relevant strings: {len(security_strings)} categories found")

    report = {
        "ipa": ipa_path, "size_mb": round(size_mb, 1),
        "bundle_id": bundle_id, "version": version, "build": build,
        "min_ios": min_ios, "architecture": arch,
        "url_schemes": url_schemes,
        "entitlements": entitlements,
        "frameworks": frameworks,
        "ssl_pinning_detected": ssl_pinning,
        "security_strings": security_strings,
        "total_strings": len(strings),
        "permissions": {k: v for k, v in info.items() if "UsageDescription" in k},
    }
    return report


def main():
    p = argparse.ArgumentParser(description="iOS IPA static analyzer")
    p.add_argument("--ipa", required=True)
    p.add_argument("--output", help="Save JSON report")
    p.add_argument("--extract-dir", help="Where to extract IPA")
    p.add_argument("--search-strings", action="store_true")
    p.add_argument("--keywords", help="Comma-separated keywords")
    args = p.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else None
    report = analyze_ipa(args.ipa, args.extract_dir, keywords)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n[+] Report saved: {args.output}")
    else:
        print(f"\n[*] Summary:")
        print(f"  Bundle  : {report['bundle_id']}")
        print(f"  Arch    : {report['architecture']}")
        print(f"  Pinning : {report.get('ssl_pinning_detected','none')}")
        print(f"  Perms   : {list(report.get('permissions',{}).keys())}")


if __name__ == "__main__":
    main()
