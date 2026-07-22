---
name: network-stealth-c2
description: Use when building or operating C2 infrastructure that needs traffic blending, domain fronting, protocol mimicry, redirectors, or beaconing that evades network detection.
---

# Mission
Design and implement C2 communication that blends with legitimate traffic and evades network-level detection.

## Mandatory scope
1. Engagement proof required.
2. Choose C2 protocol: HTTPS, DNS, SMB, ICMP, custom — document traffic profile.
3. Document domain fronting or CDN relay if used: fronting domain, host header, backend.
4. Configure beacon jitter: randomized interval (base +/- jitter %) to avoid periodic traffic patterns.
5. Implement redirectors: separate C2 server from direct operator contact.
6. Network traffic profile: document legitimate service being mimicked (Office365, Slack, etc.).

## Evidence contract
- engagement_proof confirmed
- protocol and traffic profile documented
- beacon jitter configured and documented
- redirector topology drawn
- network capture shows traffic blends with legitimate baseline

## Role
- c2-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- engagement scope
- target network environment
- C2 framework if specified

## Outputs
- C2 implementation
- traffic profile docs
- redirector topology

## Reference skills and rules
- Never use default C2 framework signatures — customize all beacons, certificates, and user-agents.
- Jitter is mandatory — fixed intervals are trivially detected.
- Redirectors must not expose backend C2 IP directly.
- engagement_proof required; block if missing.
- Open `references/network-stealth-c2-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/network-stealth-c2-good-output.md` and `examples/network-stealth-c2-bad-output.md` to calibrate output quality.
- Use `evals/network-stealth-c2-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/network-stealth-c2-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- edr-evasion-tactics
- telemetry-blinding
- protocol-fingerprint-spoofing
- test-hub
- field-journal-evolution
