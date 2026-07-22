---
name: protocol-fingerprint-spoofing
description: Use when HTTP/HTTPS/TLS traffic needs to spoof or match a specific protocol fingerprint to evade network inspection, bot detection, or TLS fingerprinting (JA3/JA4/HTTP2).
---

# Mission
Match target protocol fingerprints (TLS, HTTP/2, TCP) precisely so traffic is indistinguishable from a legitimate client.

## Mandatory scope
1. Identify fingerprint target: JA3/JA3S, JA4, HTTP/2 SETTINGS, TCP window size, User-Agent.
2. Collect reference fingerprint from legitimate client (Chrome 120+, Firefox 121+, curl).
3. Implement spoofing: custom TLS stack (utls/tls-client), HTTP/2 SETTINGS frame order, header order.
4. Verify match: run fingerprint scanner (tls.peet.ws, Scapy, Wireshark) against implementation.
5. Document cipher suite order, TLS extensions, and GREASE values used.
6. Test against target platform's detection (Cloudflare, Akamai, Datadome) in controlled env.

## Evidence contract
- reference fingerprint captured
- spoofed fingerprint matches (JA3/JA4 match documented)
- cipher suite and extension order documented
- verified against target detection platform

## Role
- protocol-fingerprint-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target protocol (TLS version, HTTP version)
- reference client fingerprint
- target platform

## Outputs
- protocol implementation
- fingerprint comparison
- detection test result

## Reference skills and rules
- Never claim fingerprint match without scanner verification.
- Document GREASE values — they are part of Chrome fingerprint.
- HTTP/2 SETTINGS frame order matters — match exactly.
- TLS extension order is as important as cipher suite choice.
- Open `references/protocol-fingerprint-spoofing-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/protocol-fingerprint-spoofing-good-output.md` and `examples/protocol-fingerprint-spoofing-bad-output.md` to calibrate output quality.
- Use `evals/protocol-fingerprint-spoofing-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/protocol-fingerprint-spoofing-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- browser-fingerprint-engineering
- antibot-challenge-solving
- network-stealth-c2
- mmo-http-api-automation
- test-hub
- field-journal-evolution
