# RelayKit MMO Fleet Operator Extension

Production-hardened Chrome Extension (Manifest V3) for fleet automation, session extraction, and anti-bot bypass.

---

## 1. Quick Installation (Load Unpacked)

1. Open Chromium browser (Chrome, Brave, Edge).
2. Navigate to `chrome://extensions/`
3. Enable **Developer mode** (toggle in top-right corner).
4. Click **Load unpacked** (Tải tiện ích đã giải nén).
5. Select directory:
   ```text
   c:\Users\Hiep\Documents\Relay-kit\extensions\relay-mmo-fleet
   ```

---

## 2. Production Features

### A. Session & Token Vault
* **One-Click Export**:
  * **JSON Format**: Export all active domain cookies into JSON.
  * **Netscape Format**: Directly compatible with anti-detect browser profiles (Multilogin, AdsPower, Dolphin Anty, GoLogin) and CLI tools (`curl -b cookies.txt`).
* **JWT & WebStorage Scan**: Scans `localStorage` and `sessionStorage` for active authentication tokens (JWT strings starting with `ey...`).

### B. CDP `isTrusted: true` Emulation
* When clicking protected buttons (e.g. Cloudflare Turnstile, verification gates):
  * Toggle **Enable CDP `isTrusted: true`**.
  * The extension automatically attaches `chrome.debugger` to the tab and issues native Chrome DevTools Protocol commands (`Input.dispatchMouseEvent` / `Input.dispatchKeyEvent`), producing authentic hardware-level input events.

### C. Reactive DOM Waiter (Zero Busy-Polling)
* Replaces CPU-killing `setInterval` loops with scoped **`MutationObserver`** instances.
* Multi-tab fleets on VPS/containers run with minimal CPU footprint.

### D. HTML5 Media Autoplay Bypass
* Forces `defaultMuted = true`, `muted = true`, `volume = 0` to bypass Chrome's `NotAllowedError` autoplay restrictions.
* Resilient timeline fast-forward (`currentTime`) with tolerance validation and element-swap recovery.

### E. Off-Page CSP Bypass Fetch Proxy
* In-page scripts send requests to `background.js` to dispatch external webhooks or telemetry, completely immune to host page Content Security Policy (CSP).

---

## 3. Automated Test Verification

Run unit tests directly without any third-party dependencies:
```bash
node --test tests/extension.test.cjs
```
Output:
```text
✔ manifest.json conforms to hardened Manifest V3 specs
✔ exportTabCookies formats cookies in JSON and Netscape formats
✔ CDP dispatcher throws when chrome.debugger is unattached or unavailable
✔ updateTaskState commits patches to chrome.storage.local
✔ content script harvestWebStorage detects JWT tokens in storage
✔ content script MediaController mutes media for autoplay policy bypass
ℹ tests 6 | pass 6 | fail 0
```
