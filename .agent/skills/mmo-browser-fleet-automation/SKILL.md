---
name: mmo-browser-fleet-automation
description: "LAYER 4 (ORCHESTRATION). Use when browser MMO work needs to run many sessions reliably: queue, lease, retry, selector drift, live operator screen. Depends on identities produced by `mmo-identity-infrastructure`. Does NOT design fingerprints (L1), configure vendors (L2), or bind identities (L3)."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Orchestrate many browser sessions reliably against a leased identity pool. One queue, one lease table, one operator screen. No fingerprint spoofing, no vendor wiring, no identity design here.

## Scope boundary (do not violate)
- IN scope: queue + lease table, selector contract, retry/backoff, operator screen, kill switch, run evidence.
- OUT of scope: canvas/WebGL/Audio spoofing → `browser-fingerprint-engineering` (L1).
- OUT of scope: GoLogin/Multilogin/AdsPower API wiring → `mmo-anti-detection-browser` (L2).
- OUT of scope: identity composition (proxy+fingerprint+UA+tz+storage) → `mmo-identity-infrastructure` (L3).
- OUT of scope: platform-rule-breaking stealth — refuse flows that depend on circumventing documented platform automation policy.

## Pre-flight (refuse the fleet run if any missing)
1. Identity pool contract from L3 exists and names session ids the fleet may lease. No pool → stop, route to L3.
2. Selector contract for every critical UI action (locator + wait strategy + timeout).
3. Per-platform rate limit explicitly stated.
4. Kill-switch signal source named (file flag, env var, or operator button).
5. Evidence sink configured (screenshot dir, console log dir, network HAR dir).

## Run loop contract
```
1. LEASE: acquire identity from L3 pool; if none available → queue backlog, return.
2. LAUNCH: open browser with the leased identity; verify fingerprint sanity-check URL passes.
3. EXECUTE: run workflow steps with explicit waits; on each step, log evidence id.
4. RETRY: transient failure (network, selector timeout) → backoff + retry up to policy.
5. RELEASE: return identity to L3 pool with state (success, soft-fail, hard-fail, quarantine).
6. NEXT-ALLOWED-AT: set per-identity cooldown from platform rate rule.
```

## Operator screen (required fields)
- live session list with: identity_id, platform, state, step, elapsed, lease_owner
- selector drift alerts (last successful selector hash vs current)
- screenshot trace, console log, network HAR per session
- manual "pause" / "kill" / "handoff to human" per session
- queue depth and backlog by platform

## Failure modes to self-check
- You created identities inside this skill ⇒ wrong layer, use L3 output.
- You wrote canvas-spoofing code ⇒ wrong layer, use L1.
- You used `time.sleep(5)` instead of an explicit wait ⇒ delete, use selector wait.
- You ran without a lease record ⇒ invalid run, refuse.
- Kill switch not wired ⇒ do not start the fleet.

## Role
- mmo-browser-automation

## Layer
- layer-4-specialists-and-standalones

## Inputs
- identity pool contract from `mmo-identity-infrastructure` — mandatory, names session ids this fleet can lease
- workflow map: ordered UI actions per session with selector contract
- platform policy + rate limits (per-platform, per-identity)
- stop conditions and emergency-kill signal source

## Outputs
- fleet runner with lease table (session id → owner → platform → state → next-allowed-at)
- selector contract file with wait strategy per critical action
- retry/backoff policy and run queue states (queued, leased, running, retry, failed, done)
- operator screen spec: live session list, screenshot trace, console/network tab, kill button

## Reference skills and rules
- This skill is LAYER 4. Do NOT define per-browser fingerprint spoofing (that is `browser-fingerprint-engineering` — L1), vendor API wiring (`mmo-anti-detection-browser` — L2), or identity binding (`mmo-identity-infrastructure` — L3). Depend on their outputs; do not duplicate them.
- Prefer official platform API over UI automation; use UI automation only for flows the API does not expose and the platform allows.
- Explicit waits, resilient locators, deterministic retry — forbid blind sleeps.
- Every run must consume an identity leased from the L3 pool; a session without a lease record is refused.
- Open `references/mmo-browser-fleet-automation-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-browser-fleet-automation-good-output.md` and `examples/mmo-browser-fleet-automation-bad-output.md` to calibrate output quality.
- Use `evals/mmo-browser-fleet-automation-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-browser-fleet-automation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-identity-infrastructure
- browser-inspector
- automation-ops
- policy-guard
- qa-governor
