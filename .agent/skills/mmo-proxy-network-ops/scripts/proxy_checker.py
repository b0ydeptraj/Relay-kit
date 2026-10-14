#!/usr/bin/env python3
"""
proxy_checker.py - Bulk proxy health checker with speed test and geo lookup.
Checks HTTP/HTTPS/SOCKS4/SOCKS5 proxies, measures latency, detects anonymity level.

Usage:
    python scripts/proxy_checker.py --input proxies.txt --output live.txt
    python scripts/proxy_checker.py --input proxies.txt --threads 50 --timeout 10
    python scripts/proxy_checker.py --input proxies.txt --filter-country US,VN
    python scripts/proxy_checker.py --rotate --input live.txt --target https://httpbin.org/ip

proxies.txt format: one per line, supports:
    http://ip:port
    socks5://user:pass@ip:port
    ip:port (defaults to http)
"""
import argparse
import concurrent.futures
import json
import os
import socket
import sys
import time
import urllib.request as ureq
import urllib.error as uerr
from typing import Optional

CHECK_URL   = "https://httpbin.org/ip"
GEO_URL     = "https://ipapi.co/{ip}/json/"
TIMEOUT_DEFAULT = 10
MAX_THREADS = 100


def parse_proxy(line: str) -> Optional[dict]:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    scheme = "http"
    if "://" in line:
        scheme, rest = line.split("://", 1)
    else:
        rest = line
    auth = None
    if "@" in rest:
        auth_part, host_part = rest.rsplit("@", 1)
        user, password = auth_part.split(":", 1) if ":" in auth_part else (auth_part, "")
        auth = {"user": user, "pass": password}
    else:
        host_part = rest
    if ":" in host_part:
        host, port_str = host_part.rsplit(":", 1)
        try:
            port = int(port_str)
        except ValueError:
            return None
    else:
        return None
    return {"scheme": scheme, "host": host, "port": port, "auth": auth, "raw": line}


def build_proxy_handler(proxy: dict):
    scheme = proxy["scheme"]
    if proxy["auth"]:
        u, p = proxy["auth"]["user"], proxy["auth"]["pass"]
        proxy_url = f"{scheme}://{u}:{p}@{proxy['host']}:{proxy['port']}"
    else:
        proxy_url = f"{scheme}://{proxy['host']}:{proxy['port']}"
    return ureq.ProxyHandler({scheme: proxy_url, "https": proxy_url})


def check_proxy(proxy: dict, timeout: int = TIMEOUT_DEFAULT, check_url: str = CHECK_URL) -> dict:
    result = proxy.copy()
    result.update({"alive": False, "latency_ms": None, "ip": None, "country": None, "anonymity": None})
    try:
        handler = build_proxy_handler(proxy)
        opener = ureq.build_opener(handler)
        start = time.time()
        resp = opener.open(check_url, timeout=timeout)
        elapsed = round((time.time() - start) * 1000)
        data = json.loads(resp.read())
        result["alive"] = True
        result["latency_ms"] = elapsed
        result["ip"] = data.get("origin", "").split(",")[0].strip()
        result["anonymity"] = "elite" if result["ip"] != proxy["host"] else "transparent"
    except Exception as e:
        result["error"] = str(e)[:80]
    return result


def geo_lookup(ip: str) -> dict:
    try:
        resp = ureq.urlopen(GEO_URL.format(ip=ip), timeout=5)
        data = json.loads(resp.read())
        return {"country": data.get("country_code"), "country_name": data.get("country_name"),
                "city": data.get("city"), "org": data.get("org")}
    except:
        return {}


def check_all(proxies: list, threads: int = 50, timeout: int = TIMEOUT_DEFAULT,
              country_filter: list = None) -> list:
    results = []
    alive = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(threads, MAX_THREADS)) as ex:
        futures = {ex.submit(check_proxy, p, timeout): p for p in proxies}
        done = 0
        for future in concurrent.futures.as_completed(futures):
            done += 1
            r = future.result()
            if r["alive"]:
                alive += 1
                if r.get("ip") and not r.get("country"):
                    geo = geo_lookup(r["ip"])
                    r.update(geo)
                if country_filter and r.get("country") not in country_filter:
                    continue
                results.append(r)
                print(f"[{done}/{len(proxies)}] ALIVE {r['latency_ms']}ms | {r['scheme']}://{r['host']}:{r['port']} | {r.get('country','?')} | {r.get('anonymity','?')}")
            else:
                if done % 50 == 0:
                    print(f"[{done}/{len(proxies)}] checked, {alive} alive...")
    print(f"\n[*] Results: {alive}/{len(proxies)} alive")
    return results


def rotate_proxy(proxies: list, target_url: str, count: int = 5):
    """Test rotating through proxy pool for a target URL."""
    import random
    alive = [p for p in proxies if p.get("alive", True)]
    for i in range(count):
        proxy = random.choice(alive)
        result = check_proxy(proxy, check_url=target_url)
        ip = result.get("ip", "unknown")
        ms = result.get("latency_ms", "?")
        status = "OK" if result["alive"] else "FAIL"
        print(f"[{i+1}/{count}] [{status}] via {proxy['host']}:{proxy['port']} -> {ip} ({ms}ms)")
        time.sleep(0.5)


def main():
    p = argparse.ArgumentParser(description="Bulk proxy checker and rotator")
    p.add_argument("--input", required=True)
    p.add_argument("--output", help="Save live proxies")
    p.add_argument("--threads", type=int, default=50)
    p.add_argument("--timeout", type=int, default=10)
    p.add_argument("--filter-country", help="Comma-separated country codes: US,VN,DE")
    p.add_argument("--rotate", action="store_true")
    p.add_argument("--target", default="https://httpbin.org/ip")
    p.add_argument("--count", type=int, default=5)
    args = p.parse_args()

    with open(args.input) as f:
        raw = f.readlines()
    proxies = [parse_proxy(l) for l in raw]
    proxies = [p for p in proxies if p]
    print(f"[*] Loaded {len(proxies)} proxies from {args.input}")

    country_filter = [c.strip().upper() for c in args.filter_country.split(",")] if args.filter_country else None

    if args.rotate:
        rotate_proxy(proxies, args.target, args.count)
        return

    results = check_all(proxies, args.threads, args.timeout, country_filter)

    if args.output:
        with open(args.output, "w") as f:
            for r in results:
                f.write(r["raw"] + "\n")
        with open(args.output.replace(".txt", "_detail.json"), "w") as f:
            json.dump(results, f, indent=2)
        print(f"[+] Saved {len(results)} live proxies to {args.output}")


if __name__ == "__main__":
    main()
