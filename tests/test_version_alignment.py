"""
Test version alignment between pyproject.toml, .relay-kit/version.json, and CHANGELOG.md.
"""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_version_alignment_across_metadata_files():
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_text, re.M)
    assert version_match is not None, "pyproject.toml missing version key"
    current_version = version_match.group(1)

    version_json_path = REPO_ROOT / ".relay-kit" / "version.json"
    assert version_json_path.exists()
    version_json_data = json.loads(version_json_path.read_text(encoding="utf-8"))
    assert version_json_data["package"]["version"] == current_version, (
        f".relay-kit/version.json version ({version_json_data['package']['version']}) "
        f"does not match pyproject.toml version ({current_version})"
    )

    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {current_version}" in changelog_text or f"## v{current_version}" in changelog_text, (
        f"CHANGELOG.md is missing heading for current version {current_version}"
    )
