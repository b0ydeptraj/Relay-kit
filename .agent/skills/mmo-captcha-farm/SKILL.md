---
name: mmo-captcha-farm
description: "Use when MMO automation hits CAPTCHA at scale: manage CAPTCHA solving farm with multiple API keys, rate optimization, cost tracking, and failover between services (2captcha, CapMonster, AntiCaptcha, DeathByCaptcha). Use when automation needs sustained CAPTCHA solving throughput without API key bans."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# CAPTCHA Farm Management

> Manage a pool of CAPTCHA solving API keys with rate limits, cost tracking, and failover.

## Mission
Maximize CAPTCHA solving throughput while minimizing cost and API key ban risk across multiple services.

## Mandatory scope checks
1. Inventory available API keys per service (2captcha, CapMonster, AntiCaptcha)
2. Define CAPTCHA type mix: reCAPTCHA v2/v3, hCaptcha, Turnstile, image
3. Define solve rate targets (solves/hour per task)
4. Define cost budget ($/1000 solves)
5. Define failover order: primary → secondary → tertiary
6. Define key rotation policy: rotate on ban, low balance, or rate limit

## Cost comparison (typical rates)
| Service | reCAPTCHA v2 | hCaptcha | Image |
|---|---|---|---|
| 2captcha | $2.99/1000 | $2.00/1000 | $0.50/1000 |
| CapMonster | $1.20/1000 | $1.00/1000 | $0.40/1000 |
| AntiCaptcha | $2.00/1000 | $1.50/1000 | $0.50/1000 |
| DeathByCaptcha | $1.39/1000 | N/A | $1.39/1000 |

## Evidence contract
- solves/hour tracked per key per service
- cost per solve logged
- API key health (balance + ban status) checked before each batch
- failover events logged with reason

## Role
- captcha-farm-operator

## Layer
- layer-4-specialists-and-standalones

## Inputs
- captcha_api_keys.json (service → key list)
- target CAPTCHA type
- volume target (solves/hour)
- budget cap

## Outputs
- solve_log.jsonl (timestamp, service, type, elapsed, cost, success)
- key_health_report.json (balance, rate, ban_status per key)
- throughput_report.json

## Likely next step
- antibot-challenge-solving
- mmo-browser-fleet-automation
- mmo-account-operations
