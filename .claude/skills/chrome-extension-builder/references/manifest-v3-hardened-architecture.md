# Manifest V3 Hardened Architecture Guide

This guide establishes the mandatory engineering standards for production Manifest V3 extensions under high reliability, anti-detection, and automation workloads.

---

## 1. Service Worker Idle Teardown & Reconnect Resilience

### The MV3 Teardown Problem
Chrome terminates background service workers after approximately 30 seconds of inactivity to conserve RAM. When a content script attempts to send a message right as the worker is unloaded, `chrome.runtime.sendMessage` fails with:
* `"Could not establish connection. Receiving end does not exist."`
* `"The message port closed before a response was received."`

### Resilient Channeling Protocol
Wrap all communication from content scripts to background in a bounded exponential-retry loop:

```javascript
const TRANSIENT_DISCONNECT_REGEX = /Could not establish connection|message port closed before a response/i;

async function sendToWorkerWithRetry(message, maxAttempts = 3) {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
            const response = await chrome.runtime.sendMessage(message);
            if (response && response.error) throw new Error(response.error);
            return response;
        } catch (err) {
            if (attempt >= maxAttempts - 1 || !TRANSIENT_DISCONNECT_REGEX.test(err?.message || '')) {
                throw err;
            }
            // Linear/exponential backoff to allow Chrome to wake the worker
            await new Promise(r => setTimeout(r, 300 * (attempt + 1)));
        }
    }
}
```

---

## 2. CSP (Content Security Policy) Network Proxying

### The Problem
Target websites frequently deploy strict CSP headers (`connect-src 'self'`). Any attempt by injected content scripts or main world code to call `fetch()` to external webhooks, telemetry servers, or remote config endpoints is blocked by the browser.

### The Standard
All network requests targeting domains other than the host origin must be proxied through the background service worker:
1. Content script sends `{ action: 'PROXY_FETCH', url, options }` via `sendToWorkerWithRetry`.
2. Background service worker executes `fetch()` natively (service workers operate outside page CSP boundaries).
3. Background returns sanitized response body to content script.

---

## 3. Storage Hierarchy & Session Fencing

1. **`chrome.storage.session`**:
   * Stored in-memory, lasts until the browser/profile closes.
   * Use for ephemeral locks, active tab lease owners, and in-flight request IDs.
2. **`chrome.storage.local`**:
   * Persisted on disk.
   * Use for task checkpoints, catalog rules, and persistent user configuration.
3. **Structured Clone Safety**:
   * When saving state across different Chrome versions, avoid complex custom prototypes. Use JSON-serializable structures to ensure backward compatibility.

---

## 4. Anti-Fingerprinting & Asset Cleanliness

* **Zero Leaked Globals**: Never attach automation states or variables directly to `window`. Wrap all content script logic inside Immediately Invoked Function Expressions (IIFE).
* **Scoped `web_accessible_resources`**: Never use wildcard `"<all_urls>"` or `"*"` in `web_accessible_resources`. Malicious target scripts can probe extension IDs via `fetch('chrome-extension://<id>/icon.png')`. Restrict resources to exact target domains or omit them completely.

---

## 5. Multi-Domain SSO Cookie Extraction & Invariant Rules

### The Problem
Modern web platforms rarely authenticate using isolated single-host cookies:
* **Google / YouTube**: Authenticated state on `youtube.com` requires authentication cookies from `.google.com` (`SID`, `HSID`, `SSID`, `SAPISID`, `__Secure-1PSID`). Querying only `https://www.youtube.com/` misses all Google authentication credentials.
* **Meta / Facebook**: Authenticated sessions cross `facebook.com`, `messenger.com`, and `meta.com`.
* **Zalo Web**: Authenticated sessions cross `zalo.me`, `chat.zalo.me`, `id.zalo.me`, and `wpa.chat.zalo.me`.

### The Standard
1. **Domain Ecosystem Resolution**: Compute the base domain (eTLD+1). Map known SSO domain pairs (e.g. `youtube.com` <-> `google.com`) and query both the active tab URL and the linked ecosystem domains.
2. **RFC 6265bis Chromium `cookies.set` Invariants**:
   * **No Leading Dot**: Do NOT pass leading dots in `details.domain` (e.g., use `'google.com'`, not `'.google.com'`). Chromium rejects leading dots.
   * **`hostOnly` Protection**: If `cookie.hostOnly === true`, omit `details.domain` completely.
   * **`__Host-` Prefix Rules**: If `name.startsWith('__Host-')`, `path` MUST be `'/'`, `secure` MUST be `true`, and `domain` MUST NOT be set.
   * **`sameSite` Invariants**: If `sameSite === 'no_restriction'`, Chromium strictly requires `secure: true`.

---

## 6. Safe IndexedDB Session Extraction Contract

### The Problem
End-to-end encrypted (E2EE) web applications (Zalo Web, WhatsApp Web, Telegram Web) store private device keys and session pairing credentials in **IndexedDB**.
However, unbounded cursor sweeps across all databases cause catastrophic failures:
* Real user profiles accumulate tens of thousands of chat records, voice notes, blobs, and cached avatars (50MB - 500MB).
* Passing multi-megabyte object graphs across extension IPC triggers memory exhaustion, message size limits, and browser renderer crashes.
* Raw `CryptoKey` and non-clonable internal references throw `DataCloneError`.

### The Standard
1. **Store Blacklisting & Whitelisting**:
   * Blacklist heavy non-auth stores: `/message|conversation|chat|sticker|emoji|attachment|media|cache|file|log|telemetry|offline_sync|history|download|thread|draft/i`.
   * Whitelist / prioritize auth stores: `/key|auth|token|session|device|crypto|account|user|config|state|profile|identity|prekey|signal|localforage/i`.
2. **Strict Quotas**:
   * Maximum 50 records per store.
   * Maximum 32KB per record value. Skip or truncate any record containing giant binary blobs.
3. **Circuit Breaker**:
   * Enforce a 2500ms timeout per database using `Promise.race`. Never allow IndexedDB extraction to freeze the tab.

---

## 7. Extension Popup Renderer Crash & OOM Prevention

### The Problem
Chrome extension popups run in a memory-constrained view. Injecting a 2MB - 10MB JSON string directly into a `<textarea>.value` causes Chromium's Blink layout engine to suffer an Out-Of-Memory (OOM) crash, resulting in a blank black/white rectangle.

### The Standard
1. **Global Error Boundaries**:
   * Install `window.addEventListener('error')` and `window.addEventListener('unhandledrejection')` on line 1 of `popup.js` to render a visible error banner instead of crashing silently.
2. **Payload-Aware Display**:
   * If exported bundle JSON exceeds 300KB, store the complete bundle in an in-memory variable and `chrome.storage.local`.
   * Display a lightweight summary in the `<textarea>` to keep DOM rendering instantaneous.
   * Clipboard copy operations (`btn-copy`) copy the complete in-memory bundle directly via `navigator.clipboard.writeText`.

