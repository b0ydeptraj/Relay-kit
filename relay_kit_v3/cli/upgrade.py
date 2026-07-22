import argparse
import sys
import json
from pathlib import Path

from relay_kit_v3.upgrade import build_upgrade_report, render_report, write_version_marker

def run_upgrade(args: argparse.Namespace) -> int:
    if args.action in {"check", "plan"}:
        report = build_upgrade_report(args.project_path, manifest_file=args.manifest_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            title = "Relay-kit upgrade plan" if args.action == "plan" else "Relay-kit upgrade check"
            print(render_report(report, title=title))
        if args.strict and report["status"] != "pass":
            return 2
        return 0
    if args.action == "mark-current":
        output_path = write_version_marker(
            args.project_path,
            bundle=args.bundle,
            adapters=args.adapter,
            manifest_file=args.manifest_file,
        )
        print(f"Wrote {output_path}")
        return 0
    return 2

