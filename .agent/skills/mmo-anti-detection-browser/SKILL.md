---
name: mmo-anti-detection-browser
description: "Use when MMO operations need anti-detection browser management: GoLogin, Multilogin, AdsPower, Dolphin Anty, or custom Chrome profile isolation with fingerprint spoofing for multi-account automation without detection."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Anti-Detection Browser Fleet Management

> Manage multi-profile anti-detection browsers for MMO operations with full fingerprint isolation.

## Mission
Operate browser profiles with complete fingerprint isolation per account: unique canvas, WebGL, fonts, timezone, screen, UA, and proxy affinity.

## Mandatory scope checks
1. Choose browser engine: GoLogin / Multilogin / AdsPower / Dolphin Anty / DIY Chromium
2. Define fingerprint isolation: canvas noise, WebGL vendor, font list, screen resolution, timezone per profile
3. Define proxy affinity: 1 profile = 1 residential proxy (sticky session)
4. Define profile storage: local folder isolation vs cloud sync
5. Define session lifecycle: create → warm → operate → park → rotate

## Evidence contract
- profile_id and fingerprint_hash per session
- proxy health check before each launch
- canvas fingerprint test URL result
- IP-profile affinity table
- screenshot proof of platform login per profile

## Platform support matrix
| Browser | API | Free tier | Fingerprint depth |
|---|---|---|---|
| GoLogin | REST API ✅ | 3 profiles | Full (canvas, WebGL, fonts, audio) |
| AdsPower | REST API ✅ | 5 profiles | Full |
| Dolphin Anty | REST API ✅ | 10 profiles | Full |
| Multilogin | REST API ✅ | Paid only | Enterprise grade |
| DIY Chromium | No API | Unlimited | Manual via JS injection |

## Role
- antidetect-browser-operator

## Layer
- layer-4-specialists-and-standalones

## Inputs
- platform account credentials
- proxy list (residential preferred)
- target platform (TikTok/Facebook/Shopee/etc.)
- number of profiles needed

## Outputs
- profile_inventory.json (id, proxy, fingerprint_hash, last_run, status)
- launch scripts per platform
- fingerprint test report

## Likely next step
- mmo-proxy-network-ops
- mmo-identity-infrastructure
- browser-fingerprint-engineering
- antibot-challenge-solving
- mmo-nick-warmup-engine
