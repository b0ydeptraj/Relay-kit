#!/usr/bin/env python3
"""
event_log_tamper.py - Windows Event Log management for red team OPSEC.
Clear, query, and analyze Windows event logs. Identify forensic artifacts.

Usage:
    python scripts/event_log_tamper.py --mode list-logs
    python scripts/event_log_tamper.py --mode query --log Security --last 100
    python scripts/event_log_tamper.py --mode analyze-artifacts
    python scripts/event_log_tamper.py --mode clear --log Security  (requires ENGAGEMENT_PROOF)

Engagement proof: set ENGAGEMENT_PROOF env var for destructive operations.
"""
import argparse
import ctypes
import os
import subprocess
import sys

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")

INTERESTING_LOGS = ["Security", "System", "Application", "Microsoft-Windows-PowerShell/Operational",
                    "Microsoft-Windows-Sysmon/Operational", "Microsoft-Windows-TaskScheduler/Operational",
                    "Microsoft-Windows-WinRM/Operational", "Microsoft-Windows-TerminalServices-LocalSessionManager/Operational"]

FORENSIC_EVENT_IDS = {
    "4624": "Logon success", "4625": "Logon failure", "4648": "Logon with explicit credentials",
    "4688": "Process creation", "4698": "Scheduled task created", "4702": "Scheduled task updated",
    "4720": "User account created", "4732": "User added to local group",
    "7045": "New service installed", "1102": "Audit log cleared",
    "4657": "Registry value modified", "4663": "File access attempt",
}


def require_proof():
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF for destructive operations"); sys.exit(1)


def list_event_logs():
    """List all Windows event logs with their sizes."""
    result = subprocess.run(["wevtutil", "el"], capture_output=True, text=True)
    logs = result.stdout.strip().split("\n")
    print(f"[*] Total event logs: {len(logs)}")
    print("[*] Key security-relevant logs:")
    for log in INTERESTING_LOGS:
        status = "PRESENT" if any(log.lower() == l.lower().strip() for l in logs) else "missing"
        print(f"  [{status}] {log}")


def query_log(log_name: str, last_n: int = 50, event_ids: list = None):
    """Query recent events from a log."""
    id_filter = ""
    if event_ids:
        id_conditions = " or ".join(f"EventID={eid}" for eid in event_ids)
        id_filter = f" and ({id_conditions})"

    query = f"*[System[{id_filter}]]" if id_filter else "*"
    cmd = ["wevtutil", "qe", log_name, f"/q:{query}", f"/c:{last_n}", "/f:text", "/rd:true"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[-] Error: {result.stderr[:200]}")
    else:
        print(result.stdout[:3000])


def analyze_forensic_artifacts():
    """Scan for forensic event IDs across key logs."""
    print("[*] Scanning for forensic artifacts...")
    for log in ["Security", "System", "Application"]:
        print(f"\n[*] Log: {log}")
        ids = list(FORENSIC_EVENT_IDS.keys())
        for eid in ids:
            cmd = ["wevtutil", "qe", log, f"/q:*[System[EventID={eid}]]", "/c:5", "/f:text", "/rd:true"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout.strip():
                desc = FORENSIC_EVENT_IDS.get(eid, "unknown")
                count_lines = result.stdout.count("Event[")
                print(f"  EventID {eid} ({desc}): {count_lines} recent events found")


def clear_log(log_name: str):
    """Clear a Windows event log (requires ENGAGEMENT_PROOF + admin rights)."""
    require_proof()
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("[-] Admin rights required to clear event logs"); sys.exit(1)
    result = subprocess.run(["wevtutil", "cl", log_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[+] Cleared: {log_name}")
    else:
        print(f"[-] Failed: {result.stderr}")


def main():
    p = argparse.ArgumentParser(description="Event log manager (authorized use only)")
    p.add_argument("--mode", choices=["list-logs","query","analyze-artifacts","clear"], required=True)
    p.add_argument("--log", help="Log name (e.g. Security)")
    p.add_argument("--last", type=int, default=50, help="Last N events to query")
    p.add_argument("--event-ids", nargs="+", help="Filter by event IDs")
    args = p.parse_args()

    if sys.platform != "win32": sys.exit("Windows only")
    {"list-logs": list_event_logs,
     "query": lambda: query_log(args.log or "Security", args.last, args.event_ids),
     "analyze-artifacts": analyze_forensic_artifacts,
     "clear": lambda: clear_log(args.log or "Security")}[args.mode]()


if __name__ == "__main__":
    main()
