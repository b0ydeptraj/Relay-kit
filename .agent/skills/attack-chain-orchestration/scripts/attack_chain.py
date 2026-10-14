#!/usr/bin/env python3
"""
attack_chain.py - Orchestrate multi-stage attack chains for authorized red team engagements.
Chains recon → exploit → post-exploitation → reporting with evidence capture.

Usage:
    python scripts/attack_chain.py --chain full --target 192.168.1.100 --proof PROOF-TOKEN
    python scripts/attack_chain.py --chain recon --target example.com --output recon.json
    python scripts/attack_chain.py --list-chains
    python scripts/attack_chain.py --chain webapp --target https://app.example.com --proof TOKEN

ENGAGEMENT_PROOF required for offensive stages.
"""
import argparse
import json
import os
import subprocess
import sys
import time

ENGAGEMENT_PROOF = os.environ.get("ENGAGEMENT_PROOF","")

ATTACK_CHAINS = {
    "recon": {
        "description": "Full reconnaissance chain",
        "stages": [
            {"name":"nmap-scan","skill":"network-scanner","script":"nmap_scan.py",
             "args":"--target {target} --ports 1-10000"},
            {"name":"subdomain-enum","skill":"dns-enumeration","script":"dns_enum.py",
             "args":"--domain {target} --ct-logs --subdomains"},
            {"name":"web-recon","skill":"web-app-scanner","script":"web_recon.py",
             "args":"--url https://{target}"},
        ],
        "requires_proof": False,
    },
    "webapp": {
        "description": "Web application attack chain",
        "stages": [
            {"name":"recon","skill":"web-app-scanner","script":"web_recon.py",
             "args":"--url {target}"},
            {"name":"vuln-scan","skill":"web-app-scanner","script":"vuln_checks.py",
             "args":"--url {target}"},
            {"name":"sqli-test","skill":"web-app-scanner","script":"sqli_test.py",
             "args":"--url {target}/search?q=TEST"},
            {"name":"api-fuzz","skill":"api-fuzzer","script":"api_fuzzer.py",
             "args":"--url {target}/api/users/{id} --fuzz-id --range 1-1000"},
        ],
        "requires_proof": True,
    },
    "network": {
        "description": "Network penetration chain",
        "stages": [
            {"name":"port-scan","skill":"network-scanner","script":"nmap_scan.py",
             "args":"--target {target} --ports top1000"},
            {"name":"vuln-lookup","skill":"vulnerability-lookup","script":"lookup_vuln.py",
             "args":"--target {target} --scan-results nmap_results.json"},
            {"name":"exploit-search","skill":"searching-exploit-db","script":"search_exploit_db.py",
             "args":"--keywords {target}"},
        ],
        "requires_proof": True,
    },
    "mobile": {
        "description": "Mobile app attack chain",
        "stages": [
            {"name":"apk-analyze","skill":"android-apk-pentester","script":"analyze_apk.py",
             "args":"--apk {target}"},
            {"name":"ssl-bypass","skill":"ssl-pinning-bypass","script":"frida_pinning_bypass.py",
             "args":"--package {target}"},
            {"name":"frida-hook","skill":"frida-hooker","script":"run_frida.py",
             "args":"--package {target} --mode intercept"},
        ],
        "requires_proof": True,
    },
    "full": {
        "description": "Full kill chain: recon → web → network → report",
        "stages": [
            {"name":"dns-enum","skill":"dns-enumeration","script":"dns_enum.py",
             "args":"--domain {target} --all"},
            {"name":"port-scan","skill":"network-scanner","script":"nmap_scan.py",
             "args":"--target {target}"},
            {"name":"web-scan","skill":"web-app-scanner","script":"scan_all.py",
             "args":"--url https://{target}"},
            {"name":"api-fuzz","skill":"api-fuzzer","script":"api_fuzzer.py",
             "args":"--url https://{target}/api/v1/users/{id} --fuzz-id"},
        ],
        "requires_proof": True,
    },
}

BASE_SKILLS = "C:\\Users\\Hiep\\Documents\\Relay-kit\\.agent\\skills"


def find_script(skill: str, script: str) -> str:
    path = os.path.join(BASE_SKILLS, skill, "scripts", script)
    return path if os.path.exists(path) else None


def run_stage(stage: dict, target: str, output_dir: str) -> dict:
    script_path = find_script(stage["skill"], stage["script"])
    if not script_path:
        return {"stage": stage["name"], "status": "SKIP",
                "reason": f"Script not found: {stage['skill']}/{stage['script']}"}

    args_str = stage.get("args","").format(target=target)
    stage_output = os.path.join(output_dir, f"{stage['name']}.json")
    cmd = f"python -X utf8 \"{script_path}\" {args_str} --output \"{stage_output}\""

    print(f"\n  [{stage['name']}] Running: {stage['skill']}/{stage['script']}")
    start = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    elapsed = round(time.time() - start, 1)

    status = "DONE" if result.returncode == 0 else "PARTIAL"
    output_snippet = (result.stdout + result.stderr)[:300]

    return {
        "stage": stage["name"], "status": status,
        "elapsed_s": elapsed, "output_file": stage_output,
        "snippet": output_snippet,
    }


def main():
    p = argparse.ArgumentParser(description="Attack chain orchestrator (authorized use only)")
    p.add_argument("--chain", choices=list(ATTACK_CHAINS.keys()))
    p.add_argument("--target", help="Target IP, domain, URL, or APK path")
    p.add_argument("--proof", default=ENGAGEMENT_PROOF)
    p.add_argument("--list-chains", action="store_true")
    p.add_argument("--output-dir", default="attack_results")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if args.list_chains:
        print("[*] Available attack chains:")
        for name, chain in ATTACK_CHAINS.items():
            req = "PROOF REQUIRED" if chain["requires_proof"] else "no auth"
            print(f"\n  [{name}] {chain['description']} ({req})")
            for s in chain["stages"]:
                print(f"    → {s['name']} ({s['skill']})")
        return

    if not args.chain or not args.target:
        print("[-] --chain and --target required"); sys.exit(1)

    chain = ATTACK_CHAINS[args.chain]
    if chain["requires_proof"] and not args.proof:
        print(f"[!] Chain '{args.chain}' requires ENGAGEMENT_PROOF")
        print(f"    Set: export ENGAGEMENT_PROOF=your-token")
        print(f"    Or: --proof your-token")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)
    print(f"\n[*] Attack Chain: {args.chain} | Target: {args.target}")
    print(f"[*] Stages: {len(chain['stages'])} | Output: {args.output_dir}")
    if args.proof:
        print(f"[*] Proof: {args.proof[:20]}...")

    results = []
    for stage in chain["stages"]:
        if args.dry_run:
            script = find_script(stage["skill"], stage["script"])
            status = "WOULD_RUN" if script else "MISSING"
            print(f"  [DRY-RUN] {stage['name']}: {stage['skill']}/{stage['script']} [{status}]")
            results.append({"stage": stage["name"], "status": status})
        else:
            r = run_stage(stage, args.target, args.output_dir)
            results.append(r)
            print(f"    Status: {r['status']} ({r.get('elapsed_s','?')}s)")

    # Summary
    done = sum(1 for r in results if r["status"] in ("DONE","WOULD_RUN"))
    print(f"\n[*] Chain complete: {done}/{len(results)} stages successful")

    report = {
        "chain": args.chain, "target": args.target,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "proof": args.proof[:10] + "..." if args.proof else None,
        "results": results,
    }
    report_path = os.path.join(args.output_dir, "chain_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"[+] Report: {report_path}")


if __name__ == "__main__":
    main()
