---
name: browser-inspector
description: Collect browser runtime evidence (DOM, console, network, screenshot, and performance) for debugging and QA decisions. Use when a hub needs concrete browser observations instead of assumptions.
version: 2.0.0
---

# Browser Inspector

Use this skill to gather reproducible browser evidence for web flows.

## When to Use

- A bug appears only in the browser.
- You need console/network proof before proposing a fix.
- A review needs screenshots or performance signals.
- A hub requests DOM state confirmation.

## Inputs

- Target URL or route.
- Scenario to reproduce.
- Expected vs actual behavior.
- Evidence needed: `dom`, `console`, `network`, `screenshot`, `perf`.

## Output Contract

Return:
- Reproduction steps.
- Observed evidence (not guesses).
- Likely fault surface.
- Suggested next action.

## Workflow

1. Confirm target URL and expected behavior.
2. Run minimal scripts needed for the question.
3. Save artifacts for traceability.
4. Summarize only evidence tied to the request.

## Scripts

Run from `templates/skills/browser-inspector/scripts/`:

- `node navigate.js --url <url>`
- `node snapshot.js --url <url>`
- `node console.js --url <url>`
- `node network.js --url <url>`
- `node screenshot.js --url <url>`
- `node performance.js --url <url>`

If dependencies are missing, follow `scripts/README.md` and `scripts/install.sh`.

## References

- `references/puppeteer-reference.md`
- `references/cdp-domains.md`
- `references/performance-guide.md`

## Guardrails

- Prefer deterministic reproduction over broad crawling.
- Do not report conclusions without matching artifacts.
- If evidence is insufficient, state what is missing.
