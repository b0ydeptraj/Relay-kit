import os
from typing import List, Optional, Dict, Any
from relay_kit_v3.extensions.quarantine import QuarantineManager, LifecycleState

class ExtensionManager:
    def __init__(self, project_path="."):
        self.project_path = project_path
        self.q_mgr = QuarantineManager(project_path)

    def list_extensions(self, state_filter: Optional[LifecycleState] = None) -> List[Dict[str, Any]]:
        entries = self.q_mgr.list_all()
        result = []
        for e in entries:
            if state_filter and e.state != state_filter:
                continue
            result.append({
                "name": e.pack_name,
                "state": e.state.value,
                "version": e.meta.get("version", "unknown"),
                "skills_count": e.meta.get("skills_count", 0),
                "trust_level": e.meta.get("trust_level", "untrusted")
            })
        return result

    def remove_extension(self, pack_name: str) -> bool:
        return self.q_mgr.remove_pack(pack_name)

    def inspect_extension(self, pack_name: str) -> Optional[Dict[str, Any]]:
        entries = self.q_mgr.list_all()
        for e in entries:
            if e.pack_name == pack_name:
                return {
                    "name": e.pack_name,
                    "state": e.state.value,
                    "meta": e.meta
                }
        return None
