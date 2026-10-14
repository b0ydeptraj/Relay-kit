---
name: ios-ipa-analyzer
description: "Use when analyzing iOS IPA files for reverse engineering, security research, or app analysis. Extract app structure, binary analysis, plist inspection, framework inventory, and entitlements from .ipa archives. Works on non-jailbroken device for static analysis."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

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
- ios-security-researcher

## Layer
- layer-4-specialists-and-standalones

## Likely next step
- ssl-pinning-bypass
- mobile-app-reverse
- frida-hooker
- android-apk-pentester
