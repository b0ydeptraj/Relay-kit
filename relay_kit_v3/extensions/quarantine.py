import os
import json
import shutil
from enum import Enum
from datetime import datetime
from typing import List
from relay_kit_v3.extensions.pack_format import ExtensionPack

class LifecycleState(Enum):
    QUARANTINED = "quarantined"
    BLOCKED = "blocked"
    ACTIVE = "active"
    NOT_FOUND = "not_found"

class QuarantineEntry:
    def __init__(self, pack_name: str, state: LifecycleState, meta: dict):
        self.pack_name = pack_name
        self.state = state
        self.meta = meta

class QuarantineManager:
    def __init__(self, project_path="."):
        self.project_path = project_path
        self.extensions_dir = os.path.join(project_path, ".relay-kit", "extensions")
        self.quarantine_dir = os.path.join(self.extensions_dir, "quarantine")
        self.active_dir = os.path.join(self.extensions_dir, "active")
        self.installed_json = os.path.join(self.extensions_dir, "installed.json")
        
        os.makedirs(self.quarantine_dir, exist_ok=True)
        os.makedirs(self.active_dir, exist_ok=True)

    def quarantine_pack(self, source_pack_dir: str, pack: ExtensionPack, trust_level: str, gauntlet_passed: bool) -> QuarantineEntry:
        target_dir = os.path.join(self.quarantine_dir, pack.name)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
            
        shutil.copytree(source_pack_dir, target_dir)
        
        state = LifecycleState.QUARANTINED if gauntlet_passed else LifecycleState.BLOCKED
        meta = {
            "install_date": datetime.now().isoformat(),
            "trust_level": trust_level,
            "gauntlet_passed": gauntlet_passed,
            "version": pack.version,
            "skills_count": len(pack.skills)
        }
        
        with open(os.path.join(target_dir, "_quarantine_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
            
        # Update installed.json
        self._update_installed_registry(pack.name, state.value, meta)
        
        return QuarantineEntry(pack.name, state, meta)

    def promote_to_active(self, pack_name: str) -> bool:
        q_dir = os.path.join(self.quarantine_dir, pack_name)
        a_dir = os.path.join(self.active_dir, pack_name)
        
        if not os.path.exists(q_dir):
            return False
            
        meta_path = os.path.join(q_dir, "_quarantine_meta.json")
        if not os.path.exists(meta_path):
            return False
            
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            
        if not meta.get("gauntlet_passed", False):
            return False
            
        if os.path.exists(a_dir):
            shutil.rmtree(a_dir)
            
        # Move to active
        shutil.move(q_dir, a_dir)
        
        # Update installed.json
        meta["activation_date"] = datetime.now().isoformat()
        self._update_installed_registry(pack_name, LifecycleState.ACTIVE.value, meta)
        return True

    def get_lifecycle_state(self, pack_name: str) -> LifecycleState:
        installed = self._load_installed_registry()
        if pack_name in installed:
            return LifecycleState(installed[pack_name].get("state", "not_found"))
        return LifecycleState.NOT_FOUND

    def list_all(self) -> List[QuarantineEntry]:
        installed = self._load_installed_registry()
        entries = []
        for name, data in installed.items():
            state = LifecycleState(data.get("state", "not_found"))
            entries.append(QuarantineEntry(name, state, data.get("meta", {})))
        return entries

    def remove_pack(self, pack_name: str) -> bool:
        q_dir = os.path.join(self.quarantine_dir, pack_name)
        a_dir = os.path.join(self.active_dir, pack_name)
        
        removed = False
        if os.path.exists(q_dir):
            shutil.rmtree(q_dir)
            removed = True
            
        if os.path.exists(a_dir):
            shutil.rmtree(a_dir)
            removed = True
            
        installed = self._load_installed_registry()
        if pack_name in installed:
            del installed[pack_name]
            self._save_installed_registry(installed)
            removed = True
            
        return removed

    def _load_installed_registry(self) -> dict:
        if os.path.exists(self.installed_json):
            try:
                with open(self.installed_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_installed_registry(self, data: dict):
        with open(self.installed_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _update_installed_registry(self, pack_name: str, state: str, meta: dict):
        data = self._load_installed_registry()
        data[pack_name] = {
            "state": state,
            "meta": meta
        }
        self._save_installed_registry(data)
