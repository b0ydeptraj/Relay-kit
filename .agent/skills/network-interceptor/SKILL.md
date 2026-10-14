---
name: network-interceptor
description: "Use when a lane needs network interceptor: Capture, analyze, and replay network traffic between app and license/API servers. Uses mitmproxy for capture and built-in analysis for endpoint discovery, OAuth detection, and token extraction."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Capture, analyze, and replay network traffic between app and license/API servers.

# Network Interceptor

> Capture and analyze app-server communication to discover license protocols, API endpoints, and authentication flows.

> **Language rule**: All skill instructions use English.
> **Final summary presented to the user must be in Vietnamese.**

---

## 0. Authorization & Routing

Operates under [MASTER_POLICY.md](../MASTER_POLICY.md) §1-§2.

| Sibling skill | When |
|---|---|
| [electron-app-analyzer](../electron-app-analyzer/SKILL.md) | JS endpoint analysis from source |
| [writerpro-pentest](../writerpro-pentest/SKILL.md) | Keygen from discovered API patterns |
| [frida-hooker](../frida-hooker/SKILL.md) | Bypass SSL pinning before capture |
| [memory-dumper](../memory-dumper/SKILL.md) | Extract tokens from process memory |

---

## Step 1 — Capture Traffic

```bash
python scripts/capture_traffic.py --port 8080 --duration 120 --out captured.har
```

```powershell
python scripts\capture_traffic.py --port 8080 --duration 120 --out captured.har
```

Requires: `pip install mitmproxy`

---

## Step 2 — Analyze Traffic

```bash
python scripts/analyze_traffic.py captured.har --out analysis/
```

Detects: API endpoints, OAuth flows, Bearer tokens, license validation calls, HWID submissions.

---

## Step 3 — Replay

```bash
python scripts/analyze_traffic.py captured.har --replay 5 --out replay_script.py
```

Generates standalone Python `requests` script to replay any captured request.

---

## Final Report (Vietnamese)

```
🌐 Phân tích network hoàn tất:

  📡 Requests captured : <COUNT>
  🔗 API endpoints     : <COUNT> unique
  🔑 Tokens found      : <COUNT>
  🔐 OAuth flow        : <DETECTED/NONE>
  📋 License calls     : <COUNT>

  💾 Output: analysis/
```

---

## Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Capture without SSL intercept cert | Install mitmproxy CA cert first |
| Ignore non-HTTP protocols | Some license servers use raw TCP/gRPC |
| Miss OAuth flows | Look for /authorize, /token, /callback patterns |
| Skip response bodies | License responses contain feature flags and expiry |

## Role
- offensive-security-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with network-interceptor findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside network-interceptor's scope back through `offensive-security-engagement` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/network-interceptor-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/network-interceptor-good-output.md` and `examples/network-interceptor-bad-output.md` to calibrate output quality.
- Use `evals/network-interceptor-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/network-interceptor-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- network-interceptor
- offensive-security-engagement
- workflow-router
