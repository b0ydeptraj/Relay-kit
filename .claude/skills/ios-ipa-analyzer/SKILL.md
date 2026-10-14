---
name: ios-ipa-analyzer
description: "Use when analyzing iOS IPA files for reverse engineering, security research, or app analysis. Extract app structure, binary analysis, plist inspection, framework inventory, and entitlements from .ipa archives. Works on non-jailbroken device for static analysis."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when analyzing iOS IPA files for reverse engineering, security research, or app analysis.

# iOS IPA Analyzer

> Static analysis of iOS IPA application packages.

## Mission
Analyze iOS IPA files to understand app structure, identify security issues, and extract useful information.

## Mandatory scope checks
1. Confirm analysis authorization
2. Extract IPA (rename to .zip, extract)
3. Identify main binary in Payload/*.app/
4. Choose analysis path: static / dynamic (requires jailbreak)

## Analysis checklist
- [ ] IPA structure mapped
- [ ] Info.plist read (bundle ID, version, permissions)
- [ ] Entitlements extracted (capabilities, iCloud, push)
- [ ] Binary class-dump or objection analysis
- [ ] Frameworks and dylibs inventoried
- [ ] Hardcoded strings (API keys, endpoints)
- [ ] SSL pinning implementation identified
- [ ] URL schemes registered

## Role
- reverse-engineering-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with ios-ipa-analyzer findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside ios-ipa-analyzer's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/ios-ipa-analyzer-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/ios-ipa-analyzer-good-output.md` and `examples/ios-ipa-analyzer-bad-output.md` to calibrate output quality.
- Use `evals/ios-ipa-analyzer-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/ios-ipa-analyzer-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- ios-ipa-analyzer
- reverse-hub
- workflow-router
