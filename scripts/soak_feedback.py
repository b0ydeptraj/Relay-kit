#!/usr/bin/env python3
"""Capture and summarize Relay-kit soak-cycle feedback."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

STATUS_CHOICES = ["open", "triaged", "resolved"]
SEVERITY_CHOICES = ["p0", "p1", "p2", "p3"]
AREA_CHOICES = [
    "install",
    "runtime",
    "adapter",
    "skills",
    "routing",
    "docs",
    "review",
    "other",
]


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Track soak-cycle findings from real usage and summarize what needs fixing.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Add one soak feedback entry")
    add_common(add)
    add.add_argument("--source", default="user", help="Feedback source, e.g. user/ai/internal")
    add.add_argument("--area", choices=AREA_CHOICES, required=True)
    add.add_argument("--severity", choices=SEVERITY_CHOICES, default="p2")
    add.add_argument("--summary", required=True, help="Short problem statement")
    add.add_argument("--evidence", default="", help="Command, log, or file path evidence")
    add.add_argument("--proposed-fix", default="", help="Suggested fix direction")
    add.add_argument("--owner", default="", help="Owner lane or person")
    add.add_argument("--status", choices=STATUS_CHOICES, default="open")
    add.add_argument("--tags", nargs="*", default=[], help="Optional tags")

    update = subparsers.add_parser("update", help="Update status or notes of an entry")
    add_common(update)
    update.add_argument("--id", required=True, help="Entry id")
    update.add_argument("--status", choices=STATUS_CHOICES, help="New status")
    update.add_argument("--note", default="", help="Update note")
    update.add_argument("--commit", default="", help="Fix commit hash")

    summary = subparsers.add_parser("summary", help="Summarize soak feedback")
    add_common(summary)
    summary.add_argument("--status", choices=STATUS_CHOICES + ["all"], default="all")
    summary.add_argument("--limit", type=int, default=10, help="Max recent items to print")
    summary.add_argument("--json", action="store_true")

    return parser.parse_args()


def add_common(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("project_path", nargs="?", default=".", help="Target project path")


def store_path(base: Path) -> Path:
    return base / ".ai-kit" / "state" / "soak-feedback.jsonl"


def load_entries(path: Path) -> List[Dict[str, object]]:
    if not path.exists():
        return []
    entries: List[Dict[str, object]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    return entries


def write_entries(path: Path, entries: List[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(item, ensure_ascii=True) for item in entries]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def add_entry(args: argparse.Namespace) -> int:
    base = Path(args.project_path).resolve()
    path = store_path(base)
    entries = load_entries(path)

    feedback_id = f"fb-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
    entry: Dict[str, object] = {
        "id": feedback_id,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "source": args.source,
        "area": args.area,
        "severity": args.severity,
        "summary": args.summary,
        "evidence": args.evidence,
        "proposed_fix": args.proposed_fix,
        "owner": args.owner,
        "status": args.status,
        "tags": list(args.tags),
        "history": [],
    }
    entries.append(entry)
    write_entries(path, entries)
    print(f"Added feedback: {feedback_id}")
    print(f"Store: {path}")
    return 0


def update_entry(args: argparse.Namespace) -> int:
    base = Path(args.project_path).resolve()
    path = store_path(base)
    entries = load_entries(path)
    for entry in entries:
        if entry.get("id") != args.id:
            continue
        changes: Dict[str, str] = {}
        if args.status:
            entry["status"] = args.status
            changes["status"] = args.status
        if args.commit:
            entry["fix_commit"] = args.commit
            changes["fix_commit"] = args.commit
        if args.note:
            history = entry.get("history")
            if not isinstance(history, list):
                history = []
                entry["history"] = history
            history.append({"at": utc_now(), "note": args.note})
            changes["note"] = args.note
        entry["updated_at"] = utc_now()
        write_entries(path, entries)
        if not changes:
            print(f"No changes applied for entry {args.id}")
            return 0
        print(f"Updated feedback: {args.id}")
        return 0
    print(f"Feedback id not found: {args.id}")
    return 1


def summarize_entries(
    entries: List[Dict[str, object]],
    status_filter: str,
    limit: int,
) -> Dict[str, object]:
    if status_filter != "all":
        scoped = [item for item in entries if item.get("status") == status_filter]
    else:
        scoped = list(entries)

    severity_counts = Counter(str(item.get("severity", "unknown")) for item in scoped)
    area_counts = Counter(str(item.get("area", "unknown")) for item in scoped)
    status_counts = Counter(str(item.get("status", "unknown")) for item in entries)
    recent = sorted(
        scoped,
        key=lambda item: str(item.get("updated_at", "")),
        reverse=True,
    )[:limit]

    return {
        "total": len(entries),
        "filtered_total": len(scoped),
        "status_filter": status_filter,
        "status_counts": dict(status_counts),
        "severity_counts": dict(severity_counts),
        "area_counts": dict(area_counts),
        "recent": recent,
    }


def print_summary(summary: Dict[str, object]) -> None:
    print(f"Total feedback entries: {summary['total']}")
    print(
        "Filtered entries "
        f"({summary['status_filter']}): {summary['filtered_total']}"
    )
    print("")
    print("Status counts:")
    for key, value in sorted(summary["status_counts"].items()):
        print(f"- {key}: {value}")
    print("")
    print("Severity counts:")
    for key, value in sorted(summary["severity_counts"].items()):
        print(f"- {key}: {value}")
    print("")
    print("Area counts:")
    for key, value in sorted(summary["area_counts"].items()):
        print(f"- {key}: {value}")
    print("")
    print("Recent items:")
    for item in summary["recent"]:
        print(
            f"- {item.get('id')} [{item.get('status')}] "
            f"{item.get('severity')} {item.get('area')} - {item.get('summary')}"
        )


def summary_command(args: argparse.Namespace) -> int:
    base = Path(args.project_path).resolve()
    path = store_path(base)
    entries = load_entries(path)
    summary = summarize_entries(entries, status_filter=args.status, limit=max(1, args.limit))
    if args.json:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    else:
        print_summary(summary)
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "add":
        return add_entry(args)
    if args.command == "update":
        return update_entry(args)
    if args.command == "summary":
        return summary_command(args)
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
