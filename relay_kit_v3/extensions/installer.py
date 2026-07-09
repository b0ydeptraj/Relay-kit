import os
import shutil
import tempfile
from relay_kit_v3.extensions.pack_format import ExtensionPack, PackValidationError
from relay_kit_v3.extensions.trust_policy import TrustPolicyEngine, TrustDecision
from relay_kit_v3.extensions.permissions import validate_permissions
from relay_kit_v3.extensions.quarantine import QuarantineManager, LifecycleState
from relay_kit_v3.extensions.gauntlet_gate import run_skill_gauntlet

class InstallResult:
    def __init__(self, exit_code: int, message: str):
        self.exit_code = exit_code
        self.message = message

class ExtensionInstaller:
    def __init__(self, project_path="."):
        self.project_path = project_path
        self.trust_engine = TrustPolicyEngine(project_path)
        self.quarantine_mgr = QuarantineManager(project_path)

    def install(self, source_path: str, user_trust_flag: str = "") -> InstallResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            if not os.path.isdir(source_path):
                return InstallResult(1, f"Source path {source_path} is not a directory")
            
            staging_dir = os.path.join(tmpdir, "staging")
            shutil.copytree(source_path, staging_dir)
            
            try:
                pack = ExtensionPack(staging_dir)
            except PackValidationError as e:
                return InstallResult(1, f"Pack validation failed: {e}")
                
            if not pack.verify_hash():
                return InstallResult(1, f"Hash mismatch! Skills directory does not match expected hash {pack.expected_hash}")
                
            trust_decision = self.trust_engine.evaluate_trust(pack, user_trust_flag)
            if trust_decision == TrustDecision.BLOCK:
                return InstallResult(2, f"Trust rejected! Pack is untrusted and cannot be installed.")
                
            trust_level = self.trust_engine.get_pack_trust_level(pack, user_trust_flag).value
            
            perm_decision = validate_permissions(pack.permissions, trust_level)
            if not perm_decision.allowed:
                reasons = "\n- ".join(perm_decision.blocked_reasons)
                return InstallResult(3, f"Permission denied! The pack requested blocked permissions:\n- {reasons}")
                
            gauntlet_result = run_skill_gauntlet(pack, self.project_path)
            
            self.quarantine_mgr.quarantine_pack(staging_dir, pack, trust_level, gauntlet_result.passed)
            
            if not gauntlet_result.passed:
                err_msg = "Skill Gauntlet failed! The pack has been quarantined but BLOCKED from activation.\nFailed checks:\n"
                for check in gauntlet_result.checks:
                    if not check.passed:
                        err_msg += f"- {check.name}: {check.message}\n"
                return InstallResult(4, err_msg)
                
            if self.quarantine_mgr.promote_to_active(pack.name):
                return InstallResult(0, f"Successfully installed and activated pack '{pack.name}'")
            else:
                return InstallResult(4, "Failed to promote pack to active state")
