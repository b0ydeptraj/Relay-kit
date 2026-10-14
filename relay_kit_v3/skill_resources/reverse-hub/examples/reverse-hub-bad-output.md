# reverse-hub — weak example (what to avoid)

**Request:** "This Electron note app copies a weird payload to the clipboard. What is it building? I only have the installer."

**Weak response:**

> It's an Electron app, so it almost certainly uses the standard `clipboard` module. There's a function called `buildBlock`, which by the name builds the clipboard block, so it's just formatting your selection into the app's block format. The app copies your text with some metadata attached. It doesn't send anything anywhere, so there's nothing to worry about. Done.

**Why this fails the contract:**

- **Guesses from names.** "A function called `buildBlock`… by the name builds the block" — concludes behavior from a symbol name without reading the body. Violates `reverse.guess-from-names`.
- **No target routing, no extraction.** Never extracts the `app.asar`, never names a specialist, never cites a file/line. There is no evidence id behind any claim.
- **Static read dressed as runtime fact.** "The app copies your text with some metadata" is stated as observed behavior though nothing was run and the handler was never read.
- **Negative claim as proof of absence.** "It doesn't send anything anywhere" after looking at nothing — a bounded (here: zero) search reported as certainty. Violates `reverse.bounded-negative`.
- **No ledger, no unknowns, no per-question verdict.** Closes with "Done" while every question is actually unresolved.

**The corrective:** route the ASAR to the specialist, extract it, cite the copy handler and the transform by file:line as evidence ids, separate what was observed from what was inferred, and mark the `v` field unresolved instead of hand-waving it as safe.
