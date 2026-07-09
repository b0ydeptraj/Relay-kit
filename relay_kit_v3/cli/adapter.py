import argparse
import json
from relay_kit_v3.adapter_parity import build_adapter_diagnostics, render_adapter_diagnostics, write_adapter_diagnostics

def run_adapter_diagnose(args: argparse.Namespace) -> int:
    report = build_adapter_diagnostics(args.project_path, adapter=args.adapter)
    if getattr(args, "output_file", None):
        write_adapter_diagnostics(args.project_path, report, output_file=args.output_file)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_adapter_diagnostics(report))
        if getattr(args, "output_file", None):
            print(f"Wrote {args.output_file}")
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0
