---
name: plan-hub
description: run the planning chain from brief to prd to architecture to stories without losing context between roles. use when work is larger than quick-flow or when existing planning artifacts are stale or incomplete.
---

# Mission
Sequence the planning roles so the lane produces buildable artifacts instead of disconnected documents.

## Mandatory order
- use `analyst` if the brief is missing or stale
- use `pm` if requirements, acceptance criteria, or slice order are missing
- use `architect` if technical boundaries or readiness are unclear
- use `scrum-master` when work must be cut into stories or a quick spec

## Planning gate
Stop and route to `review-hub` when product, architecture, and story artifacts disagree.
Route to `developer` only when the active story or tech-spec is ready for implementation.

## Role
- planning-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- workflow-state
- existing brief, prd, architecture, or epics if present
- project-context

## Outputs
- product-brief, PRD, architecture, epics, and stories or tech-spec depending track

## Reference skills and rules
- Call only the roles needed to close the current planning gap.
- Use scout-hub first if the current codebase context is too weak to plan safely.
- Route to review-hub if artifacts disagree with one another.

## Likely next step
- analyst
- pm
- architect
- scrum-master
- developer
- review-hub
