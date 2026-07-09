import os
import re
import yaml
import hashlib
from typing import Dict, List, Any, Optional
from relay_kit_v3.extensions.permissions import ExtensionPermissions

class PackValidationError(Exception):
    pass

class ExtensionPack:
    def __init__(self, pack_dir: str):
        self.pack_dir = pack_dir
        self.pack_yaml_path = os.path.join(pack_dir, 'pack.yaml')
        self.skills_dir = os.path.join(pack_dir, 'skills')
        self.trust_sig_path = os.path.join(pack_dir, 'trust.sig')
        
        self.name = ""
        self.version = ""
        self.author = ""
        self.expected_hash = ""
        self.skills: List[str] = []
        self.trust_claim = ""
        self.permissions: Optional[ExtensionPermissions] = None
        self.raw_data = {}
        
        self._load_and_validate()

    def _load_and_validate(self):
        if not os.path.exists(self.pack_yaml_path):
            raise PackValidationError("pack.yaml not found")
            
        try:
            with open(self.pack_yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise PackValidationError(f"Invalid YAML: {e}")
            
        if not isinstance(data, dict):
            raise PackValidationError("pack.yaml must be a dictionary")
            
        self.raw_data = data
        
        # Name
        self.name = data.get('name')
        if not self.name or not isinstance(self.name, str) or not re.match(r"^[a-z0-9-]+$", self.name):
            raise PackValidationError("Name must be non-empty and match [a-z0-9-]+")
            
        # Version
        self.version = data.get('version')
        if not self.version or not isinstance(self.version, str):
            raise PackValidationError("Version is required and must be a string")
            
        # Author
        self.author = data.get('author', 'unknown')
        
        # Hash
        self.expected_hash = data.get('hash')
        if not self.expected_hash or not isinstance(self.expected_hash, str) or not self.expected_hash.startswith("sha256:"):
            raise PackValidationError("Hash must start with sha256:")
            
        # Skills
        skills = data.get('skills')
        if not skills or not isinstance(skills, list) or not all(isinstance(s, str) for s in skills):
            raise PackValidationError("Skills must be a non-empty list of strings")
        self.skills = skills
        
        # Trust
        self.trust_claim = data.get('trust', 'untrusted')
        
        # Permissions
        perms = data.get('permissions')
        if perms is None or not isinstance(perms, dict):
            raise PackValidationError("Permissions block is required")
        self.permissions = ExtensionPermissions(perms)

    def verify_hash(self) -> bool:
        if not os.path.exists(self.skills_dir):
            return False
            
        hasher = hashlib.sha256()
        # To make it deterministic, sort directories and files
        for root, dirs, files in os.walk(self.skills_dir):
            dirs.sort()
            files.sort()
            for f in files:
                filepath = os.path.join(root, f)
                with open(filepath, "rb") as file:
                    while chunk := file.read(8192):
                        hasher.update(chunk)
                        
        actual_hash = "sha256:" + hasher.hexdigest()
        return actual_hash == self.expected_hash

    def has_signature(self) -> bool:
        return os.path.exists(self.trust_sig_path)
