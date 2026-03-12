---
name: workflow-router
description: route a request through the right delivery track, choose the next skill, and keep workflow-state current. use when a request arrives, the user asks what to do next, or scope or complexity is unclear.
---

# Mission
Decide how the request should move through the system and make the next step explicit.

## Mandatory routing procedure
1. Read `.ai-kit/contracts/project-context.md` if it exists.
2. Score the request on five axes: ambiguity, breadth of change, architecture risk, operational risk, and coordination cost.
3. Classify complexity:
   - `L0`: single bug or tiny refactor
   - `L1`: small feature or bug cluster
   - `L2`: multi-component feature slice
   - `L3`: product or platform change with design trade-offs
   - `L4`: enterprise, compliance, or scale-sensitive work
4. Choose track:
   - `L0-L1` -> quick-flow
   - `L2-L3` -> product-flow
   - `L4` -> enterprise-flow
5. Update `.ai-kit/state/workflow-state.md` with:
   - chosen complexity level and why
   - chosen track and why
   - artifacts already available
   - exact next skill to invoke
   - blockers or open questions
6. If quick-flow is selected, ensure `.ai-kit/contracts/tech-spec.md` exists before implementation begins.
7. If product-flow or enterprise-flow is selected, start with `analyst` unless a recent `product-brief.md` already exists and is still valid.

## Escalation rules
Escalate to the next track immediately when any of the following appears:
- The change touches multiple bounded contexts.
- Acceptance criteria are unclear or disputed.
- Security, migration, or rollout risk appears.
- A small fix now changes contracts, schemas, APIs, or infrastructure.

## Output contract
Never end with vague advice. Always name the next skill, the artifact it should create or update, and what evidence is still missing.

## Inputs
- user request
- .ai-kit/contracts/project-context.md (if present)
- .ai-kit/state/workflow-state.md (if present)

## Outputs
- .ai-kit/state/workflow-state.md
- .ai-kit/contracts/tech-spec.md or product-brief.md kickoff

## Reference skills and rules
- Use legacy support skills by role when specialized analysis is required.
- Prefer existing project-context over assumptions.
- Escalate from quick-flow to product-flow whenever hidden complexity appears.

## Likely next step
- analyst
- pm
- architect
- scrum-master
- developer
- qa-governor
