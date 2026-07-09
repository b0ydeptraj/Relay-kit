import sys
import tempfile
import traceback
import json
from pathlib import Path

from relay_kit_v3.lane_simulator import simulate_lanes

def test_lane_simulation():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        
        # Configure a simple policy
        policy_path = root / ".relay-kit/state/delegation-policy.json"
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        policy_path.write_text(json.dumps({
            "max_concurrent_subagents": 2,
            "max_total_estimated_tokens": 20000,
            "max_tokens_per_subagent": 6000,
            "max_high_reasoning_agents": 1
        }))
        
        tasks_file = root / "tasks.json"
        tasks_file.write_text(json.dumps([
            {
                "task": "Task A",
                "complexity": "L2",
                "lock_scope": "src/a.py, src/common.py",
                "artifact": "src/a.py",
                "expected_return_condition": "pass",
                "verification_command": "test"
            },
            {
                "task": "Task B",
                "complexity": "L2",
                "lock_scope": "src/b.py",
                "artifact": "src/b.py",
                "expected_return_condition": "pass",
                "verification_command": "test"
            },
            {
                "task": "Task C",
                "complexity": "L3", # High reasoning
                "lock_scope": "src/common.py, src/c.py",
                "artifact": "src/c.py",
                "expected_return_condition": "pass",
                "verification_command": "test"
            },
            {
                "task": "Task D",
                "complexity": "L3", # High reasoning
                "lock_scope": "src/d.py",
                "artifact": "src/d.py",
                "expected_return_condition": "pass",
                "verification_command": "test"
            }
        ]))
        
        # 1. Simulate Task A and Task B (No conflict)
        result1 = simulate_lanes(root, "tasks.json", num_agents=2)
        assert result1["status"] == "pass"
        assert len(result1["lock_conflicts"]) == 0
        assert len(result1["warnings"]) == 0
        assert result1["simulated_tasks"] == 2
        
        # 2. Simulate Task A, Task B, and Task C (Conflict on src/common.py and High Reasoning warning)
        result2 = simulate_lanes(root, "tasks.json", num_agents=3)
        assert result2["status"] == "hold"
        assert len(result2["lock_conflicts"]) == 1
        assert result2["lock_conflicts"][0]["file"] == "src/common.py"
        assert result2["lock_conflicts"][0]["requested_by"] == "Task C"
        
        # 3. Simulate Task C and Task D (High reasoning limit exceeded)
        # We need a new tasks file to simulate just C and D easily, 
        # but wait, simulate_lanes reads from top to bottom.
        # Let's just create a second tasks file.
        tasks2_file = root / "tasks2.json"
        tasks2_file.write_text(json.dumps([
            {
                "task": "Root-cause incident C",
                "complexity": "L3",
                "lock_scope": "src/c.py",
                "artifact": "src/c.py",
                "expected_return_condition": "pass",
                "verification_command": "test"
            },
            {
                "task": "Security incident D",
                "complexity": "L3",
                "lock_scope": "src/d.py",
                "artifact": "src/d.py",
                "expected_return_condition": "pass",
                "verification_command": "test"
            }
        ]))
        result3 = simulate_lanes(root, "tasks2.json", num_agents=2)
        assert result3["status"] == "hold"
        assert len(result3["lock_conflicts"]) == 0
        assert len(result3["warnings"]) >= 1
        assert "High reasoning agents (2) exceeds policy limit" in result3["warnings"][0] or (len(result3["warnings"]) > 1 and "High reasoning" in result3["warnings"][1])

if __name__ == '__main__':
    try:
        test_lane_simulation()
        print("RESULT: ALL LANE SIMULATION TESTS PASSED")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
