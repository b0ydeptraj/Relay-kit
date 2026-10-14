# reverse-hub operator contract

## Scope boundary
reverse-hub owns reverse engineering of shipped artifacts and observed runtime, not analysis of source you already hold. Enter it only when the question depends on a binary or package, a decompilation, passive runtime evidence, or behavior the available source cannot establish. When readable source answers the question, hand back to `scout-hub` and stop.

## Authorization boundary
The hub analyzes artifacts the operator is authorized to inspect. On-chain, wallet, or transaction-shaped follow-ups route through `mmo-onchain-security-audit` before any action that moves value. Offensive follow-ups inherit the engagement authorization already recorded in workflow-state; reverse-hub never creates that authorization itself.

## Routing order
1. Read the target the user supplied and name its type. If the target is a vague "my app", ask which artifact before touching any tool.
2. Pick the first specialist from the target type, not from a guess about intent:
   - native PE/ELF/Mach-O, packers, protections -> `binary-reverse-methodology`
   - unknown or suspicious sample, IOC work -> `malware-analysis-workflows`
   - Android/iOS/Flutter mobile native -> `mobile-app-reverse`
   - Electron/JavaScript, WASM, obfuscated web JS, client-side crypto -> `frontend-crypto-reverse`
   - detectability of a produced artifact -> `binary-stealth-obfuscation`
   - network capture or C2 traffic shape -> `network-stealth-c2`
   - on-chain or wallet reversing -> `mmo-onchain-security-audit`
3. Reuse prior evidence through `memory-search` before re-running any analysis.

## Evidence rules
- Every conclusion separates observations (what the tool returned), inferences (what you concluded from it), and unknowns (what is still open).
- Every conclusion cites an evidence id that points at the retained tool output, not at a recollection.
- Static analysis is never written up as having observed execution. Runtime claims require a runtime capture that was planned as bounded before it ran.
- A search that found nothing is reported with its boundary ("searched imports and string table, did not cover packed sections"), never as "the behavior does not exist".
- The finding ledger in `investigation-notes.md` carries, per conclusion: evidence id, confidence, search boundary, and remaining unknowns.
- Before finishing, each original question is marked answered, partially answered, or unresolved. Run `evidence-before-completion` before any "confirmed" wording.

## Hold conditions
Hold and route back instead of answering when:
- the only basis for a behavior claim is a symbol or file name
- a preview was truncated and the full result was never retrieved
- a runtime behavior is being asserted from static reads alone
- a feature is being called absent after a bounded search that did not cover the whole artifact

## Exit
End with the per-question verdict, the named specialist that should continue (or `review-hub` to turn findings into a decision, `debug-hub` when the target is actually a reproducible local bug), and the unknowns that still block a confirmed answer.
