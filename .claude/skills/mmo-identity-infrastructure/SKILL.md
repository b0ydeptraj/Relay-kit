---
name: mmo-identity-infrastructure
description: "LAYER 3 (IDENTITY BINDING). Use when multi-account browser work needs a durable binding of {proxy + fingerprint + UA + timezone + language + storage} per identity, plus a lease API. Consumes fingerprint techniques from `browser-fingerprint-engineering` (L1) and vendor setup from `mmo-anti-detection-browser` (L2). Produces the identity pool that `mmo-browser-fleet-automation` (L4) leases from. Does NOT run sessions itself."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob"]
---

# Mission
Produce a durable identity pool with a lease API. Each identity is one immutable binding of proxy + fingerprint + UA + timezone + language + storage. Downstream fleets lease from this pool; they do not compose identities on their own.

## Scope boundary (do not violate)
- IN scope: identity registry, binding record, lease API, consistency audit, rotation policy.
- OUT of scope: implementing canvas/WebGL spoofing → L1 (`browser-fingerprint-engineering`).
- OUT of scope: calling vendor APIs (GoLogin/Multilogin/AdsPower/Dolphin) → L2 (`mmo-anti-detection-browser`).
- OUT of scope: running sessions, orchestrating queues → L4 (`mmo-browser-fleet-automation`).
- OUT of scope: proxy pool management → `mmo-proxy-network-ops`.

## Pre-flight (refuse to open the pool if any missing)
1. Authorization record names the platforms the pool will serve.
2. Proxy pool exists with sticky support flagged per provider.
3. L1 catalog chosen: which fingerprint signals this pool spoofs (canvas, WebGL, Audio, fonts, tz, lang, screen).
4. L2 vendor chosen and reachable (one vendor per pool unless explicitly multi-vendor).
5. Platform locale rules named (which fields must match proxy geo).

## Identity record format (one entry in identity-pool.md)
```
- id: <stable id>
  proxy_ref: <pool id from mmo-proxy-network-ops>
  fingerprint_ref: <catalog entry from L1>
  vendor_profile_id: <id in L2 vendor>
  ua: <string>
  tz: <IANA>
  lang: <BCP47>
  storage_dir: <path, isolated per identity>
  platforms_cleared: [<platform names>]
  state: new | warming | established | cooldown | quarantined | retired
  next_allowed_at: <ISO timestamp>
  consistency_audit: pass | fail:<reason>
```

## Lease API (contract downstream must honor)
```
lease(platform) -> identity_id | None
  - picks identity where platform in platforms_cleared AND state=established AND now >= next_allowed_at
  - marks state=leased with lease_owner and lease_expires_at

release(identity_id, result)
  - result: success | soft-fail | hard-fail | challenge
  - sets next_allowed_at from platform rate rule
  - hard-fail or 3x soft-fail => state=quarantined, reason recorded

quarantine(identity_id, reason)
  - immediate; requires warmup cycle to return to established
```

## Consistency audit (run before any identity enters `established` state)
- tz(identity) within ±1h of tz(proxy.geo)
- lang(identity) ∈ allowed set for platform
- ua.platform == vendor.reported.platform
- storage_dir unique across all identities
- proxy_ref unused by any other identity in pool

## Failure modes to self-check
- You wrote canvas-spoofing code here ⇒ wrong layer, use L1.
- You called GoLogin API here ⇒ wrong layer, use L2.
- You reused a proxy across two identities ⇒ 1:1:1 violation, refuse.
- You moved an identity to `established` without warmup trace ⇒ invalid; route to `mmo-nick-warmup-engine`.
- Downstream fleet is composing identities on its own because your pool is empty ⇒ fix the pool, do not let the fleet skip the lease.

## Role
- mmo-identity-infrastructure

## Layer
- layer-4-specialists-and-standalones

## Inputs
- account inventory with risk tier (new / warming / established / cooldown)
- proxy pool inventory from `mmo-proxy-network-ops` (type, geo, ASN, sticky support, health)
- fingerprint technique catalog from `browser-fingerprint-engineering` (L1) — WHICH signals to spoof
- vendor setup from `mmo-anti-detection-browser` (L2) — HOW to apply those signals in the chosen vendor
- platform-specific locale + trust rules (which fields must match proxy geo)

## Outputs
- .relay-kit/state/identity-pool.md — identity registry: id, proxy ref, fingerprint ref, UA, tz, lang, storage dir, platform cleared list, state, next_allowed_at
- lease API contract: lease(identity_id) / release(identity_id, result) / quarantine(identity_id, reason)
- consistency audit result (per identity: tz ↔ proxy geo ↔ lang ↔ platform locale)
- rotation / retirement policy: when an identity is rotated, warmed-again, or retired

## Reference skills and rules
- This skill is LAYER 3 — BINDING ONLY. Do NOT write the fingerprint spoofing code (that is L1) or configure the vendor API (that is L2). Reference L1 and L2 outputs and compose them into a durable identity record.
- 1:1:1 rule: one proxy ⇄ one fingerprint profile ⇄ one account. A violation of this rule is refused.
- Consistency rule: timezone must match proxy geo ±1 tz; language must match platform locale rules; UA family must match vendor-reported platform. Audit before adding to pool.
- Stability rule: for established accounts (post-warmup), identity is STABLE. Rotation is a trust-reset event and must go through `mmo-nick-warmup-engine` again.
- A lane without `.relay-kit/state/offensive-authorization.md` for MMO scope → refuse to open a pool.
- Open `references/mmo-identity-infrastructure-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-identity-infrastructure-good-output.md` and `examples/mmo-identity-infrastructure-bad-output.md` to calibrate output quality.
- Use `evals/mmo-identity-infrastructure-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-identity-infrastructure-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- browser-fingerprint-engineering
- mmo-anti-detection-browser
- mmo-proxy-network-ops
- mmo-nick-warmup-engine
- mmo-browser-fleet-automation
