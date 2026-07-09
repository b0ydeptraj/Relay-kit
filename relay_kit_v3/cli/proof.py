import argparse
import sys
import json
from pathlib import Path


def run_proof(args: argparse.Namespace) -> int:
    if args.action != "audit":
        return 2
    report = build_skill_proof_report(
        args.project_path,
        workflow_fixture=args.workflow_fixture,
        real_world_cases_file=args.real_world_cases_file,
        strict=args.strict,
    )
    if args.output_file:
        write_skill_proof_report(args.project_path, report, args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_skill_proof_report(report))
    if args.strict and report["status"] != "pass":
        return 2
    return 0

