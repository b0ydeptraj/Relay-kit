import json
import shutil
import tempfile
import unittest
from pathlib import Path
from tools.video_reup_engine.auto_uploader import (
    AutoUploadQueue,
    clean_title_from_filename,
)


class TestAutoUploader(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="auto_upload_test_"))
        self.video_file_1 = self.test_dir / "user123_7106594312292453675_foryou_video_mutated.mp4"
        self.video_file_2 = self.test_dir / "cat_dancing_funny_clip_balanced.mp4"
        # Write dummy video files (>1024 bytes)
        self.video_file_1.write_bytes(b"\x00" * 2048)
        self.video_file_2.write_bytes(b"\x00" * 2048)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_clean_title_from_filename(self):
        title = clean_title_from_filename("theinthanaung344_7690205817089379604_foryou_fyp_mutated.mp4")
        self.assertIn("Theinthanaung344", title)
        # Verify tag words are stripped from title to prevent duplicate hashtags
        self.assertNotIn("Fyp", title)
        self.assertNotIn("7690205817089379604", title)
        self.assertNotIn("mutated", title.lower())

    def test_queue_status_and_lifecycle(self):
        queue = AutoUploadQueue(video_dir=self.test_dir)
        status = queue.get_status()
        self.assertEqual(status["total_videos"], 2)
        self.assertEqual(status["uploaded"], 0)
        self.assertEqual(status["pending"], 2)

        # Get next item
        item = queue.get_next_item()
        self.assertIsNotNone(item)
        self.assertTrue(item["ok"])
        self.assertIn(item["video_id"], [self.video_file_1.name, self.video_file_2.name])
        self.assertGreater(item["file_size"], 1024)
        self.assertTrue(len(item["file_base64"]) > 0)
        self.assertIn("#fyp", item["caption"])

        # Mark completed
        queue.mark_completed(item["video_id"], details={"post_clicked": True})
        status_after = queue.get_status()
        self.assertEqual(status_after["uploaded"], 1)
        self.assertEqual(status_after["pending"], 1)

        # Ledger file persistence
        self.assertTrue(queue.ledger_path.is_file())
        with open(queue.ledger_path, "r", encoding="utf-8") as f:
            ledger_data = json.load(f)
        self.assertEqual(ledger_data["uploads"][item["video_id"]]["status"], "UPLOADED")

        # Skip remaining
        next_item = queue.get_next_item()
        self.assertIsNotNone(next_item)
        queue.mark_skipped(next_item["video_id"], reason="Manual skip")

        status_final = queue.get_status()
        self.assertEqual(status_final["uploaded"], 1)
        self.assertEqual(status_final["skipped"], 1)
        self.assertEqual(status_final["pending"], 0)
        self.assertIsNone(queue.get_next_item())

    def test_deduplication_and_sync(self):
        # Create duplicate video with same title words
        dup_file = self.test_dir / "cat_dancing_funny_clip_light.mp4"
        dup_file.write_bytes(b"\x00" * 2048)

        queue = AutoUploadQueue(video_dir=self.test_dir)
        # Sync studio posted titles
        matched = queue.sync_posted_titles(["Cat Dancing Funny Clip #fyp #viral"])
        self.assertGreaterEqual(matched, 1)

        # The duplicate file should now be skipped or next item is not cat dancing
        next_item = queue.get_next_item()
        if next_item:
            self.assertNotIn("cat_dancing", next_item["file_name"])


if __name__ == "__main__":
    unittest.main()
