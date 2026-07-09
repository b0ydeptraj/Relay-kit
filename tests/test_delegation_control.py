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


import traceback
import sys
import tempfile
import shutil

class DummyCapsys:
    def __init__(self):
        self.out = ""
        self.err = ""
    def readouterr(self):
        return self
        
def test_reasoning_defaults_to_medium_and_low_requires_mechanical_l0() -> None:
    assert classify_reasoning("implement a bounded feature")[0] == "medium"
    assert classify_reasoning("investigate and rename unclear module", "L0")[0] == "medium"
    assert classify_reasoning("rename generated file", "L0")[0] == "low"

def test_critical_work_uses_high_reasoning() -> None:
    assert classify_reasoning("root-cause production authentication incident", "L3")[0] == "high"

def test_planner_keeps_l1_serial_and_delegates_bounded_l2() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_path = Path(temp_dir)
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
            apply=True
        )
        assert delegated["decision"] == "delegate"
        assert delegated["reasoning_tier"] == "medium"
        assert delegated["summary"]["planned_agents"] == 1

def test_audit_blocks_concurrency_violation() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_path = Path(temp_dir)
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

def test_close_completed_requires_handoff_and_removes_context_pack() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        tmp_path = Path(temp_dir)
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

if __name__ == '__main__':
    try:
        test_reasoning_defaults_to_medium_and_low_requires_mechanical_l0()
        test_critical_work_uses_high_reasoning()
        test_planner_keeps_l1_serial_and_delegates_bounded_l2()
        test_audit_blocks_concurrency_violation()
        test_close_completed_requires_handoff_and_removes_context_pack()
        print("RESULT: ALL DELEGATION CONTROL TESTS PASSED")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
