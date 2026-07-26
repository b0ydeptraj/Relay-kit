"""Frontmatter contract for every shipped SKILL.md.

Claude Code parses SKILL.md frontmatter as YAML. A description that is an
unquoted scalar containing a colon+space (``Use when X: Y``) makes the parse
fail, and the loader silently falls back to the body's first heading -- the
skill stays installed but its routing trigger is dead.

Nothing else in the repo parses this block with a real YAML parser:
``scripts/validate_runtime.py`` matches the description with a regex and
``scripts/skill_gauntlet.py`` splits on the first colon, so both accept files
that Claude Code cannot load. These tests are the gate that fails closed.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SURFACES = (".claude/skills", ".agent/skills", ".codex/skills")

# Keys Claude Code recognises in SKILL.md frontmatter. Anything else is either
# a typo or a convention that will be silently dropped at load time.
ALLOWED_KEYS = {"name", "description", "allowed-tools", "license", "metadata"}

FRONTMATTER = re.compile(r"^---\r?\n(.*?)^---\r?\n", re.S | re.M)


def skill_files() -> list[Path]:
    found: list[Path] = []
    for surface in SURFACES:
        found.extend(sorted((ROOT / surface).glob("*/SKILL.md")))
    return found


def skill_ids(paths: list[Path]) -> list[str]:
    return [path.relative_to(ROOT).as_posix() for path in paths]


ALL_SKILLS = skill_files()


def test_skill_surfaces_are_populated() -> None:
    assert ALL_SKILLS, "no SKILL.md found -- the glob or the surfaces moved"


@pytest.mark.parametrize("path", ALL_SKILLS, ids=skill_ids(ALL_SKILLS))
def test_frontmatter_is_loadable(path: Path) -> None:
    raw = path.read_bytes()

    # A BOM sits before the opening fence and can defeat a strict loader.
    assert not raw.startswith(b"\xef\xbb\xbf"), f"{path} starts with a UTF-8 BOM"

    text = raw.decode("utf-8")
    match = FRONTMATTER.match(text)
    assert match is not None, f"{path} has no leading --- frontmatter fence"

    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:  # pragma: no cover - message is the payload
        pytest.fail(
            f"{path} frontmatter is not valid YAML: {error}\n"
            "A description containing ': ' must be quoted."
        )

    assert isinstance(data, dict), f"{path} frontmatter must parse to a mapping"

    unknown = sorted(set(data) - ALLOWED_KEYS)
    assert not unknown, f"{path} has frontmatter keys Claude Code ignores: {unknown}"

    assert data.get("name") == path.parent.name, (
        f"{path} declares name={data.get('name')!r} but lives in {path.parent.name!r}"
    )

    description = data.get("description")
    assert isinstance(description, str) and description.strip(), (
        f"{path} has no usable description -- routing would be dead"
    )

    # The fallback the broken files produced was the body's first heading.
    assert description.strip() != "Mission", (
        f"{path} description is the body heading, so the frontmatter never parsed"
    )


@pytest.mark.parametrize("path", ALL_SKILLS, ids=skill_ids(ALL_SKILLS))
def test_allowed_tools_is_a_list_of_strings(path: Path) -> None:
    data = yaml.safe_load(FRONTMATTER.match(path.read_text(encoding="utf-8")).group(1))
    tools = data.get("allowed-tools")
    if tools is None:
        return
    assert isinstance(tools, list), f"{path} allowed-tools must be a list"
    assert all(isinstance(tool, str) and tool for tool in tools), (
        f"{path} allowed-tools must contain non-empty strings"
    )
