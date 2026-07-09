import argparse
import json
from pathlib import Path
from relay_kit_v3.agent_parity import build_agent_diagnostics, render_agent_diagnostics, write_agent_diagnostics
from relay_kit_v3.command_parity import lifecycle_command_records

def run_agent_list(args: argparse.Namespace) -> int:
    from relay_kit_v3.agent_parity import agent_profile_records
    payload = {
        "schema_version": "relay-kit.agent-profile.v1",
        "status": "pass",
        "project_path": str(Path(args.project_path).resolve()),
        "summary": {"profile_count": len(agent_profile_records())},
        "profiles": agent_profile_records(),
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print("Relay-kit agent profiles")
        print(f"- profiles: {payload['summary']['profile_count']}")
        for profile in payload["profiles"]:
            route = " -> ".join(profile["route_contract"])
            print(f"  - {profile['id']}: {route}")
    return 0

def run_agent_diagnose(args: argparse.Namespace) -> int:
    report = build_agent_diagnostics(args.project_path, adapter=args.adapter)
    if getattr(args, "output_file", None):
        write_agent_diagnostics(args.project_path, report, output_file=args.output_file)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_agent_diagnostics(report))
        if getattr(args, "output_file", None):
            print(f"Wrote {args.output_file}")
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0
