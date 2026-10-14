#!/usr/bin/env python3
"""
sms_otp.py - SMS OTP automation via 5sim, sms-activate, smspva APIs.
Rent virtual numbers, wait for OTP, extract code automatically.

Usage:
    python scripts/sms_otp.py --service 5sim --platform tiktok --country any
    python scripts/sms_otp.py --service smsactivate --platform google --country russia
    python scripts/sms_otp.py --check-balance --service 5sim
    python scripts/sms_otp.py --service 5sim --platform tiktok --count 5  (bulk mode)

API key: SMSAPI_KEY env var.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse

API_KEY = os.environ.get("SMSAPI_KEY", "")

# OTP extraction patterns by platform
OTP_PATTERNS = {
    "tiktok":    [r"Your TikTok code is[:\s]+(\d{6})", r"(\d{6}) is your TikTok code"],
    "facebook":  [r"(\d{5,8}) is your Facebook", r"FB-(\d{5,8})"],
    "google":    [r"G-(\d{6})", r"(\d{6}) is your Google"],
    "instagram": [r"(\d{6}) is your Instagram", r"Instagram.*?(\d{6})"],
    "telegram":  [r"Telegram code (\d{5,6})", r"Login code:\s*(\d+)"],
    "twitter":   [r"(\d{6}) is your Twitter", r"Twitter confirmation code: (\d+)"],
    "amazon":    [r"(\d{6}) is your Amazon OTP", r"Amazon.*?(\d{6})"],
    "generic":   [r"\b(\d{4,8})\b"],
}

# Platform codes for services
PLATFORM_CODES = {
    "5sim": {
        "tiktok": "tiktok", "facebook": "facebook", "google": "google",
        "instagram": "instagram", "telegram": "telegram", "twitter": "twitter",
        "amazon": "amazon",
    },
    "smsactivate": {
        "tiktok": "tt", "facebook": "fb", "google": "go",
        "instagram": "ig", "telegram": "tg", "twitter": "tw",
        "amazon": "am",
    }
}

COUNTRY_CODES_5SIM = {
    "any": "any", "russia": "russia", "usa": "usa", "ukraine": "ukraine",
    "indonesia": "indonesia", "vietnam": "vietnam", "philippines": "philippines",
    "india": "india", "thailand": "thailand",
}


def http_get(url: str, headers: dict = None) -> dict:
    req = ureq.Request(url, headers=headers or {})
    try:
        resp = ureq.urlopen(req, timeout=30)
        content = resp.read().decode()
        try:
            return json.loads(content)
        except:
            return {"raw": content}
    except Exception as e:
        return {"error": str(e)}


def http_post(url: str, data: dict, headers: dict = None) -> dict:
    body = json.dumps(data).encode()
    h = {"Content-Type": "application/json"}
    if headers: h.update(headers)
    req = ureq.Request(url, body, h)
    try:
        resp = ureq.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


class FiveSimAPI:
    BASE = "https://5sim.net/v1"

    def __init__(self, key: str):
        self.headers = {"Authorization": f"Bearer {key}", "Accept": "application/json"}

    def balance(self) -> float:
        r = http_get(f"{self.BASE}/user/profile", self.headers)
        return r.get("balance", 0)

    def buy_number(self, platform: str, operator: str = "any", country: str = "any") -> dict:
        url = f"{self.BASE}/user/buy/activation/{country}/{operator}/{platform}"
        return http_get(url, self.headers)

    def get_sms(self, order_id: int) -> dict:
        return http_get(f"{self.BASE}/user/check/{order_id}", self.headers)

    def finish_order(self, order_id: int):
        return http_get(f"{self.BASE}/user/finish/{order_id}", self.headers)

    def cancel_order(self, order_id: int):
        return http_get(f"{self.BASE}/user/cancel/{order_id}", self.headers)


def extract_otp(sms_text: str, platform: str) -> str:
    patterns = OTP_PATTERNS.get(platform, OTP_PATTERNS["generic"])
    for pattern in patterns:
        match = re.search(pattern, sms_text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def receive_otp_5sim(api: FiveSimAPI, platform: str, country: str = "any",
                      timeout: int = 180, poll_interval: int = 5) -> dict:
    """Rent number, wait for OTP, return result."""
    platform_code = PLATFORM_CODES["5sim"].get(platform, platform)
    country_code = COUNTRY_CODES_5SIM.get(country, country)

    print(f"[*] Renting number: platform={platform_code} country={country_code}")
    order = api.buy_number(platform_code, country=country_code)
    if "error" in order or not order.get("id"):
        print(f"[-] Number rental failed: {order}")
        return {"success": False, "error": str(order)}

    order_id = order["id"]
    phone = order.get("phone", "unknown")
    print(f"[+] Number: {phone} (order: {order_id})")

    start = time.time()
    otp = ""
    while time.time() - start < timeout:
        time.sleep(poll_interval)
        sms_data = api.get_sms(order_id)
        sms_list = sms_data.get("sms", [])
        if sms_list:
            for sms in sms_list:
                text = sms.get("text", "")
                otp = extract_otp(text, platform)
                if otp:
                    print(f"[+] OTP received: {otp} (from: '{text[:60]}')")
                    api.finish_order(order_id)
                    elapsed = round(time.time() - start, 1)
                    return {"success": True, "phone": phone, "otp": otp, "elapsed": elapsed,
                            "sms_text": text, "order_id": order_id}
        elapsed = round(time.time() - start)
        print(f"[*] Waiting... {elapsed}s/{timeout}s")

    api.cancel_order(order_id)
    print(f"[-] Timeout: no OTP received for {phone}")
    return {"success": False, "phone": phone, "error": "timeout", "order_id": order_id}


def bulk_receive(api: FiveSimAPI, platform: str, country: str, count: int):
    """Receive multiple OTPs sequentially."""
    results = []
    for i in range(count):
        print(f"\n[*] === OTP {i+1}/{count} ===")
        r = receive_otp_5sim(api, platform, country)
        results.append(r)
        if r["success"]:
            print(f"[+] {r['phone']} → {r['otp']}")
        time.sleep(2)  # Brief delay between rentals
    success = [r for r in results if r["success"]]
    print(f"\n[*] Results: {len(success)}/{count} successful")
    return results


def main():
    p = argparse.ArgumentParser(description="SMS OTP automation tool")
    p.add_argument("--service", choices=["5sim","smsactivate","smspva"], default="5sim")
    p.add_argument("--platform", default="tiktok")
    p.add_argument("--country", default="any")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--check-balance", action="store_true")
    p.add_argument("--output", help="Save results to JSON file")
    args = p.parse_args()

    if not API_KEY:
        print("[-] Set SMSAPI_KEY env var"); sys.exit(1)

    if args.service == "5sim":
        api = FiveSimAPI(API_KEY)
        if args.check_balance:
            bal = api.balance()
            print(f"[*] 5sim balance: ${bal}"); return

        if args.count == 1:
            result = receive_otp_5sim(api, args.platform, args.country, args.timeout)
        else:
            result = bulk_receive(api, args.platform, args.country, args.count)

        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"[+] Saved to {args.output}")
    else:
        print(f"[-] {args.service} not yet implemented (contribute welcome)")


if __name__ == "__main__":
    main()
