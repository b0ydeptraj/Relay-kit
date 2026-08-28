#!/usr/bin/env python3
"""Scythe - Deterministic Anti-Yap, Zero-Fluff & Code Hygiene Scanner for Relay-kit."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple

YAP_PATTERNS = [
    re.compile(r"//\s*(khởi tạo|khoi tao|init|initialize|declare)\s+[a-zA-Z0-9_$]+", re.IGNORECASE),
    re.compile(r"//\s*(trả về|tra ve|return|returns)\s+(true|false|null|undefined|[a-zA-Z0-9_$]+)", re.IGNORECASE),
    re.compile(r"//\s*(gọi hàm|goi ham|call|calls)\s+[a-zA-Z0-9_$]+", re.IGNORECASE),
    re.compile(r"//\s*(kết thúc|ket thuc|end of)\s+[a-zA-Z0-9_$]+", re.IGNORECASE),
    re.compile(r"//\s*(TODO|FIXME)\s*$", re.IGNORECASE),
]

OVERSIZE_COMMENT_LIMIT = 120

class Finding(NamedTuple):
    file: Path
    line: int
    kind: str
    message: str

def scan_file(file_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        for pattern in YAP_PATTERNS:
            if pattern.search(stripped):
                findings.append(Finding(file_path, idx, "YAP", f"Trivial/obvious comment detected: '{stripped}'"))
                break

        if (stripped.startswith("//") or stripped.startswith("#")) and len(stripped) > OVERSIZE_COMMENT_LIMIT:
            findings.append(Finding(file_path, idx, "WRAP", f"Comment exceeds {OVERSIZE_COMMENT_LIMIT} characters without wrap: '{stripped[:40]}...'"))

    return findings

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scythe Anti-Yap & Code Hygiene Scanner")
    parser.add_argument("paths", nargs="*", default=["."], help="Directories or files to scan")
    parser.add_argument("--strict", action="store_true", help="Fail with exit code 1 if findings are detected")
    args = parser.parse_args(argv)

    all_findings: list[Finding] = []
    extensions = {".ts", ".tsx", ".js", ".jsx", ".py", ".cpp", ".h", ".hpp", ".go", ".rs"}

    for p in args.paths:
        path = Path(p).resolve()
        if path.is_file() and path.suffix in extensions:
            all_findings.extend(scan_file(path))
        elif path.is_dir():
            for f in path.rglob("*"):
                if f.is_file() and f.suffix in extensions:
                    # skip node_modules, dist, build, .git
                    if any(part in f.parts for part in {"node_modules", "dist", "build", ".git", ".next", ".tmp"}):
                        continue
                    all_findings.extend(scan_file(f))

    print(f"Scythe Anti-Yap Scan: {len(all_findings)} finding(s)")
    for f in all_findings:
        print(f"  [{f.kind}] {f.file}:{f.line} -> {f.message}")

    if args.strict and all_findings:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
