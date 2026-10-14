#!/usr/bin/env python3
"""
prompt_rotator.py - LLM API pool manager with key rotation, rate limiting and cost tracking.
Manages multiple OpenAI/Gemini/Claude/Groq API keys for high-volume LLM automation.

Usage:
    python scripts/prompt_rotator.py --prompt "Write a product description for {product}" --var product="iPhone 16" --count 50
    python scripts/prompt_rotator.py --template template.txt --input items.json --output results.json
    python scripts/prompt_rotator.py --check-keys --config api_keys.json
    python scripts/prompt_rotator.py --benchmark --config api_keys.json --prompt "Say hello"

api_keys.json: {"openai": ["key1","key2"], "gemini": ["key3"], "groq": ["key4"]}
"""
import argparse
import json
import os
import random
import sys
import time
import urllib.request as ureq
from datetime import datetime

LOG_FILE = "llm_usage.jsonl"

ENDPOINTS = {
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-3.5-turbo",
        "cost_per_1k_tokens": 0.002,
        "rpm_limit": 60,
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        "model": "gemini-pro",
        "cost_per_1k_tokens": 0.0005,
        "rpm_limit": 60,
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "mixtral-8x7b-32768",
        "cost_per_1k_tokens": 0.0001,
        "rpm_limit": 30,
    },
}


class APIKeyPool:
    def __init__(self, config: dict):
        self.keys = {}
        self.call_times = {}  # key -> list of timestamps
        for service, keys in config.items():
            if service in ENDPOINTS:
                self.keys[service] = [{"key": k, "calls": 0, "errors": 0, "tokens": 0, "banned": False}
                                       for k in keys]
                self.call_times[service] = {k: [] for k in keys}

    def get_key(self, service: str = None) -> tuple:
        """Get next available API key."""
        if service and service in self.keys:
            services = [service]
        else:
            services = list(self.keys.keys())

        # Sort by load
        for svc in services:
            available = [k for k in self.keys.get(svc, []) if not k["banned"]]
            if not available:
                continue
            # Rate limit check
            rpm = ENDPOINTS[svc]["rpm_limit"]
            now = time.time()
            for key_info in sorted(available, key=lambda x: x["calls"]):
                k = key_info["key"]
                recent = [t for t in self.call_times[svc].get(k, []) if now - t < 60]
                self.call_times[svc][k] = recent
                if len(recent) < rpm:
                    return svc, key_info
        return None, None

    def record_call(self, service: str, key_info: dict, tokens: int = 0, error: bool = False):
        key_info["calls"] += 1
        key_info["tokens"] += tokens
        if error:
            key_info["errors"] += 1
            if key_info["errors"] >= 5:
                key_info["banned"] = True
                print(f"[-] API key banned after errors: {key_info['key'][:20]}...")
        self.call_times[service][key_info["key"]].append(time.time())

    def stats(self) -> dict:
        result = {}
        for svc, keys in self.keys.items():
            result[svc] = {
                "total_keys": len(keys),
                "active": sum(1 for k in keys if not k["banned"]),
                "total_calls": sum(k["calls"] for k in keys),
                "total_tokens": sum(k["tokens"] for k in keys),
                "est_cost_usd": round(sum(k["tokens"] for k in keys) / 1000 * ENDPOINTS[svc]["cost_per_1k_tokens"], 4),
            }
        return result


def call_openai(key: str, prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 500) -> dict:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = ureq.Request(ENDPOINTS["openai"]["url"], payload,
                       {"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    start = time.time()
    try:
        resp = ureq.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", len(text.split()) * 2)
        return {"success": True, "text": text, "tokens": tokens, "elapsed_ms": round((time.time()-start)*1000)}
    except Exception as e:
        return {"success": False, "error": str(e)[:100], "elapsed_ms": round((time.time()-start)*1000)}


def call_gemini(key: str, prompt: str, max_tokens: int = 500) -> dict:
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens}
    }).encode()
    url = f"{ENDPOINTS['gemini']['url']}?key={key}"
    req = ureq.Request(url, payload, {"Content-Type": "application/json"})
    start = time.time()
    try:
        resp = ureq.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        tokens = len(text.split()) * 2
        return {"success": True, "text": text, "tokens": tokens, "elapsed_ms": round((time.time()-start)*1000)}
    except Exception as e:
        return {"success": False, "error": str(e)[:100], "elapsed_ms": round((time.time()-start)*1000)}


def call_groq(key: str, prompt: str, model: str = "mixtral-8x7b-32768", max_tokens: int = 500) -> dict:
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }).encode()
    req = ureq.Request(ENDPOINTS["groq"]["url"], payload,
                       {"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    start = time.time()
    try:
        resp = ureq.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", len(text.split()) * 2)
        return {"success": True, "text": text, "tokens": tokens, "elapsed_ms": round((time.time()-start)*1000)}
    except Exception as e:
        return {"success": False, "error": str(e)[:100], "elapsed_ms": round((time.time()-start)*1000)}


CALLERS = {"openai": call_openai, "gemini": call_gemini, "groq": call_groq}


def run_prompt(pool: APIKeyPool, prompt: str, service: str = None, max_tokens: int = 500) -> dict:
    svc, key_info = pool.get_key(service)
    if not svc:
        return {"success": False, "error": "No available API keys"}
    key = key_info["key"]
    result = CALLERS[svc](key, prompt, max_tokens=max_tokens)
    pool.record_call(svc, key_info, result.get("tokens", 0), not result["success"])
    result["service"] = svc
    # Log
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({"ts": datetime.utcnow().isoformat(), **result, "prompt_len": len(prompt)}) + "\n")
    return result


def batch_process(pool: APIKeyPool, template: str, items: list, output: str, delay: float = 0.5):
    results = []
    for i, item in enumerate(items):
        if isinstance(item, dict):
            prompt = template.format(**item)
            meta = item
        else:
            prompt = template.replace("{item}", str(item))
            meta = {"item": item}

        r = run_prompt(pool, prompt)
        results.append({**meta, "output": r.get("text", ""), "success": r["success"],
                        "service": r.get("service"), "tokens": r.get("tokens", 0)})
        status = "OK" if r["success"] else "FAIL"
        print(f"  [{i+1}/{len(items)}] [{status}] {r.get('service','?')} | {r.get('elapsed_ms','?')}ms | {r.get('tokens','?')} tokens")
        if not r["success"]:
            print(f"    Error: {r.get('error','')}")
        time.sleep(delay)

    with open(output, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Saved {len(results)} results to {output}")
    print(f"[*] Pool stats: {json.dumps(pool.stats(), indent=2)}")


def main():
    p = argparse.ArgumentParser(description="LLM API pool manager and prompt rotator")
    p.add_argument("--config", default="api_keys.json", help="API keys config JSON")
    p.add_argument("--prompt", help="Prompt template (use {var} for variables)")
    p.add_argument("--var", nargs="+", help="Variables: key=value pairs")
    p.add_argument("--template", help="Prompt template text file")
    p.add_argument("--input", help="Input items JSON (list of dicts or strings)")
    p.add_argument("--output", default="llm_results.json")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--service", choices=["openai","gemini","groq"])
    p.add_argument("--max-tokens", type=int, default=500)
    p.add_argument("--delay", type=float, default=0.5)
    p.add_argument("--check-keys", action="store_true")
    p.add_argument("--benchmark", action="store_true")
    args = p.parse_args()

    config = {}
    if os.path.exists(args.config):
        with open(args.config) as f:
            config = json.load(f)
    else:
        # Use env vars as fallback
        if os.environ.get("OPENAI_API_KEY"): config["openai"] = [os.environ["OPENAI_API_KEY"]]
        if os.environ.get("GEMINI_API_KEY"):  config["gemini"] = [os.environ["GEMINI_API_KEY"]]
        if os.environ.get("GROQ_API_KEY"):    config["groq"]   = [os.environ["GROQ_API_KEY"]]

    if not config:
        print("[-] No API keys. Create api_keys.json or set OPENAI_API_KEY/GEMINI_API_KEY/GROQ_API_KEY")
        sys.exit(1)

    pool = APIKeyPool(config)
    print(f"[*] Pool: {json.dumps(pool.stats())}")

    if args.check_keys:
        test_prompt = "Reply with just: OK"
        for svc in pool.keys:
            r = run_prompt(pool, test_prompt, svc)
            print(f"  [{svc}] {'OK' if r['success'] else 'FAIL'}: {r.get('text','')[:30]} | {r.get('error','')[:50]}")
        return

    template = args.prompt or ""
    if args.template and os.path.exists(args.template):
        with open(args.template) as f:
            template = f.read().strip()

    if not template:
        print("[-] --prompt or --template required"); sys.exit(1)

    if args.input:
        with open(args.input) as f:
            items = json.load(f)
        batch_process(pool, template, items, args.output, args.delay)
    else:
        # Single or repeated
        vars_dict = {}
        if args.var:
            for v in args.var:
                k, _, val = v.partition("=")
                vars_dict[k] = val
        prompt = template.format(**vars_dict) if vars_dict else template

        for i in range(args.count):
            r = run_prompt(pool, prompt, args.service, args.max_tokens)
            print(f"\n[{i+1}/{args.count}] {r.get('service','?')} | {r.get('elapsed_ms')}ms | {r.get('tokens')} tokens")
            if r["success"]:
                print(r.get("text","")[:500])
            else:
                print(f"Error: {r.get('error')}")
            if i < args.count - 1:
                time.sleep(args.delay)


if __name__ == "__main__":
    main()
