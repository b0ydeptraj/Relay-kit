import argparse
import sys
import json
from pathlib import Path
from relay_kit_v3.cli.utils import _run_script_main
from relay_kit_v3.release_lane import build_release_lane_report, render_release_lane_report, write_release_lane_report


def run_release(args: argparse.Namespace) -> int:
    if args.action == "readiness":
        from scripts import release_readiness

        readiness_argv = [args.project_path, "--phase", args.phase]
        if args.signals_file:
            readiness_argv.extend(["--signals-file", args.signals_file])
        if args.output_file:
            readiness_argv.extend(["--output-file", args.output_file])
        if args.strict:
            readiness_argv.append("--strict")
        if args.json:
            readiness_argv.append("--json")
        return _run_script_main(release_readiness, "release_readiness.py", readiness_argv)
    if args.action != "verify":
        return 2
    report = build_release_lane_report(args.project_path, require_clean=args.require_clean)
    if args.output_file:
        write_release_lane_report(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_release_lane_report(report))
    return 0 if report["status"] == "pass" else 2

