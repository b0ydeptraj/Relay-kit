---
name: waf-bypass-toolkit
description: "Use when web application attacks are blocked by WAF (Cloudflare, Akamai, AWS WAF, F5, ModSecurity). Generate WAF bypass payloads, test encoding evasions, and identify bypass techniques for SQLi, XSS, SSRF, LFI, RCE payloads. Engagement proof required."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when web application attacks are blocked by WAF (Cloudflare, Akamai, AWS WAF, F5, ModSecurity).

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
- offensive-security-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with waf-bypass-toolkit findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside waf-bypass-toolkit's scope back through `offensive-security-engagement` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/waf-bypass-toolkit-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/waf-bypass-toolkit-good-output.md` and `examples/waf-bypass-toolkit-bad-output.md` to calibrate output quality.
- Use `evals/waf-bypass-toolkit-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/waf-bypass-toolkit-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- waf-bypass-toolkit
- offensive-security-engagement
- workflow-router
