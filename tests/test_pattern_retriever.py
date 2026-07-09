import sys
import tempfile
import traceback
from relay_kit_v3.field_journal import FieldJournal
from relay_kit_v3.pattern_retriever import PatternRetriever

def test_pattern_retriever():
    with tempfile.TemporaryDirectory() as temp_dir:
        journal = FieldJournal(temp_dir)
        
        # 1. Low confidence entry (should be ignored)
        journal.capture({
            "evidence_ref": "hash1",
            "error_signature": "NullPointerException in AuthModule"
        })
        
        # 2. Promoted entry (should be retrieved)
        c2 = journal.capture({
            "evidence_ref": "hash2",
            "error_signature": "ConnectionTimeout in NetworkModule"
        }, promotion_recommended=True)
        journal.promote_entry(c2["id"])
        
        retriever = PatternRetriever(temp_dir)
        
        # Search for AuthModule - should be empty because it's low confidence
        res1 = retriever.retrieve_similar_patterns("NullPointerException in AuthModule")
        assert len(res1) == 0
        
        # Search for NetworkModule - should find the promoted one
        res2 = retriever.retrieve_similar_patterns("Connection timeout detected in NetworkModule")
        assert len(res2) == 1
        assert res2[0]["error_signature"] == "ConnectionTimeout in NetworkModule"

if __name__ == '__main__':
    try:
        test_pattern_retriever()
        print("RESULT: ALL PATTERN RETRIEVER TESTS PASSED")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
