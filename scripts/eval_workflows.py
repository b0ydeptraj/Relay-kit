#!/usr/bin/env python3
"""Scenario evaluation harness for Relay-kit workflow routing."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from relay_kit_v3.registry.skills import ALL_V3_SKILLS
from scripts.skill_gauntlet import (
    DEFAULT_SCENARIO_FIXTURE,
    load_scenario_fixtures,
    rank_prompt_routes,
    rendered_skill_contract,
    resolve_scenario_fixture_path,
)


SCHEMA_VERSION = "relay-kit.workflow-eval.v1"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate Relay-kit workflow routing scenarios and report pass-rate signals.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project root")
    parser.add_argument(
        "--scenario-fixtures",
        default=str(DEFAULT_SCENARIO_FIXTURE),
        help="JSON scenario fixture file.",
    )
    parser.add_argument("--output-file", default=None, help="Optional JSON report output path")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when any scenario fails")
    return parser.parse_args(argv)


def evaluate_scenario(
    scenario: Mapping[str, object],
    registry: Mapping[str, object],
    *,
    top_limit: int = 5,
) -> dict[str, object]:
    scenario_id = str(scenario.get("id", "")).strip() or "unnamed-scenario"
    prompt = str(scenario.get("prompt", "")).strip()
    expected_skill = str(scenario.get("expected_skill", "")).strip()
    expected_terms = scenario.get("expected_terms", [])
    findings: list[dict[str, str]] = []
    ranked: list[tuple[int, str]] = []
    predicted_skill = ""

    if not prompt:
        findings.append({"check": "scenario-contract", "detail": "Missing prompt"})
    if not expected_skill:
        findings.append({"check": "scenario-contract", "detail": "Missing expected_skill"})
    elif expected_skill not in registry:
        findings.append({"check": "scenario-contract", "detail": f"Unknown expected_skill: {expected_skill}"})

    if not isinstance(expected_terms, list):
        findings.append({"check": "scenario-contract", "detail": "expected_terms must be a list"})
        expected_terms = []

    if prompt and expected_skill in registry:
        ranked = rank_prompt_routes(prompt, registry)
        top_score, predicted_skill = ranked[0] if ranked else (0, "")
        if predicted_skill != expected_skill:
            top = ", ".join(f"{name}:{score}" for score, name in ranked[:top_limit])
            findings.append(
                {
                    "check": "scenario-route",
                    "detail": (
                        f"Expected {expected_skill}, predicted {predicted_skill or '-'} "
                        f"with score {top_score}. Top routes: {top}"
                    ),
                }
            )

        contract = rendered_skill_contract(registry[expected_skill])
        missing_terms = [
            str(term)
            for term in expected_terms
            if str(term).strip() and str(term).lower() not in contract
        ]
        if missing_terms:
            findings.append(
                {
                    "check": "scenario-evidence-contract",
                    "detail": f"Expected skill {expected_skill} is missing scenario terms: {', '.join(missing_terms)}",
                }
            )
    else:
        missing_terms = []

    return {
        "id": scenario_id,
        "prompt": prompt,
        "expected_skill": expected_skill,
        "predicted_skill": predicted_skill,
        "passed": not findings,
        "top_routes": [{"skill": name, "score": score} for score, name in ranked[:top_limit]],
        "expected_terms": [str(term) for term in expected_terms],
        "missing_terms": missing_terms,
        "findings": findings,
    }


def build_report(
    project_path: Path | str,
    *,
    scenario_fixtures: Path | str | None = None,
) -> dict[str, object]:
    base = Path(project_path).resolve()
    fixture_path = Path(scenario_fixtures) if scenario_fixtures is not None else DEFAULT_SCENARIO_FIXTURE
    resolved_fixture = resolve_scenario_fixture_path(base, fixture_path)
    scenarios = load_scenario_fixtures(base, fixture_path)
    results = [evaluate_scenario(scenario, ALL_V3_SKILLS) for scenario in scenarios]
    failed = sum(1 for result in results if not result["passed"])
    passed = len(results) - failed
    scenario_count = len(results)

    harness_findings: list[dict[str, str]] = []
    if resolved_fixture is None:
        harness_findings.append(
            {
                "check": "scenario-fixtures",
                "detail": f"Scenario fixture file not found: {fixture_path}",
            }
        )
    elif scenario_count == 0:
        harness_findings.append(
            {
                "check": "scenario-fixtures",
                "detail": f"Scenario fixture file contains no scenarios: {resolved_fixture}",
            }
        )

    scenario_findings_count = sum(
        len(result.get("findings", []))
        for result in results
        if isinstance(result.get("findings", []), list)
    )
    findings_count = scenario_findings_count + len(harness_findings)
    pass_rate = round(passed / scenario_count, 4) if scenario_count else 0.0
    status = "pass" if findings_count == 0 else "fail"

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "project_path": str(base),
        "fixture_path": str(resolved_fixture) if resolved_fixture else str(fixture_path),
        "scenario_count": scenario_count,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "findings_count": findings_count,
        "findings": harness_findings,
        "results": results,
    }


def render_text(report: Mapping[str, object]) -> str:
    lines = [
        "Relay-kit workflow eval",
        f"- project: {report['project_path']}",
        f"- fixture: {report['fixture_path']}",
        f"- scenarios: {report['scenario_count']}",
        f"- passed: {report['passed']}",
        f"- failed: {report['failed']}",
        f"- pass rate: {float(report['pass_rate']):.2f}",
        f"- findings: {report['findings_count']}",
    ]

    findings = list(report.get("findings", []))
    for result in report.get("results", []):
        if isinstance(result, dict) and not result.get("passed", False):
            for finding in result.get("findings", []):
                if isinstance(finding, dict):
                    findings.append(
                        {
                            "check": str(finding.get("check", "scenario")),
                            "detail": f"{result.get('id', 'unnamed-scenario')}: {finding.get('detail', '')}",
                        }
                    )

    if findings:
        lines.append("")
        lines.append("Top findings:")
        for finding in findings[:20]:
            lines.append(f"- {finding['check']}: {finding['detail']}")
        if len(findings) > 20:
            lines.append(f"- ... and {len(findings) - 20} more")
    return "\n".join(lines)


def write_report(report: Mapping[str, object], output_file: Path | str) -> Path:
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args.project_path, scenario_fixtures=args.scenario_fixtures)

    if args.output_file:
        write_report(report, args.output_file)

    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_text(report))

    if args.strict and report["status"] != "pass":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
