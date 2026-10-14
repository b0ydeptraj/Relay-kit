import datetime
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MutationConfig:
    preset_name: str = "balanced"
    speed: float = 1.04
    crop_percent: float = 2.5
    mirror_horizontal: bool = True
    contrast: float = 1.04
    brightness: float = 0.01
    saturation: float = 1.05
    sharpness: bool = True
    add_micro_noise: bool = False
    audio_pitch_shift: float = 1.025
    audio_tempo_shift: float = 1.04
    crf: int = 20
    video_preset: str = "fast"
    spoof_device: str = "Apple iPhone 15 Pro"


PRESETS: Dict[str, MutationConfig] = {
    "light": MutationConfig(
        preset_name="light",
        speed=1.02,
        crop_percent=1.5,
        mirror_horizontal=False,  # Keep text readable
        contrast=1.02,
        brightness=0.005,
        saturation=1.03,
        sharpness=False,
        add_micro_noise=False,
        audio_pitch_shift=1.015,
        audio_tempo_shift=1.02,
        crf=20,
    ),
    "balanced": MutationConfig(
        preset_name="balanced",
        speed=1.04,
        crop_percent=2.5,
        mirror_horizontal=False,  # Keep on-screen text and lyrics readable
        contrast=1.04,
        brightness=0.01,
        saturation=1.05,
        sharpness=True,
        add_micro_noise=False,
        audio_pitch_shift=1.025,
        audio_tempo_shift=1.04,
        crf=20,
    ),
    "aggressive": MutationConfig(
        preset_name="aggressive",
        speed=1.06,
        crop_percent=3.5,
        mirror_horizontal=True,
        contrast=1.06,
        brightness=0.015,
        saturation=1.08,
        sharpness=True,
        add_micro_noise=True,
        audio_pitch_shift=1.04,
        audio_tempo_shift=1.06,
        crf=21,
    ),
}


def build_filter_complex(cfg: MutationConfig, has_audio: bool = True) -> Tuple[str, Optional[str]]:
    """
    Construct FFmpeg filter graph string for video and audio streams.
    Returns: (video_filter_string, audio_filter_string)
    """
    vf_chain: List[str] = []

    # 1. Playback Speed (Video PTS)
    if cfg.speed != 1.0:
        pts_factor = 1.0 / cfg.speed
        vf_chain.append(f"setpts={pts_factor:.4f}*PTS")

    # 2. Horizontal Mirror (hflip)
    if cfg.mirror_horizontal:
        vf_chain.append("hflip")

    # 3. Dynamic Micro-Crop (crops edges to disrupt spatial coordinates)
    if cfg.crop_percent > 0:
        pct = cfg.crop_percent / 100.0
        # Crop width and height by 2*pct, offset by pct*in_w, pct*in_h
        vf_chain.append(
            f"crop=in_w*(1-{2*pct:.4f}):in_h*(1-{2*pct:.4f}):in_w*{pct:.4f}:in_h*{pct:.4f}"
        )

    # 4. Color Grading (Contrast, Brightness, Saturation)
    vf_chain.append(
        f"eq=contrast={cfg.contrast:.3f}:brightness={cfg.brightness:.3f}:saturation={cfg.saturation:.3f}"
    )

    # 5. Spatial gradient filter (Unsharp mask)
    if cfg.sharpness:
        vf_chain.append("unsharp=3:3:0.5:3:3:0.0")

    # 6. Imperceptible stochastic micro-noise
    if cfg.add_micro_noise:
        vf_chain.append("noise=alls=1.5:allf=t")

    video_filter = ",".join(vf_chain)

    # Audio filter chain
    audio_filter = None
    if has_audio:
        af_chain: List[str] = []
        # Audio tempo adjustment
        # FFmpeg atempo supports values between 0.5 and 2.0
        if cfg.audio_tempo_shift != 1.0:
            af_chain.append(f"atempo={cfg.audio_tempo_shift:.4f}")

        # Pitch shift via asetrate and resample back to 44.1kHz
        if cfg.audio_pitch_shift != 1.0:
            sample_rate = 44100
            shifted_rate = int(sample_rate * cfg.audio_pitch_shift)
            # Adjust rate and compensate with atempo to maintain timing synchronization
            af_chain.append(f"asetrate={shifted_rate}")
            compensate_tempo = 1.0 / cfg.audio_pitch_shift
            af_chain.append(f"atempo={compensate_tempo:.4f}")
            af_chain.append(f"aresample={sample_rate}")

        if af_chain:
            audio_filter = ",".join(af_chain)

    return video_filter, audio_filter


def generate_spoofed_metadata(cfg: MutationConfig) -> List[str]:
    """Generate fake camera and encoding metadata tags to wipe source tracking."""
    # Generate timestamp within past 1-30 days
    delta_days = random.randint(1, 28)
    delta_secs = random.randint(100, 80000)
    fake_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=delta_days, seconds=delta_secs
    )
    time_str = fake_time.strftime("%Y-%m-%dT%H:%M:%SZ")

    random_id = f"MOV_{random.randint(1000, 9999)}_{random.randint(100, 999)}"

    metadata_args = [
        "-map_metadata", "-1",  # Strip all original metadata
        "-metadata", f"creation_time={time_str}",
        "-metadata", f"title={random_id}",
        "-metadata", f"comment=Processed via {cfg.spoof_device}",
        "-metadata", f"artist={cfg.spoof_device}",
    ]
    return metadata_args
