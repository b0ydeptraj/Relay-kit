# chrome-extension-builder Bad Output Example

## Common Anti-Patterns and Traps

1. **Deprecated Manifest V2 Syntax**:
   - Declaring `"manifest_version": 2` or `"background": { "scripts": ["bg.js"] }`.
   - Manifest V2 is rejected by modern Chromium Web Stores and runtime engines.

2. **CPU-Thrashing Busy Polling**:
   - Using `setInterval(() => { document.querySelector(...) }, 200)` across content scripts.
   - Causes severe CPU spikes when running multi-tab fleets.

3. **Leaked Global Scope & Detectable Artifacts**:
   - Attaching variables like `window.myAutomationRunner = ...` directly to the page window object.
   - Injecting un-sanitized `<script>` tags that trigger page Content Security Policy (CSP) violations.

4. **Blind Sleeps Without Cancellation**:
   - Calling `await new Promise(r => setTimeout(r, 10000))` without listening to `signal.aborted`.
   - Results in ghost executions and memory leaks when the user presses Stop or closes the tab.

5. **No Verification Evidence**:
   - Claiming "The extension is ready and works perfectly" without running unit tests or headless test suites.
