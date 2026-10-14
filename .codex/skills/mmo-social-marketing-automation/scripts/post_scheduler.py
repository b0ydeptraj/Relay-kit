#!/usr/bin/env python3
"""
post_scheduler.py - Multi-platform social media post scheduler.
Schedule posts to TikTok, Facebook, Instagram, YouTube, Telegram with timing optimization.

Usage:
    python scripts/post_scheduler.py --platform tiktok --content posts.json --schedule now
    python scripts/post_scheduler.py --platform facebook --content post.txt --schedule "2024-12-25 09:00"
    python scripts/post_scheduler.py --generate-schedule --platform instagram --posts 30 --days 7
    python scripts/post_scheduler.py --platform telegram --channel @mychannel --content msg.txt

API keys via env: TIKTOK_API_KEY, FB_ACCESS_TOKEN, IG_ACCESS_TOKEN, TG_BOT_TOKEN
"""
import argparse
import json
import os
import random
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse
from datetime import datetime, timedelta

# Optimal posting times by platform (hour, 24h)
OPTIMAL_HOURS = {
    "tiktok":    [7, 8, 12, 19, 20, 21, 22],
    "facebook":  [9, 12, 13, 15, 17, 18, 19],
    "instagram": [6, 9, 12, 17, 18, 20, 21],
    "youtube":   [14, 15, 16, 17, 20, 21],
    "twitter":   [8, 9, 12, 17, 18, 19, 20],
    "telegram":  list(range(8, 23)),
}

DAY_MULTIPLIERS = {
    "tiktok":    [1.2, 1.0, 1.0, 1.0, 1.3, 1.5, 1.4],  # Mon-Sun
    "facebook":  [1.0, 1.1, 1.2, 1.1, 1.0, 0.9, 0.8],
    "instagram": [1.1, 1.2, 1.3, 1.2, 1.1, 1.0, 0.9],
    "youtube":   [0.9, 1.0, 1.1, 1.2, 1.3, 1.2, 1.1],
    "twitter":   [1.2, 1.3, 1.2, 1.1, 1.0, 0.8, 0.7],
    "telegram":  [1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.0],
}


def generate_optimal_schedule(platform: str, num_posts: int, days: int,
                               start_date: datetime = None) -> list:
    """Generate an optimized posting schedule."""
    start = start_date or datetime.now()
    hours = OPTIMAL_HOURS.get(platform, list(range(8, 22)))
    multipliers = DAY_MULTIPLIERS.get(platform, [1.0] * 7)
    posts_per_day = max(1, num_posts // days)
    schedule = []
    post_idx = 0

    for day in range(days):
        if post_idx >= num_posts:
            break
        date = start + timedelta(days=day)
        day_of_week = date.weekday()
        weight = multipliers[day_of_week]

        # Skip low-engagement days sometimes
        if weight < 0.9 and random.random() > weight:
            continue

        day_posts = min(posts_per_day, num_posts - post_idx)
        selected_hours = random.sample(hours, min(day_posts, len(hours)))
        selected_hours.sort()

        for hour in selected_hours:
            minute = random.randint(0, 59)
            post_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            schedule.append({
                "post_num": post_idx + 1,
                "platform": platform,
                "scheduled_time": post_time.strftime("%Y-%m-%d %H:%M:%S"),
                "day_of_week": date.strftime("%A"),
                "engagement_score": round(weight * random.uniform(0.8, 1.2), 2),
            })
            post_idx += 1
            if post_idx >= num_posts:
                break

    return schedule


def send_telegram_message(bot_token: str, chat_id: str, text: str,
                           parse_mode: str = "HTML", photo_url: str = None) -> dict:
    """Send message to Telegram channel/group via Bot API."""
    if photo_url:
        endpoint = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        data = {"chat_id": chat_id, "caption": text, "photo": photo_url, "parse_mode": parse_mode}
    else:
        endpoint = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}

    payload = json.dumps(data).encode()
    req = ureq.Request(endpoint, payload, {"Content-Type": "application/json"})
    try:
        resp = ureq.urlopen(req, timeout=30)
        r = json.loads(resp.read())
        return {"success": r.get("ok", False), "message_id": r.get("result", {}).get("message_id")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def post_facebook(access_token: str, page_id: str, message: str,
                  link: str = None, scheduled_time: int = None) -> dict:
    """Post to Facebook Page via Graph API."""
    data = {"message": message, "access_token": access_token}
    if link: data["link"] = link
    if scheduled_time:
        data["scheduled_publish_time"] = scheduled_time
        data["published"] = "false"

    url = f"https://graph.facebook.com/v20.0/{page_id}/feed"
    payload = uparse.urlencode(data).encode()
    req = ureq.Request(url, payload)
    try:
        resp = ureq.urlopen(req, timeout=30)
        r = json.loads(resp.read())
        return {"success": "id" in r, "post_id": r.get("id"), "platform": "facebook"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def post_content(platform: str, content: str, config: dict) -> dict:
    """Route post to correct platform API."""
    if platform == "telegram":
        bot_token = config.get("bot_token") or os.environ.get("TG_BOT_TOKEN", "")
        chat_id = config.get("chat_id") or config.get("channel", "")
        if not bot_token or not chat_id:
            return {"success": False, "error": "Missing TG_BOT_TOKEN or chat_id"}
        return send_telegram_message(bot_token, chat_id, content)

    elif platform == "facebook":
        token = config.get("access_token") or os.environ.get("FB_ACCESS_TOKEN", "")
        page_id = config.get("page_id", "me")
        if not token:
            return {"success": False, "error": "Missing FB_ACCESS_TOKEN"}
        return post_facebook(token, page_id, content)

    else:
        return {"success": False, "error": f"{platform}: Requires platform SDK/browser automation. Use mmo-anti-detection-browser skill."}


def main():
    p = argparse.ArgumentParser(description="Multi-platform social post scheduler")
    p.add_argument("--platform", choices=["tiktok","facebook","instagram","youtube","telegram","twitter"], required=True)
    p.add_argument("--content", help="Content text or JSON file")
    p.add_argument("--schedule", help="'now' or datetime '2024-12-25 09:00'")
    p.add_argument("--generate-schedule", action="store_true")
    p.add_argument("--posts", type=int, default=10)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--channel", help="Telegram channel @name or ID")
    p.add_argument("--output", help="Save schedule/results JSON")
    args = p.parse_args()

    if args.generate_schedule:
        schedule = generate_optimal_schedule(args.platform, args.posts, args.days)
        print(f"[*] Optimal posting schedule: {args.platform} | {len(schedule)} posts over {args.days} days")
        print(f"\n{'#':<4} {'Date':<22} {'Day':<12} {'Eng.Score':<10}")
        print("-" * 50)
        for s in schedule:
            print(f"  {s['post_num']:<3} {s['scheduled_time']:<22} {s['day_of_week']:<12} {s['engagement_score']}")
        if args.output:
            with open(args.output, "w") as f:
                json.dump(schedule, f, indent=2)
            print(f"\n[+] Saved to {args.output}")
        return

    if not args.content:
        print("[-] --content required"); sys.exit(1)

    if os.path.exists(args.content):
        with open(args.content) as f:
            content = f.read().strip()
    else:
        content = args.content

    config = {"channel": args.channel}
    result = post_content(args.platform, content, config)
    print(f"[*] Post result: {result}")


if __name__ == "__main__":
    main()
