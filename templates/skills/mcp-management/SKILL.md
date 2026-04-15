---
name: mcp-management
description: Use when configuring, auditing, or troubleshooting MCP server registrations and runtime connectivity.
version: 2.0.0
---

# MCP Management

Use this skill to provide bounded, evidence-backed domain guidance to the current hub or specialist.

## When to Use

- The active task touches MCP Management behavior or tooling.
- A decision needs domain constraints before coding.
- A fix or review needs focused checks for this domain.

## Output Contract

- Key findings tied to affected files or artifacts.
- Recommended next action and verification notes.
- Risks or unknowns that still block safe completion.

## Workflow

1. Confirm scope and acceptance signal with the owning hub.
2. Gather only domain evidence needed for this pass.
3. Propose the smallest safe implementation or review path.
4. Hand results back to the owning lane with a concrete next step.

## References

- references/configuration.md
- references/gemini-cli-integration.md
- references/mcp-protocol.md

## Scripts

- scripts/.env.example
- scripts/.gitignore
- scripts/cli.ts
- scripts/mcp-client.ts
- scripts/package.json
- scripts/tsconfig.json

## Guardrails

- Keep scope narrow; do not create parallel architecture.
- Separate observed evidence from recommendation.
- Do not claim completion without lane-level verification evidence.
