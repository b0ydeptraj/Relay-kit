---
name: facebook-automation
description: "Use when automating Facebook operations: Page management, Group automation, Marketplace listing, Ads management, lead generation, friend/follow farming, and content scheduling. Supports Graph API (official), cookie session (semi-official), and browser automation approaches."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when automating Facebook operations: Page management, Group automation, Marketplace listing, Ads management, lead generation, friend/follow farming, and content scheduling.

# Facebook Automation

> Full-stack Facebook automation: pages, groups, marketplace, ads, and engagement.

## Mission
Automate Facebook operations across accounts with rate limit awareness and anti-ban strategies.

## Platform limits (safe)
| Action | Safe daily | Risky above |
|---|---|---|
| Friend requests | 20 | 50 |
| Group posts | 5 per group | 15 |
| Page posts | 3 | 8 |
| DMs | 15 | 30 |
| Marketplace listings | 10 | 25 |
| Group joins | 5 | 15 |

## Role
- mmo-automation-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with facebook-automation findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside facebook-automation's scope back through `mmo-authorization-gate` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/facebook-automation-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/facebook-automation-good-output.md` and `examples/facebook-automation-bad-output.md` to calibrate output quality.
- Use `evals/facebook-automation-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/facebook-automation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- facebook-automation
- mmo-authorization-gate
- workflow-router
