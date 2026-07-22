import argparse
import json
from relay_kit_v3.token_economy import build_token_audit, render_token_audit, write_token_audit

def run_token(args: argparse.Namespace) -> int:
    if getattr(args, "action", None) == "audit":
        return run_token_audit(args)
    return 2

def run_token_audit(args: argparse.Namespace) -> int:
    report = build_token_audit(
        args.project_path,
        max_tokens=args.max_tokens,
        scopes=args.scope,
        stale_days=args.stale_days,
    )
    output_path = write_token_audit(args.project_path, report, output_file=getattr(args, "output_file", None))
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_token_audit(report))
        print(f"Wrote {output_path}")
    if getattr(args, "strict", False) and report.get("status") != "pass":
        return 1
    return 0
