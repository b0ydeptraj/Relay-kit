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
- builder-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with chrome-extension-builder findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside chrome-extension-builder's scope back through `workflow-router` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/chrome-extension-builder-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/chrome-extension-builder-good-output.md` and `examples/chrome-extension-builder-bad-output.md` to calibrate output quality.
- Use `evals/chrome-extension-builder-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/chrome-extension-builder-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- chrome-extension-builder
- workflow-router
