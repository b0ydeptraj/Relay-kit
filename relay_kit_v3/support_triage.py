"""Support triage readiness report for Relay-kit paid/team support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.support_bundle import DEFAULT_OUTPUT as DEFAULT_BUNDLE_OUTPUT
from relay_kit_v3.support_bundle import SCHEMA_VERSION as SUPPORT_BUNDLE_SCHEMA_VERSION
from relay_kit_v3.support_bundle import redact_value, severity_levels
from relay_kit_v3.support_request import DEFAULT_OUTPUT as DEFAULT_REQUEST_OUTPUT
from relay_kit_v3.support_request import SCHEMA_VERSION as SUPPORT_REQUEST_SCHEMA_VERSION


SCHEMA_VERSION = "relay-kit.support-triage.v1"


def build_support_triage(
    project_root: Path | str,
    *,
    request_file: Path | str | None = None,
    bundle_file: Path | str | None = None,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    request_path = _resolve_path(root, request_file, DEFAULT_REQUEST_OUTPUT)
    bundle_path = _resolve_path(root, bundle_file, DEFAULT_BUNDLE_OUTPUT)
    request_payload = _read_json_object(request_path)
    bundle_payload = _read_json_object(bundle_path)

    request_check = support_request_check(request_path, request_payload)
    bundle_check = support_bundle_check(bundle_path, bundle_payload)
    checks = [request_check, bundle_check]
    request = request_payload if isinstance(request_payload, Mapping) else {}
    severity = str(request.get("severity") or "")
    sla = severity_sla(severity)
    findings = [
        {
            "gate": str(check["id"]),
            "status": str(check["status"]),
            "summary": str(check["summary"]),
        }
        for check in checks
        if check["status"] != "pass"
    ]
    status = "ready" if not findings else "hold"
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "severity": severity,
        "sla": sla,
        "request_file": str(request_path),
        "bundle_file": str(bundle_path),
        "checks": checks,
        "checks_by_id": {str(check["id"]): check for check in checks},
        "findings": findings,
        "next_actions": support_triage_next_actions(status, request_check, bundle_check),
        "residual_risks": [
            "Support triage validates local artifacts only; it does not create a legal SLA commitment.",
            "Private customer environment access and reproduction steps remain external support workflow inputs.",
        ],
    }
    return redact_value(report)


def render_support_triage(report: Mapping[str, Any]) -> str:
    sla = _mapping(report.get("sla"))
    lines = [
        "Relay-kit support triage",
        f"- project: {report.get('project_path')}",
        f"- severity: {report.get('severity') or '-'}",
        f"- target: {sla.get('target', '-')}",
        f"- status: {report.get('status')}",
        f"- findings: {len(report.get('findings', []))}",
    ]
    for finding in report.get("findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"  - {finding.get('gate')}: {finding.get('summary')}")
    actions = report.get("next_actions", [])
    if actions:
        lines.append("- next actions:")
        lines.extend(f"  - {action}" for action in actions)
    return "\n".join(lines)


def support_request_check(path: Path, payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return check("support-request", "support request", "hold", "missing or invalid support request", path=path)
    if payload.get("schema_version") != SUPPORT_REQUEST_SCHEMA_VERSION:
        return check("support-request", "support request", "hold", "support request schema does not match", path=path)
    if payload.get("status") != "ready":
        findings = payload.get("findings", [])
        count = len(findings) if isinstance(findings, list) else 0
        return check(
            "support-request",
            "support request",
            "hold",
            f"support request is {payload.get('status', 'unknown')} with {count} findings",
            path=path,
            details={"findings_count": count},
        )
    diagnostics = payload.get("diagnostics", [])
    missing = [
        str(item.get("path", ""))
        for item in diagnostics
        if isinstance(item, Mapping) and item.get("status") != "present"
    ]
    if missing:
        return check(
            "support-request",
            "support request",
            "hold",
            "support request has missing diagnostics",
            path=path,
            details={"missing_diagnostics": missing},
        )
    return check("support-request", "support request", "pass", "support request is ready", path=path)


def support_bundle_check(path: Path, payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return check("support-bundle", "support bundle", "hold", "missing or invalid support bundle", path=path)
    if payload.get("schema_version") != SUPPORT_BUNDLE_SCHEMA_VERSION:
        return check("support-bundle", "support bundle", "hold", "support bundle schema does not match", path=path)
    return check("support-bundle", "support bundle", "pass", "support bundle is present", path=path)


def support_triage_next_actions(
    status: str,
    request_check: Mapping[str, Any],
    bundle_check: Mapping[str, Any],
) -> list[str]:
    if status == "ready":
        return [
            "Open the support case with .relay-kit/support/support-request.json and .relay-kit/support/support-bundle.json.",
            "Include the failing command output and any private reproduction notes outside the repository.",
        ]
    actions: list[str] = []
    if bundle_check.get("status") != "pass":
        actions.append("Run relay-kit support bundle <project> --policy-pack enterprise before triage.")
    if request_check.get("status") != "pass":
        actions.append("Run relay-kit support request <project> --severity P1 --policy-pack enterprise --strict --json and fill missing fields.")
    return actions


def severity_sla(severity: str) -> dict[str, str]:
    for item in severity_levels():
        if item.get("severity") == severity:
            return dict(item)
    return {
        "severity": severity,
        "meaning": "Unknown or missing severity.",
        "target": "triage target unavailable until severity is set",
    }


def check(
    check_id: str,
    label: str,
    status: str,
    summary: str,
    *,
    path: Path,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "status": status,
        "summary": summary,
        "details": {"path": str(path), **dict(details or {})},
    }


def _resolve_path(root: Path, value: Path | str | None, default: Path) -> Path:
    path = Path(value) if value is not None else root / default
    return path if path.is_absolute() else root / path


def _read_json_object(path: Path) -> Mapping[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _mapping(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
