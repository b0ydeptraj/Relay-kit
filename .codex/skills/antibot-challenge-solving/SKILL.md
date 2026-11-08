---
name: antibot-challenge-solving
description: "Use when automation is blocked by a bot-detection challenge (Cloudflare Turnstile / Bot Fight Mode, Datadome, PerimeterX, reCAPTCHA v2/v3/Enterprise, hCaptcha, Arkose, or custom JS). CLASSIFIES the challenge type and CHOOSES a strategy (solver-API vs reverse-JS vs browser-based vs route-around). Does NOT solve the challenge itself; routes to `mmo-captcha-farm` (solver), `frontend-crypto-reverse` (reverse JS), or `browser-fingerprint-engineering` + `mmo-browser-fleet-automation` (clean browser path)."
allowed-tools: ["Read", "Write", "Grep", "Glob"]
---

# Mission
Identify which anti-bot system is blocking the lane and pick the right response strategy. Write one decision record. Hand off to the solver skill.

## Scope boundary (do not violate)
- IN scope: reading block symptoms, classifying detector, choosing strategy, writing the decision record, routing.
- OUT of scope: calling 2captcha/CapMonster -> `mmo-captcha-farm`.
- OUT of scope: reversing the JS challenge code -> `frontend-crypto-reverse`.
- OUT of scope: running the clean-browser path -> `browser-fingerprint-engineering` + `mmo-browser-fleet-automation`.

## Classification signals (anchor every verdict to at least one)
| Detector | Signal in response/page |
|---|---|
| Cloudflare Turnstile | `cf-chl-*` cookies, `__cf_bm`, `challenges.cloudflare.com` iframe |
| Cloudflare Bot Fight | 403 + `cf-mitigated: challenge` header, managed-challenge HTML |
| Datadome | `datadome` cookie, `ct.captcha-delivery.com` iframe |
| PerimeterX / HUMAN | `_px*` cookies, `captcha.px-cdn.net` |
| reCAPTCHA v2 | `www.google.com/recaptcha/api2` iframe |
| reCAPTCHA v3 | `grecaptcha.execute(...).then(token=>...)` scoring, no iframe |
| reCAPTCHA Enterprise | `www.google.com/recaptcha/enterprise.js` |
| hCaptcha | `hcaptcha.com/captcha` iframe, `h-captcha-response` field |
| Arkose FunCaptcha | `funcaptcha.com`, interactive puzzle UI |
| Custom JS | obfuscated JS returning a signed token in a header |

## Strategy matrix
| Challenge x client | HTTP-only client | Real browser |
|---|---|---|
| reCAPTCHA v2 / hCaptcha | solver-api -> mmo-captcha-farm | solver-api |
| reCAPTCHA v3 (low score) | reverse-js -> frontend-crypto-reverse (grecaptcha stub) | browser-clean -> warmed identity |
| Cloudflare Turnstile | solver-api (supports) or reverse-js | browser-clean |
| Cloudflare Bot Fight | browser-clean mandatory | browser-clean |
| Datadome / PX | browser-clean + behavioral humanization | browser-clean |
| Arkose FunCaptcha | solver-api (expensive) | solver-api |
| Custom signed-header JS | reverse-js -> frontend-crypto-reverse | reverse-js |

Prefer `route-around` first: if the platform has an official public API or a mobile API that does not front this detector, switch to it (-> `api-integration`).

## Decision record format (write to the lane's state dir)
```
- challenge_type: <detector>
- observed_signals: [<headers / cookies / iframe URLs>]
- client_context: http-only | browser
- strategy: solver-api | reverse-js | browser-clean | route-around
- handoff_to: <skill name>
- handoff_fields: {service_preference_order: [...], token_name: "...", ...}
- decided_at: <ISO>
```

## Failure modes to self-check
- You picked solver-api without naming the token name downstream must inject -> record is incomplete.
- You picked reverse-js without checking whether the JS is actually reversible in budget -> add a timebox fallback to browser-clean.
- You started solving/reversing/running the browser here -> wrong skill, hand off.
- You classified from the URL alone -> re-classify from response bytes.

## Role
- antibot-strategist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- symptom: raw block response (HTTP status + body snippet), or screenshot of challenge UI, or JS error
- automation context: HTTP-only client vs real browser vs headless
- budget tolerance: paid solver allowed? latency ceiling?

## Outputs
- classification record: challenge_type, detector_vendor, observed_signals
- strategy decision: solver-api | reverse-js | browser-clean | route-around
- handoff: names the next skill and the fields it needs (service preference order, token name, etc.)

## Reference skills and rules
- This skill decides the STRATEGY. It does not solve. Downstream skills solve.
- Classification is anchored to observable signals in the response or page - not to guesses from the URL.
- Prefer `route-around` (switch to official API path) when available before paying a solver.
- Record the decision; downstream skills refuse to run if no decision record exists (prevents burning solver budget on the wrong challenge).
- Open `references/antibot-challenge-solving-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/antibot-challenge-solving-good-output.md` and `examples/antibot-challenge-solving-bad-output.md` to calibrate output quality.
- Use `evals/antibot-challenge-solving-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/antibot-challenge-solving-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-captcha-farm
- frontend-crypto-reverse
- browser-fingerprint-engineering
- mmo-browser-fleet-automation
- api-integration
