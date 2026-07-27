"""Every support file a SKILL.md body points at must actually exist.

Several skills instruct the model to open `references/<name>-operator-contract.md`,
`examples/<name>-good-output.md`, `evals/<name>-cases.json`, etc. When those files
are not emitted alongside the skill, the guidance dangles -- the model is told to
read a file that is not there. This gate fails closed on any such reference.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SURFACES = (".claude/skills", ".agent/skills", ".codex/skills")
RESOURCE_REF = re.compile(r"`((?:references|examples|evals|competencies)/[^`]+)`")


def cases() -> list[tuple[Path, str]]:
    found: list[tuple[Path, str]] = []
    for surface in SURFACES:
        for skill_md in sorted((ROOT / surface).glob("*/SKILL.md")):
            body = skill_md.read_text(encoding="utf-8")
            for ref in RESOURCE_REF.findall(body):
                found.append((skill_md, ref))
    return found


CASES = cases()


def test_at_least_some_references_exist() -> None:
    assert CASES, "no support-file references found -- did the glob move?"


@pytest.mark.parametrize(
    "skill_md,ref",
    CASES,
    ids=[f"{p.parent.parent.parent.name}/{p.parent.name}:{r}" for p, r in CASES],
)
def test_skill_reference_resolves(skill_md: Path, ref: str) -> None:
    target = skill_md.parent / ref
    assert target.exists(), f"{skill_md} references missing support file {ref}"
