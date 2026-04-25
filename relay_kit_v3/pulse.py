"""Static Pulse report generation for Relay-kit quality signals."""

from __future__ import annotations

import json
from collections import Counter
from html import escape
from pathlib import Path
from typing import Any, Callable, Mapping

from relay_kit_v3.evidence_ledger import LedgerSummary, summarize_events
from relay_kit_v3.readiness import build_readiness_report
from scripts import eval_workflows


SCHEMA_VERSION = "relay-kit.pulse-report.v1"
DEFAULT_OUTPUT_DIR = Path(".relay-kit") / "pulse"

WorkflowEvalBuilder = Callable[[Path], Mapping[str, Any]]
ReadinessBuilder = Callable[[Path, str, bool], Mapping[str, Any]]
EvidenceSummarizer = Callable[[Path, int], LedgerSummary]


def build_pulse_report(
    project_root: Path | str,
    *,
    profile: str = "enterprise",
    evidence_limit: int = 20,
    include_readiness: bool = False,
    skip_tests: bool = True,
    workflow_eval_file: Path | str | None = None,
    readiness_file: Path | str | None = None,
    workflow_eval_builder: WorkflowEvalBuilder | None = None,
    readiness_builder: ReadinessBuilder | None = None,
    evidence_summarizer: EvidenceSummarizer | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    eval_report = _load_or_build_workflow_eval(root, workflow_eval_file, workflow_eval_builder)
    readiness_report = _load_or_build_readiness(
        root,
        profile=profile,
        include_readiness=include_readiness,
        skip_tests=skip_tests,
        readiness_file=readiness_file,
        readiness_builder=readiness_builder,
    )
    evidence = _evidence_payload(root, evidence_limit, evidence_summarizer)
    status = pulse_status(eval_report, readiness_report, evidence)
    score = pulse_score(eval_report, readiness_report, evidence)

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "pulse_score": score,
        "project_path": str(root),
        "profile": profile,
        "workflow_eval": eval_report,
        "readiness": readiness_report,
        "evidence": evidence,
        "outputs": {
            "default_dir": str(root / DEFAULT_OUTPUT_DIR),
        },
    }


def write_pulse_report(
    project_root: Path | str,
    report: Mapping[str, Any],
    *,
    output_dir: Path | str | None = None,
) -> dict[str, Path]:
    root = Path(project_root).resolve()
    target_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_OUTPUT_DIR
    if not target_dir.is_absolute():
        target_dir = root / target_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    json_path = target_dir / "pulse-report.json"
    html_path = target_dir / "index.html"
    json_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_pulse_html(report), encoding="utf-8")
    return {"json": json_path, "html": html_path}


def render_pulse_html(report: Mapping[str, Any]) -> str:
    workflow_eval = _mapping(report.get("workflow_eval"))
    quality = _mapping(workflow_eval.get("quality"))
    readiness = _mapping(report.get("readiness"))
    evidence = _mapping(report.get("evidence"))
    status_counts = _mapping(evidence.get("recent_status_counts"))
    recent_events = evidence.get("recent_events", [])
    if not isinstance(recent_events, list):
        recent_events = []

    cards = [
        ("Pulse score", str(report.get("pulse_score", "-"))),
        ("Status", str(report.get("status", "-"))),
        ("Eval pass rate", _percent(workflow_eval.get("pass_rate"))),
        ("Evidence coverage", _percent(quality.get("evidence_term_coverage"))),
        ("Min route margin", str(quality.get("min_route_margin", "-"))),
        ("Readiness", str(readiness.get("verdict", "not-run"))),
        ("Ledger events", str(evidence.get("total_events", 0))),
        ("Recent failures", str(status_counts.get("fail", 0))),
    ]

    card_html = "\n".join(
        f'<section class="metric"><span>{escape(label)}</span><strong>{escape(value)}</strong></section>'
        for label, value in cards
    )
    rows = "\n".join(_event_row(event) for event in recent_events[-12:])
    if not rows:
        rows = '<tr><td colspan="4">No recent evidence events.</td></tr>'

    report_json = escape(json.dumps(report, ensure_ascii=True, indent=2))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Relay-kit Pulse</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #5d6876;
      --line: #d9dee7;
      --accent: #126b5f;
      --hold: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header, main {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
    }}
    header {{
      padding: 32px 0 18px;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      line-height: 1.1;
      letter-spacing: 0;
    }}
    .subtle {{ color: var(--muted); margin: 0; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .metric {{
      min-height: 92px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 10px;
    }}
    .metric strong {{
      display: block;
      font-size: 24px;
      line-height: 1.15;
      color: var(--accent);
      word-break: break-word;
    }}
    section.panel {{
      margin: 24px 0;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      padding: 10px 8px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-weight: 600; }}
    pre {{
      overflow: auto;
      max-height: 520px;
      padding: 14px;
      background: #111820;
      color: #f3f6fa;
      border-radius: 8px;
      font-size: 12px;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Relay-kit Pulse</h1>
    <p class="subtle">{escape(str(report.get("project_path", "")))}</p>
  </header>
  <main>
    <div class="grid">
      {card_html}
    </div>
    <section class="panel">
      <h2>Workflow quality</h2>
      <table>
        <tr><th>Signal</th><th>Value</th></tr>
        <tr><td>Scenario count</td><td>{escape(str(workflow_eval.get("scenario_count", 0)))}</td></tr>
        <tr><td>Average route margin</td><td>{escape(str(quality.get("average_route_margin", "-")))}</td></tr>
        <tr><td>Mean route confidence</td><td>{escape(str(quality.get("mean_route_confidence", "-")))}</td></tr>
        <tr><td>Expected skills</td><td>{escape(", ".join(_mapping(quality.get("expected_skill_counts")).keys()))}</td></tr>
      </table>
    </section>
    <section class="panel">
      <h2>Recent evidence</h2>
      <table>
        <tr><th>Time</th><th>Gate</th><th>Status</th><th>Findings</th></tr>
        {rows}
      </table>
    </section>
    <section class="panel">
      <h2>Raw report</h2>
      <pre>{report_json}</pre>
    </section>
  </main>
</body>
</html>
"""


def pulse_status(
    workflow_eval: Mapping[str, Any],
    readiness: Mapping[str, Any] | None,
    evidence: Mapping[str, Any],
) -> str:
    if workflow_eval.get("status") != "pass":
        return "hold"
    if readiness is not None and readiness.get("status") != "pass":
        return "hold"
    if readiness is not None and readiness.get("verdict") not in {None, "commercial-ready-candidate"}:
        return "attention"
    recent_status_counts = _mapping(evidence.get("recent_status_counts"))
    if int(recent_status_counts.get("fail", 0) or 0) > 0:
        return "attention"
    return "pass"


def pulse_score(
    workflow_eval: Mapping[str, Any],
    readiness: Mapping[str, Any] | None,
    evidence: Mapping[str, Any],
) -> int:
    quality = _mapping(workflow_eval.get("quality"))
    pass_rate = _float(workflow_eval.get("pass_rate"))
    evidence_coverage = _float(quality.get("evidence_term_coverage"), default=1.0)
    if readiness is None:
        readiness_score = 8
    elif readiness.get("status") == "pass" and readiness.get("verdict") == "commercial-ready-candidate":
        readiness_score = 15
    elif readiness.get("status") == "pass":
        readiness_score = 10
    else:
        readiness_score = 0
    fail_count = int(_mapping(evidence.get("recent_status_counts")).get("fail", 0) or 0)
    evidence_score = max(0, 5 - (fail_count * 2))
    score = round((pass_rate * 70) + (evidence_coverage * 10) + readiness_score + evidence_score)
    return max(0, min(100, int(score)))


def _load_or_build_workflow_eval(
    root: Path,
    workflow_eval_file: Path | str | None,
    workflow_eval_builder: WorkflowEvalBuilder | None,
) -> Mapping[str, Any]:
    if workflow_eval_file is not None:
        return _read_json(root, workflow_eval_file)
    builder = workflow_eval_builder or (lambda project_root: eval_workflows.build_report(project_root))
    return builder(root)


def _load_or_build_readiness(
    root: Path,
    *,
    profile: str,
    include_readiness: bool,
    skip_tests: bool,
    readiness_file: Path | str | None,
    readiness_builder: ReadinessBuilder | None,
) -> Mapping[str, Any] | None:
    if readiness_file is not None:
        return _read_json(root, readiness_file)
    if not include_readiness:
        return None
    builder = readiness_builder or (
        lambda project_root, selected_profile, should_skip_tests: build_readiness_report(
            project_root,
            profile=selected_profile,
            skip_tests=should_skip_tests,
        )
    )
    return builder(root, profile, skip_tests)


def _evidence_payload(
    root: Path,
    evidence_limit: int,
    evidence_summarizer: EvidenceSummarizer | None,
) -> dict[str, Any]:
    summarizer = evidence_summarizer or (lambda project_root, limit: summarize_events(project_root, limit=limit))
    summary = summarizer(root, evidence_limit)
    recent_status_counts = Counter(str(event.get("status", "unknown")) for event in summary.recent_events)
    return {
        "ledger_path": str(summary.ledger_path),
        "total_events": summary.total_events,
        "status_counts": summary.status_counts,
        "recent_status_counts": dict(sorted(recent_status_counts.items())),
        "gate_counts": summary.gate_counts,
        "recent_events": summary.recent_events,
    }


def _read_json(root: Path, path: Path | str) -> Mapping[str, Any]:
    source = Path(path)
    if not source.is_absolute():
        source = root / source
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"Pulse source must be a JSON object: {source}")
    return payload


def _event_row(event: Mapping[str, Any]) -> str:
    gate = str(event.get("gate", event.get("command", "unknown")))
    return (
        "<tr>"
        f"<td>{escape(str(event.get('timestamp', '-')))}</td>"
        f"<td>{escape(gate)}</td>"
        f"<td>{escape(str(event.get('status', 'unknown')))}</td>"
        f"<td>{escape(str(event.get('findings_count', '-')))}</td>"
        "</tr>"
    )


def _percent(value: Any) -> str:
    return f"{_float(value) * 100:.0f}%"


def _float(value: Any, *, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
