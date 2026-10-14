---
name: telegram-automation
description: "Use when automating Telegram operations: bot management, channel/group automation, member farming, bulk messaging, scheduled broadcasting, Telegram Mini App interaction, and userbot operations via Telethon/Pyrogram. Supports both Bot API and MTProto approaches."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

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
- telegram-automation-operator

## Layer
- layer-4-specialists-and-standalones

## Likely next step
- mmo-social-marketing-automation
- mmo-content-factory
- mmo-lowcode-automation
