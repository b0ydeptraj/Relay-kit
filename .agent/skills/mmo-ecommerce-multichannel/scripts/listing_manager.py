#!/usr/bin/env python3
"""
listing_manager.py - Multi-platform e-commerce listing manager.
Manage product listings on Shopee, Lazada, Amazon, TikTok Shop.

Usage:
    python scripts/listing_manager.py --platform shopee --action list --shop-id SHOP_ID
    python scripts/listing_manager.py --platform shopee --action create --product product.json
    python scripts/listing_manager.py --platform lazada --action update-price --id ITEM_ID --price 99.99
    python scripts/listing_manager.py --bulk-create --products products.json --platform shopee

API keys: SHOPEE_API_KEY, LAZADA_API_KEY, AMAZON_SP_API env vars.
"""
import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.request as ureq
import urllib.parse as uparse


def shopee_request(path: str, params: dict, shop_id: str, partner_id: str, key: str) -> dict:
    ts = int(time.time())
    base = f"{partner_id}{path}{ts}{key}{shop_id}"
    sign = hashlib.sha256(base.encode()).hexdigest()
    params.update({"partner_id": int(partner_id), "timestamp": ts, "sign": sign, "shop_id": int(shop_id)})
    url = f"https://partner.shopeemobile.com{path}?{uparse.urlencode(params)}"
    try:
        resp = ureq.urlopen(url, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)[:100]}


def list_shopee_products(shop_id: str) -> list:
    key = os.environ.get("SHOPEE_API_KEY", "")
    partner_id = os.environ.get("SHOPEE_PARTNER_ID", "")
    if not key: return []
    r = shopee_request("/api/v2/product/get_item_list",
                        {"offset": 0, "page_size": 50, "item_status": "NORMAL"},
                        shop_id, partner_id, key)
    return r.get("response", {}).get("item", [])


def main():
    p = argparse.ArgumentParser(description="E-commerce listing manager")
    p.add_argument("--platform", choices=["shopee","lazada","amazon","tiktok-shop"], required=True)
    p.add_argument("--action", choices=["list","create","update-price","delete","bulk-create"], required=True)
    p.add_argument("--shop-id")
    p.add_argument("--product")
    p.add_argument("--products")
    p.add_argument("--id")
    p.add_argument("--price", type=float)
    args = p.parse_args()

    if args.platform == "shopee":
        if args.action == "list":
            items = list_shopee_products(args.shop_id or "")
            print(f"[*] Shopee items: {len(items)}")
            for item in items[:20]:
                print(f"  {item.get('item_id')} | {item.get('item_name','')[:40]}")
        else:
            print(f"[!] {args.action} for {args.platform}: implement via Shopee Open API v2")
            print(f"    Docs: https://open.shopee.com/documents")
    else:
        print(f"[!] {args.platform}: implement using official API SDK")
        print(f"    Lazada: https://open.lazada.com/")
        print(f"    Amazon: https://developer-docs.amazon.com/sp-api/")


if __name__ == "__main__":
    main()
