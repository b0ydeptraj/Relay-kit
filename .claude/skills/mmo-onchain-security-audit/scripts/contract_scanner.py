#!/usr/bin/env python3
"""
contract_scanner.py - Smart contract security scanner for rug pull / honeypot detection.
Analyzes EVM smart contracts for common MMO-relevant security patterns.

Usage:
    python scripts/contract_scanner.py --address 0x... --chain eth
    python scripts/contract_scanner.py --address 0x... --chain bsc --check-honeypot
    python scripts/contract_scanner.py --token-list tokens.txt --chain eth

Requires: ETHERSCAN_API_KEY or BSCSCAN_API_KEY env var.
"""
import argparse
import json
import os
import sys
import urllib.request as ureq

SCAN_APIS = {
    "eth": {"url": "https://api.etherscan.io/api", "key_env": "ETHERSCAN_API_KEY"},
    "bsc": {"url": "https://api.bscscan.com/api", "key_env": "BSCSCAN_API_KEY"},
    "polygon": {"url": "https://api.polygonscan.com/api", "key_env": "POLYGONSCAN_API_KEY"},
}

HONEYPOT_API = "https://api.honeypot.is/v2/IsHoneypot?address={addr}&chainID={cid}"
CHAIN_IDS = {"eth": 1, "bsc": 56, "polygon": 137}

RISK_PATTERNS = {
    "mint_function": ["mint(", "mintTo(", "_mint("],
    "pause_function": ["pause(", "paused("],
    "blacklist": ["blacklist", "addToBlacklist", "isBlacklisted"],
    "tax_modification": ["setFee(", "setTax(", "setTaxFee("],
    "ownership_hidden": ["Ownable", "onlyOwner"],
    "proxy": ["delegatecall", "upgradeable", "proxy"],
    "self_destruct": ["selfdestruct", "suicide("],
    "hidden_mint": ["_mint(address", "totalSupply"],
}


def get_contract_source(address: str, chain: str) -> dict:
    cfg = SCAN_APIS.get(chain, SCAN_APIS["eth"])
    key = os.environ.get(cfg["key_env"], "")
    url = f"{cfg['url']}?module=contract&action=getsourcecode&address={address}&apikey={key}"
    try:
        resp = ureq.urlopen(url, timeout=15)
        data = json.loads(resp.read())
        result = data.get("result", [{}])[0] if data.get("result") else {}
        return {"verified": bool(result.get("SourceCode")),
                "source": result.get("SourceCode",""),
                "name": result.get("ContractName","Unknown"),
                "compiler": result.get("CompilerVersion","?"),
                "abi": result.get("ABI","[]")}
    except Exception as e:
        return {"error": str(e), "verified": False}


def check_honeypot(address: str, chain: str) -> dict:
    cid = CHAIN_IDS.get(chain, 1)
    url = HONEYPOT_API.format(addr=address, cid=cid)
    try:
        resp = ureq.urlopen(url, timeout=15)
        data = json.loads(resp.read())
        return {
            "is_honeypot": data.get("isHoneypot", False),
            "honeypot_reason": data.get("honeypotResult", {}).get("reason", ""),
            "buy_tax": data.get("simulationResult", {}).get("buyTax", "?"),
            "sell_tax": data.get("simulationResult", {}).get("sellTax", "?"),
            "buy_gas": data.get("simulationResult", {}).get("buyGas", "?"),
        }
    except Exception as e:
        return {"error": str(e)}


def analyze_source(source: str) -> dict:
    risks = {}
    source_lower = source.lower()
    for risk, patterns in RISK_PATTERNS.items():
        found = [p for p in patterns if p.lower() in source_lower]
        if found:
            risks[risk] = found
    risk_score = len(risks)
    return {"risks": risks, "risk_score": risk_score,
            "risk_level": "HIGH" if risk_score >= 4 else ("MEDIUM" if risk_score >= 2 else "LOW")}


def scan_contract(address: str, chain: str, check_hp: bool = False):
    print(f"\n[*] Scanning: {address} ({chain.upper()})")
    src = get_contract_source(address, chain)

    if src.get("error"):
        print(f"[-] Error: {src['error']}")
        return

    print(f"  Contract : {src['name']}")
    print(f"  Verified : {src['verified']}")
    print(f"  Compiler : {src['compiler']}")

    if src["verified"] and src["source"]:
        analysis = analyze_source(src["source"])
        print(f"  Risk level : {analysis['risk_level']} (score: {analysis['risk_score']})")
        if analysis["risks"]:
            print(f"  Risk flags :")
            for risk, patterns in analysis["risks"].items():
                print(f"    - {risk}: {patterns[:3]}")
    else:
        print(f"  [!] Source not verified - HIGH RISK (cannot audit)")

    if check_hp:
        hp = check_honeypot(address, chain)
        if "error" not in hp:
            is_hp = hp["is_honeypot"]
            print(f"  Honeypot   : {'YES - DANGER' if is_hp else 'No'}")
            print(f"  Buy tax    : {hp['buy_tax']}%")
            print(f"  Sell tax   : {hp['sell_tax']}%")
            if hp.get("honeypot_reason"):
                print(f"  Reason     : {hp['honeypot_reason']}")


def main():
    p = argparse.ArgumentParser(description="Smart contract security scanner")
    p.add_argument("--address", help="Contract address")
    p.add_argument("--chain", choices=list(SCAN_APIS.keys()), default="eth")
    p.add_argument("--check-honeypot", action="store_true")
    p.add_argument("--token-list", help="File with contract addresses (one per line)")
    args = p.parse_args()

    if args.token_list:
        with open(args.token_list) as f:
            addresses = [l.strip() for l in f if l.strip() and l.startswith("0x")]
        print(f"[*] Scanning {len(addresses)} contracts...")
        for addr in addresses:
            scan_contract(addr, args.chain, args.check_honeypot)
    elif args.address:
        scan_contract(args.address, args.chain, args.check_honeypot)
    else:
        print("[-] --address or --token-list required"); sys.exit(1)


if __name__ == "__main__":
    main()
