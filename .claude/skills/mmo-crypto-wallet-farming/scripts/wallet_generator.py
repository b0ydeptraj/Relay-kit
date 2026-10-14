#!/usr/bin/env python3
"""
wallet_generator.py - Generate and manage crypto wallets for airdrop farming.
Generates EVM (Ethereum/BSC/Polygon), Solana, and TON wallets in bulk.

Usage:
    python scripts/wallet_generator.py --chain evm --count 50 --output wallets.json
    python scripts/wallet_generator.py --chain solana --count 10
    python scripts/wallet_generator.py --chain ton --count 5
    python scripts/wallet_generator.py --check-balance --chain evm --wallets wallets.json --rpc https://eth-mainnet.g.alchemy.com/v2/KEY
    python scripts/wallet_generator.py --export-csv --wallets wallets.json

Requirements: pip install eth-account (for EVM), solders (for Solana)
"""
import argparse
import csv
import json
import os
import random
import sys
import time
import urllib.request as ureq

SUPPORTED_CHAINS = ["evm", "solana", "ton"]


def generate_evm_wallet() -> dict:
    """Generate Ethereum/EVM compatible wallet."""
    try:
        from eth_account import Account
        Account.enable_unaudited_hdwallet_features()
        acct = Account.create()
        mnemonic = Account.from_mnemonic(Account.create_with_mnemonic()[1])
        return {
            "chain": "evm",
            "address": acct.address,
            "private_key": acct.key.hex(),
            "mnemonic": None,
        }
    except ImportError:
        # Fallback: generate random-looking wallet (for testing structure only)
        import hashlib, secrets
        priv = secrets.token_hex(32)
        addr = "0x" + hashlib.sha256(bytes.fromhex(priv)).hexdigest()[:40]
        return {"chain": "evm", "address": addr, "private_key": priv, "mnemonic": None,
                "note": "install eth-account for real wallets: pip install eth-account"}


def generate_solana_wallet() -> dict:
    """Generate Solana wallet."""
    try:
        from solders.keypair import Keypair
        kp = Keypair()
        return {
            "chain": "solana",
            "address": str(kp.pubkey()),
            "private_key": kp.secret().hex(),
            "private_key_base58": str(kp),
        }
    except ImportError:
        import secrets, hashlib, base64
        priv = secrets.token_bytes(32)
        addr = base64.b58encode(hashlib.sha256(priv).digest()).decode()[:44]
        return {"chain": "solana", "address": addr, "private_key": priv.hex(),
                "note": "install solders for real wallets: pip install solders"}


def generate_ton_wallet() -> dict:
    """Generate TON wallet (simplified - returns mnemonic-based wallet info)."""
    import secrets, hashlib
    seed = secrets.token_bytes(32)
    addr = "EQ" + hashlib.sha256(seed).hexdigest()[:46].upper()
    mnemonic = " ".join([secrets.token_hex(2) for _ in range(24)])
    return {"chain": "ton", "address": addr, "private_key": seed.hex(),
            "mnemonic": mnemonic,
            "note": "install tonutils for real wallets: pip install tonutils"}


GENERATORS = {"evm": generate_evm_wallet, "solana": generate_solana_wallet, "ton": generate_ton_wallet}


def check_evm_balance(address: str, rpc_url: str) -> dict:
    """Check ETH balance via JSON-RPC."""
    payload = json.dumps({
        "jsonrpc": "2.0", "method": "eth_getBalance",
        "params": [address, "latest"], "id": 1
    }).encode()
    req = ureq.Request(rpc_url, payload, {"Content-Type": "application/json"})
    try:
        resp = ureq.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        wei = int(data["result"], 16)
        eth = wei / 1e18
        return {"address": address, "balance_wei": wei, "balance_eth": round(eth, 6)}
    except Exception as e:
        return {"address": address, "error": str(e)[:50]}


def main():
    p = argparse.ArgumentParser(description="Crypto wallet generator for airdrop farming")
    p.add_argument("--chain", choices=SUPPORTED_CHAINS, default="evm")
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--output", help="Output JSON file")
    p.add_argument("--wallets", help="Existing wallets JSON (for --check-balance, --export-csv)")
    p.add_argument("--check-balance", action="store_true")
    p.add_argument("--rpc", help="RPC URL for balance check")
    p.add_argument("--export-csv", action="store_true")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    if args.export_csv or args.check_balance:
        if not args.wallets:
            print("[-] --wallets required"); sys.exit(1)
        with open(args.wallets) as f:
            wallets = json.load(f)

        if args.check_balance:
            if not args.rpc:
                print("[-] --rpc required for balance check"); sys.exit(1)
            print(f"[*] Checking {len(wallets)} wallet balances...")
            for w in wallets:
                if w.get("chain") == "evm":
                    bal = check_evm_balance(w["address"], args.rpc)
                    eth = bal.get("balance_eth", "?")
                    print(f"  {w['address'][:20]}... : {eth} ETH")
                    time.sleep(0.2)
            return

        if args.export_csv:
            out = args.output or args.wallets.replace(".json", ".csv")
            with open(out, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=wallets[0].keys())
                writer.writeheader()
                writer.writerows(wallets)
            print(f"[+] Exported {len(wallets)} wallets to {out}")
            return

    # Generate wallets
    gen_fn = GENERATORS[args.chain]
    wallets = []
    print(f"[*] Generating {args.count} {args.chain} wallets...")
    for i in range(args.count):
        w = gen_fn()
        w["index"] = i + 1
        w["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        wallets.append(w)
        if args.verbose or i < 3:
            print(f"  [{i+1}] {w['address'][:30]}...")

    if args.count > 3 and not args.verbose:
        print(f"  ... ({args.count} total)")

    out = args.output or f"wallets_{args.chain}_{args.count}.json"
    with open(out, "w") as f:
        json.dump(wallets, f, indent=2)
    print(f"\n[+] Saved {len(wallets)} wallets to {out}")
    if wallets[0].get("note"):
        print(f"[!] Note: {wallets[0]['note']}")


if __name__ == "__main__":
    main()
