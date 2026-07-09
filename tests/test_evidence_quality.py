import sys
import traceback
from relay_kit_v3.evidence_quality import EvidenceGate, EvidenceGateError

def test_evidence_gate_passes_with_ref():
    entry = {"id": "123", "evidence_ref": "hash_abc", "content": "test"}
    is_valid, reason = EvidenceGate.validate(entry)
    assert is_valid is True
    assert reason is None
    
    # enforce should not raise
    EvidenceGate.enforce(entry)

def test_evidence_gate_fails_missing_ref():
    entry = {"id": "123", "content": "test"}
    is_valid, reason = EvidenceGate.validate(entry)
    assert is_valid is False
    assert "Missing 'evidence_ref'" in reason
    
    try:
        EvidenceGate.enforce(entry)
        assert False, "Should have raised EvidenceGateError"
    except EvidenceGateError:
        pass

def test_evidence_gate_fails_empty_ref():
    entry = {"id": "123", "evidence_ref": "   ", "content": "test"}
    is_valid, reason = EvidenceGate.validate(entry)
    assert is_valid is False
    assert "cannot be empty" in reason
    
    try:
        EvidenceGate.enforce(entry)
        assert False, "Should have raised EvidenceGateError"
    except EvidenceGateError:
        pass

def test_evidence_gate_fails_empty_entry():
    is_valid, reason = EvidenceGate.validate({})
    assert is_valid is False
    assert "Entry is empty" in reason
    
    try:
        EvidenceGate.enforce({})
        assert False, "Should have raised EvidenceGateError"
    except EvidenceGateError:
        pass

if __name__ == '__main__':
    try:
        test_evidence_gate_passes_with_ref()
        test_evidence_gate_fails_missing_ref()
        test_evidence_gate_fails_empty_ref()
        test_evidence_gate_fails_empty_entry()
        print("RESULT: ALL EVIDENCE GATE TESTS PASSED")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
