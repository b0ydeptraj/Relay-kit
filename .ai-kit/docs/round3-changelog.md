# round3-changelog

Round 3 tightens orchestration around the 4-layer model:

- adds layer-1 orchestrators: `bootstrap`, `team`, `cook`
- adds layer-2 workflow hubs: `brainstorm-hub`, `scout-hub`, `plan-hub`, `debug-hub`, `fix-hub`, `test-hub`, `review-hub`
- adds an explicit `developer` specialist so execution has a first-class handoff target
- upgrades workflow-state to record orchestrator, hub, lane, and active specialist
- adds `team-board.md` and `investigation-notes.md` so multi-lane and debugging work have stable artifacts
- keeps round2 bundle behavior intact while adding new round3 bundles
