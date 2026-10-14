#!/usr/bin/env python3
"""
js_crypto_extractor.py - Extract crypto keys, IVs, and secrets from JavaScript bundles.
Finds hardcoded keys, AES/RSA patterns, JWT secrets, and API tokens in minified JS.

Usage:
    python scripts/js_crypto_extractor.py --file bundle.js
    python scripts/js_crypto_extractor.py --url https://app.example.com/main.js
    python scripts/js_crypto_extractor.py --dir ./js/ --recursive
    python scripts/js_crypto_extractor.py --file bundle.js --decrypt --key FOUND_KEY
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.request as ureq

CRYPTO_PATTERNS = {
    "aes_key_hex": {
        "pattern": r'["\']([0-9a-fA-F]{32}|[0-9a-fA-F]{48}|[0-9a-fA-F]{64})["\']',
        "desc": "AES-128/192/256 hex key",
        "validate": lambda m: len(m) in (32, 48, 64),
    },
    "aes_key_base64": {
        "pattern": r'["\']([A-Za-z0-9+/]{22,44}={0,2})["\']',
        "desc": "AES key in Base64",
        "validate": lambda m: len(base64.b64decode(m + "==")) in (16, 24, 32),
    },
    "jwt_secret": {
        "pattern": r'(?:secret|JWT_SECRET|jwtSecret|tokenSecret)["\s:=]+["\']([^"\']{8,100})["\']',
        "desc": "JWT signing secret",
        "validate": lambda m: len(m) >= 8,
    },
    "api_key_generic": {
        "pattern": r'(?:api[_-]?key|apiKey|API_KEY|access[_-]?key)["\s:=]+["\']([A-Za-z0-9_\-]{20,80})["\']',
        "desc": "Generic API key",
        "validate": lambda m: True,
    },
    "private_key_pem": {
        "pattern": r'-----BEGIN (?:RSA )?PRIVATE KEY-----[^-]+-----END (?:RSA )?PRIVATE KEY-----',
        "desc": "PEM private key",
        "validate": lambda m: True,
    },
    "aws_access_key": {
        "pattern": r'\b(AKIA[0-9A-Z]{16})\b',
        "desc": "AWS Access Key ID",
        "validate": lambda m: m.startswith("AKIA"),
    },
    "aws_secret_key": {
        "pattern": r'(?:aws_secret|AWS_SECRET)["\s:=]+["\']([A-Za-z0-9/+=]{40})["\']',
        "desc": "AWS Secret Access Key",
        "validate": lambda m: len(m) == 40,
    },
    "firebase_key": {
        "pattern": r'AIza[0-9A-Za-z_\-]{35}',
        "desc": "Firebase/Google API key",
        "validate": lambda m: True,
    },
    "stripe_key": {
        "pattern": r'\b(sk_(?:live|test)_[0-9a-zA-Z]{24,})\b',
        "desc": "Stripe secret key",
        "validate": lambda m: True,
    },
    "gh_token": {
        "pattern": r'\b(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{59})\b',
        "desc": "GitHub Personal Access Token",
        "validate": lambda m: True,
    },
    "crypto_iv": {
        "pattern": r'(?:iv|IV|initVector)["\s:=]+["\']([0-9a-fA-F]{24,32}|[A-Za-z0-9+/]{16,24})["\']',
        "desc": "Crypto initialization vector",
        "validate": lambda m: True,
    },
    "rsa_public_key": {
        "pattern": r'-----BEGIN PUBLIC KEY-----[^-]+-----END PUBLIC KEY-----',
        "desc": "RSA Public Key",
        "validate": lambda m: True,
    },
    "password_hash_bcrypt": {
        "pattern": r'\$2[aby]\$\d+\$[./A-Za-z0-9]{53}',
        "desc": "bcrypt hash",
        "validate": lambda m: True,
    },
    "hex_secret_short": {
        "pattern": r'(?:secret|key|token|password)["\s:=]+["\']([0-9a-fA-F]{16,32})["\']',
        "desc": "Short hex secret/key",
        "validate": lambda m: len(m) >= 16,
    },
    "bearer_token": {
        "pattern": r'Bearer\s+([A-Za-z0-9_\-\.]{20,500})',
        "desc": "Bearer auth token",
        "validate": lambda m: True,
    },
    "eval_obfuscated": {
        "pattern": r'eval\s*\(\s*(?:atob|unescape|decodeURIComponent)\s*\(',
        "desc": "Eval with encoded payload (obfuscated code)",
        "validate": lambda m: True,
    },
}


def extract_from_text(content: str, source: str = "unknown") -> list:
    """Extract all crypto patterns from text content."""
    findings = []
    seen = set()

    for pattern_name, info in CRYPTO_PATTERNS.items():
        try:
            matches = re.findall(info["pattern"], content, re.IGNORECASE | re.DOTALL)
        except re.error:
            continue

        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match else ""
            if not match or match in seen:
                continue

            try:
                valid = info["validate"](match)
            except:
                valid = True

            if valid:
                seen.add(match)
                # Get context (30 chars around match)
                idx = content.find(match)
                ctx_start = max(0, idx - 30)
                ctx_end = min(len(content), idx + len(match) + 30)
                context = content[ctx_start:ctx_end].replace("\n", " ")

                findings.append({
                    "type": pattern_name,
                    "desc": info["desc"],
                    "value": match[:200],
                    "length": len(match),
                    "source": source,
                    "context": context[:100],
                })

    return findings


def fetch_js(url: str) -> str:
    """Download JavaScript from URL."""
    headers = {"User-Agent": "Mozilla/5.0 Chrome/125.0.0.0"}
    req = ureq.Request(url, headers=headers)
    try:
        resp = ureq.urlopen(req, timeout=30)
        return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"[-] Fetch failed: {e}")
        return ""


def analyze_webpack_chunks(content: str) -> list:
    """Find webpack chunk definitions and module IDs."""
    chunks = re.findall(r'webpackChunk\w*\.push\(\[([^\]]+)\]', content)
    modules = re.findall(r'"(\d+)":function\(', content)
    return {"chunks": len(chunks), "modules": len(modules)}


def try_decode_eval(content: str) -> list:
    """Try to decode eval(atob(...)) or eval(unescape(...)) payloads."""
    decoded = []
    # Find atob patterns
    for match in re.finditer(r'atob\(["\']([A-Za-z0-9+/=]+)["\']\)', content):
        try:
            b64 = match.group(1)
            plain = base64.b64decode(b64).decode("utf-8", errors="replace")
            decoded.append({"encoding": "base64/atob", "decoded": plain[:200]})
        except:
            pass

    # Find unescape patterns
    for match in re.finditer(r'unescape\(["\'](%[0-9a-fA-F]{2}[^"\']+)["\']', content):
        try:
            from urllib.parse import unquote
            plain = unquote(match.group(1))
            decoded.append({"encoding": "unescape", "decoded": plain[:200]})
        except:
            pass

    return decoded


def scan_js_file(file_path: str) -> dict:
    """Scan a single JS file."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    print(f"[*] Scanning: {file_path} ({len(content):,} chars)")
    findings = extract_from_text(content, file_path)
    decoded = try_decode_eval(content)
    webpack_info = analyze_webpack_chunks(content)
    return {"file": file_path, "findings": findings, "decoded_evals": decoded, "webpack": webpack_info}


def main():
    p = argparse.ArgumentParser(description="JavaScript crypto key and secret extractor")
    p.add_argument("--file", help="JS file to scan")
    p.add_argument("--url", help="URL to download and scan")
    p.add_argument("--dir", help="Directory of JS files")
    p.add_argument("--recursive", action="store_true")
    p.add_argument("--output", help="Save results JSON")
    args = p.parse_args()

    all_results = []

    if args.url:
        print(f"[*] Fetching: {args.url}")
        content = fetch_js(args.url)
        if content:
            findings = extract_from_text(content, args.url)
            decoded = try_decode_eval(content)
            all_results.append({"url": args.url, "findings": findings, "decoded_evals": decoded})

    elif args.file:
        if not os.path.exists(args.file):
            print(f"[-] File not found: {args.file}"); sys.exit(1)
        result = scan_js_file(args.file)
        all_results.append(result)

    elif args.dir:
        pattern = "**/*.js" if args.recursive else "*.js"
        import glob
        files = glob.glob(os.path.join(args.dir, pattern), recursive=args.recursive)
        print(f"[*] Found {len(files)} JS files")
        for f in files:
            result = scan_js_file(f)
            all_results.append(result)

    else:
        p.print_help(); sys.exit(1)

    # Print summary
    total_findings = sum(len(r["findings"]) for r in all_results)
    print(f"\n[*] Total findings: {total_findings}")
    for result in all_results:
        src = result.get("file") or result.get("url", "?")
        if result["findings"]:
            print(f"\n  [{os.path.basename(src)}]")
            for f in result["findings"]:
                print(f"    [{f['type']}] {f['desc']}")
                print(f"      Value: {f['value'][:60]}{'...' if len(f['value'])>60 else ''}")
                print(f"      Context: {f['context'][:70]}")
        if result.get("decoded_evals"):
            print(f"  Decoded evals: {len(result['decoded_evals'])}")
            for d in result["decoded_evals"][:3]:
                print(f"    [{d['encoding']}]: {d['decoded'][:80]}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n[+] Saved: {args.output}")


if __name__ == "__main__":
    main()
