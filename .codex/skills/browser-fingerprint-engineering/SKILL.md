---
name: browser-fingerprint-engineering
description: Use when browser-based automation needs to defeat canvas fingerprinting, WebGL fingerprinting, AudioContext fingerprinting, font detection, or behavioral biometrics.
---

# Mission
Implement code-level browser fingerprint spoofing that survives advanced platform behavioral analysis.

## Mandatory scope
1. Map fingerprint vectors targeted by platform: Canvas, WebGL, AudioContext, fonts, navigator properties, screen resolution, timezone, battery API, device memory.
2. Implement spoofing at the correct level: CDP override, JS injection before page load, custom browser build, or anti-detect browser configuration.
3. Consistency rule: all spoofed values must be internally consistent (timezone == geolocation region == language == locale).
4. Dynamic noise: add small random noise to Canvas/WebGL outputs per session to prevent cross-session linking.
5. Behavioral biometrics: mouse movement entropy, typing cadence, scroll patterns — use humanization library.
6. Verify against fingerprinting test sites: fingerprintjs.com, browserleaks.com, pixelscan.net.

## Evidence contract
- fingerprint vectors listed and addressed
- consistency check passed (timezone/locale/language aligned)
- dynamic noise implemented
- behavioral humanization documented
- test site results captured

## Role
- browser-fingerprint-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target platform fingerprint detection signals
- browser automation framework
- mmo-identity-infrastructure profile

## Outputs
- fingerprint spoofing implementation
- consistency audit
- test site results

## Reference skills and rules
- Never spoof values in isolation — all signals must be internally consistent.
- Dynamic noise must be per-session, not static — static noise is as detectable as no noise.
- Behavioral biometrics matter as much as technical fingerprints.
- Verify against test sites before deployment — assumption-based spoofing fails.
- Open `references/browser-fingerprint-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/browser-fingerprint-engineering-good-output.md` and `examples/browser-fingerprint-engineering-bad-output.md` to calibrate output quality.
- Use `evals/browser-fingerprint-engineering-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/browser-fingerprint-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- protocol-fingerprint-spoofing
- antibot-challenge-solving
- mmo-identity-infrastructure
- mmo-browser-fleet-automation
- test-hub
- field-journal-evolution
