#!/usr/bin/env python3
"""
warmup_scheduler.py - Account warmup scheduler with realistic activity simulation.
Generates human-like activity patterns to warm up new accounts before main operations.

Usage:
    python scripts/warmup_scheduler.py --accounts accounts.json --platform tiktok --days 7
    python scripts/warmup_scheduler.py --accounts accounts.json --platform facebook --mode aggressive
    python scripts/warmup_scheduler.py --generate-plan --platform instagram --accounts 10 --days 14

accounts.json: [{"username":"...", "password":"...", "cookies":"..."}]
"""
import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta

WARMUP_PLANS = {
    "gentle": {
        "description": "Low risk, slow growth. Good for aged accounts.",
        "daily_actions": {"like": (5, 15), "follow": (2, 8), "view": (20, 50), "comment": (0, 2), "post": (0, 1)},
        "active_hours": list(range(8, 22)),
        "session_duration_min": (5, 20),
        "sessions_per_day": (2, 4),
        "rest_days": [6],  # Sunday
    },
    "normal": {
        "description": "Balanced activity. Best for fresh accounts.",
        "daily_actions": {"like": (20, 50), "follow": (10, 30), "view": (50, 150), "comment": (2, 8), "post": (1, 2)},
        "active_hours": list(range(7, 23)),
        "session_duration_min": (10, 45),
        "sessions_per_day": (3, 6),
        "rest_days": [],
    },
    "aggressive": {
        "description": "High volume. Higher ban risk. Use with rotation.",
        "daily_actions": {"like": (80, 150), "follow": (40, 80), "view": (200, 500), "comment": (10, 25), "post": (2, 5)},
        "active_hours": list(range(6, 24)),
        "session_duration_min": (20, 90),
        "sessions_per_day": (5, 10),
        "rest_days": [],
    },
}

PLATFORM_LIMITS = {
    "tiktok":    {"daily_like_max": 500, "daily_follow_max": 200, "daily_comment_max": 100},
    "facebook":  {"daily_like_max": 300, "daily_follow_max": 150, "daily_comment_max": 50},
    "instagram": {"daily_like_max": 350, "daily_follow_max": 200, "daily_comment_max": 60},
    "youtube":   {"daily_like_max": 200, "daily_follow_max": 100, "daily_comment_max": 30},
    "twitter":   {"daily_like_max": 400, "daily_follow_max": 400, "daily_comment_max": 100},
}


def generate_warmup_schedule(accounts: list, platform: str, days: int, mode: str = "normal") -> dict:
    plan = WARMUP_PLANS[mode]
    limits = PLATFORM_LIMITS.get(platform, PLATFORM_LIMITS["instagram"])
    schedule = {"platform": platform, "mode": mode, "duration_days": days,
                "generated_at": datetime.utcnow().isoformat(), "accounts": []}

    for account in accounts:
        acc_schedule = {"account": account.get("username", "unknown"), "days": []}
        for day in range(days):
            date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
            is_rest = day % 7 in plan["rest_days"]

            if is_rest:
                acc_schedule["days"].append({"date": date, "rest": True, "actions": {}})
                continue

            # Scale up actions over time (ramp-up curve)
            scale = min(1.0, (day + 1) / max(7, days * 0.3))

            day_actions = {}
            for action, (min_a, max_a) in plan["daily_actions"].items():
                limit_key = f"daily_{action}_max"
                platform_max = limits.get(limit_key, 9999)
                count = int(random.randint(int(min_a * scale), int(max_a * scale)))
                count = min(count, platform_max)
                day_actions[action] = count

            # Generate session times
            num_sessions = random.randint(*plan["sessions_per_day"])
            sessions = []
            used_hours = set()
            for _ in range(num_sessions):
                avail_hours = [h for h in plan["active_hours"] if h not in used_hours]
                if not avail_hours:
                    break
                hour = random.choice(avail_hours)
                used_hours.add(hour)
                duration = random.randint(*plan["session_duration_min"])
                sessions.append({"start_hour": hour, "duration_min": duration})

            acc_schedule["days"].append({
                "date": date, "day_num": day + 1, "scale": round(scale, 2),
                "actions": day_actions, "sessions": sorted(sessions, key=lambda s: s["start_hour"])
            })

        schedule["accounts"].append(acc_schedule)

    return schedule


def print_schedule_summary(schedule: dict):
    print(f"\n[*] Warmup Schedule: {schedule['platform']} | Mode: {schedule['mode']} | {schedule['duration_days']} days")
    for acc in schedule["accounts"]:
        print(f"\n  Account: {acc['account']}")
        total_actions = {}
        for day in acc["days"]:
            if day.get("rest"):
                continue
            for action, count in day.get("actions", {}).items():
                total_actions[action] = total_actions.get(action, 0) + count
        for action, total in total_actions.items():
            print(f"    {action}: {total} total over {schedule['duration_days']} days")

        # Show first 3 days
        print(f"  First 3 days preview:")
        for day in acc["days"][:3]:
            if day.get("rest"):
                print(f"    Day {day.get('day_num',0)}: REST")
            else:
                acts = ", ".join(f"{k}:{v}" for k, v in day["actions"].items() if v > 0)
                sess = len(day.get("sessions", []))
                print(f"    Day {day['day_num']} ({day['date']}): {acts} | {sess} sessions")


def main():
    p = argparse.ArgumentParser(description="Account warmup scheduler")
    p.add_argument("--accounts", help="Accounts JSON file")
    p.add_argument("--platform", choices=list(PLATFORM_LIMITS.keys()), default="tiktok")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--mode", choices=list(WARMUP_PLANS.keys()), default="normal")
    p.add_argument("--generate-plan", action="store_true", help="Generate plan without accounts file")
    p.add_argument("--count", type=int, default=3, help="Number of accounts for generate-plan")
    p.add_argument("--output", help="Save schedule JSON")
    args = p.parse_args()

    if args.generate_plan:
        dummy_accounts = [{"username": f"account_{i+1:03d}"} for i in range(args.count)]
        accounts = dummy_accounts
    elif args.accounts:
        with open(args.accounts) as f:
            accounts = json.load(f)
        if isinstance(accounts, dict):
            accounts = [accounts]
    else:
        print("[-] --accounts or --generate-plan required"); sys.exit(1)

    schedule = generate_warmup_schedule(accounts, args.platform, args.days, args.mode)
    print_schedule_summary(schedule)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)
        print(f"\n[+] Schedule saved: {args.output}")
    else:
        print(f"\n[+] Use --output to save full schedule JSON")


if __name__ == "__main__":
    main()
