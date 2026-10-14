#!/usr/bin/env python3
"""
cf_clearance.py - Cloudflare clearance cookie bypass via headless browser fingerprinting.
Obtains cf_clearance cookie by solving Cloudflare Bot Fight Mode / Turnstile challenges.

Usage:
    python scripts/cf_clearance.py --url https://target.com --output cookies.json
    python scripts/cf_clearance.py --url https://target.com --proxy http://127.0.0.1:8080

Requirements: pip install playwright && playwright install chromium
"""
import argparse
import json
import os
import sys
import time


def solve_cf_clearance(url: str, proxy: str = None, headless: bool = True, timeout: int = 30) -> dict:
    """Use playwright with stealth fingerprint to obtain CF clearance."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[-] playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    cookies = {}
    with sync_playwright() as p:
        launch_args = {
            "headless": headless,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        }
        if proxy:
            launch_args["proxy"] = {"server": proxy}

        browser = p.chromium.launch(**launch_args)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="America/New_York",
            java_script_enabled=True,
        )

        # Stealth: remove webdriver fingerprint
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = {runtime: {}};
        """)

        page = context.new_page()
        print(f"[*] Navigating to {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)

        # Wait for CF challenge to resolve
        deadline = time.time() + timeout
        while time.time() < deadline:
            if "Just a moment" not in page.title() and "Checking your browser" not in page.content():
                break
            print("[*] Waiting for Cloudflare challenge to clear...")
            page.wait_for_timeout(2000)

        # Extract cookies
        raw_cookies = context.cookies()
        for c in raw_cookies:
            cookies[c["name"]] = c["value"]

        if "cf_clearance" in cookies:
            print(f"[+] cf_clearance obtained: {cookies['cf_clearance'][:30]}...")
        else:
            print(f"[-] cf_clearance not obtained. Cookies: {list(cookies.keys())}")

        # Save user agent used
        ua = page.evaluate("navigator.userAgent")
        cookies["_ua"] = ua

        browser.close()
    return cookies


def main():
    p = argparse.ArgumentParser(description="Cloudflare clearance cookie extractor")
    p.add_argument("--url", required=True)
    p.add_argument("--output", default="cookies.json")
    p.add_argument("--proxy", help="Proxy URL e.g. http://127.0.0.1:8080")
    p.add_argument("--no-headless", action="store_true", help="Run browser visibly")
    p.add_argument("--timeout", type=int, default=30)
    args = p.parse_args()

    cookies = solve_cf_clearance(args.url, args.proxy, not args.no_headless, args.timeout)
    with open(args.output, "w") as f:
        json.dump(cookies, f, indent=2)
    print(f"[+] Cookies saved to {args.output}")
    print(f"[+] Got {len(cookies)} cookies: {', '.join(cookies.keys())}")


if __name__ == "__main__":
    main()
