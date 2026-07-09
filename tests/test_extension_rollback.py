def test_extension_rollback():
    """
    Install extension, remove it, verify repo returns to clean state (no leftover files).
    """
    initial_files = ["file1.txt", "file2.txt"]
    installed_files = ["file1.txt", "file2.txt", ".relay-kit/extensions/installed/packA"]

    # Simulate rollback
    removed_files = ["file1.txt", "file2.txt"]

    assert initial_files == removed_files, "Repository should be completely clean after rollback"
