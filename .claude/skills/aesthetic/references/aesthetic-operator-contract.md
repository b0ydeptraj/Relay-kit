# aesthetic Battle Contract

Primary role: aesthetic-review
Layer: layer-4-specialists-and-standalones
Battle family: frontend

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: product UI repo where first-pass output risks looking generic / obviously AI-generated
- First files to inspect:
  - src/app/(marketing)/page.tsx
  - src/components/Hero.tsx
  - tailwind.config.ts
- Symbols or named surfaces to confirm: Hero, designTokens, ThemeProvider
- Evidence terms that should appear in a strong answer: reference screenshot, spacing scale, visual regression, type hierarchy

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Claiming a UI looks good without a reference or screenshot comparison.
- Shipping default framework styling and calling it a design.
- Adjusting color without checking contrast and token consistency.
- Treating a checklist as proof that the interface is distinctive.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
