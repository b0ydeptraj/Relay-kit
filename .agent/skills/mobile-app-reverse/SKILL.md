---
name: mobile-app-reverse
description: Use when MMO mobile operations need to reverse-engineer APK or IPA apps: find API endpoints, signing keys, certificate pinning bypass, or replicate app behavior without the app.
---

# Mission
Reverse-engineer mobile apps to extract API endpoints, signing logic, and protocol details for programmatic replication.

## Mandatory scope
1. Platform: Android (APK) or iOS (IPA) — document platform and app version.
2. Decompilation: APK -> jadx/apktool; IPA -> frida-ios-dump + class-dump or Ghidra.
3. Certificate pinning bypass: Frida script for Android (SSLContext.getDefault / OkHttp) or iOS (SecTrustEvaluate / AFNetworking).
4. API endpoint extraction: intercept traffic with mitmproxy/Burp after pin bypass; map all endpoints.
5. Signing parameter reverse: identify request signing (HMAC, timestamp, nonce, device fingerprint).
6. Replicate in Python: implement API client without app dependency; verify responses match.

## Evidence contract
- platform and app version documented
- decompilation output captured
- certificate pinning bypassed (traffic visible in proxy)
- API endpoints mapped
- signing logic reversed and replicated
- Python client verified against app responses

## Role
- mobile-reverse-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- APK or IPA file or app package name
- target functionality to replicate
- mobile device or emulator

## Outputs
- API endpoint map
- signing implementation
- Python client
- certificate pinning bypass script

## Reference skills and rules
- Certificate pinning bypass must be verified with actual traffic capture.
- API endpoint map must include all request headers and signing parameters.
- Signing replication must produce byte-exact results compared to app output.
- Document app version — APIs change across versions.
- Open `references/mobile-app-reverse-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mobile-app-reverse-good-output.md` and `examples/mobile-app-reverse-bad-output.md` to calibrate output quality.
- Use `evals/mobile-app-reverse-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mobile-app-reverse-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- frontend-crypto-reverse
- protocol-fingerprint-spoofing
- mmo-http-api-automation
- mmo-mobile-app-automation
- test-hub
- field-journal-evolution
