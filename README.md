<div align="center">

# ⚡ Relay-kit

**A structured skill system for coding agents.**  
Install once. Your agent stops guessing and starts working like an engineer.

[![PyPI](https://img.shields.io/pypi/v/relay-kit?color=4f46e5&label=relay-kit&logo=pypi&logoColor=white)](https://pypi.org/project/relay-kit/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org)
[![Skills](https://img.shields.io/badge/skills-73%20production%20skills-22c55e)](https://github.com/b0ydeptraj/Relay-kit)
[![Adapters](https://img.shields.io/badge/adapters-Claude%20·%20Codex%20·%20Antigravity-8b5cf6)](https://github.com/b0ydeptraj/Relay-kit)
[![License](https://img.shields.io/badge/license-Proprietary-gray)](LICENSE)

[English](README.md) · [Tiếng Việt](README.vi.md) · [Docs](docs/public-docs-index.md)

</div>

---

## The problem

You're using Claude, Codex, or Cursor to build things. But the agent:

- starts coding before understanding the problem
- drifts from what you actually approved
- patches bugs without finding root cause
- says "done" when nothing is proven

Relay-kit solves this. It installs a structured workflow system into your project — 73 skills that agents actually follow, with built-in proof gates before anything is called done.

---

## Quick install

**Claude Code:**
```bash
pip install relay-kit && relay-kit . --claude && relay-kit doctor .
```

**Codex:**
```bash
pip install relay-kit && relay-kit . --codex && relay-kit doctor .
```

**Antigravity / custom agent:**
```bash
pip install relay-kit && relay-kit . --antigravity && relay-kit doctor .
```

**From GitHub (latest build):**
```bash
pipx install "git+https://github.com/b0ydeptraj/Relay-kit.git"
relay-kit . --claude && relay-kit doctor .
```

> `relay-kit doctor .` verifies the install is healthy. Run it after every update.

---

## How agents use it

Eight short names. That's all you need to remember.

| Type this | What happens |
|---|---|
| `start-here` | Agent finds the right path for your request |
| `brainstorm` | Shapes a rough idea before any code is written |
| `write-steps` | Slices approved work into verifiable steps |
| `build-it` | Implements with scope control and evidence |
| `debug-systematically` | Root-cause debugging — no random patches |
| `review-pr` | Deliberate PR review before merge |
| `ready-check` | Real go/no-go verdict with a QA report |
| `prove-it` | Final evidence check before calling work done |

**For new work:** `start-here` → `brainstorm` → `write-steps` → `build-it` → `ready-check`

**For bugs:** `start-here` → `debug-systematically` → `build-it` → `ready-check`

**For PRs:** `review-pr` → `ready-check`

---

## What's installed

Running `relay-kit . --claude` writes structured skills into `.claude/skills/`. Same for `.codex/` and `.agent/`.

```
your-project/
├── .claude/skills/          ← 73 SKILL.md files Claude reads
├── .codex/skills/           ← same for Codex
├── .agent/skills/           ← same for Antigravity
└── .relay-kit/
    ├── contracts/           ← planning and QA contracts
    ├── state/               ← workflow state across sessions
    ├── references/          ← skill reference docs
    └── evidence/            ← gate run history
```

Everything lives in your project. No cloud. No API keys required.

---

## Skill catalog

<details>
<summary><strong>Core engineering skills (always installed)</strong></summary>

`developer` · `architect` · `pm` · `scrum-master` · `qa-governor`  
`api-integration` · `data-persistence` · `dependency-management`  
`testing-patterns` · `go-service-engineering` · `next-product-frontend`  
`accessibility-review` · `ux-structure` · `frontend-design`

</details>

<details>
<summary><strong>Workflow hubs (routing backbone)</strong></summary>

`plan-hub` · `fix-hub` · `debug-hub` · `test-hub`  
`review-hub` · `scout-hub` · `brainstorm-hub`

</details>

<details>
<summary><strong>Context & memory utilities</strong></summary>

`context-continuity` · `memory-search` · `repo-map`  
`doc-pointers` · `handoff-context` · `token-economy` · `sequential-thinking`

</details>

<details>
<summary><strong>Proof & safety gates</strong></summary>

`policy-guard` · `signal-calibration` · `runtime-doctor`  
`skill-gauntlet` · `evidence-before-completion` · `impact-radar`  
`migration-guard` · `release-readiness`

</details>

<details>
<summary><strong>MMO / Multi-account pack (15 skills)</strong></summary>

Built for multi-account automation, social marketing, and ecommerce at scale.

| Skill | For |
|---|---|
| `mmo-identity-infrastructure` | Fingerprint profiles + proxy-to-account binding |
| `mmo-proxy-network-ops` | Proxy pool management, health checks, sticky sessions |
| `mmo-nick-warmup-engine` | Account warmup — 7 to 14 day behavioral program |
| `mmo-account-operations` | Account lifecycle, health scoring, recovery |
| `mmo-browser-fleet-automation` | Browser fleet with anti-flake session controls |
| `mmo-social-marketing-automation` | Social API campaigns, quota-aware scheduling |
| `mmo-content-factory` | AI bulk content generation and cross-platform scheduling |
| `mmo-reup-automation` | Content reup with dedup and rights controls |
| `mmo-data-harvesting` | UID targeting lists and AI seeding content |
| `mmo-ecommerce-multichannel` | Shopee / TikTok Shop / Lazada multi-store sync |
| `mmo-http-api-automation` | Contract-safe API automation with replay-safe logs |
| `mmo-lowcode-automation` | n8n / Make / no-code workflow operations |
| `mmo-mobile-app-automation` | Mobile device and emulator automation |
| `mmo-cloud-operations-automation` | Cloud worker pools, queue, retry, cost guards |
| `mmo-crypto-wallet-farming` | Multi-wallet DeFi with Sybil-avoidance strategy |

</details>

---

## Adapter support

| Flag | Output | Works with |
|---|---|---|
| `--claude` | `.claude/skills/` | Claude Code |
| `--codex` | `.codex/skills/` | OpenAI Codex |
| `--antigravity` | `.agent/skills/` | Antigravity, custom agents |
| `--all` | All three | Generate everything at once |

All adapters stay in sync. Check parity anytime:

```bash
relay-kit adapter diagnose . --adapter all --strict
```

---

## Useful commands

```bash
# After install — verify everything is healthy
relay-kit doctor .

# Check all adapter surfaces match
relay-kit adapter diagnose . --adapter all --strict

# Full readiness gate
relay-kit readiness check . --profile enterprise

# Turn a vague request into skill-aware guidance
relay-kit prompt enhance . --prompt "fix the auth bug"

# Find relevant files without dumping your whole codebase
relay-kit context search . --query "payment middleware"

# Check for stale context before resuming a long task
relay-kit context audit . --strict
```

---

## Vietnamese locale

```bash
relay-kit locale set . --locale vi
```

Applies Vietnamese metadata to skill pickers and command surfaces. Routing contracts stay in English.

---

## Requirements

- Python 3.10 or higher
- Works with Claude Code, OpenAI Codex, Antigravity, Cursor, any agent that reads skill files

Optional — local context indexing without API keys:

```bash
pip install relay-kit[context]
```

Adds local embedding and tree-sitter symbol lookup.

---

## More docs

- [Start flow walkthrough](docs/relay-kit-start-flow.md)
- [Debug and review flow](docs/relay-kit-review-flow.md)
- [Context continuity across sessions](docs/relay-kit-context-continuity.md)
- [Writing custom skills](docs/how-to-write-skills.md)
- [Release readiness gate](docs/relay-kit-release-readiness.md)
- [Full docs index](docs/public-docs-index.md)
- [Contributing](CONTRIBUTING.md)

---

<div align="center">

**Relay-kit v4 · 73 skills · Claude · Codex · Antigravity**

</div>
