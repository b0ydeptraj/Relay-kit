---
name: performance-optimization
description: Use when latency, throughput, memory, or cost regresses and needs disciplined profiling: measure a baseline, find the real bottleneck, fix the hot path, and prove the gain.
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Fix performance by measurement, not guesswork: establish a baseline, profile to the real bottleneck, change one thing, and prove the delta.

## Mandatory scope
1. Define the metric and workload: p50/p95/p99 latency, throughput, memory, or cost, under a stated load.
2. Capture a baseline measurement before changing anything.
3. Profile to locate the dominant cost (CPU, allocations, I/O, N+1 queries, lock contention) — do not assume.
4. Change one variable, then re-measure against the same workload.
5. Guard against regression: keep or add a benchmark so the gain does not silently erode.

## Evidence contract
- baseline number with workload and environment stated
- profiler evidence identifying the bottleneck
- after number from the same workload, with the delta
- benchmark or check that locks in the improvement

## Role
- performance-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- hot path or slow endpoint
- profiling access or benchmark harness
- target metric and budget

## Outputs
- .relay-kit/references/performance.md
- optimized code
- before/after benchmark evidence

## Reference skills and rules
- Never optimize without a baseline measurement.
- Profile before changing — intuition about hot paths is often wrong.
- Change one variable at a time so the delta is attributable.
- Prove the gain on the same workload; a faster microbenchmark is not a faster system.
- Open `references/performance-optimization-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/performance-optimization-good-output.md` and `examples/performance-optimization-bad-output.md` to calibrate output quality.
- Use `evals/performance-optimization-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/performance-optimization-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- observability-instrumentation
- testing-patterns
- review-hub
- runtime-doctor
