"""
Test that pyproject.toml license declaration and LICENSE file content are aligned.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_license_file_matches_pyproject_toml():
    pyproject_path = REPO_ROOT / "pyproject.toml"
    license_path = REPO_ROOT / "LICENSE"

    assert pyproject_path.exists()
    assert license_path.exists()

    license_content = license_path.read_text(encoding="utf-8")
    assert "MIT License" in license_content, "LICENSE file must contain standard MIT License text"
    assert "Proprietary" not in license_content, "LICENSE file must not contain Proprietary restrictions"
