---
name: mmo-sms-otp-automation
description: "Use when MMO operations need SMS OTP verification at scale: receive SMS for account registration/verification via virtual number services (5sim, sms-activate, smspva, getsmscode). Handles service selection, number rental, OTP polling, and retry logic."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when MMO operations need SMS OTP verification at scale: receive SMS for account registration/verification via virtual number services (5sim, sms-activate, smspva, getsmscode).

# SMS OTP Automation for MMO

> Rent virtual phone numbers and receive OTPs automatically at scale.

## Mission
Automate phone number rental and SMS OTP reception for account registration workflows.

## Mandatory scope checks
1. Define target platform (TikTok, Facebook, Instagram, Gmail, etc.)
2. Choose SMS service: 5sim / sms-activate / smspva / getsmscode / textverified
3. Define retry strategy: max attempts, number blacklisting on fail
4. Define cost tracking: budget cap per session
5. Handle OTP extraction: regex per platform

## OTP regex patterns by platform
| Platform | OTP pattern |
|---|---|
| TikTok | `Your TikTok code is: (\d{6})` |
| Facebook | `(\d{5,8}) is your Facebook confirmation code` |
| Gmail | `G-(\d{6}) is your Google verification code` |
| Instagram | `(\d{6}) is your Instagram code` |
| Telegram | `Telegram code (\d{5,6})` |

## Evidence contract
- number rented with country and service logged
- OTP received or "no OTP" status with timeout
- cost per OTP tracked
- banned/used numbers logged to avoid re-rental

## Role
- mmo-automation-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with mmo-sms-otp-automation findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside mmo-sms-otp-automation's scope back through `mmo-authorization-gate` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/mmo-sms-otp-automation-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-sms-otp-automation-good-output.md` and `examples/mmo-sms-otp-automation-bad-output.md` to calibrate output quality.
- Use `evals/mmo-sms-otp-automation-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-sms-otp-automation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-sms-otp-automation
- mmo-authorization-gate
- workflow-router
