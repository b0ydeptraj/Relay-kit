#!/usr/bin/env python3
"""
ua_generator.py - Generate realistic browser User-Agent strings with matching fingerprint data.
Produces consistent UA + Accept-Language + Sec-CH-UA headers for stealth automation.

Usage:
    python scripts/ua_generator.py --browser chrome --os windows --output ua.json
    python scripts/ua_generator.py --random --count 10
    python scripts/ua_generator.py --profile gaming-pc
"""
import argparse
import json
import random
import sys

# Chrome versions (recent range)
CHROME_VERSIONS = list(range(122, 127))
EDGE_VERSIONS   = list(range(122, 127))
FIREFOX_VERSIONS= list(range(124, 129))

WINDOWS_VERSIONS = [
    ("Windows NT 10.0", "Win64; x64", "10"),
    ("Windows NT 11.0", "Win64; x64", "11"),
]
MACOS_VERSIONS = [
    ("Macintosh", "Intel Mac OS X 14_0", "14.0"),
    ("Macintosh", "Intel Mac OS X 13_6", "13.6"),
    ("Macintosh", "Intel Mac OS X 14_4", "14.4"),
]
LINUX_VERSIONS = [
    ("X11; Linux x86_64", "Linux x86_64", "Linux"),
]

PROFILES = {
    "gaming-pc": {"browser": "chrome", "os": "windows", "screen": "2560x1440",
                  "gpu": "NVIDIA GeForce RTX 3070", "cores": 16, "ram": 32},
    "office-laptop": {"browser": "edge", "os": "windows", "screen": "1920x1080",
                      "gpu": "Intel Iris Xe Graphics", "cores": 8, "ram": 16},
    "macbook-dev": {"browser": "chrome", "os": "macos", "screen": "2560x1600",
                    "gpu": "Apple M2 Pro", "cores": 12, "ram": 32},
    "linux-user": {"browser": "firefox", "os": "linux", "screen": "1920x1080",
                   "gpu": "AMD Radeon RX 6800 XT", "cores": 8, "ram": 16},
}

COMMON_SCREEN_SIZES = ["1920x1080", "1366x768", "2560x1440", "1440x900", "1280x800"]
COMMON_TIMEZONES = ["America/New_York", "America/Chicago", "America/Los_Angeles",
                    "Europe/London", "Europe/Paris", "Asia/Tokyo", "Asia/Bangkok"]


def generate_chrome_ua(os_type: str = "windows") -> dict:
    ver = random.choice(CHROME_VERSIONS)
    build = f"{ver}.0.{random.randint(5000, 9999)}.{random.randint(10, 200)}"

    if os_type == "windows":
        nt, platform, win_ver = random.choice(WINDOWS_VERSIONS)
        ua = f"Mozilla/5.0 ({nt}; {platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{build} Safari/537.36"
        sec_ch_ua = f'"Google Chrome";v="{ver}", "Chromium";v="{ver}", "Not A Brand";v="24"'
        sec_ch_platform = f'"Windows"'
    elif os_type == "macos":
        mac_os, mac_cpu, mac_ver = random.choice(MACOS_VERSIONS)
        ua = f"Mozilla/5.0 ({mac_os}; {mac_cpu}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{build} Safari/537.36"
        sec_ch_ua = f'"Google Chrome";v="{ver}", "Chromium";v="{ver}", "Not A Brand";v="24"'
        sec_ch_platform = '"macOS"'
    else:
        linux, lplatform, _ = random.choice(LINUX_VERSIONS)
        ua = f"Mozilla/5.0 ({linux}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{build} Safari/537.36"
        sec_ch_ua = f'"Google Chrome";v="{ver}", "Chromium";v="{ver}", "Not A Brand";v="24"'
        sec_ch_platform = '"Linux"'

    return {
        "useragent": ua,
        "browser": "Chrome", "version": str(ver),
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept_language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.9,en-US;q=0.8"]),
        "accept_encoding": "gzip, deflate, br, zstd",
        "sec_ch_ua": sec_ch_ua,
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": sec_ch_platform,
        "sec_fetch_dest": "document",
        "sec_fetch_mode": "navigate",
        "sec_fetch_site": "none",
        "upgrade_insecure_requests": "1",
    }


def generate_fingerprint(profile_name: str = None, ua_data: dict = None) -> dict:
    profile = PROFILES.get(profile_name, {})
    screen = profile.get("screen", random.choice(COMMON_SCREEN_SIZES))
    w, h = map(int, screen.split("x"))
    cores = profile.get("cores", random.choice([4, 8, 12, 16]))
    ram   = profile.get("ram", random.choice([8, 16, 32]))
    gpu   = profile.get("gpu", "ANGLE (Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)")
    tz    = random.choice(COMMON_TIMEZONES)

    return {
        "screen": {"width": w, "height": h, "availWidth": w, "availHeight": h - 40,
                   "colorDepth": 24, "pixelRatio": 1 if w < 2000 else 2},
        "navigator": {"hardwareConcurrency": cores, "deviceMemory": ram,
                      "platform": ua_data.get("sec_ch_ua_platform", '"Windows"').strip('"'),
                      "languages": ["en-US", "en"],
                      "cookieEnabled": True, "doNotTrack": None},
        "timezone": tz,
        "gpu": {"vendor": "Google Inc. (NVIDIA)", "renderer": f"ANGLE ({gpu} Direct3D11 vs_5_0 ps_5_0)"},
        "canvas_noise": round(random.uniform(0.00001, 0.0001), 7),
        "audio_context_hash": hex(random.randint(0xA0000000, 0xFFFFFFFF)),
    }


def main():
    p = argparse.ArgumentParser(description="Browser fingerprint & UA generator")
    p.add_argument("--browser", choices=["chrome","edge","firefox"], default="chrome")
    p.add_argument("--os", choices=["windows","macos","linux"], default="windows")
    p.add_argument("--profile", choices=list(PROFILES.keys()), help="Use preset profile")
    p.add_argument("--random", action="store_true", help="Fully random UA")
    p.add_argument("--count", type=int, default=1, help="Number of UAs to generate")
    p.add_argument("--output", help="Output JSON file")
    args = p.parse_args()

    results = []
    for _ in range(args.count):
        os_type = PROFILES.get(args.profile, {}).get("os", args.os) if args.profile else args.os
        ua_data = generate_chrome_ua(os_type)
        fp = generate_fingerprint(args.profile, ua_data)
        results.append({"headers": ua_data, "fingerprint": fp})

    if args.count == 1:
        print(json.dumps(results[0], indent=2))
    else:
        for i, r in enumerate(results):
            print(f"\n[{i+1}] {r['headers']['useragent'][:80]}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results if args.count > 1 else results[0], f, indent=2)
        print(f"\n[+] Saved to {args.output}")


if __name__ == "__main__":
    main()
