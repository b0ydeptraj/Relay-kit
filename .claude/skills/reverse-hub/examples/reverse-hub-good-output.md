# reverse-hub — strong example

**Request:** "This Electron note app copies a weird payload to the clipboard. What is it building? I only have the installer."

**reverse-hub response:**

Target type: shipped Electron app, delivered as `app.asar`. No source repo, so this is a reverse-hub lane, not a scout-hub read. Routing the ASAR to `frontend-crypto-reverse`; `electron-app-analyzer` handles the extraction.

Question checklist:
1. What does the app write to the clipboard on copy? (needs: the copy handler + the value it passes to `clipboard.writeText`)
2. Is the payload transformed or signed before write? (needs: the transform path)

Findings (ledger):

| id | observation | inference | confidence | search boundary | unknown |
|----|-------------|-----------|-----------|-----------------|---------|
| E1 | `preload.js:212` calls `clipboard.writeText(buildBlock(sel))` on the `copy` IPC | the copy handler delegates to `buildBlock` | high | extracted asar `main.js`, `preload.js` | none |
| E2 | `buildBlock` (main.js:1180) wraps the selection in a JSON envelope with a `v` field and base64-encodes it | the payload is a base64 JSON envelope, not plain text | high | `buildBlock` body + its two callees | whether `v` is a format version or a signature |

Answer: on copy, the app writes a base64-encoded JSON envelope (not the raw text). The `v` field is **unresolved** — it reads as a version tag but I have not traced a verifier, so I am not calling it a signature.

Verdict per question: Q1 answered (E1→E2); Q2 partially answered — transform confirmed, the `v` field's role is unresolved.

Next: `frontend-crypto-reverse` to resolve whether `v` feeds a verify path. This is static only — I did not run the app, so I am making no claim about what it does at paste time.
