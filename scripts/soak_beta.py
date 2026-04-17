#!/usr/bin/env python3
"""Run Relay-kit beta soak across multiple projects and append a markdown report."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO_ROOT / "docs" / "relay-kit-beta-soak-log.md"

REQUIRED_DIRS = [
    ".claude/skills",
    ".agent/skills",
    ".codex/skills",
    ".relay-kit/contracts",
    ".relay-kit/state",
    ".relay-kit/docs",
    ".relay-kit/references",
]


@dataclass(frozen=True)
class SoakItem:
    project: str
    duration_sec: float
    status: str
    missing_dirs: List[str]
    stderr_tail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Relay-kit baseline generation smoke across multiple projects.",
    )
    parser.add_argument(
        "projects",
        nargs="+",
        help="Project paths to run soak against",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report to stdout")
    parser.add_argument(
        "--append-report",
        action="store_true",
        help="Append a markdown checkpoint into docs/relay-kit-beta-soak-log.md",
    )
    return parser.parse_args()


def run_generation(project: Path) -> SoakItem:
    start = time.perf_counter()
    cmd = [
        sys.executable,
        str(REPO_ROOT / "relay_kit.py"),
        str(project),
        "--bundle",
        "baseline",
        "--ai",
        "all",
        "--emit-contracts",
        "--emit-docs",
        "--emit-reference-templates",
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    duration = time.perf_counter() - start

    missing_dirs = [
        rel for rel in REQUIRED_DIRS if not (project / rel).is_dir()
    ]

    ok = result.returncode == 0 and not missing_dirs
    return SoakItem(
        project=str(project),
        duration_sec=round(duration, 2),
        status="pass" if ok else "fail",
        missing_dirs=missing_dirs,
        stderr_tail="\n".join(result.stderr.splitlines()[-15:]),
    )


def append_markdown_report(items: List[SoakItem]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "",
        f"## Soak checkpoint {timestamp}",
        "",
        "| Project | Status | Duration (s) | Missing dirs |",
        "|---|---|---:|---|",
    ]
    for item in items:
        missing = ", ".join(item.missing_dirs) if item.missing_dirs else "-"
        lines.append(f"| `{item.project}` | `{item.status}` | `{item.duration_sec}` | {missing} |")

    failed = [item for item in items if item.status != "pass"]
    if failed:
        lines.extend(["", "### Failure tails", ""])
        for item in failed:
            lines.append(f"#### {item.project}")
            lines.append("```text")
            lines.append(item.stderr_tail or "(no stderr)")
            lines.append("```")
            lines.append("")

    if REPORT_PATH.exists():
        existing = REPORT_PATH.read_text(encoding="utf-8")
    else:
        existing = "# Relay-kit beta soak log\n\nTrack real-project soak checkpoints before broader rollout.\n"
    REPORT_PATH.write_text(existing.rstrip() + "\n" + "\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()

    items: List[SoakItem] = []
    for raw in args.projects:
        project = Path(raw).resolve()
        if not project.exists():
            print(f"Missing project path: {project}", file=sys.stderr)
            return 2
        items.append(run_generation(project))

    payload = {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "count": len(items),
        "results": [
            {
                "project": item.project,
                "status": item.status,
                "duration_sec": item.duration_sec,
                "missing_dirs": item.missing_dirs,
            }
            for item in items
        ],
    }

    if args.append_report:
        append_markdown_report(items)

    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        for item in items:
            missing = ", ".join(item.missing_dirs) if item.missing_dirs else "-"
            print(f"{item.project}: {item.status} ({item.duration_sec}s) missing_dirs={missing}")

    return 0 if all(item.status == "pass" for item in items) else 2


if __name__ == "__main__":
    raise SystemExit(main())
