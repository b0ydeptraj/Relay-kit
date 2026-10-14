#!/usr/bin/env python3
"""
tiktok_shop.py - TikTok Shop seller automation: product management, order handling,
flash deals, and promotion management via TikTok Shop Seller API.

Usage:
    python scripts/tiktok_shop.py --action list-products --shop-id SHOP_ID
    python scripts/tiktok_shop.py --action orders --status pending
    python scripts/tiktok_shop.py --action update-stock --product-id ID --quantity 100
    python scripts/tiktok_shop.py --action create-promo --product-id ID --discount 20 --duration 24h
    python scripts/tiktok_shop.py --action analytics --days 7

API key: TIKTOK_SHOP_API_KEY, TIKTOK_SHOP_SECRET env vars.
Official docs: https://partner.tiktokshop.com/doc
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

SHOP_API_BASE = "https://open-api.tiktokglobalshop.com"
API_KEY    = os.environ.get("TIKTOK_SHOP_API_KEY", "")
API_SECRET = os.environ.get("TIKTOK_SHOP_SECRET", "")
ACCESS_TOKEN = os.environ.get("TIKTOK_SHOP_ACCESS_TOKEN", "")

ORDER_STATUSES = {
    "pending": "AWAITING_SHIPMENT",
    "shipped": "SHIPPED",
    "delivered": "DELIVERED",
    "cancelled": "CANCELLED",
    "return": "IN_CANCEL",
}


def sign_request(path: str, params: dict, body: str = "") -> dict:
    """Sign TikTok Shop API request."""
    ts = int(time.time())
    params["timestamp"] = ts
    params["app_key"] = API_KEY
    params["access_token"] = ACCESS_TOKEN

    # Build sign string: secret + path + sorted_params + body + secret
    sorted_params = "".join(f"{k}{v}" for k, v in sorted(params.items()) if k != "sign")
    sign_str = f"{API_SECRET}{path}{sorted_params}{body}{API_SECRET}"
    sign = hashlib.sha256(sign_str.encode()).hexdigest()
    params["sign"] = sign
    return params


def api_get(path: str, params: dict = None) -> dict:
    params = sign_request(path, params or {})
    url = f"{SHOP_API_BASE}{path}?{uparse.urlencode(params)}"
    req = ureq.Request(url, headers={
        "Content-Type": "application/json",
        "x-tts-access-token": ACCESS_TOKEN,
    })
    try:
        resp = ureq.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"code": -1, "message": str(e)[:100]}


def api_post(path: str, body: dict, params: dict = None) -> dict:
    body_str = json.dumps(body)
    params = sign_request(path, params or {}, body_str)
    url = f"{SHOP_API_BASE}{path}?{uparse.urlencode(params)}"
    req = ureq.Request(url, body_str.encode(), {
        "Content-Type": "application/json",
        "x-tts-access-token": ACCESS_TOKEN,
    })
    try:
        resp = ureq.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        return {"code": -1, "message": str(e)[:100]}


def list_products(shop_id: str, page: int = 1, page_size: int = 20) -> list:
    r = api_get("/api/products/search", {
        "shop_id": shop_id, "page_number": page, "page_size": page_size
    })
    if r.get("code") == 0:
        products = r.get("data", {}).get("products", [])
        print(f"[*] Products ({len(products)}):")
        for p in products:
            skus = p.get("skus", [])
            stock = sum(sku.get("stock_infos", [{}])[0].get("available_stock", 0) for sku in skus if sku.get("stock_infos"))
            price = skus[0].get("price", {}).get("sale_price", "?") if skus else "?"
            print(f"  {p.get('id')} | {p.get('title','')[:40]} | stock:{stock} | ${price}")
        return products
    else:
        print(f"[-] Error: {r.get('message')}")
        return []


def get_orders(shop_id: str, status: str = "pending", days: int = 7) -> list:
    from_time = int(time.time()) - days * 86400
    r = api_get("/api/orders/search", {
        "shop_id": shop_id,
        "order_status": ORDER_STATUSES.get(status, "AWAITING_SHIPMENT"),
        "create_time_from": from_time,
        "create_time_to": int(time.time()),
        "page_size": 50,
    })
    if r.get("code") == 0:
        orders = r.get("data", {}).get("order_list", [])
        print(f"[*] Orders ({status}): {len(orders)}")
        total_revenue = 0
        for o in orders:
            amt = float(o.get("payment", {}).get("total_amount", 0))
            total_revenue += amt
            print(f"  {o.get('order_id')} | {o.get('order_status')} | ${amt:.2f} | {o.get('create_time','')[:10]}")
        print(f"  Total revenue: ${total_revenue:.2f}")
        return orders
    else:
        print(f"[-] Error: {r.get('message')}")
        return []


def update_stock(shop_id: str, product_id: str, sku_id: str, quantity: int) -> dict:
    r = api_post("/api/products/stocks", {
        "product_id": product_id,
        "skus": [{"id": sku_id, "stock_infos": [{"available_stock": quantity, "warehouse_id": ""}]}]
    }, {"shop_id": shop_id})
    ok = r.get("code") == 0
    print(f"[{'OK' if ok else 'FAIL'}] Update stock {product_id}: {quantity} units")
    return r


def get_analytics(shop_id: str, days: int = 7) -> dict:
    end_time = int(time.time())
    start_time = end_time - days * 86400
    r = api_get("/api/seller/analytics/overview", {
        "shop_id": shop_id,
        "start_timestamp": start_time,
        "end_timestamp": end_time,
    })
    if r.get("code") == 0:
        data = r.get("data", {})
        print(f"[*] Analytics ({days} days):")
        print(f"  GMV: ${data.get('gmv', 0)}")
        print(f"  Orders: {data.get('orders', 0)}")
        print(f"  Visitors: {data.get('visitors', 0)}")
        print(f"  Conversion: {data.get('conversion_rate', 0)}%")
        return data
    print(f"[-] No analytics data or error: {r.get('message')}")
    return {}


def main():
    if not API_KEY or not ACCESS_TOKEN:
        print("[!] Set TIKTOK_SHOP_API_KEY and TIKTOK_SHOP_ACCESS_TOKEN env vars")
        print("    Docs: https://partner.tiktokshop.com/doc/page/282837")

    p = argparse.ArgumentParser(description="TikTok Shop seller automation")
    p.add_argument("--action", choices=["list-products","orders","update-stock","analytics"], required=True)
    p.add_argument("--shop-id", default=os.environ.get("TIKTOK_SHOP_ID",""))
    p.add_argument("--product-id")
    p.add_argument("--sku-id")
    p.add_argument("--quantity", type=int)
    p.add_argument("--status", default="pending")
    p.add_argument("--days", type=int, default=7)
    args = p.parse_args()

    if args.action == "list-products":
        list_products(args.shop_id)
    elif args.action == "orders":
        get_orders(args.shop_id, args.status, args.days)
    elif args.action == "update-stock":
        if not args.product_id or args.quantity is None:
            print("[-] --product-id and --quantity required"); sys.exit(1)
        update_stock(args.shop_id, args.product_id, args.sku_id or "", args.quantity)
    elif args.action == "analytics":
        get_analytics(args.shop_id, args.days)


if __name__ == "__main__":
    main()
