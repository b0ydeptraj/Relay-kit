#!/usr/bin/env python3
"""
adb_automator.py - Android device automation via ADB for MMO mobile operations.
Controls multiple Android devices/emulators: tap, swipe, input, screenshot, app control.

Usage:
    python scripts/adb_automator.py --action list-devices
    python scripts/adb_automator.py --action tap --x 540 --y 960 --device emulator-5554
    python scripts/adb_automator.py --action swipe --x1 540 --y1 1500 --x2 540 --y2 500
    python scripts/adb_automator.py --action input-text --text "hello world"
    python scripts/adb_automator.py --action screenshot --output screen.png
    python scripts/adb_automator.py --action launch-app --package com.tiktok.app
    python scripts/adb_automator.py --action run-script --script actions.json
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time


def run_adb(args: list, device: str = None, capture: bool = True) -> str:
    cmd = ["adb"]
    if device:
        cmd += ["-s", device]
    cmd += args
    try:
        result = subprocess.run(cmd, capture_output=capture, text=True, timeout=30)
        return result.stdout.strip() if capture else ""
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except FileNotFoundError:
        print("[-] ADB not found. Install Android SDK Platform Tools.")
        sys.exit(1)
    except Exception as e:
        return f"ERROR: {e}"


def list_devices() -> list:
    output = run_adb(["devices"])
    lines = output.strip().split("\n")[1:]  # Skip header
    devices = []
    for line in lines:
        if line.strip() and "\t" in line:
            serial, status = line.split("\t", 1)
            devices.append({"serial": serial.strip(), "status": status.strip()})
    return devices


def tap(x: int, y: int, device: str = None, humanize: bool = True):
    """Tap at coordinates with optional human-like offset."""
    if humanize:
        x += random.randint(-3, 3)
        y += random.randint(-3, 3)
    run_adb(["shell", "input", "tap", str(x), str(y)], device)
    if humanize:
        time.sleep(random.uniform(0.1, 0.4))


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300, device: str = None):
    """Swipe from point to point."""
    run_adb(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)], device)
    time.sleep(random.uniform(0.3, 0.8))


def input_text(text: str, device: str = None, char_delay: float = 0.05):
    """Type text with optional per-character delay for realism."""
    # ADB doesn't handle unicode well, use clipboard trick for non-ASCII
    escaped = text.replace(" ", "%s").replace("'", "\\'")
    run_adb(["shell", "input", "text", escaped], device)
    time.sleep(char_delay * len(text))


def press_key(keycode: int, device: str = None):
    """Press Android key by keycode. Common: 4=BACK, 3=HOME, 187=APP_SWITCH."""
    run_adb(["shell", "input", "keyevent", str(keycode)], device)
    time.sleep(0.2)


def screenshot(output_path: str = "screenshot.png", device: str = None):
    """Capture screenshot from device."""
    run_adb(["shell", "screencap", "-p", "/sdcard/tmp_screen.png"], device)
    run_adb(["pull", "/sdcard/tmp_screen.png", output_path], device)
    run_adb(["shell", "rm", "/sdcard/tmp_screen.png"], device)
    if os.path.exists(output_path):
        size = os.path.getsize(output_path)
        print(f"[+] Screenshot: {output_path} ({size:,} bytes)")
    return output_path


def launch_app(package: str, activity: str = None, device: str = None):
    """Launch an app by package name."""
    if activity:
        run_adb(["shell", "am", "start", "-n", f"{package}/{activity}"], device)
    else:
        run_adb(["shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"], device)
    time.sleep(2)


def get_current_package(device: str = None) -> str:
    """Get the currently focused app package."""
    output = run_adb(["shell", "dumpsys", "window", "windows"], device)
    for line in output.split("\n"):
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            m = __import__("re").search(r"([a-z][a-z0-9_.]+)/", line)
            if m:
                return m.group(1)
    return ""


def get_screen_size(device: str = None) -> tuple:
    output = run_adb(["shell", "wm", "size"], device)
    m = __import__("re").search(r"(\d+)x(\d+)", output)
    if m:
        return int(m.group(1)), int(m.group(2))
    return 1080, 1920


def run_action_script(script_path: str, device: str = None):
    """Execute a JSON action script."""
    with open(script_path) as f:
        actions = json.load(f)

    print(f"[*] Running {len(actions)} actions on {device or 'default'}")
    for i, action in enumerate(actions):
        atype = action.get("type", "")
        print(f"  [{i+1}/{len(actions)}] {atype}...")

        if atype == "tap":
            tap(action["x"], action["y"], device, action.get("humanize", True))
        elif atype == "swipe":
            swipe(action["x1"], action["y1"], action["x2"], action["y2"],
                  action.get("duration_ms", 300), device)
        elif atype == "text":
            input_text(action["text"], device)
        elif atype == "key":
            press_key(action["keycode"], device)
        elif atype == "sleep":
            time.sleep(action.get("seconds", 1))
        elif atype == "screenshot":
            screenshot(action.get("output", f"screen_{i}.png"), device)
        elif atype == "launch":
            launch_app(action["package"], action.get("activity"), device)
        elif atype == "shell":
            out = run_adb(["shell"] + action["cmd"].split(), device)
            print(f"    -> {out[:80]}")
        else:
            print(f"  [!] Unknown action type: {atype}")

        delay = action.get("delay", 0)
        if delay:
            time.sleep(delay)

    print("[+] Script completed")


def main():
    p = argparse.ArgumentParser(description="ADB device automation for MMO mobile ops")
    p.add_argument("--action", choices=["list-devices","tap","swipe","input-text","screenshot",
                                          "launch-app","key","current-app","screen-size","run-script"], required=True)
    p.add_argument("--device", help="Device serial (use 'adb devices' to find)")
    p.add_argument("--x", type=int); p.add_argument("--y", type=int)
    p.add_argument("--x1", type=int); p.add_argument("--y1", type=int)
    p.add_argument("--x2", type=int); p.add_argument("--y2", type=int)
    p.add_argument("--text"); p.add_argument("--package"); p.add_argument("--activity")
    p.add_argument("--keycode", type=int, default=4)
    p.add_argument("--output", default="screenshot.png")
    p.add_argument("--script", help="JSON action script file")
    p.add_argument("--duration-ms", type=int, default=300)
    args = p.parse_args()

    d = args.device
    if args.action == "list-devices":
        devices = list_devices()
        print(f"[*] {len(devices)} device(s):")
        for dv in devices:
            print(f"  {dv['serial']} [{dv['status']}]")
    elif args.action == "tap":
        tap(args.x or 540, args.y or 960, d)
        print(f"[+] Tapped ({args.x},{args.y})")
    elif args.action == "swipe":
        swipe(args.x1 or 540, args.y1 or 1500, args.x2 or 540, args.y2 or 500, args.duration_ms, d)
        print("[+] Swiped")
    elif args.action == "input-text":
        input_text(args.text or "", d)
        print(f"[+] Typed: {args.text}")
    elif args.action == "screenshot":
        screenshot(args.output, d)
    elif args.action == "launch-app":
        launch_app(args.package or "", args.activity, d)
        print(f"[+] Launched: {args.package}")
    elif args.action == "key":
        press_key(args.keycode, d)
    elif args.action == "current-app":
        pkg = get_current_package(d)
        print(f"[*] Current: {pkg}")
    elif args.action == "screen-size":
        w, h = get_screen_size(d)
        print(f"[*] Screen: {w}x{h}")
    elif args.action == "run-script":
        if not args.script: print("[-] --script required"); sys.exit(1)
        run_action_script(args.script, d)


if __name__ == "__main__":
    main()
