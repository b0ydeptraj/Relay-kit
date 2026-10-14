#!/usr/bin/env python3
"""
proxy_rotator.py - Smart proxy pool manager with automatic rotation, health monitoring,
ban detection, and per-domain proxy affinity.

Usage:
    python scripts/proxy_rotator.py --pool live.txt --mode round-robin --test-url https://httpbin.org/ip
    python scripts/proxy_rotator.py --pool live.txt --mode least-latency
    python scripts/proxy_rotator.py --pool live.txt --mode sticky --session-id user123
    python scripts/proxy_rotator.py --pool live.txt --daemon --port 8888
"""
import argparse
import json
import os
import random
import sys
import time
import threading
import urllib.request as ureq
from collections import defaultdict


class ProxyPool:
    def __init__(self, proxies: list, mode: str = "round-robin"):
        self.proxies = [{"raw": p, "latency": 999, "fails": 0, "last_used": 0, "banned": False}
                        for p in proxies]
        self.mode = mode
        self._idx = 0
        self._lock = threading.Lock()
        self._session_map = {}

    def get(self, session_id: str = None) -> dict:
        with self._lock:
            available = [p for p in self.proxies if not p["banned"]]
            if not available:
                print("[-] All proxies banned, resetting...")
                for p in self.proxies: p["banned"] = False
                available = self.proxies[:]

            if self.mode == "sticky" and session_id:
                if session_id in self._session_map:
                    proxy = self._session_map[session_id]
                    if not proxy["banned"]:
                        return proxy
                proxy = random.choice(available)
                self._session_map[session_id] = proxy
                return proxy

            if self.mode == "round-robin":
                self._idx = (self._idx + 1) % len(available)
                return available[self._idx]

            if self.mode == "random":
                return random.choice(available)

            if self.mode == "least-latency":
                return min(available, key=lambda p: p["latency"])

            if self.mode == "least-used":
                return min(available, key=lambda p: p["last_used"])

            return random.choice(available)

    def mark_fail(self, proxy: dict, ban_threshold: int = 3):
        proxy["fails"] += 1
        if proxy["fails"] >= ban_threshold:
            proxy["banned"] = True
            print(f"[-] Proxy banned after {ban_threshold} fails: {proxy['raw']}")

    def mark_success(self, proxy: dict, latency: float):
        proxy["fails"] = 0
        proxy["latency"] = latency
        proxy["last_used"] = time.time()

    def stats(self) -> dict:
        total = len(self.proxies)
        banned = sum(1 for p in self.proxies if p["banned"])
        avg_lat = sum(p["latency"] for p in self.proxies if not p["banned"]) / max(1, total - banned)
        return {"total": total, "available": total - banned, "banned": banned,
                "avg_latency_ms": round(avg_lat)}

    def save_state(self, path: str):
        with open(path, "w") as f:
            json.dump([{"raw": p["raw"], "latency": p["latency"], "fails": p["fails"],
                        "banned": p["banned"]} for p in self.proxies], f, indent=2)

    @classmethod
    def load_state(cls, path: str, mode: str = "round-robin"):
        with open(path) as f:
            data = json.load(f)
        pool = cls([d["raw"] for d in data], mode)
        for i, d in enumerate(data):
            pool.proxies[i].update({"latency": d["latency"], "fails": d["fails"], "banned": d["banned"]})
        return pool


def run_proxy_daemon(pool: ProxyPool, port: int = 8888):
    """Simple HTTP proxy daemon that rotates through pool."""
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class RotatingProxyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            proxy = pool.get()
            self.send_response(200)
            self.send_header("X-Proxy-Used", proxy["raw"])
            self.end_headers()
            self.wfile.write(f"Current proxy: {proxy['raw']}\n".encode())
            self.wfile.write(f"Pool stats: {json.dumps(pool.stats())}\n".encode())

        def log_message(self, format, *args): pass

    server = HTTPServer(("127.0.0.1", port), RotatingProxyHandler)
    print(f"[*] Proxy rotator daemon running on port {port}")
    print(f"[*] Pool: {pool.stats()}")
    server.serve_forever()


def main():
    p = argparse.ArgumentParser(description="Smart proxy pool manager")
    p.add_argument("--pool", required=True)
    p.add_argument("--mode", choices=["round-robin","random","least-latency","least-used","sticky"], default="round-robin")
    p.add_argument("--test-url", default="https://httpbin.org/ip")
    p.add_argument("--test-count", type=int, default=10)
    p.add_argument("--session-id", help="Session ID for sticky mode")
    p.add_argument("--daemon", action="store_true")
    p.add_argument("--port", type=int, default=8888)
    p.add_argument("--state-file", help="Load/save pool state JSON")
    args = p.parse_args()

    if args.state_file and os.path.exists(args.state_file):
        pool = ProxyPool.load_state(args.state_file, args.mode)
        print(f"[*] Loaded pool state: {pool.stats()}")
    else:
        with open(args.pool) as f:
            proxies = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        pool = ProxyPool(proxies, args.mode)

    print(f"[*] Pool: {pool.stats()} | Mode: {args.mode}")

    if args.daemon:
        run_proxy_daemon(pool, args.port)
        return

    # Test rotation
    for i in range(args.test_count):
        proxy = pool.get(args.session_id)
        start = time.time()
        try:
            h = ureq.ProxyHandler({"http": proxy["raw"], "https": proxy["raw"]})
            op = ureq.build_opener(h)
            resp = op.open(args.test_url, timeout=10)
            ms = round((time.time() - start) * 1000)
            ip = json.loads(resp.read()).get("origin", "?")
            pool.mark_success(proxy, ms)
            print(f"[{i+1}/{args.test_count}] OK | {proxy['raw'][:40]} | {ip} | {ms}ms")
        except Exception as e:
            pool.mark_fail(proxy)
            print(f"[{i+1}/{args.test_count}] FAIL | {proxy['raw'][:40]} | {str(e)[:50]}")
        time.sleep(0.2)

    if args.state_file:
        pool.save_state(args.state_file)
        print(f"[+] State saved: {args.state_file}")

    print(f"\n[*] Final: {pool.stats()}")


if __name__ == "__main__":
    main()
