import sys
import tempfile
import traceback
from pathlib import Path

from relay_kit_v3.field_journal import FieldJournal
from relay_kit_v3.evidence_quality import EvidenceGateError

def test_journal_capture_success():
    with tempfile.TemporaryDirectory() as temp_dir:
        journal = FieldJournal(temp_dir)
        
        entry = {
            "evidence_ref": "hash_123",
            "content": "Fixed a bug containing my token api_key=secret_token_abc"
        }
        
        captured = journal.capture(entry)
        
        assert captured["status"] == "candidate"
        assert captured["confidence"] == "low"
        assert captured["promotion_recommended"] is False
        assert captured["evidence_ref"] == "hash_123"
        assert "api_key=[REDACTED_API_KEY]" in captured["content"]
        assert "secret_token_abc" not in captured["content"]
        
        entries = journal.list_entries()
        assert len(entries) == 1
        assert entries[0]["id"] == captured["id"]

def test_journal_capture_rejects_no_evidence():
    with tempfile.TemporaryDirectory() as temp_dir:
        journal = FieldJournal(temp_dir)
        
        entry = {
            "content": "Fixed a bug but no evidence"
        }
        
        try:
            journal.capture(entry)
            assert False, "Should have raised EvidenceGateError"
        except EvidenceGateError:
            pass
            
        entries = journal.list_entries()
        assert len(entries) == 0

def test_journal_promotion():
    with tempfile.TemporaryDirectory() as temp_dir:
        journal = FieldJournal(temp_dir)
        entry = {"evidence_ref": "hash_123", "content": "test"}
        captured = journal.capture(entry, promotion_recommended=True)
        
        assert captured["status"] == "candidate" # still candidate initially
        assert captured["promotion_recommended"] is True
        
        entry_id = captured["id"]
        
        # Promote it
        success = journal.promote_entry(entry_id)
        assert success is True
        
        # Verify
        promoted_entry = journal.get_entry(entry_id)
        assert promoted_entry["status"] == "promoted"
        assert promoted_entry["confidence"] == "high"

if __name__ == '__main__':
    try:
        test_journal_capture_success()
        test_journal_capture_rejects_no_evidence()
        test_journal_promotion()
        print("RESULT: ALL FIELD JOURNAL TESTS PASSED")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
