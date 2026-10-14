---
name: mmo-sms-otp-automation
description: "Use when MMO operations need SMS OTP verification at scale: receive SMS for account registration/verification via virtual number services (5sim, sms-activate, smspva, getsmscode). Handles service selection, number rental, OTP polling, and retry logic."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

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
- sms-otp-operator

## Layer
- layer-4-specialists-and-standalones

## Inputs
- target platform name
- country preference
- SMS API key (SMSAPI_KEY env var)
- SMS service choice

## Outputs
- virtual number + OTP pairs
- cost log
- failed number blacklist

## Likely next step
- mmo-account-operations
- mmo-identity-infrastructure
- mmo-anti-detection-browser
