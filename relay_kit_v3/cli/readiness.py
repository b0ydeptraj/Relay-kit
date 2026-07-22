import argparse
import sys
import json
from pathlib import Path

from relay_kit_v3.readiness import build_readiness_report, render_readiness_report

def run_readiness(args: argparse.Namespace) -> int:
    if args.action != "check":
        return 2
    report = build_readiness_report(args.project_path, profile=args.profile, skip_tests=args.skip_tests)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_readiness_report(report))
    return 0 if report["status"] == "pass" else 2

