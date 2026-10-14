---
name: ssl-pinning-bypass
description: "Use when mobile or desktop app SSL certificate pinning blocks MITM traffic interception. Bypass certificate pinning via Frida hooks, objection, root bypass, or patching. Works on Android (APK) and iOS (IPA) apps. Engagement proof required."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when mobile or desktop app SSL certificate pinning blocks MITM traffic interception.

# SSL Pinning Bypass

> Bypass certificate pinning in mobile and desktop apps for authorized traffic analysis.

## Mission
Intercept HTTPS traffic from apps with SSL pinning by dynamically patching the pinning validation.

## Mandatory scope checks
1. Engagement proof required.
2. Identify pinning method: OkHttp / TrustManager / NSURLSession / custom
3. Choose bypass method: Frida script / Objection / APK patch / MagiskTrustUserCerts
4. Set up proxy: Burp Suite / mitmproxy / Charles
5. Verify bypass: check if HTTPS traffic visible in proxy

## Bypass methods by platform
| Platform | Method | Tool |
|---|---|---|
| Android (rooted) | Frida + objection | `objection -g app explore --startup-command "android sslpinning disable"` |
| Android (rooted) | Magisk TrustUserCerts | Install module → system trusts user CA |
| Android (non-root) | APK repack | Decompile → patch network_security_config → repack |
| iOS (jailbroken) | Frida + SSL Kill Switch 2 | Tweak or Frida script |
| Desktop (.NET) | dnSpy + dotnet-patcher | Patch ServicePointManager.ServerCertificateValidationCallback |
| Desktop (Electron) | electron-app-analyzer | Patch --ignore-certificate-errors or custom TLS |

## Evidence contract
- engagement_proof confirmed
- pinning method identified (tools, library, code location)
- bypass applied and proxy traffic visible
- sample intercepted request documented

## Role
- reverse-engineering-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with ssl-pinning-bypass findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside ssl-pinning-bypass's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/ssl-pinning-bypass-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/ssl-pinning-bypass-good-output.md` and `examples/ssl-pinning-bypass-bad-output.md` to calibrate output quality.
- Use `evals/ssl-pinning-bypass-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/ssl-pinning-bypass-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- ssl-pinning-bypass
- reverse-hub
- workflow-router
