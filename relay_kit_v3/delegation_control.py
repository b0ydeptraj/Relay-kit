from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from relay_kit_v3.token_economy import build_context_pack
from relay_kit_v3.lane_lock import LaneLockManager
from relay_kit_v3.event_ledger import EventLedger


PLAN_SCHEMA_VERSION = "relay-kit.delegation-plan.v1"
AUDIT_SCHEMA_VERSION = "relay-kit.delegation-audit.v1"
CAPABILITY_SCHEMA_VERSION = "relay-kit.delegation-capabilities.v1"
POLICY_SCHEMA_VERSION = "relay-kit.delegation-policy.v1"
LEDGER_SCHEMA_VERSION = "relay-kit.delegation-ledger-event.v1"

POLICY_PATH = Path(".relay-kit/state/delegation-policy.json")
LEDGER_PATH = Path(".relay-kit/state/delegation-ledger.jsonl")
PLAN_DIR = Path(".relay-kit/delegation/plans")
CONTEXT_DIR = Path(".relay-kit/delegation/context")

DEFAULT_POLICY: dict[str, Any] = {
    "schema_version": POLICY_SCHEMA_VERSION,
    "default_reasoning_tier": "medium",
    "uncertain_reasoning_fallback": "medium",
    "max_concurrent_subagents": 2,
    "max_subagents_per_task": 3,
    "max_total_estimated_tokens": 20000,
    "max_tokens_per_subagent": 6000,
    "max_high_reasoning_agents": 1,
    "close_after_handoff": True,
}

HIGH_RISK_TERMS = {
    "architecture", "architect", "security", "auth", "migration", "root cause",
    "root-cause", "production", "incident", "encryption", "payment", "database",
    "distributed", "race condition",
}
LOW_MECHANICAL_TERMS = {
    "rename", "format", "typo", "copy", "list", "sort", "update version",
    "replace text", "documentation typo", "generated file", "lint-only",
}
AMBIGUITY_TERMS = {
    "investigate", "unknown", "unclear", "decide", "trade-off", "tradeoff",
    "explore", "why", "maybe",
}
ACTIVE_STATUSES = {"approved", "running", "handoff-received"}


def ensure_policy(project_root: Path | str) -> Path:
    root = Path(project_root).resolve()
    path = root / POLICY_PATH
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(DEFAULT_POLICY, indent=2) + "\n", encoding="utf-8")
    return path


def load_policy(project_root: Path | str) -> dict[str, Any]:
    path = ensure_policy(project_root)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {}
    return {**DEFAULT_POLICY, **payload, "schema_version": POLICY_SCHEMA_VERSION}


def adapter_capabilities(adapter: str = "all") -> dict[str, Any]:
    records = {
        "codex": _capability("codex", usage="advisory", note="enforce only when the active Codex runtime exposes matching controls"),
        "claude": _capability("claude", usage="advisory", note="model and turn controls vary by Claude runtime surface"),
        "agent": _capability("agent", usage="unsupported", note="Antigravity/custom-agent enforcement remains capability-dependent"),
    }
    if adapter == "all":
        selected = list(records.values())
    elif adapter == "antigravity":
        selected = [records["agent"]]
    else:
        selected = [records.get(adapter, records["agent"])]
    return {"schema_version": CAPABILITY_SCHEMA_VERSION, "status": "pass", "adapter": adapter, "capabilities": selected}


def _capability(adapter: str, *, usage: str, note: str) -> dict[str, str]:
    return {
        "adapter": adapter,
        "reasoning_tier": "advisory",
        "spawn": "advisory",
        "close": "advisory",
        "usage_metadata": usage,
        "note": note,
    }


def classify_reasoning(task: str, complexity: str | None = None) -> tuple[str, str]:
    text = task.casefold()
    if complexity == "L4" or any(term in text for term in HIGH_RISK_TERMS):
        return "high", "critical architecture, security, migration, production, or root-cause work"
    mechanical = any(term in text for term in LOW_MECHANICAL_TERMS)
    ambiguous = any(term in text for term in AMBIGUITY_TERMS)
    if complexity == "L0" and mechanical and not ambiguous:
        return "low", "proven mechanical low-risk task with no ambiguity"
    return "medium", "normal or uncertain work defaults to medium reasoning"


def build_delegation_plan(
    project_root: Path | str,
    *,
    task: str,
    budget: int | None = None,
    complexity: str | None = None,
    adapter: str = "all",
    artifact: str | None = None,
    lock_scope: str | None = None,
    expected_return_condition: str | None = None,
    verification_command: str | None = None,
    independent: bool = False,
    apply: bool = False,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    policy = load_policy(root)
    tier, reason = classify_reasoning(task, complexity)
    max_total = min(int(budget or policy["max_total_estimated_tokens"]), int(policy["max_total_estimated_tokens"]))
    per_agent = min(int(policy["max_tokens_per_subagent"]), max_total)
    required = {
        "artifact": artifact,
        "lock_scope": lock_scope,
        "expected_return_condition": expected_return_condition,
        "verification_command": verification_command,
    }
    missing = [key for key, value in required.items() if not value]
    complexity_value = int((complexity or "L1")[1])
    should_delegate = independent and complexity_value >= 2 and not missing
    planned_agents = min(2 if complexity_value >= 3 else 1, int(policy["max_concurrent_subagents"])) if should_delegate else 0
    decision = "delegate" if should_delegate else "serial"
    findings: list[dict[str, Any]] = []
    if independent and missing:
        findings.append({"id": "incomplete-delegation-contract", "status": "attention", "summary": f"missing: {', '.join(missing)}"})
    if not independent and complexity_value <= 1:
        findings.append({"id": "unnecessary-spawn-avoided", "status": "pass", "summary": "main agent keeps the bounded low-complexity task"})
    if planned_agents * per_agent > max_total:
        decision = "blocked" if tier == "high" else "serial"
        planned_agents = 0
        findings.append({"id": "delegation-budget-violation", "status": "hold", "summary": "planned agents exceed delegation budget"})
        
    # V5.4.3: Check lane locks before delegation
    acquired_locks = []
    lane_id = f"{_slug(task)}-lane"
    lock_mgr = LaneLockManager(root)
    if should_delegate and lock_scope:
        files_to_lock = [f.strip() for f in lock_scope.split(",") if f.strip()]
        for f in files_to_lock:
            if lock_mgr.acquire(lane_id, f, agent_id="delegator"):
                acquired_locks.append(f)
            else:
                # Rollback locks
                for acq in acquired_locks:
                    lock_mgr.release(lane_id, acq)
                acquired_locks = []
                decision = "blocked"
                planned_agents = 0
                findings.append({"id": "lock-conflict", "status": "hold", "summary": f"File {f} is currently locked by another lane"})
                break
                
    context_pack_path = None
    if planned_agents:
        pack = build_context_pack(root, task=task, max_tokens=per_agent)
        context_target = root / CONTEXT_DIR / f"{_slug(task)}.json"
        context_target.parent.mkdir(parents=True, exist_ok=True)
        context_target.write_text(json.dumps(pack, indent=2) + "\n", encoding="utf-8")
        context_pack_path = context_target.relative_to(root).as_posix()
        
    status = "hold" if decision == "blocked" else "pass"
    report = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "status": status,
        "project_path": str(root),
        "task": task,
        "complexity": complexity or "L1",
        "decision": decision,
        "reasoning_tier": tier,
        "reasoning_reason": reason,
        "enforcement": _adapter_enforcement(adapter),
        "policy": policy,
        "contract": {**required, "independent": independent},
        "context_pack_path": context_pack_path,
        "summary": {"planned_agents": planned_agents, "estimated_tokens": planned_agents * per_agent, "budget": max_total, "findings": len(findings)},
        "findings": findings,
    }
    if apply and decision == "delegate":
        write_plan(root, report)
        ledger = EventLedger(root)
        ledger.log_event("lane_started", lane_id, {"task": task, "agents": planned_agents})
        for f in acquired_locks:
            ledger.log_event("file_locked", lane_id, {"file": f})
        ledger.close()
        
        for index in range(planned_agents):
            append_ledger_event(root, {
                "agent_id": f"{_slug(task)}-{index + 1}",
                "event": "approved",
                "status": "approved",
                "adapter": adapter,
                "task": task,
                "artifact": artifact,
                "lock_scope": lock_scope,
                "expected_return_condition": expected_return_condition,
                "verification_command": verification_command,
                "reasoning_tier": tier,
                "reasoning_reason": reason,
                "enforcement": report["enforcement"],
                "estimated_tokens": per_agent,
                "actual_tokens": None,
                "context_pack_path": context_pack_path,
            })
    
    lock_mgr.close()
    return report


def append_ledger_event(project_root: Path | str, event: Mapping[str, Any]) -> Path:
    root = Path(project_root).resolve()
    path = root / LEDGER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**event, "schema_version": LEDGER_SCHEMA_VERSION, "timestamp": datetime.now(timezone.utc).isoformat()}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    return path


def read_ledger(project_root: Path | str) -> list[dict[str, Any]]:
    path = Path(project_root).resolve() / LEDGER_PATH
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def latest_agent_states(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    states: dict[str, dict[str, Any]] = {}
    for record in records:
        agent_id = str(record.get("agent_id", "")).strip()
        if agent_id:
            states[agent_id] = {**states.get(agent_id, {}), **record}
    return states


def build_delegation_audit(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    policy = load_policy(root)
    states = latest_agent_states(read_ledger(root))
    active = [item for item in states.values() if item.get("status") in ACTIVE_STATUSES]
    high = [item for item in active if item.get("reasoning_tier") == "high"]
    estimated = sum(int(item.get("estimated_tokens") or 0) for item in active)
    actual = [int(item["actual_tokens"]) for item in states.values() if item.get("actual_tokens") is not None]
    findings: list[dict[str, Any]] = []
    if len(active) > int(policy["max_concurrent_subagents"]):
        findings.append({"id": "concurrency-limit-exceeded", "status": "hold", "summary": "active subagents exceed policy"})
    if len(high) > int(policy["max_high_reasoning_agents"]):
        findings.append({"id": "high-reasoning-limit-exceeded", "status": "hold", "summary": "high reasoning subagents exceed policy"})
    if estimated > int(policy["max_total_estimated_tokens"]):
        findings.append({"id": "delegation-budget-violation", "status": "hold", "summary": "active estimated tokens exceed policy"})
    for item in active:
        missing = [key for key in ("artifact", "lock_scope", "expected_return_condition", "context_pack_path") if not item.get(key)]
        if missing:
            findings.append({"id": "incomplete-active-delegation", "status": "hold", "agent_id": item.get("agent_id"), "summary": f"missing: {', '.join(missing)}"})
    summary = {
        "agents": len(states),
        "active_agents": len(active),
        "closed_agents": sum(1 for item in states.values() if item.get("status") == "closed"),
        "estimated_tokens": estimated,
        "actual_tokens": sum(actual) if actual else None,
        "budget_violations": sum(1 for item in findings if "budget" in item["id"]),
        "high_reasoning_agents": len(high),
        "low_reasoning_agents": sum(1 for item in active if item.get("reasoning_tier") == "low"),
        "unnecessary_spawns": sum(1 for item in findings if item["id"] == "unnecessary-spawn"),
        "findings": len(findings),
    }
    return {"schema_version": AUDIT_SCHEMA_VERSION, "status": "hold" if findings else "pass", "project_path": str(root), "policy": policy, "summary": summary, "agents": list(states.values()), "findings": findings}


def close_completed(project_root: Path | str) -> dict[str, Any]:
    root = Path(project_root).resolve()
    closed: list[str] = []
    
    lock_mgr = LaneLockManager(root)
    ledger = EventLedger(root)
    
    for agent_id, state in latest_agent_states(read_ledger(root)).items():
        if state.get("status") != "handoff-received" or not state.get("handoff_evidence"):
            continue
        context_path = state.get("context_pack_path")
        if context_path:
            target = root / str(context_path)
            if target.is_file():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
                
        # V5.4.3: Release lock and log event
        lane_id = f"{_slug(state.get('task', 'delegation'))}-lane"
        lock_scope = state.get("lock_scope")
        if lock_scope:
            files_to_unlock = [f.strip() for f in lock_scope.split(",") if f.strip()]
            for f in files_to_unlock:
                lock_mgr.release(lane_id, f)
                ledger.log_event("file_unlocked", lane_id, {"file": f, "agent_id": agent_id})
                
        ledger.log_event("task_completed", lane_id, {"agent_id": agent_id})
        append_ledger_event(root, {**state, "event": "closed", "status": "closed", "close_reason": "handoff evidence received"})
        closed.append(agent_id)
        
    lock_mgr.close()
    ledger.close()
    return {"schema_version": AUDIT_SCHEMA_VERSION, "status": "pass", "closed_agents": closed, "closed_count": len(closed)}


def record_usage(project_root: Path | str, *, agent_id: str, input_tokens: int, output_tokens: int) -> dict[str, Any]:
    current = latest_agent_states(read_ledger(project_root)).get(agent_id, {"agent_id": agent_id, "status": "running"})
    actual = input_tokens + output_tokens
    append_ledger_event(project_root, {**current, "event": "usage-recorded", "actual_tokens": actual, "input_tokens": input_tokens, "output_tokens": output_tokens})
    return {"schema_version": LEDGER_SCHEMA_VERSION, "status": "pass", "agent_id": agent_id, "actual_tokens": actual}


def write_plan(project_root: Path | str, report: Mapping[str, Any]) -> Path:
    root = Path(project_root).resolve()
    path = root / PLAN_DIR / f"{_slug(str(report.get('task', 'delegation')))}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def render_delegation_report(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    return "\n".join([
        "Relay-kit delegation control",
        f"- status: {report.get('status')}",
        f"- decision: {report.get('decision', 'audit')}",
        f"- reasoning: {report.get('reasoning_tier', 'n/a')}",
        f"- active agents: {summary.get('active_agents', summary.get('planned_agents', 0))}",
        f"- estimated tokens: {summary.get('estimated_tokens', 0)}",
        f"- budget violations: {summary.get('budget_violations', 0)}",
    ])


def _adapter_enforcement(adapter: str) -> str:
    return "advisory" if adapter in {"codex", "claude", "agent", "antigravity", "all"} else "unsupported"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")[:48] or "delegation"
