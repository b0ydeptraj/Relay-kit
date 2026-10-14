import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, Optional
import requests

TIKWM_API_URL = "https://www.tikwm.com/api/"
SSSTIK_API_URL = "https://ssstik.io/abc?url=dl"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
}


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    Sanitize string into an ASCII/safe filename for Windows NTFS and terminal safety.
    Strips emojis, non-ascii characters, and special shell symbols.
    """
    # Normalize unicode (decompose accented chars)
    normalized = unicodedata.normalize("NFKD", name)
    # Filter to ASCII only (strips emojis, surrogates, complex unicode)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    # Replace non-alphanumeric (except hyphen and underscore) with underscore
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", ascii_text)
    # Collapse consecutive underscores
    cleaned = re.sub(r"_+", "_", cleaned).strip("._")
    if not cleaned:
        cleaned = "reup_video"
    return cleaned[:max_length]


def resolve_short_url(url: str, timeout: int = 10) -> str:
    """Resolve short sharing links (e.g. vt.tiktok.com, vm.tiktok.com) to canonical URLs."""
    url = url.strip()
    if any(k in url for k in ["vt.tiktok.com", "vm.tiktok.com", "v.douyin.com", "t.co"]):
        try:
            resp = requests.head(url, headers=DEFAULT_HEADERS, allow_redirects=True, timeout=timeout)
            if resp.url:
                return resp.url
        except Exception:
            pass
    return url


def parse_via_tikwm(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """Parse video metadata and direct MP4 URL via TikWM."""
    try:
        resp = requests.post(TIKWM_API_URL, data={"url": url, "hd": 1}, headers=DEFAULT_HEADERS, timeout=timeout)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if data.get("code") != 0 or "data" not in data:
            return None

        item = data["data"]
        candidates = []
        for key in ["play", "hdplay", "wmplay"]:
            u = item.get(key)
            if u:
                if u.startswith("/"):
                    u = f"https://www.tikwm.com{u}"
                if u not in candidates:
                    candidates.append(u)

        if not candidates:
            return None

        return {
            "id": str(item.get("id", "unknown_id")),
            "title": item.get("title", ""),
            "author": item.get("author", {}).get("unique_id", "unknown_author"),
            "nickname": item.get("author", {}).get("nickname", ""),
            "duration": item.get("duration", 0),
            "video_url": candidates[0],
            "candidate_urls": candidates,
            "provider": "tikwm",
        }
    except Exception:
        return None


def parse_via_ssstik(url: str, timeout: int = 12) -> Optional[Dict[str, Any]]:
    """Fallback parser using SSSTik to extract watermark-free CDN link."""
    headers = {
        "User-Agent": DEFAULT_HEADERS["User-Agent"],
        "Referer": "https://ssstik.io/en",
    }
    payload = {"id": url, "locale": "en", "tt": 0}
    try:
        resp = requests.post(SSSTIK_API_URL, data=payload, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            return None

        match = re.search(
            r'href=[\"\']([^\"\']+)[\"\'][^>]*class=[\"\'][^\"\']*without_watermark',
            resp.text,
        )
        if not match:
            return None

        video_url = match.group(1)

        # Extract title from h2 if available
        title_match = re.search(r'<h2>([^<]+)</h2>', resp.text)
        title = title_match.group(1).strip() if title_match else ""

        # Extract video ID from URL
        vid_id_match = re.search(r'/(\d{15,22})', url)
        vid_id = vid_id_match.group(1) if vid_id_match else "ssstik_video"

        return {
            "id": vid_id,
            "title": title,
            "author": "tiktok_user",
            "nickname": "",
            "duration": 0,
            "video_url": video_url,
            "provider": "ssstik",
        }
    except Exception:
        return None


def fetch_tiktok_media_info(url: str) -> Dict[str, Any]:
    """Multi-provider resolver for TikTok video streams without watermark."""
    resolved_url = resolve_short_url(url)

    # Attempt 1: TikWM
    res = parse_via_tikwm(resolved_url)
    if res:
        return res

    # Attempt 2: SSSTik fallback
    res = parse_via_ssstik(resolved_url)
    if res:
        return res

    raise ValueError(f"Unable to parse video stream from URL: {url} (all providers failed or video is private)")


def download_stream(
    stream_url: str,
    output_path: Path | str,
    chunk_size: int = 1048576,
    timeout: int = 30
) -> Path:
    """Download binary media stream to disk with streaming chunks."""
    target_path = Path(output_path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    headers = {
        "User-Agent": DEFAULT_HEADERS["User-Agent"],
        "Referer": "https://www.tikwm.com/",
    }

    with requests.get(stream_url, headers=headers, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

    return target_path


def download_video(
    url_or_id: str,
    output_dir: Path | str = "raw_videos",
    custom_filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entrypoint for downloading a video without watermark.
    Supports TikTok / Douyin short links, web links, or direct MP4 URLs.
    Guarantees clean, ASCII-safe filenames without emoji corruption.
    """
    target_dir = Path(output_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    url = url_or_id.strip()

    # Case 0: Local file on disk
    if os.path.isfile(url):
        in_p = Path(url).resolve()
        target_p = target_dir / in_p.name
        if in_p != target_p:
            import shutil
            shutil.copy2(in_p, target_p)
        return {
            "source_type": "local_file",
            "url": str(in_p),
            "output_path": str(target_p),
            "file_size": target_p.stat().st_size,
        }

    # Case 1: Direct MP4 or video file URL
    if url.lower().endswith(".mp4") or "cdn" in url.lower():
        stem = custom_filename or sanitize_filename(Path(url.split("?")[0]).name)
        if not stem.endswith(".mp4"):
            stem += ".mp4"
        out_file = target_dir / stem
        download_stream(url, out_file)
        return {
            "source_type": "direct_url",
            "url": url,
            "output_path": str(out_file),
            "file_size": out_file.stat().st_size,
        }

    # Case 2: TikTok / Douyin link
    info = fetch_tiktok_media_info(url)
    clean_title = sanitize_filename(info["title"] or f"tiktok_{info['id']}")
    clean_author = sanitize_filename(info["author"])
    out_filename = custom_filename or f"{clean_author}_{info['id']}_{clean_title}.mp4"
    if not out_filename.endswith(".mp4"):
        out_filename += ".mp4"

    out_file = target_dir / out_filename

    urls_to_try = info.get("candidate_urls") or [info["video_url"]]
    downloaded = False
    last_err = None

    for stream_url in urls_to_try:
        try:
            download_stream(stream_url, out_file)
            downloaded = True
            break
        except Exception as e:
            last_err = e
            continue

    if not downloaded:
        raise RuntimeError(f"Failed to download video stream from all candidate URLs: {last_err}")

    info["output_path"] = str(out_file)
    info["file_size"] = out_file.stat().st_size
    info["source_type"] = f"tiktok_no_watermark_{info.get('provider', 'generic')}"
    return info
