"""
Test that root scripts/ contain only thin shims to relay_kit_v3/scripts/
and no duplicate implementation code exists across the repository.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT_SCRIPTS = REPO_ROOT / "scripts"
V3_SCRIPTS = REPO_ROOT / "relay_kit_v3" / "scripts"


def test_v3_scripts_package_exists():
    assert V3_SCRIPTS.exists()
    assert (V3_SCRIPTS / "__init__.py").exists()


def test_root_scripts_are_thin_shims():
    for root_py in ROOT_SCRIPTS.glob("*.py"):
        if root_py.name == "__init__.py":
            continue
        v3_py = V3_SCRIPTS / root_py.name
        assert v3_py.exists(), f"Implementation missing in relay_kit_v3/scripts/{root_py.name}"

        content = root_py.read_text(encoding="utf-8")
        assert f"relay_kit_v3.scripts" in content, (
            f"Root script {root_py.name} is not forwarding to relay_kit_v3.scripts"
        )
        assert len(content.splitlines()) < 20, (
            f"Root script {root_py.name} contains implementation code instead of being a thin shim"
        )
