# chrome-extension-builder Good Output Example

## User Request
"Create a hardened Chrome extension that automates answering questions on a protected LMS web portal and handles cross-origin embedded YouTube videos."

## Expected Good Output Structure

1. **Architecture Boundary Statement**:
   - Identifies Manifest V3 compliance requirements.
   - Declares isolated world vs main world boundaries.
   - Implements background service worker proxying to avoid host CSP restrictions.

2. **Source Artifacts**:
   - **`manifest.json`**: Minimal permissions (`storage`, exact host permissions, `all_frames: true` for video embeds).
   - **`background.js`**: Resilient message handling, transient error retry support, off-page network routing.
   - **`content.js`**: Zero-polling `MutationObserver` selector waiting, `AbortController` signal pipeline, bounded timeouts (15s skip for non-critical steps).
   - **`youtube-frame.js`**: Cross-origin `postMessage` RPC bridge, autoplay bypass (`muted`, `volume=0`), resilient seek.

3. **Verifiable Test Proof**:
   - Executes unit tests using standard `node --test tests/*.test.cjs`.
   - Produces passing test output with zero skipped or failed assertions.
