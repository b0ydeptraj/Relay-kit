#!/usr/bin/env python3
"""
profile_manager.py - Manage anti-detection browser profiles via API (GoLogin/AdsPower/Dolphin).
Create, launch, list, and delete browser profiles with proxy assignment.

Usage:
    python scripts/profile_manager.py --browser gologin --action list
    python scripts/profile_manager.py --browser adspower --action create --proxy "socks5://user:pass@ip:port" --name "acc001"
    python scripts/profile_manager.py --browser gologin --action launch --profile-id <id>
    python scripts/profile_manager.py --browser dolphin --action delete --profile-id <id>

API Key: ANTIDETECT_API_KEY env var. Browser API URL: ANTIDETECT_API_URL env var.
"""
import argparse
import json
import os
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse
import random

API_KEY = os.environ.get("ANTIDETECT_API_KEY", "")
API_URL = os.environ.get("ANTIDETECT_API_URL", "http://localhost:3001")  # AdsPower default

# Fingerprint templates
FINGERPRINT_TEMPLATES = {
    "windows-chrome": {
        "os": "Windows", "os_version": "10", "browser": "chrome", "browser_version": "125",
        "screen_resolution": random.choice(["1920x1080","1366x768","2560x1440"]),
        "timezone": "America/New_York",
        "language": "en-US,en",
        "canvas_mode": "noise",
        "webgl_mode": "noise",
    },
    "macos-chrome": {
        "os": "MacOS", "os_version": "13", "browser": "chrome", "browser_version": "125",
        "screen_resolution": "2560x1600",
        "timezone": "America/Los_Angeles",
        "language": "en-US,en",
        "canvas_mode": "noise",
        "webgl_mode": "noise",
    }
}


def api_request(method: str, endpoint: str, data: dict = None, token: str = None) -> dict:
    url = f"{API_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = ureq.Request(url, body, headers, method=method)
    try:
        resp = ureq.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


# --- GoLogin API ---
def gologin_list(token: str):
    r = api_request("GET", "/browser/v2", token=token)
    profiles = r.get("profiles", [])
    print(f"[*] GoLogin profiles: {len(profiles)}")
    for p in profiles[:20]:
        print(f"  {p.get('id')} | {p.get('name')} | proxy: {p.get('proxy',{}).get('host','none')}")
    return profiles


def gologin_create(token: str, name: str, proxy: str = None):
    fp = FINGERPRINT_TEMPLATES["windows-chrome"].copy()
    payload = {
        "name": name,
        "os": "win",
        "navigator": {"userAgent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"},
        "fonts": {"families": ["Arial", "Verdana", "Times New Roman"]},
        "canvas": {"mode": "noise"},
        "webGL": {"mode": "noise"},
        "timezone": {"enabled": True, "fillBasedOnExternalIp": False, "timezone": fp["timezone"]},
    }
    if proxy:
        proxy_parts = proxy.replace("socks5://","").replace("http://","").split("@")
        host_port = proxy_parts[-1].split(":")
        payload["proxy"] = {
            "mode": "socks5" if "socks5" in proxy else "http",
            "host": host_port[0], "port": int(host_port[1]) if len(host_port) > 1 else 1080,
        }
        if len(proxy_parts) > 1:
            creds = proxy_parts[0].split(":")
            payload["proxy"]["username"] = creds[0]
            payload["proxy"]["password"] = creds[1] if len(creds) > 1 else ""
    r = api_request("POST", "/browser/v2", payload, token=token)
    if r.get("id"):
        print(f"[+] Profile created: {r['id']} ({name})")
    else:
        print(f"[-] Create failed: {r}")
    return r


# --- AdsPower API ---
def adspower_list():
    r = api_request("GET", "/api/v1/user/list?page=1&page_size=20")
    profiles = r.get("data", {}).get("list", [])
    print(f"[*] AdsPower profiles: {len(profiles)}")
    for p in profiles[:20]:
        print(f"  {p.get('user_id')} | {p.get('name')} | status: {p.get('ip_country','?')}")


def adspower_launch(profile_id: str):
    r = api_request("GET", f"/api/v1/browser/start?user_id={profile_id}&open_tabs=1&ip_tab=0")
    if r.get("code") == 0:
        ws = r.get("data", {}).get("ws", {})
        print(f"[+] Browser launched. CDP: {ws.get('selenium','')}")
        print(f"[+] Connect via: playwright.chromium.connect_over_cdp('{ws.get('selenium','')}')")
        return ws
    print(f"[-] Launch failed: {r}")
    return None


# --- Dolphin Anty API ---
def dolphin_list(token: str):
    r = api_request("GET", "/v1.0/browser_profiles?page=1&perPage=20", token=token)
    data = r.get("data", {}).get("browserProfiles", [])
    print(f"[*] Dolphin profiles: {len(data)}")
    for p in data[:20]:
        print(f"  {p.get('id')} | {p.get('name')}")


def main():
    p = argparse.ArgumentParser(description="Anti-detection browser profile manager")
    p.add_argument("--browser", choices=["gologin","adspower","dolphin"], required=True)
    p.add_argument("--action", choices=["list","create","launch","delete"], required=True)
    p.add_argument("--profile-id")
    p.add_argument("--name", default=f"profile_{random.randint(1000,9999)}")
    p.add_argument("--proxy")
    p.add_argument("--token", default=os.environ.get("ANTIDETECT_API_KEY",""))
    args = p.parse_args()

    if args.browser == "gologin":
        if args.action == "list": gologin_list(args.token)
        elif args.action == "create": gologin_create(args.token, args.name, args.proxy)
        else: print(f"[-] {args.action} for gologin: use their official client/API")
    elif args.browser == "adspower":
        if args.action == "list": adspower_list()
        elif args.action == "launch": adspower_launch(args.profile_id or "")
        else: print(f"[-] Use AdsPower REST API docs for {args.action}")
    elif args.browser == "dolphin":
        if args.action == "list": dolphin_list(args.token)
        else: print(f"[-] Use Dolphin API docs for {args.action}")


if __name__ == "__main__":
    main()
