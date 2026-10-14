---
name: mmo-captcha-farm
description: "Use when MMO automation hits CAPTCHA at scale: manage CAPTCHA solving farm with multiple API keys, rate optimization, cost tracking, and failover between services (2captcha, CapMonster, AntiCaptcha, DeathByCaptcha). Use when automation needs sustained CAPTCHA solving throughput without API key bans."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when MMO automation hits CAPTCHA at scale: manage CAPTCHA solving farm with multiple API keys, rate optimization, cost tracking, and failover between services (2captcha, CapMonster, AntiCaptcha, DeathByCaptcha).

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
- mmo-automation-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with mmo-captcha-farm findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside mmo-captcha-farm's scope back through `mmo-authorization-gate` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/mmo-captcha-farm-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-captcha-farm-good-output.md` and `examples/mmo-captcha-farm-bad-output.md` to calibrate output quality.
- Use `evals/mmo-captcha-farm-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-captcha-farm-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-captcha-farm
- mmo-authorization-gate
- workflow-router
