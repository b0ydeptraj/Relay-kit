---
name: tiktok-automation
description: "Use when automating TikTok operations at scale: account management, content posting, engagement automation (likes/follows/comments/views), TikTok Shop management, live stream automation, hashtag research, and analytics tracking. Supports cookie-based sessions, API reverse engineering, and browser automation approaches."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# TikTok Automation

> Full-stack TikTok automation: accounts, content, engagement, shop, and analytics.

## Mission
Automate TikTok operations across multiple accounts with anti-detection and platform limit awareness.

## Mandatory scope checks
1. Define operation type: organic growth / shop / analytics / content
2. Define account pool size and proxy affinity (1 account = 1 proxy)
3. Define daily limits per account (stay 30% below platform limits)
4. Define content strategy: reup / original / AI-generated
5. Session management: cookie-based or browser automation

## Platform limits (safe thresholds - 30% under real limits)
| Action | Safe daily limit | Risky above |
|---|---|---|
| Likes | 350 | 500 |
| Follows | 140 | 200 |
| Comments | 70 | 100 |
| DMs | 35 | 50 |
| Video uploads | 3 | 5 |
| Live hours | 4 | 8 |

## API endpoints (internal, subject to change)
- Login: `POST /passport/user/login/`
- Feed: `GET /aweme/v1/feed/`
- Like: `POST /aweme/v1/commit/item/digg/`
- Follow: `POST /aweme/v1/commit/follow/user/`
- Comment: `POST /aweme/v1/comment/publish/`
- Upload: `POST /aweme/v1/aweme/post/`
- Shop: `GET /ec/shop/product/list/`

## Session management
- Method A: Cookie session (msToken, sessionid, tt-csrf-token)
- Method B: Browser automation (anti-detect browser + fingerprint)
- Method C: Official Creator API (limited features, no engagement)

## Role
- tiktok-automation-operator

## Layer
- layer-4-specialists-and-standalones

## Inputs
- accounts.json (cookie sessions or credentials)
- content/ directory (videos, captions, hashtags)
- proxy_pool.txt

## Outputs
- engagement_log.jsonl
- account_health.json
- analytics_report.json

## Likely next step
- mmo-anti-detection-browser
- mmo-proxy-network-ops
- mmo-content-factory
- mmo-nick-warmup-engine
- mmo-reup-automation
