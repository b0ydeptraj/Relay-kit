import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from relay_kit_v3.evidence_ledger import append_event, new_run_id, parse_findings_count
from relay_kit_v3.policy_packs import DEFAULT_POLICY_PACK

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def _source_runtime_surfaces_available() -> bool:
    return all((REPO_ROOT / relative).exists() for relative in (".claude/skills", ".agent/skills", ".codex/skills"))

def _doctor_adapter_args(project: Path) -> list[str]:
    adapters = []
    for adapter, relative in (
        ("claude", ".claude/skills"),
        ("agent", ".agent/skills"),
        ("codex", ".codex/skills"),
    ):
        if (project / relative).exists():
            adapters.append(adapter)
    if not adapters or len(adapters) == 3:
        return []
    return ["--adapters", *adapters]

def _doctor_commands(project_path: str, skip_tests: bool, policy_pack: str = DEFAULT_POLICY_PACK) -> list[tuple[str, list[str]]]:
    project = Path(project_path)
    adapter_args = _doctor_adapter_args(project)
    commands = []

    if _source_runtime_surfaces_available():
        commands.append(
            ("validate runtime", [sys.executable, str(REPO_ROOT / "scripts" / "validate_runtime.py")])
        )

    commands.extend(
        [
            (
                "runtime doctor template",
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "runtime_doctor.py"),
                    project_path,
                    "--strict",
                    *adapter_args,
                ],
            ),
            (
                "runtime doctor live",
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "runtime_doctor.py"),
                    project_path,
                    "--strict",
                    *adapter_args,
                    "--state-mode",
                    "live",
                ],
            ),
            (
                "naming guard",
                [sys.executable, str(REPO_ROOT / "scripts" / "naming_guard.py"), project_path, "--strict"],
            ),
            (
                "policy guard",
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "policy_guard.py"),
                    project_path,
                    "--strict",
                    "--pack",
                    policy_pack,
                ],
            ),
        ]
    )

    if policy_pack == "enterprise":
        commands.append(
            (
                "trusted manifest",
                [
                    sys.executable,
                    str(REPO_ROOT / "relay_kit_public_cli.py"),
                    "manifest",
                    "verify",
                    project_path,
                    "--trusted",
                ],
            )
        )

    commands.extend(
        [
            (
                "srs guard",
                [sys.executable, str(REPO_ROOT / "scripts" / "srs_guard.py"), project_path, "--strict"],
            ),
            (
                "skill gauntlet",
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "skill_gauntlet.py"),
                    project_path,
                    "--strict",
                    "--semantic",
                ],
            ),
            (
                "workflow eval",
                [sys.executable, str(REPO_ROOT / "scripts" / "eval_workflows.py"), project_path, "--strict"],
            ),
        ]
    )

    if not skip_tests and (REPO_ROOT / "tests").exists():
        commands.append(("pytest", [sys.executable, "-m", "pytest", "tests", "-q"]))

    return commands

def _print_doctor_output(label: str, result: subprocess.CompletedProcess[str], verbose: bool) -> None:
    status = "pass" if result.returncode == 0 else "fail"
    print(f"- {label}: {status}")
    if verbose or result.returncode != 0:
        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip())

def run_doctor(args: argparse.Namespace) -> int:
    project_path = str(Path(args.project_path).resolve())
    run_id = new_run_id()
    if not args.json:
        print("Relay-kit doctor")
        print(f"- project: {project_path}")

    exit_code = 0
    gate_results: list[dict[str, object]] = []
    
    policy = getattr(args, "policy_pack", DEFAULT_POLICY_PACK)
    skip = getattr(args, "skip_tests", False)

    for label, command in _doctor_commands(project_path, skip, policy):
        started = time.perf_counter()
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        status = "pass" if result.returncode == 0 else "fail"
        gate_event = {
            "run_id": run_id,
            "command": "doctor",
            "gate": label,
            "adapter": None,
            "selected_skill": None,
            "status": status,
            "exit_code": result.returncode,
            "findings_count": parse_findings_count(result.stdout, result.stderr),
            "evidence_files": [],
            "elapsed_ms": elapsed_ms,
        }
        append_event(project_path, gate_event)
        gate_results.append(gate_event)
        if not args.json:
            _print_doctor_output(label, result, getattr(args, "verbose", False))
        if result.returncode != 0:
            exit_code = 1

    if args.json:
        print(json.dumps(gate_results, indent=2))
        
    return exit_code
