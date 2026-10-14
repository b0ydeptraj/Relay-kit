#!/usr/bin/env python3
"""
tiktok_session.py - TikTok session manager via internal API.
Handles cookie-based authentication, device fingerprint, and API signing.

Usage:
    python scripts/tiktok_session.py --cookies cookies.json --action profile
    python scripts/tiktok_session.py --cookies cookies.json --action feed --count 10
    python scripts/tiktok_session.py --cookies cookies.json --action like --video-id VIDEO_ID
    python scripts/tiktok_session.py --cookies cookies.json --action follow --user-id USER_ID
    python scripts/tiktok_session.py --cookies cookies.json --action comment --video-id VID --text "Great!"
    python scripts/tiktok_session.py --cookies cookies.json --action search --query "trending"

cookies.json: {"sessionid": "...", "msToken": "...", "tt-csrf-token": "...", "tiktok-cookie": "..."}
Or: {"cookie_string": "sessionid=xxx; msToken=yyy; ..."}
"""
import argparse
import hashlib
import json
import os
import random
import re
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse

API_BASE = "https://www.tiktok.com/api"
M_API    = "https://m.tiktok.com/api"
WEB_API  = "https://www.tiktok.com"

DEVICE_TYPES = ["iPhone14,3", "iPhone13,4", "SM-G998B", "Pixel 7 Pro", "iPhone15,3"]
APP_VERSION  = "27.6.4"

# Common headers for TikTok API
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TikTok/27.6.4 (iPhone; iOS 17.0; Scale/3.00)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
}


class TikTokSession:
    def __init__(self, cookies: dict, proxy: str = None):
        self.cookies = cookies
        self.proxy = proxy
        self.device_id = self._get_or_gen_device_id()
        self._opener = self._build_opener()

    def _get_or_gen_device_id(self) -> str:
        did = self.cookies.get("device_id")
        if not did:
            did = str(random.randint(7000000000000000000, 7999999999999999999))
        return did

    def _build_cookie_string(self) -> str:
        if "cookie_string" in self.cookies:
            return self.cookies["cookie_string"]
        parts = []
        for k, v in self.cookies.items():
            if k not in ("proxy", "note", "cookie_string"):
                parts.append(f"{k}={v}")
        return "; ".join(parts)

    def _build_opener(self):
        handlers = [ureq.HTTPCookieProcessor()]
        if self.proxy:
            handlers.append(ureq.ProxyHandler({"http": self.proxy, "https": self.proxy}))
        return ureq.build_opener(*handlers)

    def _request(self, url: str, method: str = "GET", params: dict = None, data: dict = None) -> dict:
        if params:
            url = f"{url}?{uparse.urlencode(params)}"
        headers = BASE_HEADERS.copy()
        headers["Cookie"] = self._build_cookie_string()
        csrf = self.cookies.get("tt-csrf-token", self.cookies.get("ttwid", ""))
        if csrf:
            headers["x-tt-params"] = csrf
        if self.cookies.get("tt-csrf-token"):
            headers["X-Secsdk-Csrf-Token"] = self.cookies["tt-csrf-token"]

        payload = None
        if data:
            payload = uparse.urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = ureq.Request(url, data=payload, headers=headers, method=method)
        try:
            resp = self._opener.open(req, timeout=20)
            content = resp.read()
            return json.loads(content)
        except Exception as e:
            return {"error": str(e)[:100], "status_code": 0}

    def get_profile(self) -> dict:
        """Get own profile info."""
        r = self._request(f"{WEB_API}/api/user/detail/",
                          params={"uniqueId": "", "msToken": self.cookies.get("msToken","")})
        user = r.get("userInfo", {}).get("user", {})
        stats = r.get("userInfo", {}).get("stats", {})
        return {"username": user.get("uniqueId"), "nickname": user.get("nickname"),
                "uid": user.get("id"), "followers": stats.get("followerCount",0),
                "following": stats.get("followingCount",0), "likes": stats.get("heartCount",0),
                "videos": stats.get("videoCount",0)}

    def get_feed(self, count: int = 10) -> list:
        """Get For You page feed."""
        r = self._request(f"{M_API}/item_list/", params={
            "count": count, "id": "1", "type": 5,
            "secUid": "", "maxCursor": 0, "minCursor": 0,
            "sourceType": 12, "appId": 1233,
            "msToken": self.cookies.get("msToken",""),
        })
        return r.get("itemList", [])

    def like_video(self, video_id: str) -> dict:
        """Like a video."""
        r = self._request(f"{WEB_API}/api/commit/item/digg/", method="POST", data={
            "aweme_id": video_id, "type": 1,
            "msToken": self.cookies.get("msToken",""),
        })
        return {"success": r.get("status_code") == 0 or r.get("is_digg") == 1,
                "video_id": video_id, "response": r}

    def follow_user(self, user_id: str) -> dict:
        """Follow a user."""
        r = self._request(f"{WEB_API}/api/commit/follow/user/", method="POST", data={
            "from": 0, "from_pre": -1, "type": 1,
            "user_id": user_id,
            "msToken": self.cookies.get("msToken",""),
        })
        return {"success": r.get("status_code") == 0,
                "user_id": user_id, "follow_status": r.get("follow_status")}

    def post_comment(self, video_id: str, text: str) -> dict:
        """Post a comment on a video."""
        r = self._request(f"{WEB_API}/api/comment/publish/", method="POST", data={
            "aweme_id": video_id, "text": text,
            "is_self_see": 0,
            "msToken": self.cookies.get("msToken",""),
        })
        return {"success": r.get("status_code") == 0,
                "video_id": video_id, "comment_id": r.get("comment",{}).get("cid","")}

    def search_videos(self, query: str, count: int = 20) -> list:
        """Search for videos by keyword."""
        r = self._request(f"{WEB_API}/api/search/general/full/", params={
            "keyword": query, "offset": 0, "count": count,
            "search_source": "normal_search",
            "msToken": self.cookies.get("msToken",""),
        })
        return r.get("data", [])

    def get_user_videos(self, user_id: str, count: int = 20) -> list:
        """Get videos from a user's profile."""
        r = self._request(f"{WEB_API}/api/post/item_list/", params={
            "userId": user_id, "count": count, "cursor": 0,
            "coverFormat": 2,
            "msToken": self.cookies.get("msToken",""),
        })
        return r.get("itemList", [])

    def run_engagement(self, video_ids: list, actions: list = None,
                       delay_range: tuple = (3, 8)) -> dict:
        """Run bulk engagement on a list of videos."""
        actions = actions or ["like"]
        results = {"like": 0, "follow": 0, "comment": 0, "errors": 0}
        comments = ["Amazing!", "Love this!", "So good!", "Keep it up!", "Fire content!",
                    "Wow!", "Great video!", "This is so cool!", "Incredible!", "Awesome!"]

        for vid_id in video_ids:
            for action in actions:
                try:
                    if action == "like":
                        r = self.like_video(vid_id)
                        if r["success"]: results["like"] += 1
                    elif action == "comment":
                        r = self.post_comment(vid_id, random.choice(comments))
                        if r["success"]: results["comment"] += 1
                    else:
                        results["errors"] += 1
                except Exception as e:
                    results["errors"] += 1

                delay = random.uniform(*delay_range)
                time.sleep(delay)

        return results


def main():
    p = argparse.ArgumentParser(description="TikTok session manager and engagement bot")
    p.add_argument("--cookies", required=True, help="Cookies JSON file")
    p.add_argument("--action", choices=["profile","feed","like","follow","comment",
                                          "search","user-videos","bulk-engage"], required=True)
    p.add_argument("--video-id", help="Target video ID")
    p.add_argument("--user-id", help="Target user ID")
    p.add_argument("--text", help="Comment text")
    p.add_argument("--query", help="Search query")
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--actions", default="like", help="Bulk actions: like,comment,follow")
    p.add_argument("--proxy", help="Proxy URL")
    p.add_argument("--output", help="Save results JSON")
    p.add_argument("--delay-min", type=float, default=3.0)
    p.add_argument("--delay-max", type=float, default=8.0)
    args = p.parse_args()

    with open(args.cookies) as f:
        cookies = json.load(f)

    sess = TikTokSession(cookies, args.proxy)

    if args.action == "profile":
        profile = sess.get_profile()
        print(json.dumps(profile, indent=2, ensure_ascii=False))
    elif args.action == "feed":
        feed = sess.get_feed(args.count)
        print(f"[*] Feed: {len(feed)} videos")
        for v in feed[:5]:
            vid = v.get("video", {})
            author = v.get("author", {})
            print(f"  {v.get('id')} | @{author.get('uniqueId','')} | {v.get('stats',{}).get('diggCount',0)} likes")
    elif args.action == "like":
        if not args.video_id: print("[-] --video-id required"); sys.exit(1)
        r = sess.like_video(args.video_id)
        print(f"[{'OK' if r['success'] else 'FAIL'}] Like: {args.video_id}")
    elif args.action == "follow":
        if not args.user_id: print("[-] --user-id required"); sys.exit(1)
        r = sess.follow_user(args.user_id)
        print(f"[{'OK' if r['success'] else 'FAIL'}] Follow: {args.user_id}")
    elif args.action == "comment":
        if not args.video_id: print("[-] --video-id required"); sys.exit(1)
        r = sess.post_comment(args.video_id, args.text or "Amazing!")
        print(f"[{'OK' if r['success'] else 'FAIL'}] Comment on {args.video_id}")
    elif args.action == "search":
        results = sess.search_videos(args.query or "trending", args.count)
        print(f"[*] Search '{args.query}': {len(results)} results")
        for r in results[:5]:
            item = r.get("item", {})
            print(f"  {item.get('id','')} | {item.get('desc','')[:50]}")
    elif args.action == "user-videos":
        if not args.user_id: print("[-] --user-id required"); sys.exit(1)
        videos = sess.get_user_videos(args.user_id, args.count)
        print(f"[*] @{args.user_id}: {len(videos)} videos")
        for v in videos[:5]:
            print(f"  {v.get('id')} | {v.get('stats',{}).get('playCount',0)} views")
    elif args.action == "bulk-engage":
        feed = sess.get_feed(args.count)
        video_ids = [v.get("id") for v in feed if v.get("id")]
        actions = [a.strip() for a in args.actions.split(",")]
        print(f"[*] Bulk engage: {len(video_ids)} videos | actions: {actions}")
        results = sess.run_engagement(video_ids, actions, (args.delay_min, args.delay_max))
        print(f"[*] Results: {results}")

    if args.output:
        print(f"[+] Use --output flag with specific actions to save results")


if __name__ == "__main__":
    main()
