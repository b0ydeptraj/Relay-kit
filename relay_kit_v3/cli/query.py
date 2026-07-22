import argparse
import json
from relay_kit_v3.query_search import build_query_search, render_query_search, write_query_search

def run_query(args: argparse.Namespace) -> int:
    if getattr(args, "action", None) == "search":
        return run_query_search(args)
    return 2

def run_query_search(args: argparse.Namespace) -> int:
    report = build_query_search(
        args.project_path,
        query=args.query,
        scopes=getattr(args, "scope", None),
        limit=args.limit,
        stale_days=getattr(args, "stale_days", 30),
    )
    if getattr(args, "output_file", None):
        write_query_search(args.project_path, report, output_file=args.output_file)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_query_search(report))
        if getattr(args, "output_file", None):
            print(f"Wrote {args.output_file}")
    return 0 if report.get("status") in {"pass", "empty"} else 2
