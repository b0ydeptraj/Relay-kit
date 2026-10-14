#!/usr/bin/env python3
"""
fleet_orchestrator.py - Orchestrate a fleet of automated browser sessions in parallel.
Manages multiple Playwright browser contexts with proxy rotation and fingerprint isolation.

Usage:
    python scripts/fleet_orchestrator.py --workers 5 --task-file tasks.json --proxy-file proxies.txt
    python scripts/fleet_orchestrator.py --workers 10 --task login --accounts accounts.json
    python scripts/fleet_orchestrator.py --test --workers 3 --url https://httpbin.org/ip

tasks.json: [{"url": "...", "actions": [{"type":"click","selector":"..."}]}]
"""
import argparse
import json
import os
import random
import sys
import time
import concurrent.futures
import threading

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

results_lock = threading.Lock()
all_results = []


def run_browser_task(task: dict, proxy: str = None, worker_id: int = 0) -> dict:
    """Execute a single browser task using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"worker": worker_id, "success": False,
                "error": "playwright not installed: pip install playwright && playwright install chromium"}

    result = {"worker": worker_id, "task": task.get("url","?")[:50], "success": False}
    with sync_playwright() as p:
        launch_args = {
            "headless": task.get("headless", True),
            "args": ["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        }
        if proxy:
            launch_args["proxy"] = {"server": proxy}

        browser = p.chromium.launch(**launch_args)
        ua = random.choice(UA_LIST)
        context = browser.new_context(
            user_agent=ua, viewport={"width": 1366, "height": 768},
            locale="en-US", java_script_enabled=True
        )
        context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        page = context.new_page()

        try:
            url = task.get("url", "https://httpbin.org/ip")
            page.goto(url, timeout=30000)
            time.sleep(random.uniform(1, 3))

            for action in task.get("actions", []):
                atype = action.get("type", "")
                optional = action.get("optional", False)
                try:
                    if atype == "click":
                        page.click(action["selector"], timeout=action.get("timeout", 10000))
                    elif atype == "fill":
                        page.fill(action["selector"], action["value"])
                    elif atype == "wait":
                        page.wait_for_timeout(action.get("ms", 2000))
                    elif atype == "screenshot":
                        page.screenshot(path=action.get("path", f"worker_{worker_id}.png"))
                    elif atype == "extract":
                        sel = action["selector"]
                        els = page.query_selector_all(sel)
                        result["extracted"] = [el.text_content() for el in els[:10]]
                    elif atype == "media_play":
                        sel = action.get("selector", "video")
                        page.evaluate("""(selector) => {
                            const video = document.querySelector(selector);
                            if (video) {
                                video.defaultMuted = true;
                                video.muted = true;
                                video.volume = 0;
                                video.playsInline = true;
                                return video.play().then(() => true).catch(() => false);
                            }
                            return false;
                        }""", sel)
                    elif atype == "media_seek":
                        target_sec = float(action.get("seconds", 0))
                        sel = action.get("selector", "video")
                        tol = float(action.get("tolerance", 2.0))
                        timeout_sec = float(action.get("timeout", 15.0))
                        page.evaluate("""([selector, target, tolerance, timeoutSec]) => {
                            return new Promise((resolve, reject) => {
                                const deadline = Date.now() + (timeoutSec * 1000);
                                let video = document.querySelector(selector);
                                if (!video) return reject(new Error('Video element not found: ' + selector));
                                video.defaultMuted = true;
                                video.muted = true;
                                video.volume = 0;
                                video.currentTime = target;
                                const check = () => {
                                    const cur = document.querySelector(selector) || video;
                                    if (!cur.seeking && Math.abs(cur.currentTime - target) <= tolerance) {
                                        return resolve({ currentTime: cur.currentTime, duration: cur.duration });
                                    }
                                    if (Date.now() >= deadline) {
                                        return reject(new Error('Timeout seeking video'));
                                    }
                                    setTimeout(check, 250);
                                };
                                check();
                            });
                        }""", [sel, target_sec, tol, timeout_sec])
                    elif atype == "iframe_action":
                        frame_sel = action["frame_selector"]
                        sub_action = action["action"]
                        frame = page.frame_locator(frame_sel)
                        stype = sub_action.get("type", "")
                        if stype == "click":
                            frame.locator(sub_action["selector"]).click(timeout=sub_action.get("timeout", 10000))
                        elif stype == "fill":
                            frame.locator(sub_action["selector"]).fill(sub_action["value"])
                        elif stype == "media_seek":
                            frame.locator(sub_action.get("selector", "video")).evaluate("""(video, target) => {
                                video.defaultMuted = true;
                                video.muted = true;
                                video.currentTime = target;
                                return video.currentTime;
                            }""", float(sub_action.get("seconds", 0)))
                except Exception as step_err:
                    if optional:
                        print(f"  [W{worker_id}] Warning: optional action {atype} timed out/skipped: {step_err}")
                    else:
                        raise step_err
                time.sleep(random.uniform(0.5, 1.5))

            result["success"] = True
            result["title"] = page.title()
            result["url_final"] = page.url

            if task.get("extract_ip"):
                try:
                    body = page.content()
                    import re
                    ip_match = re.search(r'"origin":\s*"([^"]+)"', body)
                    result["ip"] = ip_match.group(1) if ip_match else "unknown"
                except: pass

        except Exception as e:
            result["error"] = str(e)[:100]
        finally:
            browser.close()

    return result


def fleet_run(tasks: list, proxies: list, workers: int, delay: float = 0.5) -> list:
    print(f"[*] Fleet: {len(tasks)} tasks | {workers} workers | {len(proxies)} proxies")

    def run_with_proxy(args):
        task, idx = args
        proxy = proxies[idx % len(proxies)] if proxies else None
        r = run_browser_task(task, proxy, idx)
        with results_lock:
            all_results.append(r)
            ok = sum(1 for x in all_results if x["success"])
            print(f"  [W{idx}] {'OK' if r['success'] else 'FAIL'} | {r.get('title','?')[:30]} | {r.get('error','')[:40]}")
        time.sleep(delay)
        return r

    task_args = [(task, i) for i, task in enumerate(tasks)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(run_with_proxy, task_args))

    ok = sum(1 for r in all_results if r["success"])
    print(f"\n[*] Fleet done: {ok}/{len(tasks)} success")
    return all_results


def main():
    p = argparse.ArgumentParser(description="Browser fleet orchestrator")
    p.add_argument("--workers", type=int, default=3)
    p.add_argument("--task-file", help="Tasks JSON file")
    p.add_argument("--proxy-file", help="Proxy list file")
    p.add_argument("--url", help="URL for test mode")
    p.add_argument("--test", action="store_true", help="Run test with httpbin.org/ip")
    p.add_argument("--output", help="Results JSON output")
    p.add_argument("--delay", type=float, default=0.5)
    args = p.parse_args()

    proxies = []
    if args.proxy_file and os.path.exists(args.proxy_file):
        with open(args.proxy_file) as f:
            proxies = [l.strip() for l in f if l.strip()]

    if args.test or args.url:
        url = args.url or "https://httpbin.org/ip"
        tasks = [{"url": url, "extract_ip": True, "headless": True}
                 for _ in range(args.workers)]
    elif args.task_file:
        with open(args.task_file) as f:
            tasks = json.load(f)
    else:
        print("[-] --task-file, --test, or --url required"); sys.exit(1)

    results = fleet_run(tasks, proxies, args.workers, args.delay)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"[+] Results saved: {args.output}")


if __name__ == "__main__":
    main()
