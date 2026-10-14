#!/usr/bin/env python3
"""
scraper.py - Structured web scraper with XPath/CSS selectors, pagination, and export.

Usage:
    python scripts/scraper.py --url https://example.com --selector "div.item h2" --field title
    python scripts/scraper.py --config scrape_config.json --output data.csv
    python scripts/scraper.py --url URL --paginate --max-pages 10 --delay 2
    python scripts/scraper.py --sitemap https://example.com/sitemap.xml --selector "p.content"

scrape_config.json: {"url":"...","fields":{"title":"h1","price":".price","link":"a[href]@href"}}
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import random
import urllib.request as ureq
import urllib.parse as uparse

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
]


def fetch_page(url: str, proxy: str = None, cookies: dict = None, timeout: int = 20) -> str:
    headers = {"User-Agent": random.choice(UA_LIST), "Accept-Language": "en-US,en;q=0.9",
               "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"}
    if cookies:
        headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
    req = ureq.Request(url, headers=headers)
    handlers = []
    if proxy:
        handlers.append(ureq.ProxyHandler({"http": proxy, "https": proxy}))
    opener = ureq.build_opener(*handlers)
    try:
        resp = opener.open(req, timeout=timeout)
        encoding = resp.headers.get_content_charset("utf-8")
        return resp.read().decode(encoding, errors="replace")
    except Exception as e:
        print(f"[-] Fetch failed {url}: {e}")
        return ""


def css_to_regex_extract(html: str, selector: str) -> list:
    """Simplified CSS selector extraction using regex (no BeautifulSoup needed)."""
    # Extract attribute: div.class[attr] → get attr value
    attr_match = re.match(r"(.+)\[([a-z-]+)\]$", selector)
    attr = None
    if attr_match:
        selector = attr_match.group(1)
        attr = attr_match.group(2)

    # Convert simple CSS to regex patterns
    tag = re.sub(r"[.#\[\]~+>:*].*", "", selector).strip() or r"\w+"
    class_match = re.search(r"\.([a-zA-Z0-9_-]+)", selector)
    id_match    = re.search(r"#([a-zA-Z0-9_-]+)", selector)

    if class_match:
        pattern = rf'<{tag}[^>]*class="[^"]*{re.escape(class_match.group(1))}[^"]*"[^>]*>(.*?)</{tag}>'
    elif id_match:
        pattern = rf'<{tag}[^>]*id="{re.escape(id_match.group(1))}"[^>]*>(.*?)</{tag}>'
    else:
        pattern = rf'<{re.escape(tag)}[^>]*>(.*?)</{re.escape(tag)}>'

    # Find all matches
    matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
    # Strip inner HTML tags
    results = [re.sub(r"<[^>]+>", "", m).strip() for m in matches if m.strip()]

    if attr:
        attr_pattern = rf'<[^>]+{attr}="([^"]+)"[^>]*>'
        results = re.findall(attr_pattern, html)

    return results[:100]  # Cap at 100 results per page


def find_next_page(html: str, current_url: str) -> str:
    """Find next page link."""
    patterns = [
        r'<a[^>]+href="([^"]+)"[^>]*>[^<]*(?:Next|next|>|»)[^<]*</a>',
        r'<link[^>]+rel="next"[^>]+href="([^"]+)"',
        r'href="([^"]+page=\d+[^"]*)"',
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            href = m.group(1)
            if href.startswith("http"):
                return href
            return uparse.urljoin(current_url, href)
    return ""


def scrape_site(config: dict, proxy: str = None, max_pages: int = 10,
                delay: float = 2.0, paginate: bool = False) -> list:
    url = config["url"]
    fields = config.get("fields", {})
    if not fields and config.get("selector"):
        fields = {"value": config["selector"]}

    all_data = []
    current_url = url
    page_num = 1

    while current_url and page_num <= max_pages:
        print(f"[*] Page {page_num}: {current_url[:70]}...")
        html = fetch_page(current_url, proxy)
        if not html:
            break

        # Extract each field
        page_items = {}
        for field_name, selector in fields.items():
            page_items[field_name] = css_to_regex_extract(html, selector)
            print(f"    {field_name}: {len(page_items[field_name])} items")

        # Zip fields into records
        max_len = max((len(v) for v in page_items.values()), default=0)
        for i in range(max_len):
            record = {"_page": page_num, "_url": current_url}
            for field, values in page_items.items():
                record[field] = values[i] if i < len(values) else ""
            all_data.append(record)

        if not paginate:
            break
        next_url = find_next_page(html, current_url)
        if not next_url or next_url == current_url:
            print("[*] No more pages")
            break
        current_url = next_url
        page_num += 1
        time.sleep(delay + random.uniform(0, delay * 0.5))

    print(f"[*] Total: {len(all_data)} records from {page_num} pages")
    return all_data


def main():
    p = argparse.ArgumentParser(description="Web scraper with pagination and export")
    p.add_argument("--url", help="Target URL")
    p.add_argument("--selector", help="CSS selector (e.g. 'h2.title')")
    p.add_argument("--field", default="value", help="Field name for selector output")
    p.add_argument("--config", help="Scrape config JSON file")
    p.add_argument("--output", default="scraped.json", help="Output file (.json or .csv)")
    p.add_argument("--paginate", action="store_true")
    p.add_argument("--max-pages", type=int, default=10)
    p.add_argument("--delay", type=float, default=2.0)
    p.add_argument("--proxy")
    args = p.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    elif args.url:
        config = {"url": args.url, "fields": {args.field: args.selector} if args.selector else {}}
    else:
        print("[-] --url or --config required"); sys.exit(1)

    data = scrape_site(config, args.proxy, args.max_pages, args.delay, args.paginate)

    if args.output.endswith(".csv") and data:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"[+] Saved {len(data)} records to {args.output}")


if __name__ == "__main__":
    main()
