# refactoring-discipline Battle-Calibrated Output

Request: handle a refactoring-discipline request, name files first, and identify the proof surface before editing

Recommended skill: `refactoring-discipline` because the request matches `refactor-discipline` work and has concrete repo anchors.

Read first:

- `src/orders/service.py`
- `src/orders/legacy.py`
- `tests/orders/test_service.py`

Evidence gathered:

- Confirmed `OrderService` ownership before recommending changes.
- Checked `green test net` and `characterization test` against the relevant source path.
- Identified `behavior preserved` as a required proof term before completion.

Answer:

The safe next move is to inspect the named path, compare it with the expected test, metric, config, or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `atomic commit` remains unverified until the focused gate or proof surface is captured.
