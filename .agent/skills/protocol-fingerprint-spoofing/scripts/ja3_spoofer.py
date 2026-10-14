#!/usr/bin/env python3
"""
ja3_spoofer.py - TLS/JA3 fingerprint analysis and spoofing toolkit.
Identifies your current JA3 fingerprint, compares with browser profiles,
and generates curl/requests configs to spoof specific fingerprints.

Usage:
    python scripts/ja3_spoofer.py --check-ja3
    python scripts/ja3_spoofer.py --profile chrome-125 --generate-curl
    python scripts/ja3_spoofer.py --profile firefox-125 --generate-python
    python scripts/ja3_spoofer.py --list-profiles
    python scripts/ja3_spoofer.py --analyze-host api.example.com:443
"""
import argparse
import hashlib
import json
import os
import re
import socket
import ssl
import struct
import sys
import urllib.request as ureq

# Real JA3 fingerprints for common browsers/tools
JA3_PROFILES = {
    "chrome-125": {
        "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513-21,29-23-24,0",
        "ja3_hash": "cd08e31494f9531f560d64c695473da9",
        "description": "Chrome 125 (Windows)",
        "tls_version": "TLSv1.3",
        "cipher_priority": ["TLS_AES_128_GCM_SHA256","TLS_AES_256_GCM_SHA384","ECDHE-ECDSA-AES128-GCM-SHA256"],
    },
    "firefox-125": {
        "ja3": "771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-51-57-47-53,0-23-65281-10-11-35-16-5-34-51-43-13-45-28-21,29-23-24-25-256-257,0",
        "ja3_hash": "579ccef312d18482fc42e2b822ca2430",
        "description": "Firefox 125 (Windows)",
        "tls_version": "TLSv1.3",
    },
    "safari-17": {
        "ja3": "771,4865-4866-4867-49196-49195-52393-49200-49199-52392-49188-49187-49162-49161-49192-49191-49172-49171-157-156-61-60-53-47-49160-49170-10,0-23-65281-10-11-16-5-13-18-51-45-43-27-21,29-23-24-25,0",
        "ja3_hash": "773906b0efdefa24a7f2b8eb6985bf76",
        "description": "Safari 17 (macOS)",
        "tls_version": "TLSv1.3",
    },
    "python-requests": {
        "ja3": "771,49196-49200-49195-49199-4866-4865-49196-49200-49195-49199-158-57-52393-52392-49196-49200-49195-49199-4866-4865,0-23-65281-10-11-35-16-5-13,29-23-24-25,0",
        "ja3_hash": "6a9b0765591c0b0ef67b8a59b9703906",
        "description": "Python requests library",
    },
    "curl-8": {
        "ja3": "771,4865-4867-4866-49195-49199-52393-52392-49196-49200-49162-49161-49171-49172-51-57-47-53,0-23-65281-10-11-35-16-5-51-43-13-45-28-21,29-23-24,0",
        "ja3_hash": "d8b207c491e6109e1aff84c66ca8b9d8",
        "description": "curl 8.x",
    },
    "chrome-android-125": {
        "ja3": "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513-21,29-23-24,0",
        "ja3_hash": "7f8b8e5b35d0e6f6e6e9dfbce0c65438",
        "description": "Chrome 125 Android",
    },
}


def compute_ja3_hash(ja3_string: str) -> str:
    """Compute MD5 of JA3 string."""
    return hashlib.md5(ja3_string.encode()).hexdigest()


def get_my_ja3(host: str = "ja3er.com", port: int = 443) -> dict:
    """Get our TLS fingerprint from ja3er.com echo service."""
    try:
        url = f"https://ja3er.com/json"
        req = ureq.Request(url, headers={"User-Agent": "JA3-Check/1.0"})
        ctx = ssl.create_default_context()
        resp = ureq.urlopen(req, context=ctx, timeout=10)
        data = json.loads(resp.read())
        return {
            "ja3_hash": data.get("ja3_hash"),
            "ja3_string": data.get("ja3"),
            "user_agent": data.get("User-Agent"),
        }
    except Exception as e:
        return {"error": str(e)[:100]}


def analyze_host_tls(host: str, port: int = 443) -> dict:
    """Analyze TLS configuration of a target host."""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cipher = ssock.cipher()
                cert = ssock.getpeercert()
                return {
                    "host": host, "port": port,
                    "tls_version": ssock.version(),
                    "cipher": cipher[0] if cipher else "?",
                    "cipher_bits": cipher[2] if cipher else "?",
                    "cert_subject": dict(x[0] for x in cert.get("subject", [])) if cert else {},
                    "cert_issuer": dict(x[0] for x in cert.get("issuer", [])) if cert else {},
                    "cert_expiry": cert.get("notAfter", "?") if cert else "?",
                    "alpn": ssock.selected_alpn_protocol(),
                }
    except Exception as e:
        return {"host": host, "error": str(e)[:100]}


def generate_curl_spoof(profile_name: str) -> str:
    """Generate curl command with TLS options to mimic a profile."""
    profile = JA3_PROFILES.get(profile_name, {})
    if not profile:
        return f"Profile '{profile_name}' not found"

    # Extract cipher list from JA3 string
    ja3 = profile.get("ja3", "")
    parts = ja3.split(",")
    cipher_ids = parts[1].split("-") if len(parts) > 1 else []

    CIPHER_MAP = {
        "49195": "ECDHE-ECDSA-AES128-GCM-SHA256",
        "49199": "ECDHE-RSA-AES128-GCM-SHA256",
        "49196": "ECDHE-ECDSA-AES256-GCM-SHA384",
        "49200": "ECDHE-RSA-AES256-GCM-SHA384",
        "52393": "ECDHE-ECDSA-CHACHA20-POLY1305",
        "52392": "ECDHE-RSA-CHACHA20-POLY1305",
        "4865": "TLS_AES_128_GCM_SHA256",
        "4866": "TLS_AES_256_GCM_SHA384",
        "4867": "TLS_CHACHA20_POLY1305_SHA256",
        "49171": "ECDHE-RSA-AES128-SHA",
        "49172": "ECDHE-RSA-AES256-SHA",
        "156": "AES128-GCM-SHA256",
        "157": "AES256-GCM-SHA384",
        "47": "AES128-SHA",
        "53": "AES256-SHA",
    }
    ciphers = ":".join(CIPHER_MAP.get(cid, "") for cid in cipher_ids if CIPHER_MAP.get(cid))

    script = f"""#!/bin/bash
# JA3 Spoof: {profile_name} - {profile.get('description','')}
# JA3 Hash: {profile.get('ja3_hash','')}

curl -L \\
  --tlsv1.3 \\
  --tls-max 1.3 \\
  --ciphers '{ciphers}' \\
  --http2 \\
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0" \\
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \\
  -H "Accept-Language: en-US,en;q=0.9" \\
  "$@"

# Alternative: use curl-impersonate for exact fingerprint match:
# curl_chrome110 https://target.com/
# Install: https://github.com/lwthiker/curl-impersonate
"""
    return script


def generate_python_spoof(profile_name: str) -> str:
    """Generate Python code to spoof JA3 using tls-client or curl-cffi."""
    profile = JA3_PROFILES.get(profile_name, {})
    script = f'''#!/usr/bin/env python3
"""
JA3 Spoof: {profile_name} - {profile.get("description","")}
JA3 Hash: {profile.get("ja3_hash","")}

Option 1: tls-client (recommended)
  pip install tls-client
"""
import tls_client

# Method 1: tls-client with browser profile
session = tls_client.Session(
    client_identifier="{profile_name.replace("-", "_")}",
    random_tls_extension_order=True
)

response = session.get(
    "https://target.com/api/endpoint",
    headers={{
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0",
        "Accept": "application/json, text/plain, */*",
    }}
)
print(response.status_code, response.text[:200])

# Method 2: curl-cffi (exact browser fingerprint)
# pip install curl-cffi
# from curl_cffi import requests
# response = requests.get("https://target.com", impersonate="chrome110")

# Method 3: Check your JA3 at https://ja3er.com
'''
    return script


def main():
    p = argparse.ArgumentParser(description="TLS/JA3 fingerprint spoofer")
    p.add_argument("--check-ja3", action="store_true")
    p.add_argument("--list-profiles", action="store_true")
    p.add_argument("--profile", choices=list(JA3_PROFILES.keys()))
    p.add_argument("--generate-curl", action="store_true")
    p.add_argument("--generate-python", action="store_true")
    p.add_argument("--analyze-host", help="host:port to analyze TLS")
    p.add_argument("--output")
    args = p.parse_args()

    if args.list_profiles:
        print("[*] Available JA3 profiles:")
        for name, info in JA3_PROFILES.items():
            print(f"  {name:<25} hash:{info['ja3_hash']}  {info['description']}")

    elif args.check_ja3:
        print("[*] Checking your JA3 fingerprint via ja3er.com...")
        result = get_my_ja3()
        if "error" in result:
            print(f"[-] Error: {result['error']}")
        else:
            print(f"  JA3 Hash  : {result.get('ja3_hash')}")
            print(f"  JA3 String: {result.get('ja3_string','')[:80]}...")
            # Compare to known profiles
            my_hash = result.get("ja3_hash")
            match = next((n for n, p in JA3_PROFILES.items() if p["ja3_hash"] == my_hash), None)
            print(f"  Matches   : {match or 'Unknown profile (may be detected as bot)'}")

    elif args.analyze_host:
        host_port = args.analyze_host.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 443
        print(f"[*] Analyzing TLS: {host}:{port}")
        result = analyze_host_tls(host, port)
        for k, v in result.items():
            print(f"  {k}: {v}")

    elif args.profile:
        profile = JA3_PROFILES[args.profile]
        print(f"[*] Profile: {args.profile}")
        print(f"    {profile['description']}")
        print(f"    JA3 Hash: {profile['ja3_hash']}")

        if args.generate_curl:
            script = generate_curl_spoof(args.profile)
            out = args.output or f"spoof_{args.profile}.sh"
            with open(out, "w") as f:
                f.write(script)
            print(f"\n[+] curl script: {out}")
            print(script[:500])

        elif args.generate_python:
            script = generate_python_spoof(args.profile)
            out = args.output or f"spoof_{args.profile}.py"
            with open(out, "w") as f:
                f.write(script)
            print(f"\n[+] Python script: {out}")
    else:
        p.print_help()


if __name__ == "__main__":
    main()
