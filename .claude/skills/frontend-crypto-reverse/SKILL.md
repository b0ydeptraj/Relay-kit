---
name: frontend-crypto-reverse
description: Use when web applications use client-side cryptography, obfuscated JS, WASM, or signing parameters that must be reversed to replicate API calls without a browser.
---

# Mission
Reverse-engineer frontend signing, encryption, and obfuscation to replicate API calls programmatically.

## Mandatory scope
1. Map signing pipeline: identify where request signature, timestamp, nonce, or token is computed (JS bundle, WASM, ServiceWorker).
2. Deobfuscate JS: use AST transformation (babel-plugin-deobfuscator, js-beautify) or manual analysis.
3. For WASM: extract and decompile (wasm-decompile, Ghidra WASM plugin) to identify crypto primitives.
4. Replicate in Python/Go/Node: implement signing logic outside browser without CDP.
5. Verify: compare replicated signature against browser-captured signature for same input.
6. Document key material: where signing keys are embedded (hardcoded, derived from device fingerprint, fetched at runtime).

## Evidence contract
- signing pipeline mapped
- deobfuscation method documented
- replication implemented and verified (signatures match)
- key material source documented
- works without browser dependency

## Role
- crypto-reverse-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target web application
- captured network traffic (HAR)
- JS bundle or WASM

## Outputs
- signing implementation
- deobfuscation analysis
- verification comparison

## Reference skills and rules
- Never claim signature replication without byte-exact comparison to browser output.
- Document key derivation — hardcoded keys may rotate.
- WASM decompilation output should be treated as pseudocode, not exact code.
- If signing keys are device-fingerprint-derived, integrate with browser-fingerprint-engineering.
- Open `references/frontend-crypto-reverse-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/frontend-crypto-reverse-good-output.md` and `examples/frontend-crypto-reverse-bad-output.md` to calibrate output quality.
- Use `evals/frontend-crypto-reverse-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/frontend-crypto-reverse-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- protocol-fingerprint-spoofing
- browser-fingerprint-engineering
- mmo-http-api-automation
- mmo-data-harvesting
- test-hub
- field-journal-evolution
