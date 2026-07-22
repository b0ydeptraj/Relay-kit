import argparse
import json

from relay_kit_v3.context_governance import build_context_audit, render_context_audit, write_context_audit
from relay_kit_v3.context_index import (
    build_context_explain_symbol,
    build_context_mcp_tool_result,
    build_context_index,
    build_context_related,
    build_context_search,
    context_mcp_manifest,
    read_active_context,
    render_active_context,
    render_context_explain_symbol,
    render_context_index,
    render_context_mcp,
    render_context_related,
    render_context_search,
    render_context_watch,
    watch_context_index,
    write_active_context,
    write_context_index,
)
from relay_kit_v3.token_economy import (
    DEFAULT_MAX_TOKENS,
    build_context_budget,
    build_context_pack,
    render_context_budget,
    render_context_pack,
    write_context_budget,
    write_context_pack,
)

def run_context_audit(args: argparse.Namespace) -> int:
    report = build_context_audit(args.project_path, stale_days=args.stale_days)
    if args.output_file:
        write_context_audit(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_context_audit(report))
        if args.output_file:
            print(f"Wrote {args.output_file}")
    if args.strict and report["status"] != "pass":
        return 1
    return 0

def run_context_index(args: argparse.Namespace) -> int:
    report = build_context_index(args.project_path)
    output_path = write_context_index(args.project_path, report, output_file=args.output_file)
    if args.json:
        payload = dict(report)
        payload["output_file"] = str(output_path)
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(render_context_index(report))
        print(f"Wrote {output_path}")
    return 0

def run_context_search(args: argparse.Namespace) -> int:
    report = build_context_search(
        args.project_path,
        query=args.query,
        limit=args.limit,
        index_file=args.index_file,
        embedding_model=getattr(args, "embedding_model", None),
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_context_search(report))
    return 0 if report["status"] in {"pass", "empty"} else 2

def run_context_related(args: argparse.Namespace) -> int:
    report = build_context_related(
        args.project_path,
        path=args.path,
        limit=args.limit,
        index_file=args.index_file,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_context_related(report))
    return 0 if report["status"] in {"pass", "empty"} else 2

def run_context_explain_symbol(args: argparse.Namespace) -> int:
    report = build_context_explain_symbol(
        args.project_path,
        symbol=args.symbol,
        limit=args.limit,
        index_file=args.index_file,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_context_explain_symbol(report))
    return 0 if report["status"] in {"pass", "empty"} else 2

def run_context_active_set(args: argparse.Namespace) -> int:
    report = write_active_context(args.project_path, file_path=args.file, selection=args.selection)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_active_context(report))
    return 0 if report["status"] in {"pass", "empty"} else 2

def run_context_active_show(args: argparse.Namespace) -> int:
    report = read_active_context(args.project_path)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_active_context(report))
    return 0 if report["status"] in {"pass", "empty"} else 2

def run_context_mcp(args: argparse.Namespace) -> int:
    if args.tool:
        tool_args = {"limit": args.limit}
        if args.query is not None:
            tool_args["query"] = args.query
        if getattr(args, "path", None) is not None:
            tool_args["path"] = args.path
        if getattr(args, "symbol", None) is not None:
            tool_args["symbol"] = args.symbol
        report = build_context_mcp_tool_result(args.project_path, args.tool, tool_args)
    else:
        report = context_mcp_manifest(args.project_path)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_context_mcp(report) if report.get("schema_version") == "relay-kit.context-mcp.v1" else json.dumps(report, indent=2))
    return 0 if report["status"] in {"pass", "empty"} else 2

def run_context_watch(args: argparse.Namespace) -> int:
    report = watch_context_index(
        args.project_path,
        output_file=args.output_file,
        once=args.once,
        interval_seconds=args.interval,
        max_iterations=args.max_iterations,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_context_watch(report))
    return 0 if report["status"] == "pass" else 2

def run_context_budget(args: argparse.Namespace) -> int:
    report = build_context_budget(
        args.project_path,
        max_tokens=args.max_tokens,
        query=args.query,
        scopes=getattr(args, "scope", None),
        stale_days=args.stale_days,
    )
    output_path = write_context_budget(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_context_budget(report))
        print(f"Wrote {output_path}")
    if getattr(args, "strict", False) and report["status"] != "pass":
        return 1
    return 0

def run_context_pack(args: argparse.Namespace) -> int:
    report = build_context_pack(
        args.project_path,
        task=args.task,
        max_tokens=args.max_tokens,
        scopes=getattr(args, "scope", None),
        stale_days=args.stale_days,
    )
    output_path = write_context_pack(args.project_path, report, output_file=args.output_file)
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_context_pack(report))
        print(f"Wrote {output_path}")
    if getattr(args, "strict", False) and report["status"] != "pass":
        return 1
    return 0


def run_context(args):
    action = getattr(args, "action", None)
    if action == "search": return run_context_search(args)
    elif action == "related": return run_context_related(args)
    elif action == "audit": return run_context_audit(args)
    elif action == "index": return run_context_index(args)
    elif action == "pack": return run_context_pack(args)
    elif action == "budget": return run_context_budget(args)
    elif action == "watch": return run_context_watch(args)
    elif action in {"explain-symbol", "explain_symbol"}: return run_context_explain_symbol(args)
    elif action == "mcp": return run_context_mcp(args)
    elif action == "active":
        sub_action = getattr(args, "action_active", None)
        if sub_action == "show": return run_context_active_show(args)
        elif sub_action == "set": return run_context_active_set(args)
    raise ValueError(f"Unknown context action: {action}")
