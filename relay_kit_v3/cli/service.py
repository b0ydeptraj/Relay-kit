import argparse
import json
from relay_kit_v3.service_boundary import build_service_boundary_report, render_service_boundary_report, write_service_boundary_report

def run_service_boundaries(args: argparse.Namespace) -> int:
    report = build_service_boundary_report(args.project_path)
    if getattr(args, "output_file", None):
        write_service_boundary_report(args.project_path, report, output_file=args.output_file)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_service_boundary_report(report))
        if getattr(args, "output_file", None):
            print(f"Wrote {args.output_file}")
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0
