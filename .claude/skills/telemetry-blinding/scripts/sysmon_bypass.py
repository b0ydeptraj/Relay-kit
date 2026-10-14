#!/usr/bin/env python3
"""
sysmon_bypass.py - Techniques to evade Sysmon event monitoring.
Analyzes current Sysmon config and identifies bypass opportunities.

Usage:
    python scripts/sysmon_bypass.py --mode analyze-config
    python scripts/sysmon_bypass.py --mode check-driver
    python scripts/sysmon_bypass.py --mode find-gaps --config sysmon.xml

Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import ctypes
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")
SYSMON_SERVICE_NAMES = ["SysmonDrv", "Sysmon", "Sysmon64"]
SYSMON_DRIVER_ALTITUDE = "385201"  # Known Sysmon minifilter altitude


def require_proof():
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF"); sys.exit(1)


def check_sysmon_running() -> bool:
    """Check if Sysmon service/driver is active."""
    try:
        result = subprocess.run(["sc", "query", "SysmonDrv"], capture_output=True, text=True)
        if "RUNNING" in result.stdout:
            print("[!] SysmonDrv: RUNNING")
            return True
        result = subprocess.run(["sc", "query", "Sysmon64"], capture_output=True, text=True)
        if "RUNNING" in result.stdout:
            print("[!] Sysmon64: RUNNING")
            return True
        print("[*] Sysmon: NOT detected")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False


def analyze_sysmon_config(config_path: str = None):
    """Analyze Sysmon XML config for bypass opportunities."""
    if not config_path:
        # Try to dump current config
        try:
            import tempfile
            tmp = tempfile.mktemp(suffix=".xml")
            result = subprocess.run(["sysmon64", "-c"], capture_output=True, text=True)
            print("[*] Sysmon config summary:")
            print(result.stdout[:2000])
        except:
            print("[-] Could not retrieve Sysmon config. Provide --config path.")
        return

    try:
        tree = ET.parse(config_path)
        root = tree.getroot()
    except Exception as e:
        print(f"[-] Config parse error: {e}"); return

    print(f"[*] Analyzing: {config_path}")
    event_types = {}

    for rule_group in root.iter("RuleGroup"):
        for child in rule_group:
            tag = child.tag
            onmatch = child.get("onmatch", "include")
            rules = list(child)
            event_types[tag] = {"onmatch": onmatch, "rules": len(rules)}

    print("\n[*] Monitored event types:")
    important = {
        "ProcessCreate": "Monitor process execution (evade: rename binary, hollow process)",
        "NetworkConnect": "Monitor outbound connections (evade: use allowed ports/IPs)",
        "FileCreate": "Monitor file writes (evade: write to monitored-excluded dirs)",
        "RegistryEvent": "Monitor registry changes (evade: use non-monitored keys)",
        "ImageLoad": "Monitor DLL loads (evade: load from temp/excluded paths)",
        "CreateRemoteThread": "Monitor thread injection (evade: APC/threadless methods)",
        "ProcessAccess": "Monitor process reads (evade: use handle duplication)",
        "RawAccessRead": "Monitor raw disk reads (evade: file system API instead)",
    }
    for etype, info in important.items():
        if etype in event_types:
            print(f"  [MONITORED] {etype}: {event_types[etype]}")
            print(f"              Bypass: {info}")
        else:
            print(f"  [NOT LOGGED] {etype} → Freely usable")

    print("\n[*] Bypass recommendations based on config gaps:")
    not_monitored = [k for k in important if k not in event_types]
    for etype in not_monitored:
        print(f"  ✓ {etype}: {important[etype].split('(evade: ')[0].strip()}")


def find_exclusion_paths(config_path: str):
    """Find excluded paths in Sysmon config that can be used to bypass logging."""
    try:
        tree = ET.parse(config_path)
    except Exception as e:
        print(f"[-] {e}"); return

    print("[*] Finding exclude rules (usable bypass paths):")
    for elem in tree.iter():
        if elem.get("onmatch") == "exclude":
            for child in elem:
                condition = child.get("condition", "is")
                print(f"  [{elem.tag}] EXCLUDE: {child.text} (condition: {condition})")


def main():
    p = argparse.ArgumentParser(description="Sysmon bypass analyzer (authorized use only)")
    p.add_argument("--mode", choices=["check-driver","analyze-config","find-gaps"], required=True)
    p.add_argument("--config", help="Sysmon XML config file path")
    args = p.parse_args()

    if args.mode == "check-driver":
        check_sysmon_running()
    elif args.mode == "analyze-config":
        analyze_sysmon_config(args.config)
    elif args.mode == "find-gaps":
        if not args.config: print("[-] --config required"); sys.exit(1)
        find_exclusion_paths(args.config)


if __name__ == "__main__":
    main()
