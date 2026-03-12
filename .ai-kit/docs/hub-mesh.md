# hub-mesh

Workflow hubs are allowed to call across the mesh when the current lane hits ambiguity, risk, or missing evidence.

## Cross-hub references

### brainstorm-hub
Can hand off to:
- plan-hub
- workflow-router

### scout-hub
Can hand off to:
- plan-hub
- debug-hub
- review-hub
- workflow-router

### plan-hub
Can hand off to:
- brainstorm-hub
- scout-hub
- fix-hub
- review-hub
- workflow-router

### debug-hub
Can hand off to:
- fix-hub
- test-hub
- scout-hub
- workflow-router

### fix-hub
Can hand off to:
- debug-hub
- test-hub
- review-hub
- workflow-router

### test-hub
Can hand off to:
- debug-hub
- fix-hub
- review-hub
- workflow-router

### review-hub
Can hand off to:
- plan-hub
- debug-hub
- fix-hub
- test-hub
- workflow-router

## Recommended support map

### brainstorm-hub
- analyst
- pm
- research-expert
- ui-ux-pro-max

### scout-hub
- project-architecture
- dependency-management
- api-integration
- data-persistence
- testing-patterns
- docs-seeker
- repomix
- context-engineering

### plan-hub
- analyst
- pm
- architect
- scrum-master
- research-expert
- ui-ux-pro-max

### debug-hub
- developer
- testing-patterns
- systematic-debugging
- problem-solving
- sequential-thinking
- chrome-devtools

### fix-hub
- developer
- agentic-loop
- project-architecture
- api-integration
- data-persistence
- refactoring-expert

### test-hub
- qa-governor
- testing-patterns
- agentic-loop
- systematic-debugging

### review-hub
- qa-governor
- testing-patterns
- code-review
- project-architecture
