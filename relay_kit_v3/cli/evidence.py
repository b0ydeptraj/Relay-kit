import argparse
import json
from relay_kit_v3.evidence_ledger import summarize_events

def run_evidence_summary(args: argparse.Namespace) -> int:
    summary = summarize_events(args.project_path, limit=args.limit)
    if args.json:
        payload = {
            "ledger_path": str(summary.ledger_path),
            "total_events": summary.total_events,
            "status_counts": summary.status_counts,
            "gate_counts": summary.gate_counts,
            "recent_events": summary.recent_events,
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return 0

    print("Relay-kit evidence summary")
    print(f"- ledger: {summary.ledger_path}")
    print(f"- total events: {summary.total_events}")
    if summary.status_counts:
        statuses = ", ".join(f"{key}={value}" for key, value in summary.status_counts.items())
        print(f"- statuses: {statuses}")
    if summary.recent_events:
        print("- recent:")
        for event in summary.recent_events:
            gate = event.get("gate", event.get("command", "unknown"))
            status = event.get("status", "unknown")
            timestamp = event.get("timestamp", "-")
            print(f"  - {timestamp} {gate}: {status}")

    return 0
