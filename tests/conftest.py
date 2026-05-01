from __future__ import annotations

import re
import shutil
import uuid
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
TMP_ROOT = ROOT / ".tmp" / "pytest-fixtures"


def _safe_test_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", name).strip("-")[:80] or "test"


@pytest.fixture
def tmp_path(request: pytest.FixtureRequest) -> Path:
    """Stable tmp_path replacement for Windows environments with locked pytest temp roots."""
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TMP_ROOT / f"{_safe_test_name(request.node.name)}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
