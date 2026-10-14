#!/usr/bin/env python3
"""
auth_validator.py - Authorization gate for MMO operations.
Validates engagement proofs, operation scope, and risk level before allowing execution.

Usage:
    python scripts/auth_validator.py --check --proof "engagement-001" --operation "account-create" --platform tiktok
    python scripts/auth_validator.py --generate-proof --operator "MyTeam" --target "TikTok MMO" --expiry 30
    python scripts/auth_validator.py --list-allowed
"""
import argparse
import hashlib
import json
import os
import sys
import time

ALLOWED_OPERATIONS = {
    "account-create":      {"risk": "medium", "requires_proof": True, "platforms": ["all"]},
    "browser-fleet":       {"risk": "medium", "requires_proof": True, "platforms": ["all"]},
    "captcha-solve":       {"risk": "low",    "requires_proof": False, "platforms": ["all"]},
    "warmup":              {"risk": "low",    "requires_proof": False, "platforms": ["all"]},
    "data-harvest":        {"risk": "medium", "requires_proof": True,  "platforms": ["all"]},
    "social-post":         {"risk": "low",    "requires_proof": False, "platforms": ["all"]},
    "bypass-edr":          {"risk": "high",   "requires_proof": True,  "platforms": ["internal"]},
    "process-injection":   {"risk": "critical","requires_proof": True, "platforms": ["internal"]},
    "kernel-exploit":      {"risk": "critical","requires_proof": True, "platforms": ["internal"]},
    "proxy-check":         {"risk": "low",    "requires_proof": False, "platforms": ["all"]},
}


def generate_proof(operator: str, target: str, expiry_days: int = 30) -> dict:
    ts = int(time.time())
    exp = ts + expiry_days * 86400
    payload = f"{operator}|{target}|{ts}|{exp}"
    token = hashlib.sha256(payload.encode()).hexdigest()[:16].upper()
    proof = {
        "token": f"PROOF-{token}",
        "operator": operator,
        "target": target,
        "issued": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
        "expires": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(exp)),
        "expiry_days": expiry_days,
        "raw": payload,
    }
    print(f"[+] Engagement proof generated:")
    print(f"    Token    : {proof['token']}")
    print(f"    Operator : {operator}")
    print(f"    Target   : {target}")
    print(f"    Expires  : {proof['expires']}")
    print(f"\n    Usage: set ENGAGEMENT_PROOF={proof['token']}")
    return proof


def validate_operation(proof: str, operation: str, platform: str = "any") -> dict:
    op = ALLOWED_OPERATIONS.get(operation)
    if not op:
        return {"allowed": False, "reason": f"Unknown operation: {operation}"}

    if op["requires_proof"] and not proof:
        return {"allowed": False, "reason": f"Operation '{operation}' requires ENGAGEMENT_PROOF",
                "risk": op["risk"]}

    if op["risk"] == "critical" and not proof:
        return {"allowed": False, "reason": "CRITICAL risk operation requires proof",
                "risk": "critical"}

    if op.get("platforms") != ["all"] and platform not in (op.get("platforms", []) + ["internal"]):
        return {"allowed": False, "reason": f"Platform '{platform}' not allowed for '{operation}'"}

    return {"allowed": True, "operation": operation, "risk": op["risk"],
            "proof_present": bool(proof), "platform": platform}


def main():
    p = argparse.ArgumentParser(description="MMO authorization gate validator")
    p.add_argument("--check", action="store_true")
    p.add_argument("--proof", default=os.environ.get("ENGAGEMENT_PROOF",""))
    p.add_argument("--operation", default="account-create")
    p.add_argument("--platform", default="any")
    p.add_argument("--generate-proof", action="store_true")
    p.add_argument("--operator", default="MMO-Operator")
    p.add_argument("--target", default="Internal MMO Operations")
    p.add_argument("--expiry", type=int, default=30)
    p.add_argument("--list-allowed", action="store_true")
    args = p.parse_args()

    if args.list_allowed:
        print("[*] Allowed operations:")
        print(f"  {'Operation':<25} {'Risk':<10} {'Requires Proof':<16} {'Platforms'}")
        print("-" * 70)
        for op, meta in ALLOWED_OPERATIONS.items():
            print(f"  {op:<25} {meta['risk']:<10} {str(meta['requires_proof']):<16} {','.join(meta['platforms'])}")
        return

    if args.generate_proof:
        generate_proof(args.operator, args.target, args.expiry)
        return

    if args.check:
        result = validate_operation(args.proof, args.operation, args.platform)
        allowed = result["allowed"]
        print(f"[{'OK' if allowed else 'BLOCKED'}] Operation: {args.operation} | Platform: {args.platform}")
        print(f"  Risk: {result.get('risk','?')} | Proof: {'present' if args.proof else 'missing'}")
        if not allowed:
            print(f"  Reason: {result['reason']}")
        sys.exit(0 if allowed else 1)


if __name__ == "__main__":
    main()
