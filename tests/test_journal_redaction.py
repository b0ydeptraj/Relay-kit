import sys
import json
import traceback
from pathlib import Path
from relay_kit_v3.journal_redaction import RedactionGate

def test_redaction_fixtures():
    fixtures_path = Path(__file__).parent / "journal_redaction_fixtures.json"
    with open(fixtures_path, "r", encoding="utf-8") as f:
        fixtures = json.load(f)
        
    for fixture in fixtures:
        input_text = fixture["input"]
        expected = fixture["expected"]
        desc = fixture["description"]
        
        redacted = RedactionGate.redact_text(input_text)
        assert redacted == expected, f"Failed on '{desc}': Expected '{expected}', got '{redacted}'"

def test_redaction_entry_recursive():
    entry = {
        "id": "123",
        "evidence_ref": "hash_abc",
        "content": "Contact us at admin@test.com",
        "nested": {
            "key": "api_key=secretXYZ",
            "list": ["Authorization: Bearer myToken"]
        }
    }
    
    redacted = RedactionGate.redact_entry(entry)
    
    assert redacted["content"] == "Contact us at [REDACTED_EMAIL]"
    assert redacted["nested"]["key"] == "api_key=[REDACTED_API_KEY]"
    assert redacted["nested"]["list"][0] == "Authorization: Bearer [REDACTED]"
    assert redacted["evidence_ref"] == "hash_abc"  # Untouched since it doesn't match a secret pattern

if __name__ == '__main__':
    try:
        test_redaction_fixtures()
        test_redaction_entry_recursive()
        print("RESULT: ALL REDACTION GATE TESTS PASSED")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
