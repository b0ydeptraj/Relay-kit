# BANG CHUNG THUC THI 100% ROADMAP V3

> Bao cao tu dong trich xuat truc tiep tu source code hien tai cua Relay-Kit.


## 1. 23 Ky nang moi
- [x] offensive-security-engagement/SKILL.md (2800 bytes)
- [x] cpp-systems-engineering/SKILL.md (2562 bytes)
- [x] windows-native-internals/SKILL.md (2482 bytes)
- [x] advanced-python-engineering/SKILL.md (2393 bytes)
- [x] binary-stealth-obfuscation/SKILL.md (2499 bytes)
- [x] edr-evasion-tactics/SKILL.md (2256 bytes)
- [x] telemetry-blinding/SKILL.md (2293 bytes)
- [x] process-injection-techniques/SKILL.md (2421 bytes)
- [x] network-stealth-c2/SKILL.md (2263 bytes)
- [x] protocol-fingerprint-spoofing/SKILL.md (2448 bytes)
- [x] browser-fingerprint-engineering/SKILL.md (2779 bytes)
- [x] antibot-challenge-solving/SKILL.md (2673 bytes)
- [x] frontend-crypto-reverse/SKILL.md (2534 bytes)
- [x] desktop-imgui-development/SKILL.md (2448 bytes)
- [x] desktop-python-ui/SKILL.md (2452 bytes)
- [x] terminal-operator-ui/SKILL.md (2347 bytes)
- [x] malware-analysis-workflows/SKILL.md (2435 bytes)
- [x] binary-reverse-methodology/SKILL.md (2589 bytes)
- [x] attack-chain-orchestration/SKILL.md (2426 bytes)
- [x] field-journal-evolution/SKILL.md (2621 bytes)
- [x] mmo-onchain-security-audit/SKILL.md (2520 bytes)
- [x] mmo-llm-automation/SKILL.md (2491 bytes)
- [x] mobile-app-reverse/SKILL.md (2554 bytes)

## 2. Bang chung file kien truc: skills.manifest.yaml
- [x] skills.manifest.yaml chua offensive-security-engagement
- [x] skills.manifest.yaml chua cpp-systems-engineering
- [x] skills.manifest.yaml chua field-journal-evolution

## 2. Bang chung file kien truc: layer-model.md
- [x] layer-model.md chua optional-discipline-overlays
- [x] layer-model.md chua field-journal-evolution
- [x] layer-model.md chua offensive-security-engagement

## 2. Bang chung file kien truc: standalone-taxonomy.md
- [x] standalone-taxonomy.md chua security-and-systems
- [x] standalone-taxonomy.md chua desktop-and-tooling
- [x] standalone-taxonomy.md chua mmo-intelligence

## 3. Bang chung Hub Updates (Trich xuat code that)

**workflow-router** (authorization_risk):
`markdown
Line 20: 2. Score the request on six axes: ambiguity, breadth of change, architecture risk, operational risk, coordination cost, and authorization_risk (presence of offensive/red-team/evasion/injection/stealth/C2 keywords or explicit red-team scope).
Line 31: - `authorization_risk >= medium` -> offensive-flow (call `offensive-security-engagement` as first L3 utility before picking specialist)
`

**workflow-router** (offensive-flow):
`markdown
Line 31: - `authorization_risk >= medium` -> offensive-flow (call `offensive-security-engagement` as first L3 utility before picking specialist)
`

**cook** (engagement_proof):
`markdown
Line 20: - When `workflow-state.engagement_proof` exists or the lane mode is `offensive`, call `offensive-security-engagement` as the first utility before picking any specialist.
`

**developer** (cpp-systems-engineering):
`markdown
Line 69: - cpp-systems-engineering
`

**debug-hub** (Offensive failure routing):
`markdown
Line 15: 6. Offensive failure routing: when symptoms include EDR detection, bypass failure, injection error, antibot block, or fingerprint mismatch -> route to the matching offensive specialist before proposing fixes:
`

**fix-hub** (Offensive fix handoff):
`markdown
Line 15: 6. Offensive fix handoff: when the fix involves native systems or security-sensitive code, route to the matching specialist:
`

**test-hub** (Offensive evidence contracts):
`markdown
Line 15: 6. Offensive evidence contracts: when the implementation involves binary, evasion, or bypass work, the qa-report must include:
`

**scout-hub** (Offensive recon routing):
`markdown
Line 15: 6. Offensive recon routing: when the codebase is binary, native, or mobile-focused, pull the matching analysis skill before planning:
`

**policy-guard** (Cooperation contract):
`markdown
Line 24: - Cooperation contract with offensive-security-engagement: policy-guard is fail-closed for secrets, shell, and path risk. offensive-security-engagement is fail-open-for-authorized for offensive techniques. When both are active in the same lane, policy-guard runs LAST as a post-execution gate, not as a pre-execution block on authorized offensive actions. Do not block offensive actions that have a valid engagement_proof in workflow-state.
`

## 4. Bang chung MMO Skill Gaps (Da noi cap thanh cong)

**Gap 8: mmo-browser-fleet-automation** (antibot-challenge-solving):
`markdown
Line 42: - Forbid automation patterns that rely on stealth evasion or non-API scraping prohibited by policy inside the fleet scope. If antibot challenges (Cloudflare, Datadome, CAPTCHA) are encountered, delegate immediately to `antibot-challenge-solving` outside the fleet.
Line 53: - antibot-challenge-solving
`

**Gap 9: mmo-identity-infrastructure** (browser-fingerprint-engineering):
`markdown
Line 54: - browser-fingerprint-engineering
`

**Gap 10: mmo-crypto-wallet-farming** (mmo-onchain-security-audit):
`markdown
Line 53: - mmo-onchain-security-audit
`

**Gap 11: mmo-data-harvesting** (frontend-crypto-reverse):
`markdown
Line 54: - frontend-crypto-reverse
`

**Gap 12: evidence-before-completion** (Offensive claim mapping):
`markdown
Line 20: - Offensive claim mapping required:
`

**Gap: mmo-http-api-automation** (frontend-crypto-reverse):
`markdown
Line 52: - frontend-crypto-reverse
`

**Gap: mmo-cloud-operations-automation** (mmo-llm-automation):
`markdown
Line 52: - mmo-llm-automation
`