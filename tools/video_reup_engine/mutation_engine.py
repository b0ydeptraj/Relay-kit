import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .ffmpeg_wrapper import probe_video, run_ffmpeg
from .filter_pipeline import MutationConfig, PRESETS, build_filter_complex, generate_spoofed_metadata


def mutate_video(
    input_file: Path | str,
    output_file: Optional[Path | str] = None,
    config: Optional[MutationConfig] = None,
    overwrite: bool = True,
    timeout: int = 600,
) -> Dict[str, Any]:
    """
    Process a video file through the anti-copyright mutation pipeline.
    Guarantees:
      - New MD5 & SHA-256 hash.
      - Disrupted perceptual video & audio fingerprints.
      - Clean container metadata.
      - Web-optimized (+faststart) container for instant upload.
    """
    in_path = Path(input_file).resolve()
    if not in_path.is_file():
        raise FileNotFoundError(f"Input video file not found: {in_path}")

    cfg = config or PRESETS["balanced"]

    # Default output file naming
    if output_file is None:
        out_dir = in_path.parent / "reup_mutated"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{in_path.stem}_mutated_{cfg.preset_name}{in_path.suffix}"
    else:
        out_path = Path(output_file).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Probe input video properties
    in_info = probe_video(in_path)

    # 2. Build filter complex
    vf_str, af_str = build_filter_complex(cfg, has_audio=in_info["has_audio"])
    meta_args = generate_spoofed_metadata(cfg)

    # 3. Assemble FFmpeg command line arguments
    ffmpeg_args = ["-hide_banner", "-loglevel", "warning"]
    if overwrite:
        ffmpeg_args.append("-y")

    ffmpeg_args.extend(["-i", str(in_path)])

    if vf_str:
        ffmpeg_args.extend(["-vf", vf_str])

    if af_str and in_info["has_audio"]:
        ffmpeg_args.extend(["-af", af_str])

    # Video encoding params: H.264, yuv420p for 100% device & platform compatibility
    ffmpeg_args.extend([
        "-c:v", "libx264",
        "-preset", cfg.video_preset,
        "-crf", str(cfg.crf),
        "-pix_fmt", "yuv420p",
    ])

    # Audio encoding params
    if in_info["has_audio"]:
        ffmpeg_args.extend(["-c:a", "aac", "-b:a", "192k"])
    else:
        ffmpeg_args.extend(["-an"])

    # Web faststart: moves MOOV atom to the beginning of the MP4 container
    ffmpeg_args.extend(["-movflags", "+faststart"])

    # Add stripped and spoofed metadata
    ffmpeg_args.extend(meta_args)

    ffmpeg_args.append(str(out_path))

    # 4. Execute FFmpeg
    start_time = time.time()
    code, stdout, stderr = run_ffmpeg(ffmpeg_args, timeout=timeout)
    elapsed_seconds = round(time.time() - start_time, 2)

    if code != 0 or not out_path.is_file():
        raise RuntimeError(
            f"FFmpeg processing failed with exit code {code}.\n"
            f"Command: ffmpeg {' '.join(ffmpeg_args)}\n"
            f"Stderr: {stderr}"
        )

    # 5. Probe output video properties & verify mutation
    out_info = probe_video(out_path)

    hashes_differ = in_info["md5"] != out_info["md5"]
    if not hashes_differ:
        raise RuntimeError("FATAL: Original and Mutated MD5 hashes are identical!")

    result: Dict[str, Any] = {
        "status": "MUTATION_SUCCESS",
        "preset": cfg.preset_name,
        "input": {
            "path": str(in_path),
            "md5": in_info["md5"],
            "sha256": in_info["sha256"],
            "duration": in_info["duration_seconds"],
            "resolution": f"{in_info['width']}x{in_info['height']}",
            "size_bytes": in_info["file_size_bytes"],
        },
        "output": {
            "path": str(out_path),
            "md5": out_info["md5"],
            "sha256": out_info["sha256"],
            "duration": out_info["duration_seconds"],
            "resolution": f"{out_info['width']}x{out_info['height']}",
            "size_bytes": out_info["file_size_bytes"],
        },
        "filters_applied": {
            "speed": cfg.speed,
            "crop_percent": cfg.crop_percent,
            "mirror_horizontal": cfg.mirror_horizontal,
            "contrast": cfg.contrast,
            "saturation": cfg.saturation,
            "sharpness": cfg.sharpness,
            "micro_noise": cfg.add_micro_noise,
            "audio_tempo": cfg.audio_tempo_shift,
            "audio_pitch": cfg.audio_pitch_shift,
        },
        "elapsed_seconds": elapsed_seconds,
        "hash_verified": hashes_differ,
    }

    return result
