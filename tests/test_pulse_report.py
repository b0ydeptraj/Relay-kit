from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3 import pulse
from relay_kit_v3.evidence_ledger import append_event


def sample_eval_report() -> dict[str, object]:
    return {
        "schema_version": "relay-kit.workflow-eval.v1",
        "status": "pass",
        "scenario_count": 2,
        "passed": 2,
        "failed": 0,
        "pass_rate": 1.0,
        "quality": {
            "min_route_margin": 3,
            "average_route_margin": 8.5,
            "evidence_term_coverage": 1.0,
            "expected_skill_counts": {"developer": 1, "qa-governor": 1},
        },
        "findings_count": 0,
        "findings": [],
    }


def sample_readiness_report() -> dict[str, object]:
    return {
        "schema_version": "relay-kit.readiness-report.v1",
        "status": "pass",
        "verdict": "commercial-ready-candidate",
        "profile": "enterprise",
        "findings": [],
        "gates": [
            {"id": "pytest", "status": "pass"},
            {"id": "workflow-eval", "status": "pass"},
        ],
    }


def test_pulse_report_summarizes_eval_readiness_and_evidence(tmp_path: Path) -> None:
    append_event(tmp_path, {"command": "doctor", "gate": "policy guard", "status": "pass"})
    append_event(tmp_path, {"command": "doctor", "gate": "workflow eval", "status": "fail"})

    report = pulse.build_pulse_report(
        tmp_path,
        include_readiness=True,
        workflow_eval_builder=lambda root: sample_eval_report(),
        readiness_builder=lambda root, profile, skip_tests: sample_readiness_report(),
    )

    assert report["schema_version"] == "relay-kit.pulse-report.v1"
    assert report["status"] == "attention"
    assert report["pulse_score"] < 100
    assert report["workflow_eval"]["quality"]["average_route_margin"] == 8.5
    assert report["readiness"]["verdict"] == "commercial-ready-candidate"
    assert report["evidence"]["status_counts"]["fail"] == 1


def test_pulse_report_writes_json_and_html(tmp_path: Path) -> None:
    report = pulse.build_pulse_report(
        tmp_path,
        workflow_eval_builder=lambda root: sample_eval_report(),
    )

    outputs = pulse.write_pulse_report(tmp_path, report, output_dir=tmp_path / "pulse")

    assert outputs["json"].exists()
    assert outputs["html"].exists()
    assert json.loads(outputs["json"].read_text(encoding="utf-8"))["schema_version"] == "relay-kit.pulse-report.v1"
    html = outputs["html"].read_text(encoding="utf-8")
    assert "Relay-kit Pulse" in html
    assert "Workflow quality" in html


def test_pulse_report_marks_limited_beta_readiness_as_attention(tmp_path: Path) -> None:
    limited_readiness = {
        **sample_readiness_report(),
        "verdict": "limited-beta",
    }

    report = pulse.build_pulse_report(
        tmp_path,
        include_readiness=True,
        workflow_eval_builder=lambda root: sample_eval_report(),
        readiness_builder=lambda root, profile, skip_tests: limited_readiness,
    )

    assert report["status"] == "attention"
    assert report["pulse_score"] < 100


def test_public_cli_pulse_build_json(tmp_path: Path, capsys) -> None:
    exit_code = relay_kit_public_cli.main(["pulse", "build", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["report"]["schema_version"] == "relay-kit.pulse-report.v1"
    assert Path(payload["outputs"]["json"]).exists()
    assert Path(payload["outputs"]["html"]).exists()
