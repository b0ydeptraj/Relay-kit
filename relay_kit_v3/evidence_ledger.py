"""Structured evidence ledger utilities for Relay-kit gate runs."""

from __future__ import annotations

import json
import re
import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


LEDGER_PATH = Path(".relay-kit") / "evidence" / "events.jsonl"
FINDINGS_PATTERN = re.compile(r"findings:\s*(?P<count>\d+)", re.IGNORECASE)


@dataclass(frozen=True)
class LedgerSummary:
    ledger_path: Path
    total_events: int
    status_counts: dict[str, int]
    gate_counts: dict[str, int]
    recent_events: list[dict[str, Any]]


def new_run_id() -> str:
    return uuid.uuid4().hex


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def ledger_path(project_root: Path | str) -> Path:
    return Path(project_root).resolve() / LEDGER_PATH


def parse_findings_count(*streams: str) -> int | None:
    for stream in streams:
        match = FINDINGS_PATTERN.search(stream or "")
        if match is not None:
            return int(match.group("count"))
    return None


def append_event(project_root: Path | str, event: dict[str, Any]) -> Path:
    path = ledger_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": utc_timestamp(),
        **event,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True, sort_keys=True))
        handle.write("\n")
    return path


def read_events(project_root: Path | str) -> list[dict[str, Any]]:
    path = ledger_path(project_root)
    if not path.exists():
        return []

    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        payload = json.loads(stripped)
        if isinstance(payload, dict):
            events.append(payload)
    return events


def summarize_events(project_root: Path | str, *, limit: int = 20) -> LedgerSummary:
    events = read_events(project_root)
    status_counts = Counter(str(event.get("status", "unknown")) for event in events)
    gate_counts = Counter(str(event.get("gate", event.get("command", "unknown"))) for event in events)
    return LedgerSummary(
        ledger_path=ledger_path(project_root),
        total_events=len(events),
        status_counts=dict(sorted(status_counts.items())),
        gate_counts=dict(sorted(gate_counts.items())),
        recent_events=list(_tail(events, limit)),
    )


def _tail(events: Iterable[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    items = list(events)
    if limit <= 0:
        return []
    return items[-limit:]
