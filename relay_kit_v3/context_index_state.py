"""
relay_kit_v3/context_index_state.py

V5.2.7 — Index Freshness & Invalidation
Stores file hash, mtime, model name, and index version to avoid redundant re-indexing
of unmodified files.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class ContextIndexState:
    """Manages the state and freshness of the semantic and lexical indices."""
    
    VERSION = "v1"

    def __init__(self, project_root: Path | str, model_name: str | None = None) -> None:
        self.project_root = Path(project_root).resolve()
        self.model_name = model_name or "tier0-bm25-graph"
        self.state_file = self.project_root / ".agent" / "index_state.json"
        self.state: dict[str, Any] = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Invalidate if version or model changed
                    if data.get("version") != self.VERSION or data.get("model_name") != self.model_name:
                        return self._empty_state()
                    return data
            except json.JSONDecodeError:
                pass
        return self._empty_state()

    def _empty_state(self) -> dict[str, Any]:
        return {
            "version": self.VERSION,
            "model_name": self.model_name,
            "files": {}
        }

    def save(self) -> None:
        """Persist state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def is_fresh(self, file_path: Path) -> bool:
        """Check if a file's index is fresh based on mtime and hash."""
        if not file_path.exists():
            return False
            
        rel_path = str(file_path.relative_to(self.project_root))
        file_info = self.state["files"].get(rel_path)
        if not file_info:
            return False

        # Fast check: mtime
        current_mtime = file_path.stat().st_mtime
        if current_mtime == file_info.get("mtime"):
            return True
            
        # Slower check: hash (in case mtime changed but content didn't)
        current_hash = self._compute_hash(file_path)
        if current_hash == file_info.get("hash"):
            # Update mtime so next time is fast
            self._update_file_state(file_path, current_mtime, current_hash)
            return True

        return False

    def get_stale_files(self, files: list[Path]) -> list[Path]:
        """Given a list of files, return only those that are stale."""
        stale = []
        for f in files:
            if not self.is_fresh(f):
                stale.append(f)
        return stale

    def mark_fresh(self, file_path: Path) -> None:
        """Update the state for a file, marking it as fresh."""
        if not file_path.exists():
            return
        mtime = file_path.stat().st_mtime
        file_hash = self._compute_hash(file_path)
        self._update_file_state(file_path, mtime, file_hash)

    def _update_file_state(self, file_path: Path, mtime: float, file_hash: str) -> None:
        rel_path = str(file_path.relative_to(self.project_root))
        self.state["files"][rel_path] = {
            "mtime": mtime,
            "hash": file_hash
        }

    @staticmethod
    def _compute_hash(file_path: Path) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
