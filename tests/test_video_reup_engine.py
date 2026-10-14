import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.video_reup_engine.batch_processor import process_video_batch
from tools.video_reup_engine.ffmpeg_wrapper import get_ffmpeg_path, probe_video, run_ffmpeg
from tools.video_reup_engine.filter_pipeline import PRESETS, build_filter_complex
from tools.video_reup_engine.mutation_engine import mutate_video


class TestVideoReupEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ffmpeg_bin = get_ffmpeg_path()
        cls.test_dir = Path(tempfile.mkdtemp(prefix="reup_engine_test_"))
        cls.sample_video = cls.test_dir / "sample_source.mp4"

        # Generate a clean 2-second synthetic MP4 video with video test pattern and sine wave audio
        cmd = [
            "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=25",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "64k",
            str(cls.sample_video)
        ]
        ret, out, err = run_ffmpeg(cmd, timeout=30, ffmpeg_bin=cls.ffmpeg_bin)
        if ret != 0:
            raise RuntimeError(f"Failed to generate synthetic test video: {err}")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def test_01_ffmpeg_binary_and_probe(self):
        self.assertTrue(Path(self.ffmpeg_bin).is_file())
        info = probe_video(self.sample_video)
        self.assertEqual(info["file_name"], "sample_source.mp4")
        self.assertEqual(info["width"], 320)
        self.assertEqual(info["height"], 240)
        self.assertAlmostEqual(info["duration_seconds"], 2.0, delta=0.2)
        self.assertTrue(info["has_audio"])
        self.assertTrue(len(info["md5"]) == 32)

    def test_02_filter_pipeline_presets(self):
        for preset_name, cfg in PRESETS.items():
            vf, af = build_filter_complex(cfg, has_audio=True)
            self.assertIn("eq=contrast=", vf)
            self.assertIn("crop=", vf)
            self.assertIsNotNone(af)
            self.assertIn("atempo=", af)

    def test_03_mutation_engine_balanced(self):
        output_file = self.test_dir / "sample_mutated_balanced.mp4"
        res = mutate_video(
            input_file=self.sample_video,
            output_file=output_file,
            config=PRESETS["balanced"],
            overwrite=True
        )

        self.assertEqual(res["status"], "MUTATION_SUCCESS")
        self.assertTrue(output_file.is_file())
        self.assertTrue(res["hash_verified"])
        self.assertNotEqual(res["input"]["md5"], res["output"]["md5"])
        self.assertNotEqual(res["input"]["sha256"], res["output"]["sha256"])

        # Probe mutated output
        out_info = probe_video(output_file)
        self.assertTrue(out_info["has_audio"])
        self.assertGreater(out_info["file_size_bytes"], 0)
        # Expected duration: 2.0s / 1.04 ~= 1.92s
        self.assertAlmostEqual(out_info["duration_seconds"], 1.92, delta=0.2)

    def test_04_batch_processor_and_ledger(self):
        batch_in = self.test_dir / "batch_input"
        batch_out = self.test_dir / "batch_output"
        batch_in.mkdir(parents=True, exist_ok=True)

        # Copy sample into batch_in with 2 different names
        shutil.copy(self.sample_video, batch_in / "video_clip_1.mp4")
        shutil.copy(self.sample_video, batch_in / "video_clip_2.mp4")

        summary = process_video_batch(
            input_dir=batch_in,
            output_dir=batch_out,
            config=PRESETS["light"],
            overwrite=True
        )

        self.assertEqual(summary["total_files"], 2)
        self.assertEqual(summary["success_count"], 2)
        self.assertEqual(summary["fail_count"], 0)

        ledger_file = batch_out / "reup_audit_ledger.json"
        self.assertTrue(ledger_file.is_file())

        with open(ledger_file, "r", encoding="utf-8") as f:
            ledger_data = json.load(f)

        self.assertEqual(len(ledger_data["records"]), 2)
        self.assertEqual(ledger_data["records"][0]["status"], "MUTATION_SUCCESS")
        self.assertEqual(ledger_data["records"][1]["status"], "MUTATION_SUCCESS")

    def test_05_file_pipeline_command(self):
        links_file = self.test_dir / "test_links.txt"
        out_dir = self.test_dir / "file_pipeline_out"
        raw_dir = self.test_dir / "file_pipeline_raw"

        # Write 2 video file paths/urls into test_links.txt
        with open(links_file, "w", encoding="utf-8") as f:
            f.write(f"# Comment line should be ignored\n\n")
            f.write(f"{self.sample_video}\n")
            f.write(f"{self.sample_video}\n")

        # Invoke CLI via subprocess
        import subprocess
        import sys
        cmd = [
            sys.executable, "scripts/video_reup.py", "file", str(links_file),
            "--raw-dir", str(raw_dir),
            "--output-dir", str(out_dir),
            "--preset", "light"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Batch finished!", res.stdout)

        ledger_file = out_dir / "links_batch_ledger.json"
        self.assertTrue(ledger_file.is_file())
        with open(ledger_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["total"], 2)
        self.assertEqual(data["success"], 2)
        self.assertEqual(data["failed"], 0)


if __name__ == "__main__":
    unittest.main()
