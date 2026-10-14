#!/usr/bin/env python3
"""
dns_enum.py - Comprehensive DNS enumeration tool.
Zone transfer, record collection, subdomain brute force, and CT log query.

Usage:
    python scripts/dns_enum.py --domain example.com --all
    python scripts/dns_enum.py --domain example.com --records A,AAAA,MX,TXT,NS,CNAME
    python scripts/dns_enum.py --domain example.com --subdomains --wordlist subs.txt
    python scripts/dns_enum.py --domain example.com --zone-transfer
    python scripts/dns_enum.py --domain example.com --ct-logs --output results.json

Engagement proof: set ENGAGEMENT_PROOF env var.
"""
import argparse
import concurrent.futures
import json
import os
import socket
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF", "")

# Built-in small subdomain wordlist
DEFAULT_SUBS = [
    "www","mail","ftp","smtp","pop","imap","remote","vpn","api","app","dev","staging",
    "test","beta","admin","portal","intranet","internal","secure","cdn","media","static",
    "img","images","assets","blog","shop","store","pay","payment","checkout","support",
    "help","docs","wiki","git","gitlab","github","jenkins","jira","confluence","grafana",
    "monitoring","dashboard","panel","cpanel","webmail","owa","autodiscover","mx","ns",
    "ns1","ns2","dns","mail2","smtp2","relay","m","mobile","wap","api2","backend",
    "server","server1","server2","web","web1","web2","db","database","mysql","redis",
    "elasticsearch","kibana","prometheus","nagios","zabbix","backup","vpn2",
]

RECORD_TYPES = ["A","AAAA","MX","TXT","NS","CNAME","SOA","SRV","PTR","CAA","DKIM","DMARC"]


def dns_query(host: str, record_type: str, timeout: float = 5) -> list:
    """Simple DNS query using socket (no dnspython required)."""
    if record_type == "A":
        try:
            results = socket.getaddrinfo(host, None, socket.AF_INET)
            return list(set(r[4][0] for r in results))
        except: return []
    elif record_type == "AAAA":
        try:
            results = socket.getaddrinfo(host, None, socket.AF_INET6)
            return list(set(r[4][0] for r in results))
        except: return []
    else:
        # Use system dig/nslookup for other types
        try:
            import subprocess
            result = subprocess.run(
                ["dig", "+short", host, record_type],
                capture_output=True, text=True, timeout=timeout
            )
            lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
            return lines
        except:
            try:
                result = subprocess.run(
                    ["nslookup", f"-type={record_type}", host],
                    capture_output=True, text=True, timeout=timeout
                )
                # Parse nslookup output
                lines = [l.strip() for l in result.stdout.split("\n")]
                return [l for l in lines if l and not l.startswith(("Server","Address","Non-authoritative"))]
            except:
                return []


def zone_transfer(domain: str) -> dict:
    """Attempt DNS zone transfer (AXFR) on all nameservers."""
    if not ENGAGEMENT_PROOF:
        print("[!] Set ENGAGEMENT_PROOF for zone transfer attempts")
    results = {}
    ns_records = dns_query(domain, "NS")
    print(f"[*] Zone transfer attempt on {len(ns_records)} nameservers...")
    for ns in ns_records:
        ns = ns.rstrip(".")
        try:
            import subprocess
            result = subprocess.run(["dig", "AXFR", domain, f"@{ns}"],
                                     capture_output=True, text=True, timeout=30)
            if "Transfer failed" not in result.stdout and result.returncode == 0:
                lines = [l for l in result.stdout.split("\n") if l and not l.startswith(";")]
                if len(lines) > 5:
                    results[ns] = {"success": True, "records": lines[:50]}
                    print(f"  [+] ZONE TRANSFER SUCCESS on {ns}! {len(lines)} records")
                else:
                    results[ns] = {"success": False}
                    print(f"  [-] {ns}: transfer failed or empty")
            else:
                results[ns] = {"success": False}
                print(f"  [-] {ns}: AXFR refused")
        except FileNotFoundError:
            print("  [-] dig not found. Install: bind-utils / dnsutils")
            break
        except Exception as e:
            results[ns] = {"success": False, "error": str(e)[:50]}
    return results


def collect_records(domain: str, types: list = None) -> dict:
    """Collect all DNS records for a domain."""
    types = types or ["A","AAAA","MX","TXT","NS","CNAME","SOA"]
    results = {}
    for rtype in types:
        records = dns_query(domain, rtype)
        if records:
            results[rtype] = records
            print(f"  {rtype:8} {records[:3]}")
    return results


def brute_subdomains(domain: str, wordlist: list, threads: int = 50) -> list:
    """Brute force subdomains using word list."""
    found = []
    lock = __import__("threading").Lock()
    total = len(wordlist)
    done = [0]

    def check_sub(sub: str):
        fqdn = f"{sub}.{domain}"
        ips = dns_query(fqdn, "A")
        with lock:
            done[0] += 1
            if ips:
                found.append({"subdomain": fqdn, "ips": ips})
                print(f"  [+] {fqdn} -> {ips}")
            elif done[0] % 100 == 0:
                print(f"  [*] {done[0]}/{total} checked, {len(found)} found...", end="\r")

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        ex.map(check_sub, wordlist)
    print()
    return found


def ct_log_query(domain: str) -> list:
    """Query crt.sh certificate transparency logs for subdomains."""
    url = f"https://crt.sh/?q=%.{uparse.quote(domain)}&output=json"
    try:
        req = ureq.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = ureq.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        subdomains = set()
        for cert in data:
            name = cert.get("name_value", "")
            for sub in name.split("\n"):
                sub = sub.strip().lstrip("*.")
                if sub.endswith(f".{domain}") or sub == domain:
                    subdomains.add(sub)
        subs_list = sorted(subdomains)
        print(f"[*] CT logs: {len(subs_list)} unique subdomains found")
        return subs_list
    except Exception as e:
        print(f"[-] CT log query failed: {e}")
        return []


def reverse_dns(ips: list) -> dict:
    """Perform reverse DNS lookups on a list of IPs."""
    results = {}
    for ip in ips:
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            results[ip] = hostname
            print(f"  {ip} -> {hostname}")
        except:
            results[ip] = None
    return results


def main():
    if not ENGAGEMENT_PROOF:
        print("[!] WARNING: Set ENGAGEMENT_PROOF. Only scan authorized domains.")

    p = argparse.ArgumentParser(description="DNS enumeration toolkit (authorized use only)")
    p.add_argument("--domain", required=True)
    p.add_argument("--all", action="store_true", help="Run all enumeration methods")
    p.add_argument("--records", help="Record types: A,AAAA,MX,TXT,NS")
    p.add_argument("--subdomains", action="store_true")
    p.add_argument("--wordlist", help="Subdomain wordlist file")
    p.add_argument("--zone-transfer", action="store_true")
    p.add_argument("--ct-logs", action="store_true")
    p.add_argument("--reverse-dns", help="IP range or comma-separated IPs")
    p.add_argument("--threads", type=int, default=50)
    p.add_argument("--output", help="Results JSON file")
    args = p.parse_args()

    domain = args.domain.strip().lower()
    print(f"\n[*] DNS Enumeration: {domain}")
    print(f"[*] Engagement proof: {'SET' if ENGAGEMENT_PROOF else 'NOT SET'}\n")

    report = {"domain": domain, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    if args.all or args.records:
        types = [t.strip().upper() for t in args.records.split(",")] if args.records else ["A","AAAA","MX","TXT","NS","SOA","CAA"]
        print(f"[*] Collecting {types} records...")
        report["dns_records"] = collect_records(domain, types)

    if args.all or args.zone_transfer:
        print(f"\n[*] Zone transfer attempt...")
        report["zone_transfer"] = zone_transfer(domain)

    if args.all or args.ct_logs:
        print(f"\n[*] Certificate Transparency logs...")
        ct_subs = ct_log_query(domain)
        report["ct_subdomains"] = ct_subs

    if args.all or args.subdomains:
        if args.wordlist and os.path.exists(args.wordlist):
            with open(args.wordlist) as f:
                wordlist = [l.strip() for l in f if l.strip()]
        else:
            wordlist = DEFAULT_SUBS
            print(f"[*] Using built-in wordlist ({len(wordlist)} entries)")
        print(f"\n[*] Subdomain brute force ({len(wordlist)} words, {args.threads} threads)...")
        report["subdomains_found"] = brute_subdomains(domain, wordlist, args.threads)

    if args.reverse_dns:
        ips = [ip.strip() for ip in args.reverse_dns.split(",")]
        print(f"\n[*] Reverse DNS for {len(ips)} IPs...")
        report["reverse_dns"] = reverse_dns(ips)

    # Summary
    print(f"\n[*] Summary:")
    print(f"  DNS records: {len(report.get('dns_records',{}))}")
    print(f"  Subdomains (CT): {len(report.get('ct_subdomains',[]))}")
    print(f"  Subdomains (brute): {len(report.get('subdomains_found',[]))}")
    if report.get("zone_transfer"):
        zt_success = sum(1 for v in report["zone_transfer"].values() if v.get("success"))
        print(f"  Zone transfer: {zt_success} successful")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n[+] Saved: {args.output}")


if __name__ == "__main__":
    main()
