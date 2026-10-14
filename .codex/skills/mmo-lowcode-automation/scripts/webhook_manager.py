#!/usr/bin/env python3
"""
webhook_manager.py - Manage webhook endpoints for n8n/Make/Zapier/custom low-code automation.

Usage:
    python scripts/webhook_manager.py --listen --port 9090 --secret MYSECRET
    python scripts/webhook_manager.py --trigger --url https://hook.example.com --payload payload.json
    python scripts/webhook_manager.py --test-n8n --url https://n8n.example.com/webhook/xxx
    python scripts/webhook_manager.py --forward --from 9090 --to https://hook.example.com
"""
import argparse
import json
import os
import sys
import time
import hashlib
import hmac
import urllib.request as ureq
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread


RECEIVED = []


def send_webhook(url: str, payload: dict, headers: dict = None, secret: str = None) -> dict:
    body = json.dumps(payload).encode()
    h = {"Content-Type": "application/json"}
    if headers: h.update(headers)
    if secret:
        sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        h["X-Hub-Signature-256"] = f"sha256={sig}"
    req = ureq.Request(url, body, h)
    start = time.time()
    try:
        resp = ureq.urlopen(req, timeout=30)
        elapsed = round((time.time() - start) * 1000)
        content = resp.read()
        return {"success": True, "status": resp.status, "elapsed_ms": elapsed,
                "response": content.decode()[:200]}
    except Exception as e:
        return {"success": False, "error": str(e)[:100]}


def start_listener(port: int, secret: str = None, forward_url: str = None):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body)
            except:
                payload = {"raw": body.decode()[:500]}

            ts = time.strftime("%H:%M:%S")
            print(f"\n[{ts}] Webhook received from {self.client_address[0]}:")
            print(f"  Path: {self.path}")
            print(f"  Payload: {json.dumps(payload)[:200]}")
            RECEIVED.append({"time": ts, "path": self.path, "payload": payload})

            if forward_url:
                r = send_webhook(forward_url, payload)
                print(f"  Forwarded: {r['status'] if r['success'] else r['error']}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())

        def log_message(self, *args): pass

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[*] Webhook listener on port {port}")
    print(f"[*] URL: http://0.0.0.0:{port}/webhook")
    if forward_url: print(f"[*] Forwarding to: {forward_url}")
    print("[*] Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n[*] Received {len(RECEIVED)} webhooks")


def main():
    p = argparse.ArgumentParser(description="Webhook manager for low-code automation")
    p.add_argument("--listen", action="store_true")
    p.add_argument("--port", type=int, default=9090)
    p.add_argument("--secret", help="Webhook signing secret")
    p.add_argument("--trigger", action="store_true")
    p.add_argument("--url", help="Webhook URL")
    p.add_argument("--payload", help="Payload JSON file or inline JSON")
    p.add_argument("--forward", help="Forward URL for received webhooks")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--delay", type=float, default=1.0)
    args = p.parse_args()

    if args.listen:
        start_listener(args.port, args.secret, args.forward)
    elif args.trigger:
        if not args.url: print("[-] --url required"); sys.exit(1)
        payload = {}
        if args.payload:
            if os.path.exists(args.payload):
                with open(args.payload) as f: payload = json.load(f)
            else:
                payload = json.loads(args.payload)
        for i in range(args.count):
            r = send_webhook(args.url, payload, secret=args.secret)
            print(f"  [{i+1}/{args.count}] {'OK' if r['success'] else 'FAIL'} | {r.get('elapsed_ms','?')}ms | {r.get('response','')[:80]}")
            if i < args.count - 1: time.sleep(args.delay)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
