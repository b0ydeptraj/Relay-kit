from __future__ import annotations

import json
from pathlib import Path

import relay_kit_public_cli
from relay_kit_v3.delegation_control import (
    append_ledger_event,
    build_delegation_audit,
    build_delegation_plan,
    classify_reasoning,
    close_completed,
)


def test_reasoning_defaults_to_medium_and_low_requires_mechanical_l0() -> None:
    assert classify_reasoning("implement a bounded feature")[0] == "medium"
    assert classify_reasoning("investigate and rename unclear module", "L0")[0] == "medium"
    assert classify_reasoning("rename generated file", "L0")[0] == "low"


def test_critical_work_uses_high_reasoning() -> None:
    assert classify_reasoning("root-cause production authentication incident", "L3")[0] == "high"


def test_planner_keeps_l1_serial_and_delegates_bounded_l2(tmp_path: Path) -> None:
    serial = build_delegation_plan(tmp_path, task="implement helper", complexity="L1")
    assert serial["decision"] == "serial"
    delegated = build_delegation_plan(
        tmp_path,
        task="implement independent bounded helper",
        complexity="L2",
        independent=True,
        artifact="src/helper.py",
        lock_scope="src/helper.py",
        expected_return_condition="focused test passes",
        verification_command="pytest tests/test_helper.py -q",
    )
    assert delegated["decision"] == "delegate"
    assert delegated["reasoning_tier"] == "medium"
    assert delegated["summary"]["planned_agents"] == 1


def test_audit_blocks_concurrency_violation(tmp_path: Path) -> None:
    for index in range(3):
        append_ledger_event(tmp_path, {
            "agent_id": f"agent-{index}",
            "status": "running",
            "artifact": f"src/{index}.py",
            "lock_scope": f"src/{index}.py",
            "expected_return_condition": "test passes",
            "context_pack_path": f".relay-kit/delegation/context/{index}.json",
            "reasoning_tier": "medium",
            "estimated_tokens": 1000,
        })
    report = build_delegation_audit(tmp_path)
    assert report["status"] == "hold"
    assert any(item["id"] == "concurrency-limit-exceeded" for item in report["findings"])


def test_close_completed_requires_handoff_and_removes_context_pack(tmp_path: Path) -> None:
    context = tmp_path / ".relay-kit/delegation/context/agent.json"
    context.parent.mkdir(parents=True)
    context.write_text("{}\n", encoding="utf-8")
    append_ledger_event(tmp_path, {
        "agent_id": "agent-1",
        "status": "handoff-received",
        "handoff_evidence": "tests passed",
        "context_pack_path": ".relay-kit/delegation/context/agent.json",
    })
    report = close_completed(tmp_path)
    assert report["closed_agents"] == ["agent-1"]
    assert not context.exists()
    assert build_delegation_audit(tmp_path)["summary"]["closed_agents"] == 1


def test_public_cli_plan_and_capabilities(tmp_path: Path, capsys) -> None:
    code = relay_kit_public_cli.main([
        "delegation", "plan", str(tmp_path), "--task", "bounded independent implementation",
        "--complexity", "L2", "--independent", "--artifact", "src/a.py", "--lock-scope", "src/a.py",
        "--expected-return-condition", "test passes", "--verification-command", "pytest -q", "--json",
    ])
    assert code == 0
    assert json.loads(capsys.readouterr().out)["reasoning_tier"] == "medium"
    code = relay_kit_public_cli.main(["delegation", "capabilities", str(tmp_path), "--adapter", "all", "--json"])
    assert code == 0
    assert len(json.loads(capsys.readouterr().out)["capabilities"]) == 3
