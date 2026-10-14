---
name: telegram-automation
description: "Use when automating Telegram operations: bot management, channel/group automation, member farming, bulk messaging, scheduled broadcasting, Telegram Mini App interaction, and userbot operations via Telethon/Pyrogram. Supports both Bot API and MTProto approaches."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when automating Telegram operations: bot management, channel/group automation, member farming, bulk messaging, scheduled broadcasting, Telegram Mini App interaction, and userbot operations via Telethon/Pyrogram.

# Telegram Automation

> Full-stack Telegram automation: bots, channels, groups, userbot, and broadcasting.

## Mission
Automate Telegram channel/group operations at scale with anti-spam awareness.

## Approaches
| Method | Tools | Features |
|---|---|---|
| Bot API | python-telegram-bot / requests | Posts, messages, commands, inline keyboards |
| Userbot | Telethon / Pyrogram | Member scraping, mass DM, group join, forward |
| MTProto | Direct TDLib | Full feature access, no rate limit label |

## Daily limits (safe)
| Action | Safe | Risky |
|---|---|---|
| Bot messages | 1000/s (group) | Flood wait |
| Userbot DMs | 30/day | 50+ = spam risk |
| Group joins | 10/day | 20+ = ban risk |
| Forwards | 100/day | 200+ |
| Member scraping | 200/run | 500+ |

## Role
- mmo-automation-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with telegram-automation findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside telegram-automation's scope back through `mmo-authorization-gate` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/telegram-automation-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/telegram-automation-good-output.md` and `examples/telegram-automation-bad-output.md` to calibrate output quality.
- Use `evals/telegram-automation-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/telegram-automation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- telegram-automation
- mmo-authorization-gate
- workflow-router
