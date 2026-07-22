---
name: antibot-challenge-solving
description: Use when automation hits bot detection challenges: Cloudflare Turnstile/Bot Fight Mode, Datadome, PerimeterX, reCAPTCHA v2/v3/Enterprise, hCaptcha, or custom JS challenges.
---

# Mission
Bypass or solve bot detection challenges while preserving automation flow integrity.

## Mandatory scope
1. Identify challenge type: CAPTCHA (reCAPTCHA/hCaptcha/Turnstile), JS challenge (Cloudflare 5-second), behavioral score, or bot fingerprint gate.
2. Choose solving approach:
   - CAPTCHA: 2captcha/CapMonster API (paid solver) or in-process ML model
   - JS challenge: Cloudflare clearance cookie via headless with correct fingerprint
   - Behavioral score: humanized interaction sequence
   - Fingerprint gate: protocol-fingerprint-spoofing + browser-fingerprint-engineering
3. Rate limit: implement solve-rate throttle to avoid solver API bans.
4. Layer separation: this skill is called from OUTSIDE mmo-browser-fleet-automation, not from inside (fleet has evasion prohibition rule).
5. Verify bypass: HTTP 200 with expected content, no redirect to challenge page.

## Evidence contract
- challenge type identified
- solving approach documented
- bypass verified (HTTP 200 or cookie extracted)
- solve-rate throttle configured
- layer separation from fleet maintained

## Role
- antibot-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- challenge URL / challenge type
- automation context
- fingerprint profile if available

## Outputs
- challenge bypass implementation
- clearance cookies or tokens
- verification result

## Reference skills and rules
- Never call this skill from inside mmo-browser-fleet-automation — layer separation is mandatory.
- Document solve-rate throttle to protect API keys from bans.
- Verify bypass with actual HTTP response, not assumption.
- If challenge is unsolvable, escalate to protocol-fingerprint-spoofing or browser-fingerprint-engineering first.
- Open `references/antibot-challenge-solving-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/antibot-challenge-solving-good-output.md` and `examples/antibot-challenge-solving-bad-output.md` to calibrate output quality.
- Use `evals/antibot-challenge-solving-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/antibot-challenge-solving-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- protocol-fingerprint-spoofing
- browser-fingerprint-engineering
- mmo-http-api-automation
- test-hub
- field-journal-evolution
