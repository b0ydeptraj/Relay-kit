from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from scripts import policy_guard


def test_policy_guard_enterprise_pack_passes_current_repo() -> None:
    findings = policy_guard.collect_findings(Path(__file__).resolve().parents[1], pack_name="enterprise")

    assert findings == []


def test_policy_guard_enterprise_pack_requires_governance_files(tmp_path: Path) -> None:
    findings = policy_guard.collect_findings(tmp_path, pack_name="enterprise")

    checks = {finding.check for finding in findings}
    assert "required-policy-file" in checks
    assert any(".relay-kit/references/security-patterns.md" in finding.detail for finding in findings)
    assert any(".relay-kit/docs/review-loop.md" in finding.detail for finding in findings)


def test_policy_guard_json_reports_pack(tmp_path: Path, capsys) -> None:
    exit_code = policy_guard.main([str(tmp_path), "--pack", "team", "--json"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["pack"] == "team"
    assert payload["findings_count"] > 0


def test_public_cli_policy_list_and_check(capsys) -> None:
    list_exit = relay_kit_public_cli.main(["policy", "list"])
    check_exit = relay_kit_public_cli.main(["policy", "check", ".", "--pack", "baseline", "--strict", "--json"])

    output = capsys.readouterr().out
    payload = json.loads(output[output.index("{") :])

    assert list_exit == 0
    assert check_exit == 0
    assert "enterprise" in output
    assert payload["pack"] == "baseline"
    assert payload["findings_count"] == 0
