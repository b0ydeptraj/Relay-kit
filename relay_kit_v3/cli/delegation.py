import argparse
import json
from relay_kit_v3.delegation_control import (
    adapter_capabilities,
    build_delegation_audit,
    build_delegation_plan,
    close_completed,
    record_usage,
    render_delegation_report,
)

def run_delegation_plan(args: argparse.Namespace) -> int:
    report = build_delegation_plan(
        args.project_path,
        task=args.task,
        budget=args.budget,
        complexity=args.complexity,
        adapter=args.adapter,
        artifact=args.artifact,
        lock_scope=args.lock_scope,
        expected_return_condition=args.expected_return_condition,
        verification_command=args.verification_command,
        independent=args.independent,
        apply=args.apply,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_delegation_report(report))
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0

def run_delegation_audit(args: argparse.Namespace) -> int:
    report = build_delegation_audit(args.project_path)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_delegation_report(report))
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0

def run_delegation_close_completed(args: argparse.Namespace) -> int:
    report = close_completed(args.project_path)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_delegation_report(report))
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0

def run_delegation_record_usage(args: argparse.Namespace) -> int:
    report = record_usage(
        args.project_path,
        agent_id=args.agent_id,
        input_tokens=args.input_tokens,
        output_tokens=args.output_tokens,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_delegation_report(report))
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0

def run_delegation_capabilities(args: argparse.Namespace) -> int:
    report = adapter_capabilities(args.adapter)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_delegation_report(report))
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0
