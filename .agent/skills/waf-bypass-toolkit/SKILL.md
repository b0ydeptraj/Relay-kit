---
name: waf-bypass-toolkit
description: "Use when web application attacks are blocked by WAF (Cloudflare, Akamai, AWS WAF, F5, ModSecurity). Generate WAF bypass payloads, test encoding evasions, and identify bypass techniques for SQLi, XSS, SSRF, LFI, RCE payloads. Engagement proof required."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# WAF Bypass Toolkit

> Generate and test WAF bypass payloads for authorized penetration testing.

## Mission
Evade WAF signature-based detection to test true application vulnerabilities.

## Mandatory scope checks
1. Engagement proof required.
2. Identify WAF vendor: Cloudflare / Akamai / AWS WAF / ModSecurity / F5 ASM
3. Identify WAF rule set if possible (ModSecurity CRS version)
4. Choose bypass category: SQLi / XSS / SSRF / LFI / RCE / Path traversal
5. Test payload in controlled environment first
6. Document which bypass works and log to evidence artifact

## Bypass techniques by WAF
| WAF | Known bypass surface |
|---|---|
| Cloudflare | Case variation, Unicode normalization, chunked encoding |
| ModSecurity CRS | comment injection, encoding chains, keyword splitting |
| AWS WAF | URL encoding, double encoding, JSON body obfuscation |
| Akamai | Header injection, multipart body bypass |

## Evidence contract
- engagement_proof confirmed
- target WAF identified
- bypass payload documented with test request/response
- real vulnerability confirmed (not just WAF bypass)

## Role
- waf-bypass-specialist

## Layer
- layer-4-specialists-and-standalones

## Likely next step
- web-app-scanner
- web-logic-auditor
- searching-exploit-db
- offensive-security-engagement
