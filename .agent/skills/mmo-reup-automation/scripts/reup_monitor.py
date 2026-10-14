#!/usr/bin/env python3
"""
reup_monitor.py - Monitor and automate content re-upload (reup) operations.
Tracks source channels/accounts, detects new content, and auto-downloads for reup.

Usage:
    python scripts/reup_monitor.py --source "https://www.tiktok.com/@account" --output ./downloads
    python scripts/reup_monitor.py --config sources.json --interval 300
    python scripts/reup_monitor.py --platform youtube --channel CHANNEL_ID --api-key KEY
    python scripts/reup_monitor.py --download-queue queue.json --output ./videos

sources.json: [{"platform":"tiktok","url":"...","interval":600}]
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse
import re

YT_DLP = "yt-dlp"  # Must be installed: pip install yt-dlp


def check_ytdlp():
    result = subprocess.run([YT_DLP, "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print("[-] yt-dlp not found. Install: pip install yt-dlp")
        sys.exit(1)
    return result.stdout.strip()


def download_video(url: str, output_dir: str = "./downloads", quality: str = "best",
                   format_str: str = "mp4") -> dict:
    """Download video using yt-dlp."""
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, "%(uploader)s_%(id)s.%(ext)s")
    cmd = [YT_DLP, url, "-o", output_template,
           f"--format", f"bestvideo[ext={format_str}]+bestaudio/best[ext={format_str}]/best",
           "--write-info-json", "--no-playlist", "--quiet", "--no-warnings"]

    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    elapsed = round(time.time() - start, 1)

    # Find downloaded file
    downloaded = []
    for f in os.listdir(output_dir):
        if f.endswith(".mp4") or f.endswith(".webm"):
            filepath = os.path.join(output_dir, f)
            if os.path.getmtime(filepath) > start:
                downloaded.append(filepath)

    if result.returncode == 0 or downloaded:
        return {"success": True, "url": url, "files": downloaded, "elapsed_s": elapsed}
    else:
        return {"success": False, "url": url, "error": result.stderr[:200], "elapsed_s": elapsed}


def get_channel_videos_youtube(channel_id: str, api_key: str, max_results: int = 10) -> list:
    """Get latest videos from YouTube channel via Data API."""
    url = (f"https://www.googleapis.com/youtube/v3/search?key={api_key}"
           f"&channelId={channel_id}&part=snippet&order=date&type=video&maxResults={max_results}")
    try:
        resp = ureq.urlopen(url, timeout=15)
        data = json.loads(resp.read())
        videos = []
        for item in data.get("items", []):
            vid_id = item["id"]["videoId"]
            title  = item["snippet"]["title"]
            published = item["snippet"]["publishedAt"]
            videos.append({"id": vid_id, "url": f"https://youtube.com/watch?v={vid_id}",
                           "title": title, "published": published})
        return videos
    except Exception as e:
        print(f"[-] YouTube API error: {e}")
        return []


def load_seen_ids(cache_file: str) -> set:
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return set(json.load(f))
    return set()


def save_seen_ids(cache_file: str, ids: set):
    with open(cache_file, "w") as f:
        json.dump(list(ids), f)


def monitor_source(source: dict, output_dir: str, seen_ids: set) -> list:
    """Check source for new content and download."""
    platform = source.get("platform", "generic")
    url = source.get("url", "")
    new_downloads = []

    if platform == "youtube" and source.get("api_key") and source.get("channel_id"):
        videos = get_channel_videos_youtube(source["channel_id"], source["api_key"],
                                             source.get("max_results", 5))
        for v in videos:
            if v["id"] not in seen_ids:
                print(f"[+] New: {v['title'][:50]}...")
                result = download_video(v["url"], output_dir)
                if result["success"]:
                    seen_ids.add(v["id"])
                    new_downloads.append(result)
                    print(f"    Downloaded: {result['files']}")
    else:
        # Generic: use yt-dlp to list and download latest
        cmd = [YT_DLP, url, "--flat-playlist", "--get-id", "--playlist-end", "5", "--quiet"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        ids = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        for vid_id in ids:
            if vid_id not in seen_ids:
                vid_url = f"https://www.tiktok.com/video/{vid_id}" if platform == "tiktok" else url
                print(f"[+] New ID: {vid_id}")
                dl_result = download_video(vid_url if platform != "generic" else f"{url}/{vid_id}", output_dir)
                if dl_result["success"]:
                    seen_ids.add(vid_id)
                    new_downloads.append(dl_result)

    return new_downloads


def main():
    p = argparse.ArgumentParser(description="Reup content monitor and downloader")
    p.add_argument("--source", help="Single source URL")
    p.add_argument("--platform", choices=["tiktok","youtube","instagram","generic"], default="generic")
    p.add_argument("--config", help="Sources config JSON")
    p.add_argument("--output", default="./reup_downloads")
    p.add_argument("--interval", type=int, default=300, help="Check interval in seconds (daemon mode)")
    p.add_argument("--channel", help="YouTube channel ID")
    p.add_argument("--api-key", help="YouTube Data API key")
    p.add_argument("--daemon", action="store_true", help="Run continuously")
    p.add_argument("--download-queue", help="Queue file with URLs to download")
    args = p.parse_args()

    ver = check_ytdlp()
    print(f"[*] yt-dlp v{ver}")

    if args.download_queue:
        with open(args.download_queue) as f:
            queue = json.load(f) if args.download_queue.endswith(".json") else [l.strip() for l in f]
        print(f"[*] Downloading {len(queue)} videos from queue...")
        for item in queue:
            url = item if isinstance(item, str) else item.get("url", "")
            result = download_video(url, args.output)
            status = "OK" if result["success"] else "FAIL"
            print(f"  [{status}] {url[:50]} | {result['elapsed_s']}s")
        return

    if args.source:
        sources = [{"platform": args.platform, "url": args.source,
                    "channel_id": args.channel, "api_key": args.api_key}]
    elif args.config:
        with open(args.config) as f:
            sources = json.load(f)
    else:
        print("[-] --source or --config required"); sys.exit(1)

    cache_file = os.path.join(args.output, ".seen_ids.json")
    os.makedirs(args.output, exist_ok=True)
    seen = load_seen_ids(cache_file)

    while True:
        print(f"\n[{time.strftime('%H:%M:%S')}] Checking {len(sources)} source(s)...")
        for source in sources:
            new = monitor_source(source, args.output, seen)
            print(f"  {source.get('url','?')[:50]}: {len(new)} new downloads")
        save_seen_ids(cache_file, seen)

        if not args.daemon:
            break
        print(f"[*] Sleeping {args.interval}s...")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
