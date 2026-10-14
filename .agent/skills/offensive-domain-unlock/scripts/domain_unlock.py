#!/usr/bin/env python3
"""domain_unlock.py - Domain takeover detection: dangling DNS, expired services.
Usage:
    python scripts/domain_unlock.py --domain sub.example.com --check-takeover
    python scripts/domain_unlock.py --list subs.txt --scan
    python scripts/domain_unlock.py --list-services
ENGAGEMENT_PROOF required.
"""
import argparse, concurrent.futures, json, os, re, socket, subprocess, sys, time
import urllib.request as ureq, urllib.error

PROOF = os.environ.get("ENGAGEMENT_PROOF","")

TAKEOVER_SIGS = {
    "github-pages":    (r"github\.io", "There isn't a GitHub Pages site here", "Easy"),
    "aws-s3":          (r"s3\.amazonaws\.com", "NoSuchBucket", "Easy"),
    "heroku":          (r"herokudns\.com|herokuapp\.com", "No such app", "Easy"),
    "shopify":         (r"myshopify\.com", "Sorry, this shop is currently unavailable", "Easy"),
    "netlify":         (r"netlify\.app|netlify\.com", "Not Found - Request ID", "Easy"),
    "azure":           (r"azurewebsites\.net|trafficmanager\.net", "404 Web Site not found", "Medium"),
    "pantheon":        (r"pantheonsite\.io", "404 error unknown site", "Medium"),
    "zendesk":         (r"zendesk\.com", "Help Center Closed", "Medium"),
    "wordpress-com":   (r"wordpress\.com", "Do you want to register", "Easy"),
    "fastly":          (r"fastly\.net", "Fastly error: unknown domain", "Medium"),
    "read-the-docs":   (r"readthedocs\.io", "is not a registered Read the Docs website", "Easy"),
}

def get_cname(domain):
    try:
        r=subprocess.run(["dig","+short","CNAME",domain],capture_output=True,text=True,timeout=8)
        return r.stdout.strip().rstrip(".")
    except: pass
    try:
        socket.getaddrinfo(domain,None); return ""
    except socket.gaierror: return "NXDOMAIN"

def http_body(domain, timeout=8):
    for scheme in ("https","http"):
        try:
            resp=ureq.urlopen(ureq.Request(f"{scheme}://{domain}",
                              headers={"User-Agent":"Mozilla/5.0"}),timeout=timeout)
            return resp.status, resp.read(4096).decode("utf-8","replace")
        except ureq.error.HTTPError as e:
            body=e.read(4096).decode("utf-8","replace") if e.fp else ""
            return e.code, body
        except: pass
    return 0, ""

def check_takeover(domain):
    cname=get_cname(domain)
    result={"domain":domain,"cname":cname,"vulnerable":False,"service":None}
    if cname=="NXDOMAIN":
        result.update({"vulnerable":True,"service":"dangling-nxdomain","note":"DNS points to nothing"}); return result
    status,body=http_body(domain)
    for svc,(pat,fp,diff) in TAKEOVER_SIGS.items():
        if re.search(pat,cname,re.I):
            if fp.lower() in body.lower():
                result.update({"vulnerable":True,"service":svc,"difficulty":diff,
                               "fingerprint":fp,"cname":cname}); return result
            result["note"]=f"CNAME={svc} but fingerprint not confirmed"
            result["service"]=svc; break
    return result

def scan_list(domains, threads=20):
    vulns=[]
    def check(d):
        r=check_takeover(d)
        if r["vulnerable"]:
            print(f"  [!!!] VULN: {d} -> {r.get('service','?')} [{r.get('difficulty','?')}]")
            vulns.append(r)
        else: print(f"  [ok]  {d}: {r.get('cname','?')[:50]}")
        return r
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futs={ex.submit(check,d):d for d in domains}
        for f in concurrent.futures.as_completed(futs):
            try: results.append(f.result())
            except Exception as e: results.append({"domain":futs[f],"error":str(e)[:50]})
    return results, vulns

def main():
    if not PROOF: print("[!] Set ENGAGEMENT_PROOF. Authorized testing only.")
    p=argparse.ArgumentParser()
    p.add_argument("--domain"); p.add_argument("--check-takeover",action="store_true")
    p.add_argument("--list",help="File with subdomains")
    p.add_argument("--scan",action="store_true"); p.add_argument("--threads",type=int,default=20)
    p.add_argument("--list-services",action="store_true"); p.add_argument("--output")
    args=p.parse_args()

    if args.list_services:
        print("[*] Takeover-vulnerable services:")
        for svc,(pat,fp,diff) in TAKEOVER_SIGS.items():
            print(f"  [{diff}] {svc}: fingerprint='{fp}'"); return

    if args.domain and args.check_takeover:
        r=check_takeover(args.domain)
        if r["vulnerable"]:
            print(f"\n[!!!] VULNERABLE: {args.domain} -> {r.get('service','?')} [{r.get('difficulty','?')}]")
            print(f"  CNAME: {r.get('cname','?')}")
        else: print(f"[*] Not vulnerable: {args.domain} | {r.get('note','')}")
        if args.output: json.dump(r,open(args.output,"w"),indent=2)
        return

    if args.list and args.scan:
        subs=[l.strip() for l in open(args.list) if l.strip()]
        print(f"[*] Scanning {len(subs)} subdomains...")
        results,vulns=scan_list(subs,args.threads)
        print(f"\n[*] Vulnerable: {len(vulns)}/{len(results)}")
        for v in vulns: print(f"  {v['domain']} -> {v.get('service','?')} [{v.get('difficulty','?')}]")
        if args.output: json.dump({"total":len(results),"vulnerable":vulns},open(args.output,"w"),indent=2)
        return
    p.print_help()

if __name__=="__main__": main()
