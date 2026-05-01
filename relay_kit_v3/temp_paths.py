from __future__ import annotations

import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def stable_temp_dir(root: Path | str, prefix: str) -> Path:
    base = Path(root) / ".tmp" / "relay-kit-temp"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{prefix}-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    return path


@contextmanager
def temp_dir(root: Path | str, prefix: str) -> Iterator[Path]:
    path = stable_temp_dir(root, prefix)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
