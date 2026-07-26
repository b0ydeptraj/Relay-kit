# performance-optimization Battle Contract

Primary role: performance-specialist
Layer: layer-4-specialists-and-standalones
Battle family: reliability

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: service repo with a slow endpoint, a database layer, and a benchmark or load-test harness
- First files to inspect:
  - src/api/search.py
  - src/db/queries.py
  - bench/search_bench.py
- Symbols or named surfaces to confirm: search_handler, run_query, benchmark
- Evidence terms that should appear in a strong answer: baseline p95, profiler, hot path, delta

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

- Optimizing without a baseline, so the gain cannot be proven.
- Guessing the bottleneck instead of profiling.
- Changing several things at once so the delta is unattributable.
- Reporting a microbenchmark win that does not move the real system.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
