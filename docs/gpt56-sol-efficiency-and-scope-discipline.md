# GPT-5.6 Sol efficiency and scope policy

Status: validated locally on 2026-09-05. Owner: Relay-kit skill registry and generated adapter surfaces.

## Decisions

1. **Native compaction is the default.** OpenAI documents server-side and standalone compaction as Responses API primitives that preserve state needed for later turns. Codex should use its native long-context behavior; a skill must not imitate or rewrite encrypted compaction items. See [OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction) and [the GPT-5.6 builder guide](https://openai.com/index/builders-guide-to-gpt-5-6/).
2. **One Sol, one active lane.** The registry no longer ships `team` or `delegation-control`; routing uses `cook`, durable state, and sequential checkpoints. Multi-agent remains a documented API capability, not this runtime's default.
3. **StateM is optional, not installed.** StateM is a zero-dependency Python CLI with its own YAML runbooks and `.statem/` runtime state. Relay-kit already has workflow-state, contracts, checkpoints, and gates; installing StateM would duplicate control-plane state for the requested single-Sol profile. Reconsider only if a task needs checked graph transitions or a durable cyclic runbook beyond Relay-kit's existing gates. Source: [StateM repository](https://github.com/henryqin1997/statem), [StateM paper](https://arxiv.org/abs/2608.15089).
4. **Scope discipline is a skill, not a second orchestrator.** `scope-discipline` rejects unearned abstractions, agents, dependencies, loops, and research passes while preserving safety, correctness, accessibility, compliance, and raw failure evidence.
5. **No global reasoning downgrade was applied.** The local Codex config is `gpt-5.6-sol` with medium effort; the GPT-5.6 guide reports strong low-effort results, but this repo has no paired Sol low-vs-medium acceptance benchmark. Lower effort should be an explicit experiment, not an unverified default change.

## Operating rule

Before adding complexity, state the minimum complete contract, inspect the current surface, remove optional work, set a stopping rule, and run the cheapest verification that can falsify the minimal design. Use `token-economy` for context blocks and raw failure pointers; use native Codex compaction for conversation state.

## 50-source research ledger

The ledger is a scan of recent primary papers and the named verifier project. It is evidence for design direction, not a claim that every result transfers to Codex.

1. [2608.24876 Recursive Experiential-Working Memory Evolution](https://arxiv.org/abs/2608.24876) — durable working memory for long horizons.
2. [2608.24804 StarHarness](https://arxiv.org/abs/2608.24804) — harness evolution; warns that harness complexity is a first-class variable.
3. [2608.24358 The Handoff Tax](https://arxiv.org/abs/2608.24358) — cross-model trajectory handoffs carry cost.
4. [2608.24188 Paritok-4B](https://arxiv.org/abs/2608.24188) — extractive, intent-conditioned code-context compression.
5. [2608.24024 Retrieval-Grounded Voting](https://arxiv.org/abs/2608.24024) — external evidence can beat confidence-weighted voting.
6. [2608.24004 AgentSpec](https://arxiv.org/abs/2608.24004) — speculative decoding with dynamic agent budgets.
7. [2608.23956 Recursive Agentic Reasoning](https://arxiv.org/abs/2608.23956) — compares grow, prune, and branch under matched budgets.
8. [2608.23953 Architectural Convergence in Agent Harnesses](https://arxiv.org/abs/2608.23953) — harness, not model, can be the binding constraint.
9. [2608.23921 HAP](https://arxiv.org/abs/2608.23921) — relevance-conditioned token pruning.
10. [2608.23740 AgentRoom](https://arxiv.org/abs/2608.23740) — concurrent coding coordination overhead.
11. [2608.23564 SWE Refactor Bench](https://arxiv.org/abs/2608.23564) — whole-repository migration difficulty.
12. [2608.23552 Prime Agent](https://arxiv.org/abs/2608.23552) — persistent REPL harness for long-horizon work.
13. [2608.23471 InjecMEM](https://arxiv.org/abs/2608.23471) — persistent memory can be poisoned.
14. [2608.23268 DG-Mem](https://arxiv.org/abs/2608.23268) — dual-grained memory and attribution.
15. [2608.22975 Budget-Constrained Embodied Perception](https://arxiv.org/abs/2608.22975) — query-conditioned access beats context growth in a fixed budget.
16. [2608.22971 ParallelWorld](https://arxiv.org/abs/2608.22971) — verifier-guided branching for embodied reasoning.
17. [2608.22883 FOVEA](https://arxiv.org/abs/2608.22883) — on-demand visual evidence budgets.
18. [2608.22767 The Retriever Should Remember](https://arxiv.org/abs/2608.22767) — retrieval experience can be amortized.
19. [2608.22752 The Compaction Cliff](https://arxiv.org/abs/2608.22752) — exact rules need protection during compression.
20. [2608.22345 Tree-of-Thought Smart Contract Repair](https://arxiv.org/abs/2608.22345) — branching can recover from error propagation.
21. [2608.23623 Evidence-Carrying Termination](https://arxiv.org/abs/2608.23623) — agents need proof-linked stopping.
22. [2608.21860 ChainPrune](https://arxiv.org/abs/2608.21860) — evaluates and removes redundant reasoning.
23. [2608.21884 Loop Engineering](https://arxiv.org/abs/2608.21884) — the control loop is an abstraction layer with adoption cost.
24. [2608.21867 MemGuard](https://arxiv.org/abs/2608.21867) — persistent verifier signals for memory governance.
25. [2608.22191 Disagree to Explore, Agree to Commit](https://arxiv.org/abs/2608.22191) — selective exploration can be cheaper than always branching.
26. [2608.20664 DreamBench-SWE](https://arxiv.org/abs/2608.20664) — multi-session memory hygiene with executable oracles.
27. [2608.20631 Weighted Memory Tree](https://arxiv.org/abs/2608.20631) — importance-weighted long-horizon memory.
28. [2608.20256 Learning When to Think](https://arxiv.org/abs/2608.20256) — adaptive reasoning allocates compute by difficulty.
29. [2608.19993 Optimal Skill Selection](https://arxiv.org/abs/2608.19993) — skill loading is a token/performance optimization problem.
30. [2608.19535 Adaptive Compression for Edge RAG](https://arxiv.org/abs/2608.19535) — compression must be query- and budget-aware.
31. [2608.19047 Eureka](https://arxiv.org/abs/2608.19047) — obligation graphs can make long tasks inspectable.
32. [2608.17414 REChart](https://arxiv.org/abs/2608.17414) — reasoning-efficient editing under bounded compute.
33. [2608.17075 Foundation Agents Meet Deep Research](https://arxiv.org/abs/2608.17075) — evidence grounding for agent workflows.
34. [2608.16003 Prior Audit-Repair Context Shifts Verifier Thresholds](https://arxiv.org/abs/2608.16003) — audit context can bias later verification.
35. [2608.15935 Token Distribution versus Data Volume](https://arxiv.org/abs/2608.15935) — remove low-value tokens without assuming quality loss.
36. [2608.15614 EgoGazeLite](https://arxiv.org/abs/2608.15614) — selective evidence can preserve multimodal quality.
37. [2608.15065 Funnel of Thoughts](https://arxiv.org/abs/2608.15065) — lexical signals can prune unproductive reasoning trajectories.
38. [2608.15008 Harness the Memory](https://arxiv.org/abs/2608.15008) — no memory substrate dominates every workload.
39. [2608.14161 BiasTrace](https://arxiv.org/abs/2608.14161) — overthinking is a measurable reasoning behavior.
40. [2608.13883 MemoryLake on MemoryArena](https://arxiv.org/abs/2608.13883) — memory backend results are workload-dependent.
41. [2608.13334 RippleMem](https://arxiv.org/abs/2608.13334) — associative retrieval can lower graph construction cost.
42. [2608.12990 LycheeMemory V2](https://arxiv.org/abs/2608.12990) — segment-level consolidation reduces memory construction tokens.
43. [2608.09025 Context Is Not Authority](https://arxiv.org/abs/2608.09025) — structured runtime governance separates data from control.
44. [2608.08888 Full-bandwidth Transformer](https://arxiv.org/abs/2608.08888) — latent feedback can shorten visible reasoning traces.
45. [2606.06574 Skip a Layer or Loop It](https://arxiv.org/abs/2606.06574) — adaptive depth supports shorter valid computations.
46. [2602.03814 Conformal Thinking](https://arxiv.org/abs/2602.03814) — risk-controlled stopping under compute budgets.
47. [2604.02460 Single-Agent LLMs Outperform Multi-Agent Systems](https://arxiv.org/abs/2604.02460) — single-agent wins under equal thinking-token budgets except degraded-context regimes.
48. [2511.11306 iMAD](https://arxiv.org/abs/2511.11306) — debate should be selectively triggered, not automatic.
49. [2509.23537 Multi-Turn Multi-Agent Orchestration vs Single LLMs](https://arxiv.org/abs/2509.23537) — orchestration can help, but authorship and vote visibility introduce bias.
50. [LLM-as-a-Verifier](https://llm-as-a-verifier.com/) — fine-grained, repeated, decomposed verification and budget-aware candidate selection.

## Residual risk

The sources are heterogeneous preprints, benchmark reports, and one project site; they do not prove a universal Sol policy. The local proof is the registry/resource/route suite, not field performance. Re-run paired Sol evaluations before changing the global reasoning effort or reintroducing orchestration.
