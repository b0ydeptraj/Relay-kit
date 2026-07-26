# frontend-design Battle Contract

Primary role: frontend-design
Layer: layer-4-specialists-and-standalones
Battle family: frontend

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: component/page repo where the user asks to build UI and visual quality matters
- First files to inspect:
  - src/components/LoginForm.tsx
  - src/app/dashboard/page.tsx
  - src/styles/tokens.css
- Symbols or named surfaces to confirm: LoginForm, DashboardLayout, Button
- Evidence terms that should appear in a strong answer: component boundary, responsive behavior, accessibility state, visual regression

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Building UI without naming the component and route boundary first.
- Skipping loading, empty, and error states.
- Claiming responsive/accessible without a check.
- Producing generic AI aesthetics with no distinctive system.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
