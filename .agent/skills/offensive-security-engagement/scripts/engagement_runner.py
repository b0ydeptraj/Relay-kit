#!/usr/bin/env python3
"""engagement_runner.py - Pentest engagement manager with scope, findings, CVSS scoring."""
import argparse, ipaddress, json, os, sys, time

PROOF = os.environ.get("ENGAGEMENT_PROOF","")
ENG_FILE = "engagement.json"
CVSS = {"CRITICAL":(9,10),"HIGH":(7,8.9),"MEDIUM":(4,6.9),"LOW":(0.1,3.9),"INFO":(0,0)}
CWE  = {"sql":"CWE-89","xss":"CWE-79","idor":"CWE-639","ssrf":"CWE-918","rce":"CWE-78"}

def load(f=ENG_FILE): return json.load(open(f)) if os.path.exists(f) else None
def save(d,f=ENG_FILE): json.dump(d,open(f,"w"),indent=2)

def init_eng(client,scope_file=None,out=ENG_FILE):
    scope=[]
    if scope_file and os.path.exists(scope_file):
        scope=[l.strip() for l in open(scope_file) if l.strip() and not l.startswith("#")]
    eng={"client":client,"date":time.strftime("%Y-%m-%d"),"proof":PROOF,
         "scope":scope,"findings":[],"stats":{s:0 for s in ("critical","high","medium","low","info")}}
    save(eng,out); print(f"[+] Engagement: {client} | {len(scope)} scope entries"); return eng

def in_scope(target,scope):
    t=target.lower().strip()
    for e in scope:
        e=e.lower().strip()
        if e in t or t in e: return True,e
        try:
            if ipaddress.ip_address(t) in ipaddress.ip_network(e,strict=False): return True,e
        except ValueError: pass
    return False,None

def add_finding(eng,title,sev,url=None,desc=None,impact=None,remed=None,cvss=None):
    sev=sev.upper()
    fid=f"FIND-{len(eng['findings'])+1:03d}"
    score=cvss or round(sum(CVSS.get(sev,(4,6.9)))/2,1)
    cwe=next((v for k,v in CWE.items() if k in title.lower()),"CWE-200")
    f={"id":fid,"title":title,"severity":sev,"cvss":score,"cwe":cwe,"url":url,
       "description":desc or title,"impact":impact or "TBD","remediation":remed or "TBD",
       "ts":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    eng["findings"].append(f); eng["stats"][sev.lower()]=eng["stats"].get(sev.lower(),0)+1
    print(f"[+] [{fid}] {sev} – {title} CVSS:{score}"); return f

def report_md(eng):
    lines=[f"# Report – {eng['client']}",f"**Date:** {eng['date']}","## Summary","||Count|","|---|---|"]
    for s in ("CRITICAL","HIGH","MEDIUM","LOW","INFO"):
        lines.append(f"|{s}|{eng['stats'].get(s.lower(),0)}|")
    lines.append("## Findings")
    for f in sorted(eng["findings"],key=lambda x:x.get("cvss",0),reverse=True):
        lines+=[f"### [{f['id']}] {f['title']}",
                f"**{f['severity']}** | CVSS:{f['cvss']} | {f['cwe']} | `{f.get('url','N/A')}`",
                f"**Desc:** {f['description']}  **Impact:** {f['impact']}  **Fix:** {f['remediation']}\n"]
    return "\n".join(lines)

def main():
    if not PROOF: print("[!] Set ENGAGEMENT_PROOF")
    p=argparse.ArgumentParser()
    p.add_argument("--init",action="store_true"); p.add_argument("--client")
    p.add_argument("--scope"); p.add_argument("--add-finding",action="store_true")
    p.add_argument("--title"); p.add_argument("--severity",choices=list(CVSS.keys()))
    p.add_argument("--url"); p.add_argument("--description"); p.add_argument("--cvss",type=float)
    p.add_argument("--impact"); p.add_argument("--remediation")
    p.add_argument("--report",action="store_true"); p.add_argument("--format",default="md")
    p.add_argument("--check-scope"); p.add_argument("--output")
    p.add_argument("--engagement-file",default=ENG_FILE)
    args=p.parse_args()
    if args.init:
        if not args.client: print("[-] --client required"); sys.exit(1)
        init_eng(args.client,args.scope,args.engagement_file); return
    eng=load(args.engagement_file)
    if not eng: print("[-] No engagement. Run --init"); sys.exit(1)
    if args.check_scope:
        ok,e=in_scope(args.check_scope,eng.get("scope",[]))
        print(f"[{'IN' if ok else 'OUT OF'} SCOPE] {args.check_scope}" +(f" -> {e}" if ok else "")); return
    if args.add_finding:
        if not args.title or not args.severity: print("[-] --title --severity required"); sys.exit(1)
        add_finding(eng,args.title,args.severity,args.url,args.description,args.impact,args.remediation,args.cvss)
        save(eng,args.engagement_file); return
    if args.report:
        rpt=report_md(eng) if args.format=="md" else json.dumps(eng,indent=2)
        out=args.output or f"report.{args.format}"
        open(out,"w").write(rpt); print(f"[+] Report: {out}")

if __name__=="__main__": main()
