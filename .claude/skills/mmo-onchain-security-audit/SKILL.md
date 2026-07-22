---
name: mmo-onchain-security-audit
description: Use when MMO crypto operations involve on-chain script execution, smart contract interaction, or wallet automation that requires security audit before deployment.
---

# Mission
Audit on-chain scripts and smart contract interactions for security vulnerabilities before any wallet or funds are committed.

## Mandatory scope
1. Static analysis: read all contract functions being called; identify reentrancy, approval abuse, infinite approve risk.
2. Simulation first: dry-run all transactions with fork simulation (Tenderly / Hardhat mainnet fork / Foundry fork) before live execution.
3. Approval audit: identify any approve() or setApprovalForAll() calls; flag unlimited approvals as high-risk.
4. Slippage and MEV: document slippage tolerance and MEV exposure for swap transactions.
5. Wallet isolation: confirm 1-wallet-per-strategy rule — never reuse signing key across strategies.
6. Emergency stop: document how to revoke approvals or pause automation if anomaly detected.

## Evidence contract
- static analysis of all called functions documented
- fork simulation result captured
- approval risk documented (unlimited vs limited)
- slippage and MEV tolerance documented
- emergency revocation procedure written

## Role
- onchain-auditor

## Layer
- layer-4-specialists-and-standalones

## Inputs
- smart contract addresses
- automation script
- chain (ETH/BSC/ARB/etc)

## Outputs
- security audit report
- simulation result
- risk assessment
- emergency procedures

## Reference skills and rules
- Never deploy wallet automation without fork simulation first.
- Unlimited approvals are always high-risk — document and recommend alternatives.
- Wallet isolation is mandatory — one signing key per strategy.
- Emergency stop procedure must be documented before deployment.
- Open `references/mmo-onchain-security-audit-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-onchain-security-audit-good-output.md` and `examples/mmo-onchain-security-audit-bad-output.md` to calibrate output quality.
- Use `evals/mmo-onchain-security-audit-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-onchain-security-audit-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-crypto-wallet-farming
- mmo-http-api-automation
- test-hub
- field-journal-evolution
