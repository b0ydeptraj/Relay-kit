#!/usr/bin/env python3
"""reverse_methodology.py - Systematic binary RE workflow guide and automation.
Usage:
    python scripts/reverse_methodology.py --binary target.exe
    python scripts/reverse_methodology.py --list-workflows
    python scripts/reverse_methodology.py --binary app.apk --platform android_apk
"""
import argparse, json, os, subprocess, sys, zipfile

WORKFLOWS = {
    "windows_pe": {
        "description": "Windows PE (.exe/.dll) reverse engineering",
        "steps": [
            "1. STATIC: file type, hashes, strings -> malware_triage.py",
            "2. PROTECTION: detect packers -> protection_bypass.py",
            "3. DECOMPILE: .NET -> analyze_dotnet.py | native -> IDA/Ghidra",
            "4. LICENSE: find check logic -> extract_license_algo.py",
            "5. DYNAMIC: x64dbg + anti-debug bypass -> anti_debug_bypass.py",
            "6. PATCH: apply patches -> apply_patch.py or patch_dotnet.py",
        ],
        "tools": ["malware_triage.py","protection_bypass.py","analyze_dotnet.py","apply_patch.py"],
    },
    "android_apk": {
        "description": "Android APK reverse engineering",
        "steps": [
            "1. UNPACK: apktool d app.apk",
            "2. CLASSES: jadx-gui decompile classes.dex",
            "3. NATIVE: analyze .so files -> analyze_apk.py",
            "4. FLUTTER: check libapp.so -> flutter_reverser.py",
            "5. PINNING: bypass SSL -> frida_pinning_bypass.py",
            "6. REPACK: inject frida gadget -> apk_repack.py --inject-frida",
        ],
        "tools": ["analyze_apk.py","flutter_reverser.py","frida_pinning_bypass.py","apk_repack.py"],
    },
    "ios_ipa": {
        "description": "iOS IPA reverse engineering",
        "steps": [
            "1. EXTRACT: unzip IPA -> ipa_analyzer.py",
            "2. BINARY: Mach-O analysis, detect arch",
            "3. CLASS DUMP: class-dump / dsdump",
            "4. FRIDA: objection or frida on jailbreak",
            "5. SSL PIN: detect -> frida_pinning_bypass.py",
        ],
        "tools": ["ipa_analyzer.py","frida_pinning_bypass.py"],
    },
    "flutter_app": {
        "description": "Flutter/Dart AOT snapshot reverse engineering",
        "steps": [
            "1. IDENTIFY: confirm Flutter + libapp.so/App.framework",
            "2. ANALYZE: -> flutter_reverser.py",
            "3. BLUTTER: extract class/method names (github.com/worawit/blutter)",
            "4. URLS: extract hardcoded endpoints from binary strings",
            "5. BYPASS: SSL pinning + certificate bypass",
        ],
        "tools": ["flutter_reverser.py","apk_repack.py","frida_pinning_bypass.py"],
    },
    "electron_app": {
        "description": "Electron app reverse engineering",
        "steps": [
            "1. UNPACK: asar -> unpack_electron_builder.py",
            "2. SOURCE: read app.js -> analyze_electron.py",
            "3. SECRETS: JS crypto keys -> js_crypto_extractor.py",
            "4. PATCH: modify asar -> repack_electron_builder.py",
        ],
        "tools": ["unpack_electron_builder.py","analyze_electron.py","js_crypto_extractor.py"],
    },
    "dotnet_app": {
        "description": ".NET / C# reverse engineering",
        "steps": [
            "1. DECOMPILE: dnSpy/ILSpy -> decompile_dotnet.py",
            "2. OBFUSCATION: de4dot for ConfuserEx/SmartAssembly",
            "3. LICENSE: -> extract_license_algo.py",
            "4. KEYGEN: -> generate_keygen.py",
            "5. PATCH: IL patch -> patch_dotnet.py",
            "6. NUITKA: if Nuitka-compiled -> nuitka_decryptor/",
        ],
        "tools": ["decompile_dotnet.py","extract_license_algo.py","generate_keygen.py","patch_dotnet.py"],
    },
}

def detect_type(binary_path):
    ext = os.path.splitext(binary_path)[1].lower()
    with open(binary_path,"rb") as f: magic = f.read(16)
    if magic[:2] == b"MZ":
        # Check .NET
        data = open(binary_path,"rb").read(1024*512)
        if b"mscoree.dll" in data or b"mscorlib" in data: return "dotnet_app"
        return "windows_pe"
    if magic[:4] == b"\x7fELF": return "windows_pe"
    if magic[:4] in (b"\xce\xfa\xed\xfe",b"\xcf\xfa\xed\xfe",b"\xca\xfe\xba\xbe"): return "ios_ipa"
    if magic[:4] == b"PK\x03\x04":
        if ext == ".ipa": return "ios_ipa"
        try:
            with zipfile.ZipFile(binary_path) as z:
                names = z.namelist()
            if any("libapp.so" in n for n in names): return "flutter_app"
            if any("Payload/" in n for n in names): return "ios_ipa"
        except: pass
        return "android_apk"
    if binary_path.endswith(".asar"): return "electron_app"
    return "windows_pe"

def main():
    p = argparse.ArgumentParser(description="Binary RE methodology guide")
    p.add_argument("--binary")
    p.add_argument("--platform", choices=list(WORKFLOWS.keys()))
    p.add_argument("--list-workflows", action="store_true")
    p.add_argument("--mode", choices=["guide","auto"], default="guide")
    args = p.parse_args()

    if args.list_workflows:
        print("[*] Reverse Engineering Workflows:")
        for name, wf in WORKFLOWS.items():
            print(f"\n  [{name}] {wf['description']}")
            for step in wf["steps"]: print(f"    {step}")
        return

    if not args.binary:
        p.print_help(); sys.exit(1)
    if not os.path.exists(args.binary):
        print(f"[-] Not found: {args.binary}"); sys.exit(1)

    wf_name = args.platform or detect_type(args.binary)
    wf = WORKFLOWS.get(wf_name, WORKFLOWS["windows_pe"])
    print(f"[*] Binary: {args.binary} ({os.path.getsize(args.binary):,} bytes)")
    print(f"[*] Workflow: {wf_name} – {wf['description']}")
    print(f"\n[*] Steps:")
    for step in wf["steps"]: print(f"  {step}")
    print(f"\n[*] Key tools: {', '.join(wf['tools'])}")
    print(f"\n[*] Run each tool:")
    base = "C:\\Users\\Hiep\\Documents\\Relay-kit\\.agent\\skills"
    for tool in wf["tools"]:
        for skill_dir in os.listdir(base):
            sp = os.path.join(base,skill_dir,"scripts",tool)
            if os.path.exists(sp):
                print(f"  python \"{sp}\" --binary \"{args.binary}\""); break

if __name__ == "__main__": main()
