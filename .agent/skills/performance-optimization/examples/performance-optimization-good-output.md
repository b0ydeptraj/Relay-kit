# performance-optimization Battle-Calibrated Output

Request: handle a performance-optimization request, name files first, and identify the proof surface before editing

Recommended skill: `performance-optimization` because the request matches `performance-specialist` work and has concrete repo anchors.

Read first:

- `src/api/search.py`
- `src/db/queries.py`
- `bench/search_bench.py`

Evidence gathered:

- Confirmed `search_handler` ownership before recommending changes.
- Checked `baseline p95` and `profiler` against the relevant source path.
- Identified `hot path` as a required proof term before completion.

Answer:

The safe next move is to inspect the named path, compare it with the expected test, metric, config, or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `delta` remains unverified until the focused gate or proof surface is captured.
