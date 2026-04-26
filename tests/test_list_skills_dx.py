from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_list_skills_hides_legacy_kits_by_default() -> None:
    result = run_command("relay_kit_public_cli.py", "--list-skills")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Built-in v3 bundles:" in result.stdout
    assert "Legacy kits:" not in result.stdout


def test_list_skills_can_show_legacy_kits_explicitly() -> None:
    result = run_command("relay_kit_public_cli.py", "--list-skills", "--show-legacy")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Built-in v3 bundles:" in result.stdout
    assert "Legacy kits:" in result.stdout
