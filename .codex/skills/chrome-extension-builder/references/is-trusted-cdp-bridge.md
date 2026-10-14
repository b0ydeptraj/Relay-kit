# IsTrusted CDP Emulation Bridge

This guide details how to generate genuine `event.isTrusted: true` input events from inside a Chrome Extension to bypass modern bot-detection and anti-cheat web mechanisms.

---

## 1. The `isTrusted` Challenge

Standard DOM synthetic dispatchers (`element.click()`, `element.dispatchEvent(new MouseEvent(...))`) produce events where:
```javascript
event.isTrusted === false
```
Bot defense solutions (Cloudflare Turnstile, reCAPTCHA v3/Enterprise, Arkose Labs, monitored e-learning quiz portals) inspect `event.isTrusted`. If `false`, the submission or interaction is immediately flagged or rejected.

---

## 2. Escalation Architecture: `chrome.debugger`

To produce true `isTrusted: true` events without external tools (Playwright/Puppeteer), the extension background worker leverages the native Chrome DevTools Protocol via the `chrome.debugger` API.

### Workflow:
1. Content script detects target element bounding box:
   ```javascript
   const rect = element.getBoundingClientRect();
   const x = Math.round(rect.left + rect.width / 2);
   const y = Math.round(rect.top + rect.height / 2);
   ```
2. Content script requests a trusted click from background:
   ```javascript
   await chrome.runtime.sendMessage({
       action: 'DISPATCH_TRUSTED_CLICK',
       coords: { x, y }
   });
   ```
3. Background attaches to the current tab via `chrome.debugger.attach({ tabId }, "1.3")`:
   ```javascript
   async function dispatchTrustedClick(tabId, x, y) {
       const target = { tabId };
       await chrome.debugger.attach(target, "1.3");
       try {
           // Mouse Move
           await chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", {
               type: "mouseMoved", x, y
           });
           // Mouse Down
           await chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", {
               type: "mousePressed", x, y, button: "left", clickCount: 1
           });
           // Small human-like dwell time (50-100ms)
           await new Promise(r => setTimeout(r, 60));
           // Mouse Up
           await chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", {
               type: "mouseReleased", x, y, button: "left", clickCount: 1
           });
       } finally {
           await chrome.debugger.detach(target);
       }
   }
   ```

---

## 3. Trusted Keyboard Input

When filling protected inputs that reject synthetic `value` assignments:
```javascript
async function dispatchTrustedText(tabId, text) {
    const target = { tabId };
    await chrome.debugger.attach(target, "1.3");
    try {
        for (const char of text) {
            await chrome.debugger.sendCommand(target, "Input.dispatchKeyEvent", {
                type: "keyDown", text: char
            });
            await chrome.debugger.sendCommand(target, "Input.dispatchKeyEvent", {
                type: "keyUp"
            });
            // 20-50ms natural typing jitter
            await new Promise(r => setTimeout(r, 20 + Math.random() * 30));
        }
    } finally {
        await chrome.debugger.detach(target);
    }
}
```

---

## 4. Policy & Safety Boundaries
* **Notification Banner**: Attaching `chrome.debugger` causes Chrome to display a top banner: `"Extension is debugging this browser"`.
* **Decision Rule**:
  * For standard internal automation (LMS, data extraction, intranet): Use DOM Synthetic click (faster, zero overhead, no debugger banner).
  * For bot-detection gated workflows: Escalate to `chrome.debugger`.
