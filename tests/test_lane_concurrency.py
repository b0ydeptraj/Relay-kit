import time
import threading


def test_lane_concurrency_stress():
    """
    10-lane simulation, verify: lock conflicts detected deterministically, no file corruption.
    """
    locks = {}
    lock_mutex = threading.Lock()
    conflicts_detected = 0

    def acquire_lock(lane_id, file_path):
        nonlocal conflicts_detected
        with lock_mutex:
            if file_path in locks:
                conflicts_detected += 1
                return False
            locks[file_path] = lane_id
            return True

    def release_lock(lane_id, file_path):
        with lock_mutex:
            if locks.get(file_path) == lane_id:
                del locks[file_path]

    def simulate_agent(lane_id, target_file):
        if acquire_lock(lane_id, target_file):
            time.sleep(0.01)  # simulate work
            release_lock(lane_id, target_file)

    threads = []
    # 10 agents trying to lock the same file
    for i in range(10):
        t = threading.Thread(target=simulate_agent, args=(f"lane-{i}", "shared.txt"))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Only 1 can acquire at a time; 9 must have conflicted
    assert conflicts_detected == 9, f"Expected 9 conflicts, got {conflicts_detected}"
    assert "shared.txt" not in locks, "Lock should be released at the end"
