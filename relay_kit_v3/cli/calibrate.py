import argparse
import json
from relay_kit_v3.signal_calibration import (
    build_report as build_signal_calibration_report,
    render_report as render_signal_calibration_report,
    write_report as write_signal_calibration_report,
)

def run_calibrate(args: argparse.Namespace) -> int:
    action = getattr(args, "action", None)
    if action == "claims":
        return run_calibrate_claims(args)
    if action == "skill":
        return run_calibrate_skill(args)
    if action == "readiness":
        return run_calibrate_readiness(args)
    return 2

def run_calibrate_claims(args: argparse.Namespace) -> int:
    report = build_signal_calibration_report(
        args.project_path,
        mode="claims",
        claims=getattr(args, "claim", None),
        claim_file=getattr(args, "claim_file", None),
        skill=getattr(args, "skill", "all"),
        strict=getattr(args, "strict", False),
    )
    output_path = None
    if getattr(args, "output_file", None):
        output_path = write_signal_calibration_report(args.project_path, report, args.output_file)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_signal_calibration_report(report))
        if output_path is not None:
            print(f"Wrote {output_path}")
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 2
    return 0

def run_calibrate_skill(args: argparse.Namespace) -> int:
    report = build_signal_calibration_report(
        args.project_path,
        mode="skill",
        claims=getattr(args, "claim", None),
        claim_file=getattr(args, "claim_file", None),
        skill=getattr(args, "skill", "all"),
        strict=getattr(args, "strict", False),
    )
    output_path = None
    if getattr(args, "output_file", None):
        output_path = write_signal_calibration_report(args.project_path, report, args.output_file)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_signal_calibration_report(report))
        if output_path is not None:
            print(f"Wrote {output_path}")
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 2
    return 0

def run_calibrate_readiness(args: argparse.Namespace) -> int:
    report = build_signal_calibration_report(
        args.project_path,
        mode="readiness",
        claims=getattr(args, "claim", None),
        claim_file=getattr(args, "claim_file", None),
        skill=getattr(args, "skill", "all"),
        strict=getattr(args, "strict", False),
    )
    output_path = None
    if getattr(args, "output_file", None):
        output_path = write_signal_calibration_report(args.project_path, report, args.output_file)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_signal_calibration_report(report))
        if output_path is not None:
            print(f"Wrote {output_path}")
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 2
    return 0
