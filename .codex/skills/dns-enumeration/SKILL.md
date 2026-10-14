---
name: dns-enumeration
description: "Use when performing DNS reconnaissance on a target domain: subdomain enumeration, zone transfer attempts, DNS record collection (A, AAAA, MX, TXT, NS, CNAME, SRV, SOA), DNS cache snooping, and reverse DNS lookups. Engagement proof required."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when performing DNS reconnaissance on a target domain: subdomain enumeration, zone transfer attempts, DNS record collection (A, AAAA, MX, TXT, NS, CNAME, SRV, SOA), DNS cache snooping, and reverse DNS lookups.

# DNS Enumeration

> Comprehensive DNS reconnaissance for authorized penetration testing.

## Mission
Enumerate DNS infrastructure of target domain to map attack surface.

## Mandatory scope checks
1. Engagement proof required
2. Confirm domain is in scope (check rules of engagement)
3. Define enumeration depth: passive only vs active bruteforce
4. Check for rate limiting and use delays

## Enumeration checklist
- [ ] Zone transfer attempt (AXFR) on all NS servers
- [ ] A/AAAA records for domain and www
- [ ] MX records (mail infrastructure)
- [ ] TXT records (SPF, DKIM, DMARC, verification tokens)
- [ ] NS records (nameserver inventory)
- [ ] Subdomain brute force with wordlist
- [ ] Certificate transparency logs (crt.sh) for passive subdomain discovery
- [ ] Reverse DNS on all discovered IPs

## Role
- offensive-security-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with dns-enumeration findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside dns-enumeration's scope back through `offensive-security-engagement` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/dns-enumeration-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/dns-enumeration-good-output.md` and `examples/dns-enumeration-bad-output.md` to calibrate output quality.
- Use `evals/dns-enumeration-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/dns-enumeration-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- dns-enumeration
- offensive-security-engagement
- workflow-router
