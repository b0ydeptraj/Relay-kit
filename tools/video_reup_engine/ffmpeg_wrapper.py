import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def get_ffmpeg_path() -> str:
    """Find a usable ffmpeg executable without manual PATH setup."""
    # 1. Custom env var
    env_ffmpeg = os.environ.get("FFMPEG_PATH")
    if env_ffmpeg and os.path.isfile(env_ffmpeg):
        return env_ffmpeg

    # 2. System PATH
    which_ffmpeg = shutil.which("ffmpeg")
    if which_ffmpeg:
        return which_ffmpeg

    # 3. imageio_ffmpeg bundled binary
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.isfile(exe):
            return exe
    except ImportError:
        pass

    # 4. Local binary fallback
    local_bin = Path(__file__).resolve().parent / "bin" / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
    if local_bin.is_file():
        return str(local_bin)

    raise FileNotFoundError(
        "FFmpeg binary not found. Install imageio-ffmpeg (`pip install imageio-ffmpeg`) "
        "or add ffmpeg to system PATH."
    )


def calculate_file_hash(file_path: Path | str, algorithm: str = "md5") -> str:
    """Calculate cryptographic hash of a file."""
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def run_ffmpeg(
    cmd_args: List[str],
    timeout: int = 300,
    ffmpeg_bin: Optional[str] = None
) -> Tuple[int, str, str]:
    """Execute ffmpeg command with timeout protection."""
    binary = ffmpeg_bin or get_ffmpeg_path()
    full_cmd = [binary] + cmd_args

    proc = subprocess.Popen(
        full_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return proc.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        return -1, stdout, f"Execution timed out after {timeout} seconds\n{stderr}"


def probe_video(file_path: Path | str) -> Dict[str, Any]:
    """Inspect video properties (duration, resolution, fps, audio tracks, hashes) via FFmpeg."""
    path = Path(file_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    binary = get_ffmpeg_path()
    # Run ffmpeg -i <file> to read container metadata from stderr
    ret, _, stderr = run_ffmpeg(["-hide_banner", "-i", str(path)], timeout=15, ffmpeg_bin=binary)

    info: Dict[str, Any] = {
        "file_name": path.name,
        "file_path": str(path),
        "file_size_bytes": path.stat().st_size,
        "md5": calculate_file_hash(path, "md5"),
        "sha256": calculate_file_hash(path, "sha256"),
        "duration_seconds": 0.0,
        "width": 0,
        "height": 0,
        "fps": 0.0,
        "video_codec": "unknown",
        "audio_codec": "none",
        "audio_sample_rate": 0,
        "has_audio": False,
        "raw_stderr": stderr,
    }

    # Extract Duration: 00:00:15.34
    dur_match = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)", stderr)
    if dur_match:
        h, m, s = dur_match.groups()
        info["duration_seconds"] = round(int(h) * 3600 + int(m) * 60 + float(s), 3)

    # Extract Video Stream: Video: h264 (...), yuv420p(...), 1080x1920 [SAR 1:1 DAR 9:16], 30 fps
    vid_match = re.search(r"Stream #\d+:\d+.*?: Video: ([^,\n]+).*?(\d{2,5})x(\d{2,5})", stderr)
    if vid_match:
        info["video_codec"] = vid_match.group(1).strip()
        info["width"] = int(vid_match.group(2))
        info["height"] = int(vid_match.group(3))

    fps_match = re.search(r"(\d+(?:\.\d+)?)\s*fps", stderr)
    if fps_match:
        info["fps"] = float(fps_match.group(1))

    # Extract Audio Stream: Audio: aac (...), 44100 Hz, stereo
    aud_match = re.search(r"Stream #\d+:\d+.*?: Audio: ([^,\n]+).*?(\d{4,6})\s*Hz", stderr)
    if aud_match:
        info["has_audio"] = True
        info["audio_codec"] = aud_match.group(1).strip()
        info["audio_sample_rate"] = int(aud_match.group(2))

    return info
