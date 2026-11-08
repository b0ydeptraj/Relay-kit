---
name: mmo-anti-detection-browser
description: "LAYER 2 (VENDOR ADAPTER). Use to apply L1 fingerprint recipes inside ONE anti-detect vendor: GoLogin, Multilogin, AdsPower, Dolphin Anty, Hidemyacc, or DIY Chromium. Takes recipes from `browser-fingerprint-engineering` (L1) and configures the vendor to apply them. Produces vendor-profile ids that `mmo-identity-infrastructure` (L3) binds into identities. Does NOT design techniques (L1) or compose identities (L3)."
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

# Mission
Apply L1 fingerprint recipes inside ONE chosen vendor. Produce vendor-profile ids with per-recipe applied/fallback status and a verification result. Do not design, compose, or orchestrate.

## Scope boundary (do not violate)
- IN scope: vendor API wiring (create profile, set fingerprint fields, launch, close), applying recipes vector-by-vector, verification run, fallback list.
- OUT of scope: designing a new canvas/WebGL technique -> L1 (browser-fingerprint-engineering).
- OUT of scope: deciding which identity gets which recipe, which platforms it clears, proxy binding -> L3 (mmo-identity-infrastructure).
- OUT of scope: running sessions/queues -> L4 (mmo-browser-fleet-automation).

## Pre-flight (refuse the run if any missing)
1. ONE vendor named with credentials present in secrets-management.
2. L1 recipes present for every vector the operator asked to spoof.
3. Target profile count and naming convention set.
4. Verification URL named (fingerprintjs.com / browserleaks.com / creepjs / pixelscan.net).

## Vendor capability matrix (native vector support; partial = needs L1 fallback)
| Vendor | Canvas | WebGL | Audio | Fonts | Navigator | Screen | TZ | Battery | API | Free tier |
|---|---|---|---|---|---|---|---|---|---|---|
| GoLogin | yes | yes | yes | yes | yes | yes | yes | partial | REST | 3 profiles |
| AdsPower | yes | yes | yes | yes | yes | yes | yes | yes | REST | 5 profiles |
| Dolphin Anty | yes | yes | yes | yes | yes | yes | yes | partial | REST | 10 profiles |
| Multilogin | yes | yes | yes | yes | yes | yes | yes | yes | REST | paid only |
| Hidemyacc | yes | yes | partial | yes | yes | yes | yes | no | REST | paid |
| DIY Chromium | JS | JS | JS | JS | JS | JS | JS | JS | none | unlimited |

## Apply loop (per profile)
1. CREATE profile in vendor with name from convention.
2. FOR EACH recipe IN L1 input:
   - vendor native supports it -> set via vendor API, status=applied
   - vendor missing/partial -> status=fallback, append to fallback_vectors
3. LAUNCH profile headless.
4. NAVIGATE to verification URL; capture result.
5. CLOSE profile.
6. verification pass -> register in output; fail -> rejected with reason.

## Output registry row format
```
- profile_id: <vendor id>
  vendor: <name>
  applied_vectors: [canvas, webgl, audio, fonts, navigator, screen, tz]
  fallback_vectors: [battery, behavioral]
  verification_url: <url>
  verification_result: pass | fail:<leaks>
  created_at: <ISO>
```

## Failure modes to self-check
- You wrote a canvas spoofing algorithm here -> wrong layer, request recipe from L1.
- You bound a profile to a proxy and an account -> wrong layer, hand off to L3.
- You skipped verification -> profile does not enter the registry.
- You hardcoded an API key -> delete, route via secrets-management.
- Two vendors in one run -> split into two runs.

## Role
- mmo-anti-detect-vendor-adapter

## Layer
- layer-4-specialists-and-standalones

## Inputs
- chosen vendor + API key or local control port (one vendor per run)
- fingerprint recipes from browser-fingerprint-engineering (L1) per vector
- optional consistency anchors from L3 (tz/locale/UA.platform) pass-through
- target profile count and naming convention

## Outputs
- vendor-profile registry: profile_id, vendor, applied_vectors, fallback_vectors, verification_url, verification_result
- fallback request: vectors the vendor cannot natively spoof, returned to L1 for CDP/JS injection at session start

## Reference skills and rules
- This skill is LAYER 2 - VENDOR ADAPTER ONLY. It applies L1 recipes to a vendor; it does NOT design recipes (L1) or assemble identities (L3).
- One vendor per run. Cross-vendor logic belongs in L3.
- If a vendor cannot natively spoof a vector from the L1 recipe, record it as fallback - do not silently drop it. L3 routes fallbacks to CDP/JS injection.
- A profile that fails the verification URL does not enter the output registry.
- Vendor API keys go through secrets-management, never inline.
- Open `references/mmo-anti-detection-browser-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-anti-detection-browser-good-output.md` and `examples/mmo-anti-detection-browser-bad-output.md` to calibrate output quality.
- Use `evals/mmo-anti-detection-browser-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-anti-detection-browser-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-identity-infrastructure
- browser-fingerprint-engineering
- mmo-proxy-network-ops
