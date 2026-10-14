#!/usr/bin/env python3
"""ir_toolkit.py - Incident Response: triage, artifact collection, persistence check, IOC hunt.
Usage:
    python scripts/ir_toolkit.py --triage
    python scripts/ir_toolkit.py --persistence-check
    python scripts/ir_toolkit.py --hunt-iocs --ioc-file iocs.txt
    python scripts/ir_toolkit.py --network-connections
"""
import argparse, hashlib, json, os, platform, re, subprocess, sys, time

IS_WIN = sys.platform == "win32"

def run(cmd, timeout=20):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          shell=isinstance(cmd,str))
        return r.stdout.strip()
    except Exception as e: return f"ERR:{e}"

def sysinfo():
    d={"hostname":platform.node(),"os":platform.platform(),"arch":platform.machine(),
       "ts":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
       "user":os.environ.get("USERNAME") or os.environ.get("USER","?")}
    if IS_WIN: d["whoami"]=run("whoami")
    else: d["whoami"]=run(["whoami"])
    return d

def processes():
    if IS_WIN:
        out=run("tasklist /FO CSV /NH")
        procs=[]
        for l in out.split("\n"):
            p=l.strip('"').split('","')
            if len(p)>=2: procs.append({"name":p[0],"pid":p[1]})
        return procs
    out=run(["ps","aux","--no-header"])
    return [{"user":p[0],"pid":p[1],"cmd":p[10][:80]} for l in out.split("\n")
            if l and (p:=l.split(None,10)) and len(p)>=11]

def netconns():
    out=run("netstat -ano" if IS_WIN else ["ss","-tupn"])
    return [l.strip() for l in out.split("\n")
            if any(x in l for x in ("ESTABLISHED","LISTEN","SYN_SENT"))]

def persistence_win():
    findings=[]
    for key in [r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"]:
        out=run(f'reg query "{key}" 2>nul',timeout=8)
        if out and "ERROR" not in out:
            for l in out.split("\n"):
                if "REG_" in l: findings.append({"type":"registry","key":key,"value":l.strip()[:150]})
    tasks=run("schtasks /query /FO CSV /NH",timeout=12)
    suspicious=[l.strip()[:80] for l in tasks.split("\n")
                if l and "\\Microsoft\\" not in l and len(l)>10]
    if suspicious: findings.append({"type":"sched_tasks","count":len(suspicious),"sample":suspicious[:5]})
    return findings

def hunt_iocs(ioc_file, search_paths=None):
    iocs={"hash":[],"ip":[],"domain":[],"path":[]}
    with open(ioc_file) as f:
        for l in f:
            l=l.strip()
            if not l or l.startswith("#"): continue
            if re.match(r'^[a-fA-F0-9]{32,64}$',l): iocs["hash"].append(l.lower())
            elif re.match(r'^\d+\.\d+\.\d+\.\d+$',l): iocs["ip"].append(l)
            elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',l): iocs["domain"].append(l)
            else: iocs["path"].append(l)
    print(f"[*] IOCs: hash={len(iocs['hash'])} ip={len(iocs['ip'])} domain={len(iocs['domain'])}")
    hits=[]
    paths=search_paths or (["C:\\Users","C:\\Windows\\Temp"] if IS_WIN else ["/tmp","/var","/home"])
    if iocs["hash"]:
        for sp in paths:
            if not os.path.exists(sp): continue
            for root,dirs,files in os.walk(sp):
                dirs[:]=dirs[:10]
                for fn in files[:30]:
                    fp=os.path.join(root,fn)
                    try:
                        h=hashlib.sha256(open(fp,"rb").read()).hexdigest()
                        if h in iocs["hash"]:
                            hits.append({"type":"hash","value":h,"path":fp})
                            print(f"  [HIT] {fp}")
                    except: pass
    return hits

def main():
    p=argparse.ArgumentParser(description="Incident Response toolkit")
    p.add_argument("--triage",action="store_true")
    p.add_argument("--persistence-check",action="store_true")
    p.add_argument("--network-connections",action="store_true")
    p.add_argument("--hunt-iocs",help="IOC file path")
    p.add_argument("--output",default="ir_evidence")
    args=p.parse_args()
    os.makedirs(args.output,exist_ok=True)
    report={"ts":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())}
    if args.triage:
        print("[*] System triage...")
        report["system"]=sysinfo()
        for k,v in report["system"].items(): print(f"  {k}: {v}")
        procs=processes(); report["processes"]=procs; print(f"[*] Processes: {len(procs)}")
        conns=netconns(); report["connections"]=conns; print(f"[*] Connections: {len(conns)}")
    if args.persistence_check:
        if IS_WIN:
            print("[*] Persistence check...")
            findings=persistence_win(); report["persistence"]=findings
            print(f"  Items: {len(findings)}")
            for f in findings[:5]: print(f"  [{f['type']}] {str(f)[:100]}")
        else: print("[!] Full persistence check requires Windows")
    if args.network_connections:
        print("[*] Network connections:")
        for c in netconns()[:20]: print(f"  {c}")
    if args.hunt_iocs:
        hits=hunt_iocs(args.hunt_iocs); report["ioc_hits"]=hits
        print(f"[*] IOC hits: {len(hits)}")
    out=os.path.join(args.output,"ir_report.json")
    json.dump(report,open(out,"w"),indent=2,default=str)
    print(f"[+] IR Report: {out}")

if __name__=="__main__": main()
