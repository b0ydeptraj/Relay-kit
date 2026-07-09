import json
from pathlib import Path
from typing import Any, List, Dict

from relay_kit_v3.delegation_control import build_delegation_plan, load_policy

def simulate_lanes(project_path: str | Path, tasks_file: str | Path, num_agents: int) -> dict[str, Any]:
    """
    V5.4.0 Lane Simulation Mode.
    Simulate lane locks and token budget before actually spawning agents.
    Detects lock conflicts and high reasoning count warnings.
    """
    root = Path(project_path).resolve()
    tasks_path = root / tasks_file
    
    try:
        tasks: List[Dict[str, Any]] = json.loads(tasks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {"status": "error", "message": f"Could not read tasks file: {e}"}
        
    policy = load_policy(root)
    
    total_estimated_tokens = 0
    high_reasoning_count = 0
    conflicts: List[Dict[str, Any]] = []
    locked_files: Dict[str, str] = {} # mapping file_path to task name
    
    # Simulate delegation for each task up to num_agents
    tasks_to_simulate = tasks[:num_agents]
    
    for task_data in tasks_to_simulate:
        task_name = task_data.get("task", "Unknown Task")
        lock_scope = task_data.get("lock_scope", "")
        
        # Check lock conflicts in simulation memory
        if lock_scope:
            files_to_lock = [f.strip() for f in lock_scope.split(",") if f.strip()]
            task_has_conflict = False
            
            for f in files_to_lock:
                if f in locked_files:
                    conflicts.append({
                        "file": f,
                        "requested_by": task_name,
                        "locked_by": locked_files[f]
                    })
                    task_has_conflict = True
                    break
                    
            if not task_has_conflict:
                for f in files_to_lock:
                    locked_files[f] = task_name
                    
        # Estimate tokens and reasoning
        plan = build_delegation_plan(
            project_root=root,
            task=task_name,
            complexity=task_data.get("complexity", "L1"),
            lock_scope=lock_scope,
            artifact=task_data.get("artifact"),
            expected_return_condition=task_data.get("expected_return_condition"),
            verification_command=task_data.get("verification_command"),
            independent=True,
            apply=False # IMPORTANT: Do not actually apply or acquire real locks
        )
        
        total_estimated_tokens += plan.get("summary", {}).get("estimated_tokens", 0)
        if plan.get("reasoning_tier") == "high":
            high_reasoning_count += 1
            
    warnings = []
    if high_reasoning_count > int(policy.get("max_high_reasoning_agents", 1)):
        warnings.append(f"High reasoning agents ({high_reasoning_count}) exceeds policy limit ({policy.get('max_high_reasoning_agents', 1)})")
        
    if total_estimated_tokens > int(policy.get("max_total_estimated_tokens", 20000)):
        warnings.append(f"Total estimated tokens ({total_estimated_tokens}) exceeds policy budget ({policy.get('max_total_estimated_tokens', 20000)})")
        
    status = "pass"
    if conflicts or warnings:
        status = "hold"
        
    return {
        "status": status,
        "simulated_tasks": len(tasks_to_simulate),
        "total_estimated_tokens": total_estimated_tokens,
        "high_reasoning_count": high_reasoning_count,
        "lock_conflicts": conflicts,
        "warnings": warnings,
        "policy": policy
    }
