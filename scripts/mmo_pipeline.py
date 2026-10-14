#!/usr/bin/env python3
"""
mmo_pipeline.py - MMO workflow dispatcher: classify task -> route to correct MMO skill chain.

Routing logic:
    account-create    -> mmo-sms-otp-automation -> mmo-identity-infrastructure -> mmo-account-operations
    browser-fleet     -> mmo-anti-detection-browser -> mmo-proxy-network-ops -> mmo-browser-fleet-automation
    social-post       -> mmo-social-marketing-automation -> mmo-content-factory
    warmup            -> mmo-nick-warmup-engine -> mmo-account-operations
    captcha-solve     -> mmo-captcha-farm -> antibot-challenge-solving
    harvest-data      -> mmo-data-harvesting -> mmo-http-api-automation

Usage:
    python scripts/mmo_pipeline.py account-create --platform tiktok --count 10
    python scripts/mmo_pipeline.py browser-fleet   --profiles 20 --proxy-file proxies.txt
    python scripts/mmo_pipeline.py captcha-solve   --type recaptchav2 --sitekey KEY --url URL
    python scripts/mmo_pipeline.py warmup          --platform tiktok --accounts accounts.json
    python scripts/mmo_pipeline.py --dry-run account-create --platform facebook
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON    = sys.executable

# Skill routing map: task -> ordered skill chain
PIPELINE_ROUTES = {
    "account-create": {
        "description": "Create accounts: SMS verify -> identity generate -> register",
        "skills": ["mmo-sms-otp-automation", "mmo-identity-infrastructure", "mmo-account-operations"],
        "script": "scripts/sms_otp.py",
        "params": "--platform {platform}",
    },
    "browser-fleet": {
        "description": "Launch browser fleet: anti-detect browser -> proxy assign -> fleet operate",
        "skills": ["mmo-anti-detection-browser", "mmo-proxy-network-ops", "mmo-browser-fleet-automation"],
        "script": "scripts/profile_manager.py",
        "params": "--browser gologin --action list",
    },
    "captcha-solve": {
        "description": "Solve CAPTCHA: farm manager -> service fallback -> deliver token",
        "skills": ["mmo-captcha-farm", "antibot-challenge-solving"],
        "script": "scripts/captcha_farm.py",
        "params": "--config captcha_keys.json --type {type} --sitekey {sitekey} --url {url}",
    },
    "social-post": {
        "description": "Post content: content factory -> social marketing automation",
        "skills": ["mmo-content-factory", "mmo-social-marketing-automation"],
        "script": None,  # Manual orchestration required
        "params": None,
    },
    "warmup": {
        "description": "Warmup accounts: activity simulation -> nick warmup engine",
        "skills": ["mmo-nick-warmup-engine", "mmo-account-operations"],
        "script": None,
        "params": None,
    },
    "harvest-data": {
        "description": "Harvest data: HTTP API automation -> data harvesting pipeline",
        "skills": ["mmo-http-api-automation", "mmo-data-harvesting"],
        "script": None,
        "params": None,
    },
    "proxy-check": {
        "description": "Check proxy pool health and rotate bad proxies",
        "skills": ["mmo-proxy-network-ops"],
        "script": None,
        "params": None,
    },
    "video-reup": {
        "description": "Offline Video Reup & Anti-Copyright Engine: download & mutate fingerprints",
        "skills": ["mmo-reup-automation", "mmo-content-factory"],
        "script": "scripts/video_reup.py",
        "params": "batch {input_dir} --preset {preset}",
    },
}


def route_request(task: str, args_dict: dict, dry_run: bool = False) -> dict:
    if task not in PIPELINE_ROUTES:
        print(f"[-] Unknown task: {task}")
        print(f"[*] Available: {', '.join(PIPELINE_ROUTES.keys())}")
        return {"error": f"Unknown task: {task}"}

    route = PIPELINE_ROUTES[task]
    print(f"\n[*] MMO Pipeline: {task}")
    print(f"[*] Description : {route['description']}")
    print(f"[*] Skill chain : {' -> '.join(route['skills'])}")

    if dry_run:
        print("\n[DRY-RUN] Would execute:")
        if route["script"]:
            if (REPO_ROOT / route["script"]).exists():
                script_path = REPO_ROOT / route["script"]
            else:
                script_path = REPO_ROOT / ".agent" / "skills" / route["skills"][0] / route["script"]
            params = route["params"].format(**args_dict) if route["params"] else ""
            print(f"  python {script_path} {params}")
        else:
            print(f"  [Manual orchestration required - no automated script for {task}]")
            print(f"  [Invoke skills in order: {' -> '.join(route['skills'])}]")
        return {"dry_run": True, "task": task, "chain": route["skills"]}

    # Execute
    if not route["script"]:
        print(f"\n[!] This pipeline requires manual orchestration.")
        print(f"[*] Invoke these skills in sequence:")
        for i, skill in enumerate(route["skills"]):
            print(f"  {i+1}. {skill}")
        return {"status": "manual_required", "skills": route["skills"]}

    if (REPO_ROOT / route["script"]).exists():
        script_path = REPO_ROOT / route["script"]
    else:
        skill_dir = REPO_ROOT / ".agent" / "skills" / route["skills"][0]
        script_path = skill_dir / route["script"]

    if not script_path.exists():
        print(f"[-] Script not found: {script_path}")
        return {"error": f"Script not found: {script_path}"}

    params_str = route["params"].format(**{**args_dict, **{k: args_dict.get(k, "") for k in args_dict}}) \
                 if route["params"] else ""
    cmd = [PYTHON, str(script_path)] + params_str.split()

    print(f"\n[*] Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[-] Error: {result.stderr[:500]}")
    return {"returncode": result.returncode, "stdout": result.stdout, "task": task}


def main():
    p = argparse.ArgumentParser(description="MMO pipeline dispatcher")
    p.add_argument("task", nargs="?", choices=list(PIPELINE_ROUTES.keys()), help="Pipeline task")
    p.add_argument("--platform", default="tiktok")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--proxy-file")
    p.add_argument("--profiles", type=int, default=5)
    p.add_argument("--sitekey")
    p.add_argument("--url")
    p.add_argument("--type", default="recaptchav2")
    p.add_argument("--accounts")
    p.add_argument("--input-dir", default="raw_videos")
    p.add_argument("--preset", default="balanced")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--list-routes", action="store_true")
    args = p.parse_args()

    if args.list_routes or not args.task:
        print("[*] MMO Pipeline Routes:")
        for name, route in PIPELINE_ROUTES.items():
            print(f"  {name:<20} {route['description']}")
            print(f"   Chain: {' -> '.join(route['skills'])}")
        return

    args_dict = {
        "platform": args.platform, "count": args.count,
        "sitekey": args.sitekey or "", "url": args.url or "",
        "type": args.type, "profiles": args.profiles,
        "input_dir": args.input_dir, "preset": args.preset,
    }
    route_request(args.task, args_dict, args.dry_run)


if __name__ == "__main__":
    main()

