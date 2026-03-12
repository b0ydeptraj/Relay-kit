# layer-model

This repo now follows a 4-layer hub-and-spoke topology so orchestration and execution are separate concerns.

## layer-1-orchestrators
Coordinate the whole system, choose the active lane, and keep shared state current.

- workflow-router
- bootstrap
- team
- cook

## layer-2-workflow-hubs
Run repeatable multi-step workflows and hand off to the right specialist or support skill.

- brainstorm-hub
- scout-hub
- plan-hub
- debug-hub
- fix-hub
- test-hub
- review-hub

## layer-3-utility-providers
Stateless capabilities and analysis helpers. These should be called by hubs when present rather than acting as top-level entrypoints.

- research-expert
- docs-seeker
- sequential-thinking
- problem-solving
- ai-multimodal
- chrome-devtools
- repomix
- context-engineering
- mermaidjs-v11
- ui-ux-pro-max
- media-processing

## layer-4-specialists-and-standalones
Role specialists and native support skills that actually produce architecture, stories, code, and quality evidence.

- analyst
- pm
- architect
- scrum-master
- developer
- qa-governor
- agentic-loop
- project-architecture
- dependency-management
- api-integration
- data-persistence
- testing-patterns
