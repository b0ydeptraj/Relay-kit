# Relay-kit Pulse Report

`relay-kit pulse build` writes a static JSON and HTML report for local quality review.

Pulse is Relay-kit's own report surface. It is not a copy of an external dashboard system, and it does not require a server.

## Command

```bash
relay-kit pulse build /path/to/project
relay-kit pulse build /path/to/project --include-readiness
relay-kit pulse build /path/to/project --workflow-eval-file workflow-eval.json --readiness-file readiness.json
```

Default output:

```text
.relay-kit/pulse/pulse-report.json
.relay-kit/pulse/index.html
```

## Signals

Pulse combines:

- workflow eval status, pass rate, route margin, route confidence, evidence coverage, and skill distribution
- readiness status and verdict when `--include-readiness` or `--readiness-file` is used
- evidence ledger event counts, gate counts, and recent events

## Status

- `pass`: workflow eval passed, readiness passed when included, and no recent failed evidence events are present
- `attention`: core quality gates passed, but recent evidence contains failed events
- `hold`: workflow eval or readiness is failing

`pulse_score` is a local summary score built from pass rate, evidence coverage, readiness status, and recent evidence failures. Treat it as a triage signal, not a release attestation.

## Release Use

Run Pulse after eval/readiness evidence exists:

```bash
relay-kit eval run /path/to/project --strict --json --output-file workflow-eval.json
relay-kit readiness check /path/to/project --profile enterprise --json > readiness.json
relay-kit pulse build /path/to/project --workflow-eval-file workflow-eval.json --readiness-file readiness.json
```

Use the HTML file for human review and the JSON file for support bundles or future dashboards.
