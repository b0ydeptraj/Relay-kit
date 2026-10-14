#!/usr/bin/env python3
"""
captcha_solver_api.py - CAPTCHA solving via 2captcha / CapMonster / AntiCaptcha APIs.
Unified interface for reCAPTCHA v2/v3, hCaptcha, Turnstile, image CAPTCHA.

Usage:
    python scripts/captcha_solver_api.py --service 2captcha --type recaptchav2 --sitekey KEY --url URL
    python scripts/captcha_solver_api.py --service capmonster --type hcaptcha --sitekey KEY --url URL
    python scripts/captcha_solver_api.py --service 2captcha --type image --image captcha.png
    python scripts/captcha_solver_api.py --check-balance --service 2captcha

Set API key: CAPTCHA_API_KEY env var.
"""
import argparse
import base64
import json
import os
import sys
import time
try:
    import urllib.request as ureq
    import urllib.parse as uparse
    import urllib.error as uerr
except ImportError:
    pass

API_KEY = os.environ.get("CAPTCHA_API_KEY", "")

ENDPOINTS = {
    "2captcha":   {"in": "https://2captcha.com/in.php",   "res": "https://2captcha.com/res.php"},
    "capmonster": {"in": "https://api.capmonster.cloud/createTask", "res": "https://api.capmonster.cloud/getTaskResult"},
    "anticaptcha":{"in": "https://api.anti-captcha.com/createTask","res": "https://api.anti-captcha.com/getTaskResult"},
}


def http_post(url: str, data: dict) -> dict:
    body = json.dumps(data).encode()
    req = ureq.Request(url, body, {"Content-Type": "application/json"})
    resp = ureq.urlopen(req, timeout=30)
    return json.loads(resp.read())


def http_get(url: str, params: dict) -> str:
    query = uparse.urlencode(params)
    resp = ureq.urlopen(f"{url}?{query}", timeout=30)
    return resp.read().decode()


def check_balance(service: str, api_key: str = None):
    key = api_key or API_KEY
    if not key: print("[-] Set CAPTCHA_API_KEY env var"); sys.exit(1)
    if service == "2captcha":
        result = http_get(ENDPOINTS["2captcha"]["res"], {"key": key, "action": "getbalance"})
        print(f"[*] 2captcha balance: ${result}")
    elif service == "capmonster":
        data = {"clientKey": key}
        result = http_post("https://api.capmonster.cloud/getBalance", data)
        print(f"[*] CapMonster balance: ${result.get('balance', 'unknown')}")
    elif service == "anticaptcha":
        data = {"clientKey": key}
        result = http_post("https://api.anti-captcha.com/getBalance", data)
        print(f"[*] AntiCaptcha balance: ${result.get('balance', 'unknown')}")


def solve_recaptchav2(service: str, sitekey: str, page_url: str, api_key: str = None, invisible: bool = False) -> str:
    key = api_key or API_KEY
    if not key: print("[-] Set CAPTCHA_API_KEY"); sys.exit(1)
    print(f"[*] Solving reCAPTCHA v2 via {service}...")

    if service == "2captcha":
        # Submit task
        params = {"key": key, "method": "userrecaptcha", "googlekey": sitekey,
                  "pageurl": page_url, "json": 1, "invisible": 1 if invisible else 0}
        resp = http_get(ENDPOINTS["2captcha"]["in"], params)
        data = json.loads(resp)
        if data.get("status") != 1:
            print(f"[-] Submit failed: {data}"); return ""
        task_id = data["request"]
        print(f"[*] Task ID: {task_id}, waiting...")

        for attempt in range(30):
            time.sleep(5)
            res = http_get(ENDPOINTS["2captcha"]["res"], {"key": key, "action": "get", "id": task_id, "json": 1})
            res_data = json.loads(res)
            if res_data.get("status") == 1:
                token = res_data["request"]
                print(f"[+] Token obtained ({len(token)} chars)")
                return token
            elif res_data.get("request") != "CAPCHA_NOT_READY":
                print(f"[-] Error: {res_data}"); return ""
        print("[-] Timeout"); return ""

    elif service == "capmonster":
        task = {"type": "NoCaptchaTaskProxyless" if not invisible else "NoCaptchaTask",
                "websiteURL": page_url, "websiteKey": sitekey}
        resp = http_post(ENDPOINTS["capmonster"]["in"], {"clientKey": key, "task": task})
        if resp.get("errorId"): print(f"[-] {resp}"); return ""
        task_id = resp["taskId"]
        for _ in range(30):
            time.sleep(5)
            res = http_post(ENDPOINTS["capmonster"]["res"], {"clientKey": key, "taskId": task_id})
            if res.get("status") == "ready":
                token = res["solution"]["gRecaptchaResponse"]
                print(f"[+] Token: {token[:30]}...")
                return token
        return ""

    return ""


def solve_image_captcha(service: str, image_path: str, api_key: str = None) -> str:
    key = api_key or API_KEY
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    if service == "2captcha":
        resp = http_get(ENDPOINTS["2captcha"]["in"],
                        {"key": key, "method": "base64", "body": img_b64, "json": 1})
        data = json.loads(resp)
        if data.get("status") != 1: return ""
        task_id = data["request"]
        for _ in range(20):
            time.sleep(3)
            res = http_get(ENDPOINTS["2captcha"]["res"], {"key": key, "action": "get", "id": task_id, "json": 1})
            res_data = json.loads(res)
            if res_data.get("status") == 1:
                print(f"[+] Image CAPTCHA solved: {res_data['request']}")
                return res_data["request"]
    return ""


def main():
    p = argparse.ArgumentParser(description="CAPTCHA solver API wrapper")
    p.add_argument("--service", choices=["2captcha","capmonster","anticaptcha"], default="2captcha")
    p.add_argument("--type", choices=["recaptchav2","recaptchav3","hcaptcha","turnstile","image"])
    p.add_argument("--sitekey")
    p.add_argument("--url")
    p.add_argument("--image")
    p.add_argument("--api-key")
    p.add_argument("--check-balance", action="store_true")
    args = p.parse_args()

    if args.check_balance:
        check_balance(args.service, args.api_key); return

    if not args.type: print("[-] --type required"); sys.exit(1)

    if args.type == "recaptchav2":
        token = solve_recaptchav2(args.service, args.sitekey, args.url, args.api_key)
        if token: print(f"\n[RESULT] g-recaptcha-response={token}")
    elif args.type == "image":
        if not args.image: print("[-] --image required"); sys.exit(1)
        result = solve_image_captcha(args.service, args.image, args.api_key)
        if result: print(f"\n[RESULT] {result}")
    else:
        print(f"[-] {args.type} not yet implemented (contribute welcome)")


if __name__ == "__main__":
    main()
