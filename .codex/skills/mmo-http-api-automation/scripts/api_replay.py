#!/usr/bin/env python3
"""
api_replay.py - HTTP API request automation engine with session management,
rate limiting, cookie handling, and request replay from Burp/HTTP captures.

Usage:
    python scripts/api_replay.py --har request.har --repeat 100 --delay 1
    python scripts/api_replay.py --curl "curl 'https://api.example.com/...'" --repeat 50
    python scripts/api_replay.py --url URL --method POST --body '{"key":"val"}' --headers h.json
    python scripts/api_replay.py --url URL --threads 5 --count 200 --proxy proxies.txt
"""
import argparse
import json
import os
import random
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse
import urllib.error
import concurrent.futures
import re
import http.cookiejar

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/125.0.0.0 Mobile Safari/537.36",
]


def make_request(url: str, method: str = "GET", headers: dict = None,
                 body: bytes = None, proxy: str = None, cookies: dict = None,
                 timeout: int = 30) -> dict:
    h = {"User-Agent": random.choice(USER_AGENTS)}
    if headers:
        h.update(headers)
    if cookies:
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        h["Cookie"] = cookie_str

    req = ureq.Request(url, data=body if method != "GET" else None, headers=h, method=method)
    handler_list = [ureq.HTTPCookieProcessor()]
    if proxy:
        handler_list.append(ureq.ProxyHandler({"http": proxy, "https": proxy}))
    opener = ureq.build_opener(*handler_list)

    start = time.time()
    try:
        resp = opener.open(req, timeout=timeout)
        elapsed = round((time.time() - start) * 1000)
        content = resp.read()
        return {"status": resp.status, "elapsed_ms": elapsed,
                "headers": dict(resp.headers), "body_len": len(content),
                "body_preview": content[:200].decode("utf-8", errors="replace"),
                "success": 200 <= resp.status < 300}
    except urllib.error.HTTPError as e:
        elapsed = round((time.time() - start) * 1000)
        return {"status": e.code, "elapsed_ms": elapsed, "success": False, "error": str(e)}
    except Exception as e:
        return {"status": 0, "elapsed_ms": 0, "success": False, "error": str(e)[:100]}


def parse_curl(curl_cmd: str) -> dict:
    """Parse a curl command into request components."""
    url_match = re.search(r"curl\s+['\"]?(https?://[^\s'\"]+)['\"]?", curl_cmd)
    url = url_match.group(1) if url_match else ""
    method = "POST" if "-d " in curl_cmd or "--data" in curl_cmd else "GET"
    if "-X " in curl_cmd:
        m = re.search(r"-X\s+(\w+)", curl_cmd)
        if m: method = m.group(1)
    headers = {}
    for hm in re.finditer(r"-H\s+['\"]([^'\"]+)['\"]", curl_cmd):
        k, _, v = hm.group(1).partition(": ")
        headers[k] = v
    body = None
    dm = re.search(r"(?:-d|--data)\s+['\"]([^'\"]+)['\"]", curl_cmd)
    if dm:
        body = dm.group(1).encode()
    return {"url": url, "method": method, "headers": headers, "body": body}


def load_har(har_file: str) -> list:
    """Load requests from a HAR file."""
    with open(har_file) as f:
        har = json.load(f)
    requests = []
    for entry in har.get("log", {}).get("entries", []):
        req = entry.get("request", {})
        url = req.get("url", "")
        method = req.get("method", "GET")
        headers = {h["name"]: h["value"] for h in req.get("headers", [])
                   if h["name"].lower() not in ("host", "content-length")}
        body = None
        if req.get("postData", {}).get("text"):
            body = req["postData"]["text"].encode()
        requests.append({"url": url, "method": method, "headers": headers, "body": body})
    return requests


def replay_bulk(url: str, method: str, headers: dict, body: bytes,
                proxies: list, count: int, threads: int, delay: float) -> list:
    results = []
    lock = __import__("threading").Lock()

    def worker(_):
        proxy = random.choice(proxies) if proxies else None
        r = make_request(url, method, headers, body, proxy)
        with lock:
            results.append(r)
            ok = len([x for x in results if x["success"]])
            print(f"  [{len(results)}/{count}] {r['status']} | {r['elapsed_ms']}ms | OK={ok}", end="\r")
        time.sleep(delay + random.uniform(0, delay * 0.3))

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        ex.map(worker, range(count))
    print()
    return results


def main():
    p = argparse.ArgumentParser(description="HTTP API automation and replay engine")
    p.add_argument("--url", help="Target URL")
    p.add_argument("--method", default="GET")
    p.add_argument("--body", help="Request body (JSON string or @file.json)")
    p.add_argument("--headers", help="Headers JSON file")
    p.add_argument("--curl", help="Curl command to parse and replay")
    p.add_argument("--har", help="HAR file to replay")
    p.add_argument("--repeat", "--count", type=int, default=1, dest="count")
    p.add_argument("--threads", type=int, default=1)
    p.add_argument("--delay", type=float, default=1.0)
    p.add_argument("--proxy", "--proxy-file", dest="proxy_file")
    p.add_argument("--output", help="Save results JSON")
    args = p.parse_args()

    proxies = []
    if args.proxy_file and os.path.exists(args.proxy_file):
        with open(args.proxy_file) as f:
            proxies = [l.strip() for l in f if l.strip()]

    # Build request
    if args.curl:
        req = parse_curl(args.curl)
        url, method, headers, body = req["url"], req["method"], req["headers"], req["body"]
    elif args.har:
        requests = load_har(args.har)
        print(f"[*] Loaded {len(requests)} requests from HAR")
        req = requests[0]  # Use first request
        url, method, headers, body = req["url"], req["method"], req["headers"], req["body"]
    elif args.url:
        url = args.url
        method = args.method.upper()
        headers = {}
        if args.headers:
            with open(args.headers) as f:
                headers = json.load(f)
        body = None
        if args.body:
            if args.body.startswith("@"):
                body = open(args.body[1:], "rb").read()
            else:
                body = args.body.encode()
    else:
        print("[-] --url, --curl, or --har required"); sys.exit(1)

    print(f"[*] Target: {method} {url[:80]}")
    print(f"[*] Repeats: {args.count} | Threads: {args.threads} | Delay: {args.delay}s")

    results = replay_bulk(url, method, headers, body, proxies, args.count, args.threads, args.delay)
    ok = sum(1 for r in results if r["success"])
    avg_ms = sum(r["elapsed_ms"] for r in results) / len(results) if results else 0
    print(f"\n[*] Done: {ok}/{len(results)} success | avg {avg_ms:.0f}ms")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"[+] Saved: {args.output}")


if __name__ == "__main__":
    main()
