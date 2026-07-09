import argparse
import json
from relay_kit_v3.lane_audit import build_lane_audit, render_lane_audit, write_lane_audit

def run_lane_audit(args: argparse.Namespace) -> int:
    report = build_lane_audit(args.project_path)
    if args.output_file:
        write_lane_audit(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_lane_audit(report))
        if args.output_file:
            print(f"Wrote {args.output_file}")
    if args.strict and report.get("status") != "pass":
        return 1
    return 0

def run_lane_simulate(args: argparse.Namespace) -> int:
    from relay_kit_v3.lane_simulator import simulate_lanes
    report = simulate_lanes(args.project_path, args.tasks, args.agents)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("--- Lane Simulation Report ---")
        print(f"Status: {report['status']}")
        print(f"Simulated tasks: {report.get('simulated_tasks')}")
        print(f"Total tokens: {report.get('total_estimated_tokens')}")
        print(f"High reasoning agents: {report.get('high_reasoning_count')}")
        if report.get("lock_conflicts"):
            print("Lock Conflicts:")
            for conflict in report["lock_conflicts"]:
                print(f"  - {conflict['file']} (requested by {conflict['requested_by']}, locked by {conflict['locked_by']})")
        if report.get("warnings"):
            print("Warnings:")
            for w in report["warnings"]:
                print(f"  - {w}")
    if report.get("status") != "pass":
        return 1
    return 0

def run_lane_run(args: argparse.Namespace) -> int:
    from relay_kit_v3.lane_simulator import simulate_lanes
    import subprocess
    import sys
    from pathlib import Path
    
    # First simulate to ensure no budget/lock conflicts
    sim_report = simulate_lanes(args.project_path, args.tasks, args.agents)
    if sim_report.get("status") != "pass":
        print("Simulation failed. Cannot run multi-lane safely.", file=sys.stderr)
        if args.json:
            print(json.dumps(sim_report, ensure_ascii=False))
        else:
            print(sim_report, file=sys.stderr)
        return 1
        
    print(f"Spawning {sim_report.get('simulated_tasks')} agents for multi-lane execution...")
    # Actually spawn the agents!
    # For now, we will just spawn standard python processes running delegation plan for each task.
    # In V5.4.4, we fork sub-processes.
    root = Path(args.project_path).resolve()
    tasks_path = root / args.tasks
    try:
        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to read tasks: {e}", file=sys.stderr)
        return 1
        
    processes = []
    for i, task_data in enumerate(tasks[:args.agents]):
        # We invoke the relay-kit cli delegation plan 
        cmd = [
            sys.executable, "relay_kit_public_cli.py", "delegation", "plan", str(root),
            "--task", task_data.get("task", ""),
            "--apply"
        ]
        if task_data.get("complexity"):
            cmd.extend(["--complexity", task_data["complexity"]])
        if task_data.get("artifact"):
            cmd.extend(["--artifact", task_data["artifact"]])
        if task_data.get("lock_scope"):
            cmd.extend(["--lock-scope", task_data["lock_scope"]])
        if task_data.get("expected_return_condition"):
            cmd.extend(["--expected-return-condition", task_data["expected_return_condition"]])
        if task_data.get("verification_command"):
            cmd.extend(["--verification-command", task_data["verification_command"]])
            
        print(f"Spawning Lane {i+1}: {task_data.get('task')}")
        p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
        processes.append((i+1, p))
        
    failed = False
    for i, p in processes:
        p.wait()
        if p.returncode != 0:
            print(f"Lane {i} failed with exit code {p.returncode}", file=sys.stderr)
            failed = True
            
    if failed:
        return 1
    print("All lanes completed successfully.")
    return 0

def run_lane(args: argparse.Namespace) -> int:
    action = getattr(args, "action_lane", None)
    if action == "audit":
        return run_lane_audit(args)
    elif action == "simulate":
        return run_lane_simulate(args)
    elif action == "run":
        return run_lane_run(args)
    else:
        # fallback for old signature
        return run_lane_audit(args)
