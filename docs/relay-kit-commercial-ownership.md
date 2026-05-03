# Relay-kit Commercial Ownership

This document records the public commercial proof contacts used by Relay-kit release and support gates.

It is an operational ownership statement for release evidence. It is not a separate legal contract, warranty, or customer-specific SLA. Customer-specific legal terms must be agreed separately before a paid deployment depends on guaranteed response windows.

## Public Owners

| Role | Owner | Proof surface |
|---|---|---|
| Release owner | `b0ydeptraj` | GitHub repository owner and release publisher |
| Support owner | `b0ydeptraj` | GitHub issue support intake and support SLA workflow |
| Legal/commercial owner | `b0ydeptraj` | Public repository owner for commercial proof handoff |

## Public URLs

| Proof | URL |
|---|---|
| Release page | `https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0` |
| Package wheel | `https://github.com/b0ydeptraj/Relay-kit/releases/download/v3.3.0/relay_kit-3.3.0-py3-none-any.whl` |
| Package sdist | `https://github.com/b0ydeptraj/Relay-kit/releases/download/v3.3.0/relay_kit-3.3.0.tar.gz` |
| Support SLA | `https://github.com/b0ydeptraj/Relay-kit/blob/main/docs/relay-kit-support-sla.md` |
| Support intake | `https://github.com/b0ydeptraj/Relay-kit/issues/new?template=support.yml` |
| Ownership statement | `https://github.com/b0ydeptraj/Relay-kit/blob/main/docs/relay-kit-commercial-ownership.md` |

## Commitment Boundary

The owner commits to keeping the support intake, support SLA, release page, and package artifacts available for public Relay-kit proof review.

Paid response targets are operational targets, not automatic legal guarantees. A paid team should treat a signed commercial agreement or accepted written support terms as the legal source of truth.

## Commercial Dossier Inputs

Use these stable public proof values when generating a commercial dossier for the current public release:

```bash
relay-kit commercial dossier /path/to/project \
  --channel internal \
  --ci-url https://github.com/b0ydeptraj/Relay-kit/actions/runs/25271082586 \
  --release-url https://github.com/b0ydeptraj/Relay-kit/releases/tag/v3.3.0 \
  --package-url https://github.com/b0ydeptraj/Relay-kit/releases/download/v3.3.0/relay_kit-3.3.0-py3-none-any.whl \
  --sla-url https://github.com/b0ydeptraj/Relay-kit/blob/main/docs/relay-kit-support-sla.md \
  --support-url https://github.com/b0ydeptraj/Relay-kit/issues/new?template=support.yml \
  --legal-owner b0ydeptraj \
  --support-owner b0ydeptraj \
  --strict \
  --json
```
