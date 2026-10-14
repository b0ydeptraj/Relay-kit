#!/usr/bin/env python3
"""
sandbox_detect.py - Multi-technique sandbox/VM detection for red team payload evasion.
Returns True if running in a sandbox, False if genuine target environment.

Usage:
    python scripts/sandbox_detect.py --report
    python scripts/sandbox_detect.py --mode check-all
    python scripts/sandbox_detect.py --generate-loader --output evasive_loader.py

Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import ctypes
import os
import platform
import subprocess
import sys
import time
import winreg

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")
SANDBOX_INDICATORS = []


def check_cpu_cores() -> tuple:
    import psutil
    cores = psutil.cpu_count(logical=False) or 1
    is_sandbox = cores < 2
    return is_sandbox, f"CPU cores: {cores}"


def check_ram() -> tuple:
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024**3)
        is_sandbox = ram_gb < 2.0
        return is_sandbox, f"RAM: {ram_gb:.1f}GB"
    except:
        return False, "RAM: unknown"


def check_screen_resolution() -> tuple:
    if sys.platform != "win32":
        return False, "N/A"
    user32 = ctypes.WinDLL("user32")
    w = user32.GetSystemMetrics(0)
    h = user32.GetSystemMetrics(1)
    is_sandbox = w <= 800 or h <= 600
    return is_sandbox, f"Screen: {w}x{h}"


def check_username() -> tuple:
    username = os.environ.get("USERNAME", os.environ.get("USER", ""))
    sandbox_names = ["sandbox", "malware", "virus", "analysis", "test", "admin", "john",
                     "analyst", "john-pc", "desktop-", "win-"]
    is_sandbox = any(username.lower().startswith(n) for n in sandbox_names)
    return is_sandbox, f"Username: {username}"


def check_uptime() -> tuple:
    try:
        import psutil
        uptime = time.time() - psutil.boot_time()
        is_sandbox = uptime < 300  # < 5 minutes = just booted (sandbox behavior)
        return is_sandbox, f"Uptime: {uptime:.0f}s"
    except:
        return False, "Uptime: unknown"


def check_recent_files() -> tuple:
    if sys.platform != "win32":
        return False, "N/A"
    recent = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Recent")
    try:
        files = os.listdir(recent)
        is_sandbox = len(files) < 10
        return is_sandbox, f"Recent files: {len(files)}"
    except:
        return False, "Recent: N/A"


def check_sandbox_processes() -> tuple:
    suspicious = ["vboxservice", "vboxtray", "vmwaretray", "vmwareuser", "vmtoolsd",
                  "sandboxiedcomlaunch", "sbiesvc", "cuckoo", "wireshark", "fiddler",
                  "procmon", "processhacker", "x32dbg", "x64dbg", "ollydbg", "ida64"]
    result = subprocess.run(["tasklist"], capture_output=True, text=True)
    running = [p for p in suspicious if p.lower() in result.stdout.lower()]
    is_sandbox = bool(running)
    return is_sandbox, f"Suspicious processes: {running if running else 'none'}"


def check_disk_size() -> tuple:
    try:
        import shutil
        total = shutil.disk_usage("/").total / (1024**3) if sys.platform != "win32" else \
                shutil.disk_usage("C:\\").total / (1024**3)
        is_sandbox = total < 50
        return is_sandbox, f"Disk: {total:.0f}GB"
    except:
        return False, "Disk: unknown"


def check_timing_attack() -> tuple:
    """Detect if sleep() calls are being sped up (sandbox time skipping)."""
    before = ctypes.windll.kernel32.GetTickCount64() if sys.platform == "win32" else int(time.time() * 1000)
    time.sleep(1)
    after = ctypes.windll.kernel32.GetTickCount64() if sys.platform == "win32" else int(time.time() * 1000)
    elapsed = after - before
    is_sandbox = elapsed < 500  # Sleep was skipped
    return is_sandbox, f"Sleep timing: {elapsed}ms (expected ~1000ms)"


CHECKS = {
    "cpu_cores": check_cpu_cores,
    "ram": check_ram,
    "screen_resolution": check_screen_resolution,
    "username": check_username,
    "uptime": check_uptime,
    "recent_files": check_recent_files,
    "sandbox_processes": check_sandbox_processes,
    "disk_size": check_disk_size,
    "timing_attack": check_timing_attack,
}


def run_all_checks() -> tuple:
    results = {}
    sandbox_score = 0
    for name, fn in CHECKS.items():
        try:
            is_sb, detail = fn()
        except Exception as e:
            is_sb, detail = False, f"ERROR: {e}"
        results[name] = {"is_sandbox_indicator": is_sb, "detail": detail}
        if is_sb:
            sandbox_score += 1
    is_sandbox = sandbox_score >= 3  # 3+ indicators = likely sandbox
    return is_sandbox, sandbox_score, results


def generate_evasive_loader(output: str):
    """Generate a Python loader with all sandbox checks inline."""
    code = '''#!/usr/bin/env python3
"""Evasive loader - only executes payload in genuine environment."""
import ctypes, os, time, subprocess, sys

def is_sandbox():
    score = 0
    # Check CPU cores
    try:
        import psutil
        if psutil.cpu_count(logical=False) < 2: score += 1
        if psutil.virtual_memory().total < 2 * 1024**3: score += 1
    except: pass
    # Check screen
    if sys.platform == "win32":
        u32 = ctypes.WinDLL("user32")
        if u32.GetSystemMetrics(0) <= 800: score += 1
    # Check recent files
    recent = os.path.expandvars(r"%APPDATA%\\Microsoft\\Windows\\Recent")
    try:
        if len(os.listdir(recent)) < 10: score += 1
    except: pass
    # Check timing
    before = ctypes.windll.kernel32.GetTickCount64()
    time.sleep(1)
    after = ctypes.windll.kernel32.GetTickCount64()
    if (after - before) < 500: score += 1
    return score >= 3

if is_sandbox():
    # Decoy behavior: look benign in sandbox
    print("Hello World")
    sys.exit(0)

# Real payload executes here
print("[*] Genuine environment detected, executing payload...")
# TODO: replace with actual payload
'''
    with open(output, "w") as f:
        f.write(code)
    print(f"[+] Evasive loader written: {output}")


def main():
    p = argparse.ArgumentParser(description="Sandbox detection (authorized use only)")
    p.add_argument("--mode", choices=["check-all","single"], default="check-all")
    p.add_argument("--check", choices=list(CHECKS.keys()))
    p.add_argument("--report", action="store_true")
    p.add_argument("--generate-loader", action="store_true")
    p.add_argument("--output", default="evasive_loader.py")
    args = p.parse_args()

    if args.generate_loader:
        generate_evasive_loader(args.output); return

    is_sandbox, score, results = run_all_checks()
    print(f"\n[*] Sandbox score: {score}/{len(CHECKS)}")
    print(f"[*] Verdict: {'SANDBOX DETECTED' if is_sandbox else 'Likely genuine environment'}")
    if args.report:
        print("\n--- Detailed Report ---")
        for name, r in results.items():
            flag = "⚠" if r["is_sandbox_indicator"] else "✓"
            print(f"  [{flag}] {name}: {r['detail']}")


if __name__ == "__main__":
    main()
