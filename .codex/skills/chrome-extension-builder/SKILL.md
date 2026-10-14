---
name: chrome-extension-builder
description: "Use when designing, building, or hardening production-grade Chrome/Chromium extensions (Manifest V3) for browser automation, DOM/iframe injection, network interception, anti-detection bypass, or workflow acceleration."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Design, build, and harden production-grade Chrome Extensions (Manifest V3) for automated browser execution, resilient DOM/iframe interaction, anti-detection stealth, and off-page network routing.

## Mandatory scope checks
- Verify Manifest V3 compliance: enforce background service workers, declarativeNetRequest, and minimal scoped host permissions.
- Define injection boundary: select isolated world for safe DOM manipulation, main world for prototype hooking, or chrome.debugger for isTrusted events.
- Define cross-origin iframe architecture: establish postMessage RPC bridges with strict origin validation and session fencing.
- Define network routing and CSP compliance: route external API requests and telemetry through the background worker to bypass page CSP.
- Define lifecycle resilience: implement service worker teardown reconnect retries, AbortController bounded timeouts, scoped MutationObserver waiting, and checkpoint recovery state machines.
- Enforce anti-fingerprinting cleanliness: ensure zero global pollution on window, no un-sanitized script injection, and no wildcard web_accessible_resources.
- Enforce multi-domain SSO session integrity: extract and inject cross-domain cookies (Google/YouTube, Meta/FB, Zalo subdomains) and adhere strictly to RFC 6265bis (no leading dot, hostOnly, __Host-).
- Enforce safe IndexedDB extraction: blacklist heavy non-auth stores (messages, media, cache), cap records (50 per store), cap record bytes (32KB), and enforce circuit breakers (2.5s timeout) to prevent OOM.
- Enforce popup renderer crash boundaries: install global error boundaries, cache large bundles in memory/storage, and prevent dumping unconstrained multi-megabyte JSON into DOM textareas.

## Evidence contract
- valid manifest.json passing Manifest V3 structural validation
- passing test output from zero-dependency mock test suite (node:test + node:vm)
- verified AbortController cancellation handling on every asynchronous wait loop
- verified postMessage origin validation on all iframe communication endpoints

## Role
- chrome-extension-architect

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target web platform URL and interaction requirements
- automation task definition, selector targets, or network endpoints
- anti-bot or security constraints (CSP, iframe embedding, isTrusted checks)

## Outputs
- production-hardened extension package (manifest.json, background.js, content.js, popup UI, iframe bridge)
- zero-dependency test suite (tests/extension.test.cjs)
- operator execution runbook and architecture verification evidence

## Reference skills and rules
- Enforce Manifest V3 compliance and service worker reconnect resilience via `references/manifest-v3-hardened-architecture.md`.
- Escalate to genuine isTrusted event dispatching when bypassing protected web forms via `references/is-trusted-cdp-bridge.md`.
- Eliminate CPU-thrashing busy polling by deploying reactive DOM observers via `references/mutation-observer-engine.md`.
- Implement persistent state machine checkpointing across tab reloads and navigations via `references/checkpoint-recovery.md`.
- Review operator safety, evidence standards, and battle profile via `references/chrome-extension-builder-operator-contract.md`.
- Calibrate output quality against `examples/chrome-extension-builder-good-output.md` and `examples/chrome-extension-builder-bad-output.md`.
- Use `evals/chrome-extension-builder-cases.json` for behavior regression evaluations.
- Check covered capabilities, failure traps, and domain policies via `competencies/chrome-extension-builder-competencies.json`.

## Likely next step
- mmo-browser-fleet-automation
- antibot-challenge-solving
- frontend-crypto-reverse
- policy-guard
- qa-governor
