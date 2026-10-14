---
name: dns-enumeration
description: "Use when performing DNS reconnaissance on a target domain: subdomain enumeration, zone transfer attempts, DNS record collection (A, AAAA, MX, TXT, NS, CNAME, SRV, SOA), DNS cache snooping, and reverse DNS lookups. Engagement proof required."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

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
- dns-recon-specialist

## Layer
- layer-4-specialists-and-standalones

## Likely next step
- network-scanner
- web-app-scanner
- offensive-security-engagement
- searching-exploit-db
