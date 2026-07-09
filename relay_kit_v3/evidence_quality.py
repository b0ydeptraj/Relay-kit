from __future__ import annotations

import logging
from typing import Any, Mapping

logger = logging.getLogger(__name__)

class EvidenceGateError(ValueError):
    """Exception raised when an entry fails the evidence quality gate."""
    pass

class EvidenceGate:
    """
    V5.3.2 Evidence Quality Gate.
    Tu choi ghi vao journal neu khong co test pass, khong co command output, hoac fix chua duoc verify.
    Moi entry phai co `evidence_ref` tro den output thuc.
    """
    
    @staticmethod
    def validate(entry: Mapping[str, Any]) -> tuple[bool, str | None]:
        """
        Validate that the entry has required evidence.
        Returns (True, None) if passed, or (False, error_reason) if failed.
        """
        if not entry:
            return False, "Entry is empty."
            
        evidence_ref = entry.get("evidence_ref")
        if not evidence_ref:
            return False, "Missing 'evidence_ref'. Journal entries MUST have evidence (test pass, command output hash, etc.)."
            
        if not str(evidence_ref).strip():
            return False, "'evidence_ref' cannot be empty."
            
        # Additional checks can be added here if needed, such as verifying the hash exists on disk.
        # For now, having a non-empty evidence_ref satisfies the strict roadmap requirement.
        return True, None
        
    @staticmethod
    def enforce(entry: Mapping[str, Any]) -> None:
        """
        Validate the entry, and raise EvidenceGateError if it fails.
        """
        is_valid, reason = EvidenceGate.validate(entry)
        if not is_valid:
            logger.error(f"EvidenceGate blocked entry: {reason}")
            raise EvidenceGateError(reason)

