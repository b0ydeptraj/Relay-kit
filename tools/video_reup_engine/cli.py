#!/usr/bin/env python3
"""
Offline Video Reup & Anti-Copyright Engine CLI.
Zero-proxy, 100% free, automated watermark-free downloader & fingerprint mutation engine.
"""

import argparse
import json
import sys
from pathlib import Path

# Fix Windows console charmap encoding crashes
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from .auto_uploader import run_auto_upload_server
from .batch_processor import process_video_batch
from .downloader import download_video
from .ffmpeg_wrapper import probe_video
from .filter_pipeline import MutationConfig, PRESETS
from .mutation_engine import mutate_video


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="video_reup",
        description="Offline Video Reup & Anti-Copyright Engine (Zero-Proxy, 100% Free)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # 1. Download
    p_dl = subparsers.add_parser("download", help="Download watermark-free video (TikTok / Direct)")
    p_dl.add_argument("url", type=str, help="TikTok/Douyin share URL or direct video URL")
    p_dl.add_argument("--output-dir", "-o", type=str, default="raw_videos", help="Target download directory")

    # 2. Mutate (Single file)
    p_mut = subparsers.add_parser("mutate", help="Process and alter video fingerprint")
    p_mut.add_argument("file", type=str, help="Path to input video file")
    p_mut.add_argument("--output", "-o", type=str, default=None, help="Path to output mutated file")
    p_mut.add_argument("--preset", "-p", choices=["light", "balanced", "aggressive"], default="balanced", help="Filter preset")
    p_mut.add_argument("--no-mirror", action="store_true", help="Disable horizontal flip (preserve on-screen text)")
    p_mut.add_argument("--speed", type=float, default=None, help="Custom speed multiplier (e.g. 1.04)")
    p_mut.add_argument("--crop", type=float, default=None, help="Custom crop percent (e.g. 2.5)")
    p_mut.add_argument("--noise", action="store_true", help="Force enable micro-noise injection")

    # 3. Batch
    p_batch = subparsers.add_parser("batch", help="Batch process an entire folder of videos")
    p_batch.add_argument("input_dir", type=str, help="Path to directory containing raw videos")
    p_batch.add_argument("--output-dir", "-o", type=str, default=None, help="Target output directory")
    p_batch.add_argument("--preset", "-p", choices=["light", "balanced", "aggressive"], default="balanced", help="Filter preset")
    p_batch.add_argument("--dry-run", action="store_true", help="List files without encoding")

    # 4. Pipeline (Download + Mutate)
    p_pipe = subparsers.add_parser("pipeline", help="Download watermark-free video and mutate it in 1 command")
    p_pipe.add_argument("url", type=str, help="TikTok/Douyin share URL or direct video URL")
    p_pipe.add_argument("--raw-dir", type=str, default="raw_videos", help="Directory for raw video")
    p_pipe.add_argument("--output-dir", "-o", type=str, default="mutated_videos", help="Directory for final video")
    p_pipe.add_argument("--preset", "-p", choices=["light", "balanced", "aggressive"], default="balanced", help="Filter preset")
    p_pipe.add_argument("--no-mirror", action="store_true", help="Disable horizontal flip")

    # 5. Inspect
    p_ins = subparsers.add_parser("inspect", help="Inspect video resolution, fps, audio and hashes")
    p_ins.add_argument("file", type=str, help="Path to video file")

    # 6. File batch pipeline (links.txt)
    p_file = subparsers.add_parser("file", help="Batch download & mutate from a text file containing video URLs")
    p_file.add_argument("file_path", type=str, help="Path to text file containing video URLs (one per line)")
    p_file.add_argument("--raw-dir", type=str, default="raw_videos", help="Directory for raw downloads")
    p_file.add_argument("--output-dir", "-o", type=str, default="mutated_videos", help="Directory for final videos")
    p_file.add_argument("--preset", "-p", choices=["light", "balanced", "aggressive"], default="balanced", help="Filter preset")
    p_file.add_argument("--no-mirror", action="store_true", help="Disable horizontal flip")

    # 7. Auto-Upload Server (Local bridge for Chrome Extension)
    p_srv = subparsers.add_parser("upload-server", help="Start local TikTok auto-upload bridge server")
    p_srv.add_argument("--dir", "-d", type=str, default="mutated_videos", help="Directory of videos to upload")
    p_srv.add_argument("--port", "-p", type=int, default=8765, help="Server port (default: 8765)")
    p_srv.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    p_srv.add_argument("--caption-template", type=str, default="{title} #fyp #viral #trending", help="Caption template")
    p_srv.add_argument("--schedule-interval", type=int, default=0, help="Interval in minutes between scheduled posts (0=post now)")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        return 1

    if args.subcommand == "download":
        print(f"[*] Downloading watermark-free video from: {args.url}")
        try:
            info = download_video(args.url, output_dir=args.output_dir)
            print(f"[+] Download successful: {info['output_path']} ({round(info['file_size'] / 1048576, 2)} MB)")
            return 0
        except Exception as e:
            print(f"[-] Download error: {e}", file=sys.stderr)
            return 1

    elif args.subcommand == "mutate":
        base_cfg = PRESETS[args.preset]
        cfg = MutationConfig(
            preset_name=args.preset,
            speed=args.speed if args.speed is not None else base_cfg.speed,
            crop_percent=args.crop if args.crop is not None else base_cfg.crop_percent,
            mirror_horizontal=False if args.no_mirror else base_cfg.mirror_horizontal,
            contrast=base_cfg.contrast,
            brightness=base_cfg.brightness,
            saturation=base_cfg.saturation,
            sharpness=base_cfg.sharpness,
            add_micro_noise=True if args.noise else base_cfg.add_micro_noise,
            audio_pitch_shift=base_cfg.audio_pitch_shift,
            audio_tempo_shift=base_cfg.audio_tempo_shift,
            crf=base_cfg.crf,
        )

        print(f"[*] Mutating: {args.file}")
        print(f"[*] Preset: {cfg.preset_name} | Speed: {cfg.speed}x | Mirror: {cfg.mirror_horizontal} | Crop: {cfg.crop_percent}%")
        try:
            res = mutate_video(args.file, output_file=args.output, config=cfg)
            print(f"[+] Mutation SUCCESS in {res['elapsed_seconds']}s")
            print(f"    Output: {res['output']['path']}")
            print(f"    Original MD5: {res['input']['md5']}")
            print(f"    New MD5:      {res['output']['md5']}")
            print(f"    Hash Divergence Verified: {res['hash_verified']}")
            return 0
        except Exception as e:
            print(f"[-] Mutation error: {e}", file=sys.stderr)
            return 1

    elif args.subcommand == "batch":
        cfg = PRESETS[args.preset]
        try:
            summary = process_video_batch(
                input_dir=args.input_dir,
                output_dir=args.output_dir,
                config=cfg,
                dry_run=args.dry_run,
            )
            return 0 if summary.get("fail_count", 0) == 0 else 2
        except Exception as e:
            print(f"[-] Batch error: {e}", file=sys.stderr)
            return 1

    elif args.subcommand == "pipeline":
        print(f"[*] Pipeline step 1: Downloading from {args.url}")
        try:
            dl_info = download_video(args.url, output_dir=args.raw_dir)
            raw_path = Path(dl_info["output_path"])
            print(f"[+] Downloaded raw video: {raw_path}")

            base_cfg = PRESETS[args.preset]
            cfg = MutationConfig(
                preset_name=args.preset,
                speed=base_cfg.speed,
                crop_percent=base_cfg.crop_percent,
                mirror_horizontal=False if args.no_mirror else base_cfg.mirror_horizontal,
                contrast=base_cfg.contrast,
                brightness=base_cfg.brightness,
                saturation=base_cfg.saturation,
                sharpness=base_cfg.sharpness,
                add_micro_noise=base_cfg.add_micro_noise,
                audio_pitch_shift=base_cfg.audio_pitch_shift,
                audio_tempo_shift=base_cfg.audio_tempo_shift,
                crf=base_cfg.crf,
            )

            out_dir = Path(args.output_dir).resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{raw_path.stem}_mutated{raw_path.suffix}"

            print(f"[*] Pipeline step 2: Applying anti-copyright mutation ({args.preset})...")
            res = mutate_video(raw_path, output_file=out_file, config=cfg)
            print(f"[+] Pipeline COMPLETE! Final video ready for upload:")
            print(f"    File: {res['output']['path']}")
            print(f"    Duration: {res['output']['duration']}s")
            print(f"    New MD5: {res['output']['md5']}")
            return 0
        except Exception as e:
            print(f"[-] Pipeline error: {e}", file=sys.stderr)
            return 1

    elif args.subcommand == "inspect":
        try:
            info = probe_video(args.file)
            print(json.dumps(
                {
                    "file_name": info["file_name"],
                    "resolution": f"{info['width']}x{info['height']}",
                    "fps": info["fps"],
                    "duration_seconds": info["duration_seconds"],
                    "video_codec": info["video_codec"],
                    "audio_codec": info["audio_codec"],
                    "md5": info["md5"],
                    "sha256": info["sha256"],
                    "file_size_bytes": info["file_size_bytes"],
                },
                indent=2,
            ))
            return 0
        except Exception as e:
            print(f"[-] Inspect error: {e}", file=sys.stderr)
    elif args.subcommand == "file":
        links_file = Path(args.file_path).resolve()
        if not links_file.is_file():
            print(f"[-] Links file not found: {links_file}", file=sys.stderr)
            return 1

        with open(links_file, "r", encoding="utf-8", errors="replace") as f:
            raw_lines = [line.strip() for line in f]

        urls = [line for line in raw_lines if line and not line.startswith("#")]
        if not urls:
            print(f"[-] No valid URLs found in {links_file}", file=sys.stderr)
            return 1

        print(f"[*] Loaded {len(urls)} URL(s) from {links_file.name}")
        print(f"[*] Preset: {args.preset} | Output dir: {args.output_dir}")

        base_cfg = PRESETS[args.preset]
        cfg = MutationConfig(
            preset_name=args.preset,
            speed=base_cfg.speed,
            crop_percent=base_cfg.crop_percent,
            mirror_horizontal=False if args.no_mirror else base_cfg.mirror_horizontal,
            contrast=base_cfg.contrast,
            brightness=base_cfg.brightness,
            saturation=base_cfg.saturation,
            sharpness=base_cfg.sharpness,
            add_micro_noise=base_cfg.add_micro_noise,
            audio_pitch_shift=base_cfg.audio_pitch_shift,
            audio_tempo_shift=base_cfg.audio_tempo_shift,
            crf=base_cfg.crf,
        )

        raw_dir = Path(args.raw_dir).resolve()
        raw_dir.mkdir(parents=True, exist_ok=True)
        out_dir = Path(args.output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        success_count = 0
        fail_count = 0
        records = []

        for idx, url in enumerate(urls, start=1):
            print(f"\n[{idx}/{len(urls)}] Processing URL: {url}")
            try:
                dl_info = download_video(url, output_dir=raw_dir)
                raw_path = Path(dl_info["output_path"])
                print(f"  [+] Downloaded: {raw_path.name} ({round(dl_info['file_size']/1048576, 2)} MB)")

                target_out = out_dir / f"{raw_path.stem}_mutated{raw_path.suffix}"
                res = mutate_video(raw_path, output_file=target_out, config=cfg)
                success_count += 1
                records.append(res)
                print(f"  [+] Mutated SUCCESS in {res['elapsed_seconds']}s -> {target_out.name}")
                print(f"      MD5: {res['input']['md5'][:8]}... -> {res['output']['md5'][:8]}...")
            except Exception as e:
                fail_count += 1
                print(f"  [-] FAILED: {e}", file=sys.stderr)
                records.append({"status": "FAILED", "url": url, "error": str(e)})

        ledger_path = out_dir / "links_batch_ledger.json"
        with open(ledger_path, "w", encoding="utf-8") as f:
            json.dump({
                "source_file": str(links_file),
                "total": len(urls),
                "success": success_count,
                "failed": fail_count,
                "preset": args.preset,
                "records": records,
            }, f, indent=2, ensure_ascii=False)

        print(f"\n[+] Batch finished! Total: {len(urls)} | Success: {success_count} | Failed: {fail_count}")
        print(f"[+] Output ledger: {ledger_path}")
        return 0 if fail_count == 0 else 2

    elif args.subcommand == "upload-server":
        run_auto_upload_server(
            video_dir=args.dir,
            port=args.port,
            host=args.host,
            caption_template=args.caption_template,
            schedule_interval_mins=args.schedule_interval,
        )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
