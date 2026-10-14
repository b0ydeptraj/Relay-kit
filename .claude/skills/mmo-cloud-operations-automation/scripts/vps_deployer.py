#!/usr/bin/env python3
"""
vps_deployer.py - VPS fleet deployment and management for MMO cloud operations.
Manage DigitalOcean, Vultr, Hetzner, and Linode VPS instances at scale.

Usage:
    python scripts/vps_deployer.py --provider digitalocean --action list
    python scripts/vps_deployer.py --provider vultr --action create --count 5 --region fra --size 1gb
    python scripts/vps_deployer.py --provider hetzner --action delete --ids 12345,67890
    python scripts/vps_deployer.py --provider digitalocean --action ssh-all --cmd "uptime"

API keys: DO_API_KEY, VULTR_API_KEY, HETZNER_API_KEY env vars.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request as ureq

PROVIDERS = {
    "digitalocean": {"base": "https://api.digitalocean.com/v2", "key_env": "DO_API_KEY"},
    "vultr": {"base": "https://api.vultr.com/v2", "key_env": "VULTR_API_KEY"},
    "hetzner": {"base": "https://api.hetzner.cloud/v1", "key_env": "HETZNER_API_KEY"},
}


def api_call(provider: str, endpoint: str, method: str = "GET", data: dict = None) -> dict:
    cfg = PROVIDERS[provider]
    key = os.environ.get(cfg["key_env"], "")
    if not key:
        return {"error": f"Set {cfg['key_env']} env var"}
    url = cfg["base"] + endpoint
    payload = json.dumps(data).encode() if data else None
    req = ureq.Request(url, payload, {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }, method=method)
    try:
        resp = ureq.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)[:100]}


def list_vps(provider: str):
    if provider == "digitalocean":
        r = api_call("digitalocean", "/droplets")
        droplets = r.get("droplets", [])
        print(f"[*] DigitalOcean: {len(droplets)} droplets")
        for d in droplets:
            ip = d.get("networks",{}).get("v4",[{}])[0].get("ip_address","?")
            print(f"  {d['id']} | {d['name']} | {ip} | {d['status']} | {d['size']['slug']}")
    elif provider == "vultr":
        r = api_call("vultr", "/instances")
        instances = r.get("instances", [])
        print(f"[*] Vultr: {len(instances)} instances")
        for i in instances:
            print(f"  {i['id']} | {i['label']} | {i.get('main_ip','?')} | {i['status']}")
    elif provider == "hetzner":
        r = api_call("hetzner", "/servers")
        servers = r.get("servers", [])
        print(f"[*] Hetzner: {len(servers)} servers")
        for s in servers:
            ip = s.get("public_net",{}).get("ipv4",{}).get("ip","?")
            print(f"  {s['id']} | {s['name']} | {ip} | {s['status']}")


def create_vps(provider: str, count: int, region: str, size: str, image: str = "ubuntu-22-04-x64"):
    if provider == "digitalocean":
        for i in range(count):
            data = {"name": f"mmo-bot-{int(time.time())}-{i}", "region": region,
                    "size": size or "s-1vcpu-1gb", "image": image, "backups": False}
            r = api_call("digitalocean", "/droplets", "POST", data)
            droplet = r.get("droplet", {})
            print(f"  [+] Created: {droplet.get('id')} - {droplet.get('name')}")
            time.sleep(1)
    elif provider == "vultr":
        for i in range(count):
            data = {"label": f"mmo-bot-{i}", "region": region or "fra",
                    "plan": size or "vc2-1c-1gb", "os_id": 387}  # 387=Ubuntu 22.04
            r = api_call("vultr", "/instances", "POST", data)
            inst = r.get("instance", {})
            print(f"  [+] Created: {inst.get('id')} - {inst.get('label')}")
            time.sleep(1)
    else:
        print(f"[-] Create not implemented for {provider}")


def ssh_all(provider: str, cmd: str):
    """Run command on all VPS via SSH."""
    if provider == "digitalocean":
        r = api_call("digitalocean", "/droplets")
        droplets = r.get("droplets", [])
        for d in droplets:
            ip = d.get("networks",{}).get("v4",[{}])[0].get("ip_address","")
            if ip:
                result = subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no",
                                          f"root@{ip}", cmd], capture_output=True, text=True, timeout=15)
                print(f"  {ip}: {result.stdout.strip()[:80] or result.stderr.strip()[:80]}")


def main():
    p = argparse.ArgumentParser(description="VPS fleet deployer for MMO cloud ops")
    p.add_argument("--provider", choices=list(PROVIDERS.keys()), required=True)
    p.add_argument("--action", choices=["list","create","delete","ssh-all"], required=True)
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--region", default="fra")
    p.add_argument("--size", default="1gb")
    p.add_argument("--ids", help="Comma-separated IDs for delete")
    p.add_argument("--cmd", help="SSH command to run on all instances")
    args = p.parse_args()

    if args.action == "list": list_vps(args.provider)
    elif args.action == "create": create_vps(args.provider, args.count, args.region, args.size)
    elif args.action == "ssh-all":
        if not args.cmd: print("[-] --cmd required"); sys.exit(1)
        ssh_all(args.provider, args.cmd)
    elif args.action == "delete":
        if not args.ids: print("[-] --ids required"); sys.exit(1)
        for vid in args.ids.split(","):
            if args.provider == "digitalocean":
                r = api_call("digitalocean", f"/droplets/{vid.strip()}", "DELETE")
            elif args.provider == "vultr":
                r = api_call("vultr", f"/instances/{vid.strip()}", "DELETE")
            elif args.provider == "hetzner":
                r = api_call("hetzner", f"/servers/{vid.strip()}", "DELETE")
            print(f"  Deleted {vid}: {r}")


if __name__ == "__main__":
    main()
