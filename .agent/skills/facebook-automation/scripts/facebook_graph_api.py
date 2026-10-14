#!/usr/bin/env python3
"""
facebook_graph_api.py - Facebook Graph API automation for Pages, Posts, and Insights.

Usage:
    python scripts/facebook_graph_api.py --action me --token ACCESS_TOKEN
    python scripts/facebook_graph_api.py --action post --page-id PAGE_ID --message "Hello!" --token TOKEN
    python scripts/facebook_graph_api.py --action schedule --page-id PAGE_ID --message "Scheduled!" --time "2024-12-25 09:00" --token TOKEN
    python scripts/facebook_graph_api.py --action insights --page-id PAGE_ID --token TOKEN --days 7
    python scripts/facebook_graph_api.py --action group-post --group-id GROUP_ID --message "Hi!" --token TOKEN
    python scripts/facebook_graph_api.py --action bulk-post --pages-file pages.json --content-file posts.json

API token: FB_ACCESS_TOKEN env var or --token arg.
Long-lived token generation: https://developers.facebook.com/tools/explorer/
"""
import argparse
import json
import os
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse
from datetime import datetime

GRAPH_API = "https://graph.facebook.com/v20.0"
TOKEN = os.environ.get("FB_ACCESS_TOKEN", "")


def graph_get(endpoint: str, params: dict = None, token: str = None) -> dict:
    t = token or TOKEN
    p = params or {}
    p["access_token"] = t
    url = f"{GRAPH_API}{endpoint}?{uparse.urlencode(p)}"
    try:
        resp = ureq.urlopen(url, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": {"message": str(e)[:100]}}


def graph_post(endpoint: str, data: dict, token: str = None) -> dict:
    t = token or TOKEN
    data["access_token"] = t
    url = f"{GRAPH_API}{endpoint}"
    payload = uparse.urlencode(data).encode()
    req = ureq.Request(url, payload)
    try:
        resp = ureq.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": {"message": str(e)[:100]}}


def get_me(token: str = None) -> dict:
    """Get own profile info."""
    r = graph_get("/me", {"fields": "id,name,email"}, token)
    if "id" in r:
        print(f"[*] Logged in as: {r.get('name')} (id: {r.get('id')})")
    elif "error" in r:
        print(f"[-] Error: {r['error']['message']}")
    return r


def get_pages(token: str = None) -> list:
    """Get managed pages with their tokens."""
    r = graph_get("/me/accounts", {"fields": "id,name,access_token,category,fan_count"}, token)
    pages = r.get("data", [])
    print(f"[*] Managed pages: {len(pages)}")
    for p in pages:
        print(f"  {p['id']} | {p['name']} | {p.get('category','')} | {p.get('fan_count',0):,} fans")
    return pages


def post_to_page(page_id: str, message: str, link: str = None,
                 image_url: str = None, token: str = None,
                 scheduled_time: str = None) -> dict:
    """Post content to a Facebook Page."""
    data = {"message": message}
    if link: data["link"] = link
    if image_url:
        # Post with photo
        data["url"] = image_url
        endpoint = f"/{page_id}/photos"
    else:
        endpoint = f"/{page_id}/feed"

    if scheduled_time:
        try:
            ts = int(datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M").timestamp())
            data["scheduled_publish_time"] = ts
            data["published"] = "false"
        except ValueError:
            print(f"[-] Invalid time format. Use: YYYY-MM-DD HH:MM")

    r = graph_post(endpoint, data, token)
    if r.get("id"):
        print(f"[+] Posted: {r['id']}")
        return {"success": True, "post_id": r["id"]}
    else:
        print(f"[-] Post failed: {r.get('error',{}).get('message','?')}")
        return {"success": False, "error": r.get("error",{})}


def get_insights(page_id: str, metric: str = "page_impressions,page_engaged_users,page_fans",
                 period: str = "day", since_days: int = 7, token: str = None) -> dict:
    """Get Page insights."""
    since = int(time.time()) - since_days * 86400
    r = graph_get(f"/{page_id}/insights", {
        "metric": metric, "period": period,
        "since": since, "until": int(time.time()),
    }, token)
    data = r.get("data", [])
    print(f"[*] Insights for page {page_id}:")
    metrics_data = {}
    for metric_data in data:
        name = metric_data.get("name")
        values = metric_data.get("values", [])
        total = sum(v.get("value", 0) for v in values if isinstance(v.get("value"), (int, float)))
        metrics_data[name] = {"total": total, "period_count": len(values)}
        print(f"  {name}: {total:,} (over {len(values)} periods)")
    return metrics_data


def post_to_group(group_id: str, message: str, link: str = None, token: str = None) -> dict:
    """Post to a Facebook Group."""
    data = {"message": message}
    if link: data["link"] = link
    r = graph_post(f"/{group_id}/feed", data, token)
    if r.get("id"):
        print(f"[+] Group post: {r['id']}")
        return {"success": True, "post_id": r["id"]}
    print(f"[-] Group post failed: {r.get('error',{}).get('message','?')}")
    return {"success": False}


def bulk_post(pages: list, content_list: list, token: str = None,
              delay: float = 30.0) -> list:
    """Post content to multiple pages."""
    results = []
    content_idx = 0
    for page in pages:
        page_id    = page.get("id") or page.get("page_id")
        page_token = page.get("access_token") or token
        if not page_id or not page_token:
            continue
        content = content_list[content_idx % len(content_list)]
        content_idx += 1
        r = post_to_page(page_id, content.get("message",""), content.get("link"),
                         None, page_token)
        r["page_id"] = page_id
        results.append(r)
        if delay:
            time.sleep(delay + (delay * 0.2))
    return results


def marketplace_listing(page_id: str, title: str, price: float, description: str,
                         category: str = "merchandise", token: str = None) -> dict:
    """Create a Facebook Marketplace listing (requires Commerce Manager)."""
    data = {
        "name": title,
        "description": description,
        "price": int(price * 100),  # cents
        "currency": "USD",
        "availability": "in stock",
        "condition": "new",
        "category": category,
    }
    r = graph_post(f"/{page_id}/products", data, token)
    if r.get("id"):
        print(f"[+] Marketplace listing: {r['id']}")
        return {"success": True, "product_id": r["id"]}
    print(f"[-] Listing failed: {r.get('error',{}).get('message','?')}")
    return {"success": False}


def main():
    p = argparse.ArgumentParser(description="Facebook Graph API automation")
    p.add_argument("--token", default=os.environ.get("FB_ACCESS_TOKEN",""))
    p.add_argument("--action", choices=["me","pages","post","schedule","insights",
                                          "group-post","bulk-post","marketplace"], required=True)
    p.add_argument("--page-id")
    p.add_argument("--group-id")
    p.add_argument("--message")
    p.add_argument("--link")
    p.add_argument("--image-url")
    p.add_argument("--time", help="Schedule time: YYYY-MM-DD HH:MM")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--pages-file", help="Pages JSON file for bulk post")
    p.add_argument("--content-file", help="Content JSON file for bulk post")
    p.add_argument("--delay", type=float, default=30.0)
    p.add_argument("--title"); p.add_argument("--price", type=float)
    p.add_argument("--output")
    args = p.parse_args()

    if not args.token:
        print("[!] Set FB_ACCESS_TOKEN or use --token"); sys.exit(1)

    if args.action == "me":
        get_me(args.token)
    elif args.action == "pages":
        get_pages(args.token)
    elif args.action in ("post","schedule"):
        if not args.page_id or not args.message:
            print("[-] --page-id and --message required"); sys.exit(1)
        post_to_page(args.page_id, args.message, args.link, args.image_url,
                     args.token, args.time if args.action == "schedule" else None)
    elif args.action == "insights":
        if not args.page_id: print("[-] --page-id required"); sys.exit(1)
        get_insights(args.page_id, since_days=args.days, token=args.token)
    elif args.action == "group-post":
        if not args.group_id or not args.message:
            print("[-] --group-id and --message required"); sys.exit(1)
        post_to_group(args.group_id, args.message, args.link, args.token)
    elif args.action == "bulk-post":
        if not args.pages_file or not args.content_file:
            print("[-] --pages-file and --content-file required"); sys.exit(1)
        with open(args.pages_file) as f: pages = json.load(f)
        with open(args.content_file) as f: content = json.load(f)
        results = bulk_post(pages, content, args.token, args.delay)
        print(f"\n[*] Bulk post: {sum(1 for r in results if r.get('success'))}/{len(results)} OK")
    elif args.action == "marketplace":
        if not args.page_id or not args.title or args.price is None:
            print("[-] --page-id, --title, --price required"); sys.exit(1)
        marketplace_listing(args.page_id, args.title, args.price, args.message or "", token=args.token)


if __name__ == "__main__":
    main()
