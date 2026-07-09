from typing import Dict, Any, List

class ExtensionPermissions:
    def __init__(self, data: Dict[str, Any]):
        self.shell_required = bool(data.get('shell', False))
        self.network_required = bool(data.get('network', False))
        self.write_paths = list(data.get('write_paths', []))
        self.allowed_adapters = list(data.get('adapters', []))
        self.allowed_commands = list(data.get('allowed_commands', []))
        self.requires_human_review = bool(data.get('requires_human_review', True))
        self.writes_generated_surface = bool(data.get('writes_generated_surface', False))

    def to_dict(self):
        return {
            'shell': self.shell_required,
            'network': self.network_required,
            'write_paths': self.write_paths,
            'adapters': self.allowed_adapters,
            'allowed_commands': self.allowed_commands,
            'requires_human_review': self.requires_human_review,
            'writes_generated_surface': self.writes_generated_surface
        }

class PermissionDecision:
    def __init__(self, allowed: bool, blocked_reasons: List[str], warnings: List[str]):
        self.allowed = allowed
        self.blocked_reasons = blocked_reasons
        self.warnings = warnings

def validate_permissions(perms: ExtensionPermissions, trust_level: str) -> PermissionDecision:
    blocked_reasons = []
    warnings = []
    
    # "verified" is the highest level
    if perms.shell_required and trust_level != "verified":
        blocked_reasons.append("Shell access requires 'verified' trust level")
        
    if perms.network_required and trust_level != "verified":
        blocked_reasons.append("Network access requires 'verified' trust level")
        
    for path in perms.write_paths:
        if not path.startswith(".relay-kit/"):
            warnings.append(f"Write path {path} is outside .relay-kit/ sandbox")
            
    if perms.writes_generated_surface:
        warnings.append("Extension writes to generated surface (requires gauntlet pass + review)")
        
    return PermissionDecision(
        allowed=len(blocked_reasons) == 0,
        blocked_reasons=blocked_reasons,
        warnings=warnings
    )
