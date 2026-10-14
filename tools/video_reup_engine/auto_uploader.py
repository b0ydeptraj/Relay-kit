#!/usr/bin/env python3
"""
TikTok Auto-Upload Queue Manager & Local Bridge Server.
Zero-proxy, 100% free, local automated pipeline for unattended TikTok uploading.
"""

import base64
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

# Fix Windows console charmap encoding
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_TAGS = ["#fyp", "#viral", "#trending", "#foryou", "#xuhuong"]


TAG_KEYWORDS = {
    "fyp", "viral", "trending", "foryou", "xuhuong", "xuhuongtik", "xh",
    "trend", "tiktok", "capcut", "capcutpioneer", "nhactamtrang"
}


def normalize_title(title: str) -> str:
    """Normalize title for fuzzy deduplication comparison."""
    t = (title or "").lower()
    t = re.sub(r"[#@_\-\.,!?:;'\"]+", " ", t)
    # Remove common hashtag suffixes
    words = [w for w in t.split() if w not in TAG_KEYWORDS and not w.isdigit()]
    return " ".join(words)


def clean_title_from_filename(filename: str) -> str:
    """Generate clean title from raw/mutated filename without repetitive hashtags."""
    stem = Path(filename).stem
    # Strip common suffixes
    stem = re.sub(r"_(mutated|balanced|light|aggressive|output|converted).*", "", stem, flags=re.I)
    # Strip numeric TikTok IDs (e.g. 7106594312292453675)
    stem = re.sub(r"\b\d{15,22}\b", "", stem)
    # Replace underscores/dashes with spaces
    words = [w for w in re.split(r"[_\-\s]+", stem) if w and not w.isdigit()]
    if not words:
        words = ["Video", "Trending"]
    clean_words = []
    for w in words:
        if w.startswith("@"):
            continue
        # Filter out standalone generic tag words from the title itself
        if w.lower() in TAG_KEYWORDS:
            continue
        clean_words.append(w.capitalize())
    title = " ".join(clean_words).strip()
    return title or "Trending Video"


class AutoUploadQueue:
    """Manages disk video queue and persistent upload ledger with deduplication."""

    def __init__(
        self,
        video_dir: Path,
        ledger_path: Optional[Path] = None,
        caption_template: str = "{title} #fyp #viral #trending",
        schedule_interval_mins: int = 0,
    ):
        self.video_dir = Path(video_dir).resolve()
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_path = (
            Path(ledger_path).resolve()
            if ledger_path
            else self.video_dir / "upload_ledger.json"
        )
        self.caption_template = caption_template
        self.schedule_interval_mins = schedule_interval_mins
        self.ledger: Dict[str, Any] = self._load_ledger()

    def _load_ledger(self) -> Dict[str, Any]:
        if self.ledger_path.is_file():
            try:
                with open(self.ledger_path, "r", encoding="utf-8", errors="replace") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "uploads" in data:
                        return data
            except Exception:
                pass
        return {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "uploads": {},
        }

    def _save_ledger(self) -> None:
        self.ledger["updated_at"] = datetime.now(timezone.utc).isoformat()
        with open(self.ledger_path, "w", encoding="utf-8", errors="replace") as f:
            json.dump(self.ledger, f, indent=2, ensure_ascii=False)

    def scan_videos(self) -> List[Path]:
        """Find all valid video files in video_dir sorted by modification time."""
        valid_exts = {".mp4", ".mov", ".m4v", ".webm"}
        files = [
            f for f in self.video_dir.iterdir()
            if f.is_file() and f.suffix.lower() in valid_exts and f.stat().st_size > 1024
        ]
        files.sort(key=lambda x: x.stat().st_mtime)
        return files

    def sync_posted_titles(self, titles: List[str]) -> int:
        """Sync titles already posted on TikTok Studio to ledger to prevent duplicates."""
        normalized_posted = [normalize_title(t) for t in titles if t]
        matched_count = 0
        videos = self.scan_videos()
        for v in videos:
            rec = self.ledger["uploads"].get(v.name)
            if rec and rec.get("status") == "UPLOADED":
                continue
            v_title = normalize_title(clean_title_from_filename(v.name))
            if not v_title:
                continue
            # Match if v_title is a substring of posted title or vice versa
            matched = False
            for p_title in normalized_posted:
                if not p_title:
                    continue
                if v_title == p_title or (len(v_title) > 6 and v_title in p_title) or (len(p_title) > 6 and p_title in v_title):
                    matched = True
                    break
            if matched:
                self.mark_completed(v.name, details={"synced_from_studio": True, "clean_title": clean_title_from_filename(v.name)})
                matched_count += 1
        return matched_count

    def reset_failed(self) -> int:
        """Reset failed items back to pending if user wants to retry."""
        count = 0
        for k, v in self.ledger["uploads"].items():
            if v.get("status") == "FAILED":
                del self.ledger["uploads"][k]
                count += 1
        if count > 0:
            self._save_ledger()
        return count

    def get_status(self) -> Dict[str, Any]:
        """Get summary of queue: total, uploaded, pending, failed, skipped."""
        videos = self.scan_videos()
        total = len(videos)
        uploaded = 0
        pending = 0
        failed = 0
        skipped = 0

        next_video = None
        for v in videos:
            rec = self.ledger["uploads"].get(v.name)
            if not rec:
                pending += 1
                if not next_video:
                    next_video = v.name
            elif rec.get("status") == "UPLOADED":
                uploaded += 1
            elif rec.get("status") == "FAILED":
                failed += 1
            elif rec.get("status") == "SKIPPED":
                skipped += 1
            elif rec.get("status") == "PROCESSING":
                pending += 1
                if not next_video:
                    next_video = v.name
            else:
                pending += 1
                if not next_video:
                    next_video = v.name

        return {
            "ok": True,
            "video_dir": str(self.video_dir),
            "total_videos": total,
            "uploaded": uploaded,
            "pending": pending,
            "failed": failed,
            "skipped": skipped,
            "next_file": next_video,
        }

    def get_next_item(self) -> Optional[Dict[str, Any]]:
        """Fetch the next pending video with generated metadata, base64 payload, and deduping."""
        videos = self.scan_videos()

        # Build set of normalized titles already uploaded or in progress
        uploaded_norm_titles = set()
        for k, v in self.ledger["uploads"].items():
            if v.get("status") in ("UPLOADED", "PROCESSING"):
                c_title = v.get("details", {}).get("clean_title") or clean_title_from_filename(k)
                norm = normalize_title(c_title)
                if norm:
                    uploaded_norm_titles.add(norm)

        for v in videos:
            rec = self.ledger["uploads"].get(v.name)
            # CRITICAL DEDUP RULE:
            # If status is UPLOADED, SKIPPED, or FAILED: DO NOT RETURN IT!
            # (Failed videos must NOT be automatically retried in loop, avoiding duplicate posts)
            if rec and rec.get("status") in ("UPLOADED", "SKIPPED", "FAILED"):
                continue

            # If currently marked PROCESSING, only retry if stale (> 15 mins)
            if rec and rec.get("status") == "PROCESSING":
                proc_time = rec.get("processing_at", "")
                try:
                    dt = datetime.fromisoformat(proc_time)
                    if (datetime.now(timezone.utc) - dt).total_seconds() < 900:
                        continue
                except Exception:
                    continue

            clean_title = clean_title_from_filename(v.name)
            norm_title = normalize_title(clean_title)

            # Deduplication check against already uploaded titles
            if norm_title and norm_title in uploaded_norm_titles:
                self.mark_skipped(v.name, reason=f"Duplicate title with already uploaded video: {clean_title}")
                continue

            # Read and encode base64
            file_bytes = v.read_bytes()
            b64_data = base64.b64encode(file_bytes).decode("ascii")

            caption = self.caption_template.replace("{title}", clean_title)

            # Mark as PROCESSING atomically before returning
            self.ledger["uploads"][v.name] = {
                "status": "PROCESSING",
                "processing_at": datetime.now(timezone.utc).isoformat(),
                "details": {"clean_title": clean_title}
            }
            self._save_ledger()
            if norm_title:
                uploaded_norm_titles.add(norm_title)

            # Calculate schedule time if configured
            uploaded_count = sum(
                1 for r in self.ledger["uploads"].values() if r.get("status") == "UPLOADED"
            )
            schedule_mins = (
                (uploaded_count + 1) * self.schedule_interval_mins
                if self.schedule_interval_mins > 0
                else 0
            )

            return {
                "ok": True,
                "video_id": v.name,
                "file_name": v.name,
                "file_size": len(file_bytes),
                "clean_title": clean_title,
                "caption": caption,
                "schedule_minutes": schedule_mins,
                "file_base64": b64_data,
            }
        return None

    def mark_completed(self, video_id: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Mark video as successfully uploaded in ledger."""
        d = details or {}
        if "clean_title" not in d:
            d["clean_title"] = clean_title_from_filename(video_id)
        self.ledger["uploads"][video_id] = {
            "status": "UPLOADED",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "details": d,
        }
        self._save_ledger()

    def mark_failed(self, video_id: str, error: str) -> None:
        """Mark video as failed with error reason (will be skipped on next poll)."""
        self.ledger["uploads"][video_id] = {
            "status": "FAILED",
            "failed_at": datetime.now(timezone.utc).isoformat(),
            "error": error,
        }
        self._save_ledger()

    def mark_skipped(self, video_id: str, reason: str = "User skipped") -> None:
        """Mark video as skipped."""
        self.ledger["uploads"][video_id] = {
            "status": "SKIPPED",
            "skipped_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
        }
        self._save_ledger()


class AutoUploadRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler supporting CORS for extension RPC."""

    queue: AutoUploadQueue

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def _send_json(self, status_code: int, data: Dict[str, Any]) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/status":
            status = self.queue.get_status()
            self._send_json(200, status)
        elif path == "/api/next":
            item = self.queue.get_next_item()
            if item:
                self._send_json(200, item)
            else:
                self._send_json(200, {"ok": False, "message": "No pending videos left in queue."})
        elif path == "/api/queue":
            videos = self.queue.scan_videos()
            items = []
            for v in videos:
                rec = self.queue.ledger["uploads"].get(v.name, {})
                items.append({
                    "file_name": v.name,
                    "file_size": v.stat().st_size,
                    "status": rec.get("status", "PENDING"),
                    "completed_at": rec.get("completed_at"),
                })
            self._send_json(200, {"ok": True, "items": items})
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        if path == "/api/complete":
            video_id = payload.get("video_id")
            if not video_id:
                self._send_json(400, {"error": "Missing video_id"})
                return
            self.queue.mark_completed(video_id, details=payload.get("details"))
            self._send_json(200, {"ok": True, "message": f"Marked {video_id} as UPLOADED"})
        elif path == "/api/skip":
            video_id = payload.get("video_id")
            if not video_id:
                self._send_json(400, {"error": "Missing video_id"})
                return
            self.queue.mark_skipped(video_id, reason=payload.get("reason", "Skipped via API"))
            self._send_json(200, {"ok": True, "message": f"Marked {video_id} as SKIPPED"})
        elif path == "/api/fail":
            video_id = payload.get("video_id")
            if not video_id:
                self._send_json(400, {"error": "Missing video_id"})
                return
            self.queue.mark_failed(video_id, error=payload.get("error", "Failed via API"))
            self._send_json(200, {"ok": True, "message": f"Marked {video_id} as FAILED"})
        elif path == "/api/sync-posted":
            titles = payload.get("titles", [])
            matched = self.queue.sync_posted_titles(titles)
            self._send_json(200, {"ok": True, "matched": matched, "message": f"Synced {matched} videos as already UPLOADED"})
        elif path == "/api/retry-failed":
            count = self.queue.reset_failed()
            self._send_json(200, {"ok": True, "reset_count": count, "message": f"Reset {count} failed items to pending"})
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy HTTP stdout logs
        return


def run_auto_upload_server(
    video_dir: str = "mutated_videos",
    port: int = 8765,
    host: str = "127.0.0.1",
    caption_template: str = "{title} #fyp #viral #trending",
    schedule_interval_mins: int = 0,
) -> None:
    """Start local ThreadingHTTPServer serving video upload queue."""
    v_dir = Path(video_dir).resolve()
    v_dir.mkdir(parents=True, exist_ok=True)
    queue = AutoUploadQueue(
        video_dir=v_dir,
        caption_template=caption_template,
        schedule_interval_mins=schedule_interval_mins,
    )

    class CustomHandler(AutoUploadRequestHandler):
        pass

    CustomHandler.queue = queue

    server = ThreadingHTTPServer((host, port), CustomHandler)
    status = queue.get_status()
    print(f"\n{'='*65}")
    print(f"🚀 TIKTOK AUTO-UPLOAD ENGINE (LOCAL BRIDGE ACTIVE)")
    print(f"{'='*65}")
    print(f"[*] Endpoint:        http://{host}:{port}/api/status")
    print(f"[*] Video Folder:    {v_dir}")
    print(f"[*] Total Videos:    {status['total_videos']}")
    print(f"[*] Pending Upload:  {status['pending']}")
    print(f"[*] Already Done:    {status['uploaded']}")
    print(f"[*] Next in Queue:   {status['next_file'] or 'None (Queue Empty)'}")
    print(f"{'='*65}")
    print(f"[!] Mở Chrome Extension -> Tab 'Auto-Upload' -> Bấm 'Bắt Đầu Auto Đăng'.")
    print(f"[!] Nhấn Ctrl+C để dừng server.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Auto-Upload server gracefully...")
        server.shutdown()
        server.server_close()
        print("[+] Server stopped.")


if __name__ == "__main__":
    run_auto_upload_server()
