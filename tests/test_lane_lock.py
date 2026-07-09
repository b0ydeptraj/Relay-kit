import sys
import tempfile
import time
import traceback
from pathlib import Path

from relay_kit_v3.lane_lock import LaneLockManager

def test_lane_lock_acquire_and_release():
    with tempfile.TemporaryDirectory() as temp_dir:
        lock_mgr = LaneLockManager(temp_dir)
        
        # Acquire lock
        res = lock_mgr.acquire("lane1", "file_a.txt", "agent_1", ttl_seconds=60)
        assert res is True
        
        # Check lock exists
        info = lock_mgr.check_lock("file_a.txt")
        assert info is not None
        assert info["lane_id"] == "lane1"
        assert info["agent_id"] == "agent_1"
        
        # Another lane tries to acquire
        res2 = lock_mgr.acquire("lane2", "file_a.txt", "agent_2", ttl_seconds=60)
        assert res2 is False
        
        # Same lane re-acquires (renews lock)
        res3 = lock_mgr.acquire("lane1", "file_a.txt", "agent_1", ttl_seconds=120)
        assert res3 is True
        info3 = lock_mgr.check_lock("file_a.txt")
        assert info3["ttl"] == 120.0
        
        # Release lock
        rel = lock_mgr.release("lane1", "file_a.txt")
        assert rel is True
        
        # Now lane2 can acquire
        res4 = lock_mgr.acquire("lane2", "file_a.txt", "agent_2", ttl_seconds=60)
        assert res4 is True
        lock_mgr.close()

def test_lane_lock_ttl_expiration():
    with tempfile.TemporaryDirectory() as temp_dir:
        lock_mgr = LaneLockManager(temp_dir)
        
        # Acquire lock with 0.1s TTL
        res = lock_mgr.acquire("lane1", "file_b.txt", ttl_seconds=0.1)
        assert res is True
        
        # Immediately lane2 cannot acquire
        assert lock_mgr.acquire("lane2", "file_b.txt") is False
        
        # Wait for TTL to expire
        time.sleep(0.15)
        
        # Now lane2 CAN acquire (old lock auto-cleans)
        res2 = lock_mgr.acquire("lane2", "file_b.txt")
        assert res2 is True
        lock_mgr.close()

if __name__ == '__main__':
    try:
        test_lane_lock_acquire_and_release()
        test_lane_lock_ttl_expiration()
        print("RESULT: ALL LANE LOCK TESTS PASSED")
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
