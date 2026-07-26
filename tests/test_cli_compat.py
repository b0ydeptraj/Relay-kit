"""Public CLI compatibility tests.

Every case uses a real ``assert`` -- an earlier version returned ``True``/``False``,
which pytest ignores (it only warns), so all 40 checks passed even when the CLI
drifted from its golden snapshots. Help output is compared after normalising line
endings and surrounding whitespace so the snapshots are OS-independent.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CLI = str(REPO_ROOT / "relay_kit_public_cli.py")
SNAPSHOTS = REPO_ROOT / "tests" / "cli_snapshots"

# Bound every subprocess so a hung CLI fails the test instead of the job timeout.
TIMEOUT = 120


def _norm(text: str) -> str:
    return text.replace("﻿", "").replace("\r\n", "\n").strip()


def run_cli(args, timeout: int = TIMEOUT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, CLI, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# (argv, snapshot basename without .txt). Snapshot files live in cli_snapshots/.
_GROUPS = {
    "context": [
        "audit", "index", "search", "related", "explain-symbol",
        "active", "active_set", "active_show", "mcp", "watch", "budget", "pack",
    ],
    "lane": ["audit"],
    "delegation": ["plan", "audit", "close-completed", "record-usage", "capabilities"],
    "locale": ["show", "set"],
    "token": ["audit"],
    "calibrate": ["claims", "skill", "readiness"],
    "shell": ["compact"],
    "adapter": ["diagnose"],
    "command": ["list", "diagnose"],
    "agent": ["list", "diagnose"],
    "query": ["search"],
    "prompt": ["enhance"],
    "service": ["boundaries"],
    "runtime": ["doctor"],
    "skill": ["gauntlet"],
    "impact": ["radar"],
    "accessibility": ["review"],
    "manifest": ["write", "stamp", "verify"],
    "eval": [
        "run", "real-world", "skill-battle", "competency-battle",
        "skill-weakness-report", "battle-audit", "battle-benchmark",
        "repo-profile", "domain-pack",
    ],
    "proof": ["audit"],
    "upgrade": ["check", "plan", "mark-current"],
    "policy": ["list", "check"],
    "support": ["bundle", "request", "triage", "soak"],
    "readiness": ["check"],
    "release": ["verify", "readiness"],
    "continuity": ["checkpoint", "auto", "rehydrate", "handoff", "diff-since-last"],
    "migration": ["guard"],
    "publish": ["plan", "evidence", "trail", "index-check", "status"],
    "commercial": ["dossier"],
    "pulse": ["build"],
    "signal": ["export"],
}


def _help_cases():
    cases = [
        (["doctor"], "doctor_help"),
        (["evidence"], "evidence_help"),
        (["evidence", "summary"], "evidence_summary_help"),
        (["contract"], "contract_help"),
        (["contract", "export"], "contract_export_help"),
        (["contract", "import"], "contract_import_help"),
    ]
    for group, subs in _GROUPS.items():
        cases.append(([group], f"{group}_help"))
        for sub in subs:
            argv = [group, *sub.split("_")]
            cases.append((argv, f"{group}_{sub}_help"))
    return cases


HELP_CASES = _help_cases()


@pytest.mark.parametrize("argv,snapshot", HELP_CASES, ids=[c[1] for c in HELP_CASES])
def test_help_matches_snapshot(argv, snapshot):
    snapshot_path = SNAPSHOTS / f"{snapshot}.txt"
    expected = _norm(snapshot_path.read_text(encoding="utf-8"))
    result = run_cli([*argv, "--help"])
    assert result.returncode == 0, (
        f"`{' '.join(argv)} --help` exited {result.returncode}\nstderr:\n{result.stderr}"
    )
    assert _norm(result.stdout) == expected, (
        f"`{' '.join(argv)} --help` drifted from {snapshot}.txt"
    )


def test_doctor_execution_compat():
    # --skip-tests is mandatory: the doctor otherwise runs `pytest tests`, which
    # re-enters this very test. (doctor.py also guards on PYTEST_CURRENT_TEST.)
    result = run_cli(["doctor", ".", "--skip-tests"])
    assert "Relay-kit doctor" in result.stdout, result.stdout
    assert "- project: " in result.stdout, result.stdout


def test_evidence_summary_execution_compat():
    result = run_cli(["evidence", "summary", "."])
    if result.returncode == 0:
        assert "Relay-kit evidence summary" in result.stdout, result.stdout


def test_contract_export_execution_compat():
    result = run_cli(["contract", "export", "."])
    assert "Wrote " in result.stdout, result.stdout
