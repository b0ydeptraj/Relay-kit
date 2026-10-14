#!/usr/bin/env python3
"""
apk_repack.py - Repack Android APK with Frida gadget for dynamic instrumentation.
Decompile APK, inject Frida gadget, recompile, sign, and install.

Usage:
    python scripts/apk_repack.py --apk target.apk --inject-frida
    python scripts/apk_repack.py --apk target.apk --patch-manifest --allow-backup
    python scripts/apk_repack.py --apk target.apk --inject-frida --resign --keystore debug.keystore
    python scripts/apk_repack.py --verify --apk repacked.apk

Requirements: apktool, apksigner/jarsigner, Frida gadget .so files
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile
import urllib.request as ureq

APKTOOL = "apktool"
FRIDA_GADGET_URLS = {
    "arm64-v8a":   "https://github.com/frida/frida/releases/latest/download/frida-gadget-{ver}-android-arm64.so.xz",
    "armeabi-v7a": "https://github.com/frida/frida/releases/latest/download/frida-gadget-{ver}-android-arm.so.xz",
    "x86":         "https://github.com/frida/frida/releases/latest/download/frida-gadget-{ver}-android-x86.so.xz",
    "x86_64":      "https://github.com/frida/frida/releases/latest/download/frida-gadget-{ver}-android-x86_64.so.xz",
}
FRIDA_VER = "16.3.3"

def run(cmd, check=True):
    print(f"  $ {' '.join(cmd) if isinstance(cmd,list) else cmd}")
    result = subprocess.run(cmd, capture_output=True, text=True, shell=isinstance(cmd,str))
    if check and result.returncode != 0:
        print(f"  [-] Error: {result.stderr[:200]}")
    return result

def decompile(apk_path, out_dir):
    print(f"[*] Decompiling {apk_path}...")
    r = run([APKTOOL, "d", apk_path, "-o", out_dir, "-f"])
    return r.returncode == 0

def inject_frida_gadget(decompiled_dir, arch="arm64-v8a"):
    """Inject Frida gadget .so into APK lib directory."""
    lib_dir = os.path.join(decompiled_dir, "lib", arch)
    os.makedirs(lib_dir, exist_ok=True)
    gadget_name = "libfrida-gadget.so"
    gadget_path = os.path.join(lib_dir, gadget_name)

    # Check if gadget already exists locally
    local_gadget = f"frida-gadget-{arch}.so"
    if os.path.exists(local_gadget):
        shutil.copy(local_gadget, gadget_path)
        print(f"[+] Copied local gadget to {gadget_path}")
        return True

    print(f"[!] Frida gadget not found locally.")
    print(f"    Download from: https://github.com/frida/frida/releases")
    print(f"    Save as: {local_gadget}")
    print(f"    Then place at: {gadget_path}")
    return False

def patch_manifest_for_injection(decompiled_dir):
    """Patch AndroidManifest.xml to allow network access and debugging."""
    manifest = os.path.join(decompiled_dir, "AndroidManifest.xml")
    with open(manifest, "r", encoding="utf-8") as f:
        content = f.read()

    patches = {
        'android:debuggable="false"': 'android:debuggable="true"',
        'android:allowBackup="false"': 'android:allowBackup="true"',
        'android:networkSecurityConfig="@xml/network_security_config"': '',
    }
    original = content
    for old, new in patches.items():
        content = content.replace(old, new)

    # Add debuggable if not present
    if 'android:debuggable' not in content:
        content = content.replace(
            '<application',
            '<application android:debuggable="true" android:allowBackup="true"', 1
        )

    if content != original:
        with open(manifest, "w", encoding="utf-8") as f:
            f.write(content)
        print("[+] Manifest patched: debuggable=true, allowBackup=true")
    return True

def find_main_activity_smali(decompiled_dir):
    """Find main Activity smali file for Frida gadget load injection."""
    manifest = os.path.join(decompiled_dir, "AndroidManifest.xml")
    import re
    with open(manifest) as f:
        content = f.read()
    # Find main launcher activity
    m = re.search(r'<activity[^>]+android:name="([^"]+)"[^>]*>.*?<action android:name="android\.intent\.action\.MAIN"', content, re.DOTALL)
    if m:
        class_name = m.group(1).replace(".", "/")
        if class_name.startswith("/"):
            class_name = class_name[1:]
        smali_path = os.path.join(decompiled_dir, "smali", class_name + ".smali")
        if os.path.exists(smali_path):
            return smali_path
    return None

def inject_system_load(smali_path, gadget_so="frida-gadget"):
    """Inject System.loadLibrary("frida-gadget") into onCreate."""
    LOAD_SMALI = '''
    const-string v0, "frida-gadget"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
'''
    with open(smali_path) as f:
        content = f.read()
    if "frida-gadget" in content:
        print("[*] Frida gadget load already present")
        return True
    # Inject after .method public onCreate
    target = ".method public onCreate(Landroid/os/Bundle;)V"
    if target in content:
        content = content.replace(target + "\n", target + "\n" + LOAD_SMALI + "\n")
        with open(smali_path, "w") as f:
            f.write(content)
        print(f"[+] Injected System.loadLibrary into {os.path.basename(smali_path)}")
        return True
    print(f"[-] Could not find onCreate in {smali_path}")
    return False

def recompile(decompiled_dir, output_apk):
    print(f"[*] Recompiling...")
    r = run([APKTOOL, "b", decompiled_dir, "-o", output_apk])
    return r.returncode == 0

def sign_apk(apk_path, keystore="debug.keystore", alias="debug", storepass="android"):
    """Sign APK with debug keystore."""
    if not os.path.exists(keystore):
        print(f"[*] Creating debug keystore...")
        run(["keytool", "-genkey", "-v", "-keystore", keystore, "-alias", alias,
             "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
             "-dname", "CN=Debug,O=Debug,C=US",
             "-storepass", storepass, "-keypass", storepass])
    print(f"[*] Signing APK...")
    r = run(["jarsigner", "-verbose", "-sigalg", "SHA256withRSA", "-digestalg", "SHA-256",
             "-keystore", keystore, "-storepass", storepass, "-keypass", storepass,
             apk_path, alias])
    return r.returncode == 0

def main():
    p = argparse.ArgumentParser(description="APK repack with Frida gadget injection")
    p.add_argument("--apk", required=True)
    p.add_argument("--inject-frida", action="store_true")
    p.add_argument("--patch-manifest", action="store_true")
    p.add_argument("--allow-backup", action="store_true")
    p.add_argument("--arch", default="arm64-v8a", choices=list(FRIDA_GADGET_URLS.keys()))
    p.add_argument("--resign", action="store_true")
    p.add_argument("--keystore", default="debug.keystore")
    p.add_argument("--output", help="Output repacked APK")
    p.add_argument("--verify", action="store_true")
    args = p.parse_args()

    if args.verify:
        with zipfile.ZipFile(args.apk) as z:
            names = z.namelist()
        has_gadget = any("frida-gadget" in n for n in names)
        has_lib = any(n.startswith("lib/") for n in names)
        print(f"[*] APK: {args.apk}")
        print(f"  Frida gadget: {'YES' if has_gadget else 'NO'}")
        print(f"  Has libs: {'YES' if has_lib else 'NO'}")
        print(f"  Files: {len(names)}")
        return

    work_dir = args.apk.replace(".apk","_decompiled")
    out_apk = args.output or args.apk.replace(".apk","_repacked.apk")

    # Check apktool
    r = subprocess.run([APKTOOL, "--version"], capture_output=True)
    if r.returncode != 0:
        print("[-] apktool not found. Install: https://apktool.org")
        sys.exit(1)

    if not decompile(args.apk, work_dir): sys.exit(1)
    if args.patch_manifest or args.inject_frida or args.allow_backup:
        patch_manifest_for_injection(work_dir)
    if args.inject_frida:
        inject_frida_gadget(work_dir, args.arch)
        smali = find_main_activity_smali(work_dir)
        if smali:
            inject_system_load(smali)
        else:
            print("[!] Could not find main activity smali. Inject manually.")
    if not recompile(work_dir, out_apk): sys.exit(1)
    if args.resign:
        sign_apk(out_apk, args.keystore)
    print(f"\n[+] Done: {out_apk}")
    print(f"    Install: adb install {out_apk}")
    print(f"    Then attach Frida: frida -U -n com.target.app")

if __name__ == "__main__":
    main()
