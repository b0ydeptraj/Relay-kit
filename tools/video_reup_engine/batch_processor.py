import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .filter_pipeline import MutationConfig, PRESETS
from .mutation_engine import mutate_video

SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


def process_video_batch(
    input_dir: Path | str,
    output_dir: Optional[Path | str] = None,
    config: Optional[MutationConfig] = None,
    overwrite: bool = True,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Batch process an entire directory of video files.
    Writes an audit ledger to output_dir/reup_audit_ledger.json.
    """
    src_dir = Path(input_dir).resolve()
    if not src_dir.is_dir():
        raise NotADirectoryError(f"Input directory does not exist: {src_dir}")

    cfg = config or PRESETS["balanced"]
    dest_dir = Path(output_dir).resolve() if output_dir else src_dir / "mutated_output"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Scan for video files, excluding already mutated files
    video_files = [
        f for f in src_dir.iterdir()
        if f.is_file()
        and f.suffix.lower() in SUPPORTED_EXTENSIONS
        and "_mutated_" not in f.name
    ]

    ledger_path = dest_dir / "reup_audit_ledger.json"
    audit_records: List[Dict[str, Any]] = []

    print(f"[*] Found {len(video_files)} video file(s) in {src_dir}")
    print(f"[*] Output directory: {dest_dir}")
    print(f"[*] Preset applied: {cfg.preset_name} (Speed: {cfg.speed}x, Mirror: {cfg.mirror_horizontal}, Crop: {cfg.crop_percent}%)")

    if dry_run:
        return {
            "dry_run": True,
            "total_files": len(video_files),
            "files": [str(f.name) for f in video_files],
            "output_dir": str(dest_dir),
            "preset": cfg.preset_name,
        }

    start_total_time = time.time()
    success_count = 0
    fail_count = 0

    for idx, video_path in enumerate(video_files, start=1):
        target_file = dest_dir / f"{video_path.stem}_mutated_{cfg.preset_name}{video_path.suffix}"
        print(f"[{idx}/{len(video_files)}] Processing: {video_path.name} -> {target_file.name}")

        try:
            record = mutate_video(
                input_file=video_path,
                output_file=target_file,
                config=cfg,
                overwrite=overwrite,
            )
            audit_records.append(record)
            success_count += 1
            print(f"  -> SUCCESS ({record['elapsed_seconds']}s) | MD5 changed: {record['input']['md5'][:8]}... -> {record['output']['md5'][:8]}...")
        except Exception as e:
            fail_count += 1
            err_record = {
                "status": "MUTATION_FAILED",
                "input_file": str(video_path),
                "error": str(e),
                "timestamp": time.time(),
            }
            audit_records.append(err_record)
            print(f"  -> FAILED: {e}", file=sys.stderr)

    total_elapsed = round(time.time() - start_total_time, 2)

    # Save ledger
    summary = {
        "timestamp": time.time(),
        "total_files": len(video_files),
        "success_count": success_count,
        "fail_count": fail_count,
        "total_elapsed_seconds": total_elapsed,
        "preset": cfg.preset_name,
        "records": audit_records,
    }

    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n[+] Batch completed in {total_elapsed}s. Success: {success_count}, Failed: {fail_count}")
    print(f"[+] Audit ledger written to: {ledger_path}")

    return summary
