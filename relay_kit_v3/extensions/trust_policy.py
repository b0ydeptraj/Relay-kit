import os
import yaml
from enum import Enum
from relay_kit_v3.extensions.pack_format import ExtensionPack, ExtensionPermissions

class TrustLevel(Enum):
    VERIFIED = "verified"
    REVIEWED = "reviewed"
    UNTRUSTED = "untrusted"

class TrustDecision(Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_REVIEW = "REQUIRE_REVIEW"

class TrustPolicyEngine:
    def __init__(self, project_path="."):
        self.project_path = project_path
        self.config_path = os.path.join(project_path, ".relay-kit", "trust-policy.yaml")
        self.config = {
            "default_trust_level": "untrusted",
            "allow_reviewed_without_signature": True,
            "blocked_authors": [],
            "trusted_authors": [],
            "require_signature_for_shell": True,
            "require_signature_for_network": True
        }
        self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        self.config.update(data)
            except Exception:
                pass # Fallback to defaults

    def get_pack_trust_level(self, pack: ExtensionPack, user_trust_flag: str = "") -> TrustLevel:
        if pack.has_signature():
            # In a real implementation we would actually verify the signature using GPG.
            # Here we just assume verified if the file exists.
            return TrustLevel.VERIFIED
            
        if user_trust_flag == "reviewed" and self.config["allow_reviewed_without_signature"]:
            return TrustLevel.REVIEWED
            
        # Check author based trust rules
        if pack.author in self.config["blocked_authors"]:
            return TrustLevel.UNTRUSTED
        
        if pack.author in self.config["trusted_authors"]:
            return TrustLevel.VERIFIED if self.config.get("trust_authors_as_verified", False) else TrustLevel.REVIEWED
            
        return TrustLevel.UNTRUSTED

    def evaluate_trust(self, pack: ExtensionPack, user_trust_flag: str = "") -> TrustDecision:
        level = self.get_pack_trust_level(pack, user_trust_flag)
        
        if level == TrustLevel.VERIFIED:
            return TrustDecision.ALLOW
            
        if level == TrustLevel.REVIEWED:
            return TrustDecision.ALLOW
            
        return TrustDecision.BLOCK

    def check_trust_for_permissions(self, trust_level: TrustLevel, permissions: ExtensionPermissions) -> bool:
        if permissions.shell_required and self.config["require_signature_for_shell"]:
            if trust_level != TrustLevel.VERIFIED:
                return False
                
        if permissions.network_required and self.config["require_signature_for_network"]:
            if trust_level != TrustLevel.VERIFIED:
                return False
                
        return True
