---
name: oracle
description: Provide a rigorous second-opinion analysis for complex debugging, architecture decisions, or risk-heavy changes.
version: 2.0.0
category: general
---

# Oracle

Use this skill as a deep-analysis pass when confidence is low or stakes are high.

## When to Use

- Root cause remains unclear after first investigation.
- Multiple solution paths exist with significant trade-offs.
- A large change needs independent risk review.
- You need explicit challenge to assumptions before merge.

## Output Contract

Return:
- Problem framing and assumptions.
- Top hypotheses with supporting evidence.
- Option comparison with trade-offs.
- Recommended path and validation plan.

## Workflow

1. Restate the problem precisely.
2. Identify assumptions and missing evidence.
3. Evaluate alternatives with failure modes.
4. Recommend the safest high-leverage path.

## Guardrails

- Do not produce vague advice without evidence.
- Surface uncertainty explicitly.
- Prefer reversible steps when risk is high.
- Keep analysis actionable for implementation.
