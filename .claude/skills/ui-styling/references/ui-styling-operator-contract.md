# ui-styling Battle Contract

Primary role: ui-styling
Layer: layer-4-specialists-and-standalones
Battle family: frontend

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: design-system / styling repo with tokens, themes, and reusable components
- First files to inspect:
  - src/styles/tokens.css
  - tailwind.config.ts
  - src/components/ui/Button.tsx
- Symbols or named surfaces to confirm: designTokens, ThemeProvider, Button
- Evidence terms that should appear in a strong answer: design token, theme, responsive layout, contrast ratio

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Hardcoding values instead of using design tokens.
- Adding a component variant that breaks theme consistency.
- Claiming accessible components without contrast or focus checks.
- Duplicating styles instead of extending the system.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
