#!/usr/bin/env python3
"""
captcha_farm.py - CAPTCHA solving farm with multi-key pool, rate limiting, and failover.
Manages multiple API keys across multiple services for sustained CAPTCHA throughput.

Usage:
    python scripts/captcha_farm.py --config keys.json --type recaptchav2 --sitekey KEY --url URL
    python scripts/captcha_farm.py --config keys.json --health-check
    python scripts/captcha_farm.py --config keys.json --benchmark --type recaptchav2 --count 10

keys.json format:
    {"2captcha": ["key1","key2"], "capmonster": ["key3"], "anticaptcha": ["key4"]}
"""
import argparse
import json
import os
import random
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse
from datetime import datetime

LOG_FILE = "solve_log.jsonl"


def http_get(url: str, params: dict = None) -> str:
    if params:
        url = f"{url}?{uparse.urlencode(params)}"
    try:
        resp = ureq.urlopen(url, timeout=30)
        return resp.read().decode()
    except Exception as e:
        return f"ERROR:{e}"


def http_post_json(url: str, data: dict) -> dict:
    body = json.dumps(data).encode()
    req = ureq.Request(url, body, {"Content-Type": "application/json"})
    try:
        resp = ureq.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def log_solve(service: str, key_idx: int, captcha_type: str, success: bool,
              elapsed: float, cost_estimate: float, error: str = ""):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service, "key_idx": key_idx,
        "type": captcha_type, "success": success,
        "elapsed_s": round(elapsed, 2), "cost_usd": round(cost_estimate, 5),
        "error": error
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


COST_PER_1000 = {
    "2captcha":   {"recaptchav2": 2.99, "hcaptcha": 2.00, "image": 0.50, "recaptchav3": 2.99},
    "capmonster": {"recaptchav2": 1.20, "hcaptcha": 1.00, "image": 0.40, "recaptchav3": 1.20},
    "anticaptcha":{"recaptchav2": 2.00, "hcaptcha": 1.50, "image": 0.50, "recaptchav3": 2.00},
}


def get_balance_2captcha(key: str) -> float:
    r = http_get("https://2captcha.com/res.php", {"key": key, "action": "getbalance"})
    try:
        return float(r) if "ERROR" not in r else -1
    except:
        return -1


def get_balance_capmonster(key: str) -> float:
    r = http_post_json("https://api.capmonster.cloud/getBalance", {"clientKey": key})
    return r.get("balance", -1)


def health_check(config: dict) -> dict:
    """Check balance and status for all keys."""
    report = {}
    for service, keys in config.items():
        report[service] = []
        for i, key in enumerate(keys):
            if service == "2captcha":
                bal = get_balance_2captcha(key)
            elif service == "capmonster":
                bal = get_balance_capmonster(key)
            else:
                bal = -1  # Not implemented yet
            status = "OK" if bal > 0.1 else ("EMPTY" if bal == 0 else "ERROR")
            report[service].append({"key_idx": i, "balance": round(bal, 4), "status": status})
            print(f"[*] {service} key[{i}]: ${bal:.4f} [{status}]")
    return report


def solve_recaptchav2_2captcha(key: str, sitekey: str, pageurl: str) -> tuple:
    """Returns (token, elapsed_sec) or ("", elapsed)."""
    start = time.time()
    # Submit
    r = http_get("https://2captcha.com/in.php", {
        "key": key, "method": "userrecaptcha", "googlekey": sitekey,
        "pageurl": pageurl, "json": 1
    })
    try:
        data = json.loads(r)
    except:
        return "", time.time() - start
    if data.get("status") != 1:
        return "", time.time() - start
    task_id = data["request"]
    # Poll
    for _ in range(30):
        time.sleep(5)
        res_raw = http_get("https://2captcha.com/res.php", {"key": key, "action": "get", "id": task_id, "json": 1})
        try:
            res = json.loads(res_raw)
        except:
            continue
        if res.get("status") == 1:
            return res["request"], time.time() - start
        if res.get("request") not in ("CAPCHA_NOT_READY", None):
            break
    return "", time.time() - start


def farm_solve(config: dict, captcha_type: str, sitekey: str, pageurl: str) -> dict:
    """Try keys in priority order, failover on error."""
    SERVICE_ORDER = ["capmonster", "2captcha", "anticaptcha"]
    for service in SERVICE_ORDER:
        keys = config.get(service, [])
        if not keys:
            continue
        key = random.choice(keys)  # Random key from pool
        key_idx = config[service].index(key)
        cost = COST_PER_1000.get(service, {}).get(captcha_type, 2.0) / 1000

        print(f"[*] Trying {service} key[{key_idx}] for {captcha_type}...")
        start = time.time()

        if captcha_type == "recaptchav2" and service == "2captcha":
            token, elapsed = solve_recaptchav2_2captcha(key, sitekey, pageurl)
        else:
            # Placeholder: capmonster and others would use task-based API
            time.sleep(15)  # Simulated solve time
            token, elapsed = "", time.time() - start

        success = bool(token)
        entry = log_solve(service, key_idx, captcha_type, success, elapsed, cost)

        if success:
            print(f"[+] Solved via {service} in {elapsed:.1f}s (${cost:.5f})")
            return {"token": token, **entry}
        else:
            print(f"[-] {service} failed, trying next...")

    return {"token": "", "success": False, "error": "all services failed"}


def benchmark(config: dict, captcha_type: str, count: int, sitekey: str = "test", pageurl: str = "http://test.com"):
    """Run N solves and report stats."""
    print(f"[*] Benchmark: {count}x {captcha_type}")
    results = []
    for i in range(count):
        print(f"\n[{i+1}/{count}] Solving...")
        r = farm_solve(config, captcha_type, sitekey, pageurl)
        results.append(r)
    success = [r for r in results if r.get("success")]
    total_cost = sum(r.get("cost_usd", 0) for r in results)
    avg_time = sum(r.get("elapsed_s", 0) for r in results) / count
    print(f"\n[*] Benchmark Results:")
    print(f"  Success rate : {len(success)}/{count} ({100*len(success)//count}%)")
    print(f"  Total cost   : ${total_cost:.4f}")
    print(f"  Avg time     : {avg_time:.1f}s/solve")
    print(f"  Est. $/1000  : ${total_cost/count*1000:.2f}")


def main():
    p = argparse.ArgumentParser(description="CAPTCHA farm manager")
    p.add_argument("--config", required=True, help="API keys JSON file")
    p.add_argument("--type", choices=["recaptchav2","recaptchav3","hcaptcha","turnstile","image"], default="recaptchav2")
    p.add_argument("--sitekey", help="Site key for reCAPTCHA/hCaptcha")
    p.add_argument("--url", help="Target page URL")
    p.add_argument("--health-check", action="store_true")
    p.add_argument("--benchmark", action="store_true")
    p.add_argument("--count", type=int, default=5)
    p.add_argument("--output", help="Output token to file")
    args = p.parse_args()

    if not os.path.exists(args.config):
        print(f"[-] Config not found: {args.config}"); sys.exit(1)

    with open(args.config) as f:
        config = json.load(f)

    if args.health_check:
        health_check(config)
    elif args.benchmark:
        benchmark(config, args.type, args.count, args.sitekey or "test", args.url or "http://test.com")
    else:
        if not args.sitekey or not args.url:
            print("[-] --sitekey and --url required"); sys.exit(1)
        result = farm_solve(config, args.type, args.sitekey, args.url)
        if result.get("token"):
            print(f"\n[RESULT] token={result['token'][:50]}...")
            if args.output:
                open(args.output, "w").write(result["token"])


if __name__ == "__main__":
    main()
