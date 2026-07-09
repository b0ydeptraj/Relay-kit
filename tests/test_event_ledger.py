import sys
import tempfile
import traceback

from relay_kit_v3.event_ledger import EventLedger

def test_event_ledger():
    with tempfile.TemporaryDirectory() as temp_dir:
        ledger = EventLedger(temp_dir)
        
        # Log events
        id1 = ledger.log_event("lane_started", "lane_alpha", {"task": "build"})
        id2 = ledger.log_event("file_locked", "lane_alpha", {"file": "main.py"})
        id3 = ledger.log_event("lane_started", "lane_beta", {"task": "test"})
        
        # Read all events
        all_events = ledger.read_events()
        assert len(all_events) == 3
        
        # Read events for lane_alpha
        alpha_events = ledger.read_events("lane_alpha")
        assert len(alpha_events) == 2
        assert alpha_events[0]["event_type"] == "file_locked" # Order by DESC
        assert alpha_events[1]["event_type"] == "lane_started"
        
        # Check details json parsing
        assert alpha_events[0]["details"]["file"] == "main.py"
        
        ledger.close()

if __name__ == '__main__':
    try:
        test_event_ledger()
        print("RESULT: ALL EVENT LEDGER TESTS PASSED")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
