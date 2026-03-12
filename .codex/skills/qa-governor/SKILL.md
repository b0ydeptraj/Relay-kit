---
name: qa-governor
description: check readiness and completion against acceptance criteria, risk, and regression scope; write a qa report before completion is claimed. use before saying work is done or when implementation confidence is low.
---

# Mission
Prevent premature completion claims and surface residual risk clearly.

## Produce `qa-report.md`
Include:
- scope checked
- acceptance coverage
- risk matrix
- regression surface
- evidence collected
- go or no-go recommendation

## Mandatory checks
- Compare actual evidence to acceptance criteria, not just implementation intent.
- Name the regression surface explicitly.
- Call out missing tests, weak evidence, or unverified assumptions.
- Bounce work back when story, tech-spec, or architecture is still underspecified.

## Inputs
- PRD or tech-spec
- architecture or story
- evidence from tests and reviews

## Outputs
- .ai-kit/contracts/qa-report.md

## Reference skills and rules
- Use testing-patterns, systematic-debugging, and code-review as support skills.
- Coverage must be explained against acceptance criteria and risk, not just number of tests.

## Likely next step
- developer
- workflow-router
