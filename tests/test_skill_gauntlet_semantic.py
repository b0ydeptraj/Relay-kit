from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from relay_kit_v3.registry.skills import ALL_V3_SKILLS, render_skill
from scripts.skill_gauntlet import check_semantic_skill_file


ROOT = Path(__file__).resolve().parents[1]


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_semantic_skill_gauntlet_passes_current_runtime() -> None:
    result = run_command("scripts/skill_gauntlet.py", ".", "--strict", "--semantic")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Semantic checks: on" in result.stdout
    assert "Findings: 0" in result.stdout


def test_semantic_skill_gauntlet_flags_unknown_next_step(tmp_path: Path) -> None:
    spec = ALL_V3_SKILLS["developer"]
    skill_path = tmp_path / ".codex" / "skills" / "developer" / "SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(
        render_skill(spec).replace("- qa-governor", "- missing-skill"),
        encoding="utf-8",
    )

    findings = check_semantic_skill_file(skill_path, tmp_path, spec, set(ALL_V3_SKILLS))

    assert any(finding.check == "unknown-next-step" for finding in findings)
