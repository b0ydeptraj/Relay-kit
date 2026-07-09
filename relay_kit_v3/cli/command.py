import argparse
import json
from pathlib import Path
from relay_kit_v3.command_parity import (
    build_command_diagnostics,
    lifecycle_command_records,
    render_command_diagnostics,
    write_command_diagnostics,
)

def run_command_list(args: argparse.Namespace) -> int:
    payload = {
        "schema_version": "relay-kit.command-registry.v1",
        "status": "pass",
        "project_path": str(Path(args.project_path).resolve()),
        "summary": {"command_count": len(lifecycle_command_records())},
        "commands": lifecycle_command_records(),
    }
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print("Relay-kit lifecycle commands")
        print(f"- commands: {payload['summary']['command_count']}")
        for command in payload["commands"]:
            print(f"  - {command['slash']} -> {command['route_target']}")
    return 0

def run_command_diagnose(args: argparse.Namespace) -> int:
    report = build_command_diagnostics(args.project_path, adapter=args.adapter)
    if getattr(args, "output_file", None):
        write_command_diagnostics(args.project_path, report, output_file=args.output_file)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_command_diagnostics(report))
        if getattr(args, "output_file", None):
            print(f"Wrote {args.output_file}")
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0
