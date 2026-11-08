---
name: browser-fingerprint-engineering
description: "LAYER 1 (TECHNIQUE). Use when a specific fingerprint vector needs a working spoof implementation — Canvas / WebGL / AudioContext / fonts / navigator / screen / timezone / battery / device memory / behavioral biometrics. Returns technique recipes (code snippets + consistency rules + test URL), not identities. Called by L2 (`mmo-anti-detection-browser`) when a vendor cannot spoof a vector, or by L3 (`mmo-identity-infrastructure`) when designing a new fingerprint profile."
---

# Mission
Produce verified technique recipes for individual fingerprint vectors. One recipe = one vector + one implementation level + a verification result. Do not bundle recipes into an identity; L3 does that.

## Scope boundary (do not violate)
- IN scope: canvas / WebGL / AudioContext / fonts / navigator / screen / timezone / battery / device memory / behavioral biometrics techniques; CDP/JS/vendor-config snippets; noise strategy; verification run.
- OUT of scope: deciding WHICH identity gets WHICH recipe → L3.
- OUT of scope: wiring the recipe into a specific vendor (GoLogin/Multilogin/AdsPower) → L2.
- OUT of scope: orchestrating sessions that use the recipe → L4.
- OUT of scope: solving bot-challenges (reCAPTCHA/Turnstile) → `antibot-challenge-solving`.

## Pre-flight (refuse to produce the recipe if any missing)
1. Target vector named (not "fingerprinting in general").
2. Implementation level chosen (CDP | JS pre-page | vendor-config | custom build).
3. Consistency anchors from L3 passed in (tz, locale, UA.platform) — or explicit statement that this recipe is anchor-independent.
4. At least one verification URL named.

## Recipe format (one block per vector)
```
## Vector: <canvas | webgl | audio | fonts | navigator | screen | tz | battery | memory | behavioral>
- level: CDP | JS-pre-page | vendor-config | custom-build
- snippet: <code, 5–40 lines>
- noise_strategy: static | per-session-dynamic | per-call-dynamic
- consistency_depends_on: [<other vector names>]
- verification_url: <fingerprintjs / browserleaks / creepjs / pixelscan>
- verification_result: <pass | fail: <what leaked>>
```

## Vector catalog (minimum coverage)
| Vector | Default level | Noise strategy | Primary verifier |
|---|---|---|---|
| Canvas | JS-pre-page | per-session-dynamic | browserleaks/canvas |
| WebGL | CDP + JS | per-session-dynamic | browserleaks/webgl |
| AudioContext | JS-pre-page | per-session-dynamic | audiofingerprint2 demo |
| Fonts | JS-pre-page | static (per-identity) | browserleaks/fonts |
| Navigator | CDP | static | fingerprintjs |
| Screen | CDP | static | browserleaks/javascript |
| Timezone | CDP + Date override | static (from L3) | browserleaks/ip |
| Battery | JS-pre-page | per-session | browserleaks/javascript |
| Behavioral | humanization lib | per-action-dynamic | custom scoring |

## Failure modes to self-check
- You spoofed canvas without declaring `consistency_depends_on: [UA.platform]` ⇒ incomplete, revise.
- You used static noise ⇒ replace with per-session noise.
- You produced a recipe with no verification result ⇒ run verification or mark `verification_result: pending` and warn downstream.
- You composed a full identity ⇒ wrong layer, hand off to L3.

## Role
- browser-fingerprint-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target platform fingerprint vectors (which signals to spoof, in order of importance)
- browser engine (Chromium/Firefox/WebKit) and automation framework (Playwright/Puppeteer/CDP/anti-detect vendor)
- consistency anchors from L3 (timezone, locale, platform family) that this technique must honor

## Outputs
- per-vector technique recipe: implementation level (CDP override | JS inject | vendor config), code snippet, consistency constraints, verification URL
- noise strategy per vector (per-session dynamic vs stable)
- verification evidence: result from at least one of fingerprintjs.com, browserleaks.com, creepjs, pixelscan.net

## Reference skills and rules
- This skill is LAYER 1 — TECHNIQUE ONLY. It produces recipes, not identities. Binding recipes into a durable identity is L3 (`mmo-identity-infrastructure`). Applying recipes inside a specific anti-detect vendor is L2 (`mmo-anti-detection-browser`).
- No vector is spoofed in isolation. Every recipe states which other vectors it depends on for consistency (e.g. canvas noise strategy depends on UA.platform).
- Dynamic noise is per-session, not static. Static noise is a stronger fingerprint than no noise.
- A recipe without a verification URL result is incomplete — refuse.
- Open `references/browser-fingerprint-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/browser-fingerprint-engineering-good-output.md` and `examples/browser-fingerprint-engineering-bad-output.md` to calibrate output quality.
- Use `evals/browser-fingerprint-engineering-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/browser-fingerprint-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-anti-detection-browser
- mmo-identity-infrastructure
- protocol-fingerprint-spoofing
- antibot-challenge-solving
