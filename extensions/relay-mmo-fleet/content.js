/**
 * content.js - RelayKit MMO In-Page Automation & Extraction Engine
 * 
 * Injected into top-level pages and embedded iframes (all_frames: true).
 */
(function () {
    'use strict';

    if (typeof window !== 'undefined') {
        if (window.__relay_mmo_fleet_injected) return;
        window.__relay_mmo_fleet_injected = true;
    }

    // 1. Transient Channel Error Retry for MV3 Service Worker
    const TRANSIENT_ERROR_REGEX = /Could not establish connection|message port closed before a response/i;

    async function sendToWorker(message, maxAttempts = 3) {
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                const response = await chrome.runtime.sendMessage(message);
                return response;
            } catch (err) {
                if (attempt >= maxAttempts - 1 || !TRANSIENT_ERROR_REGEX.test(err?.message || '')) throw err;
                await new Promise(r => setTimeout(r, 250 * (attempt + 1)));
            }
        }
    }

    // 2. Reactive DOM Waiter (MutationObserver - Zero Busy Polling)
    function waitFor(selector, options = {}) {
        const { timeoutMs = 15000, scope = document, visibleOnly = true, signal = null } = options;

        return new Promise((resolve, reject) => {
            const check = () => {
                const matches = [...scope.querySelectorAll(selector)];
                if (visibleOnly) {
                    return matches.find(el => el.isConnected && el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden');
                }
                return matches[0] || null;
            };

            const existing = check();
            if (existing) return resolve(existing);

            let observer = null;
            let timer = null;

            function cleanup() {
                if (observer) { observer.disconnect(); observer = null; }
                if (timer) { clearTimeout(timer); timer = null; }
                signal?.removeEventListener('abort', onAbort);
            }

            function onAbort() {
                cleanup();
                reject(new DOMException('Wait aborted', 'AbortError'));
            }

            if (signal?.aborted) return onAbort();
            signal?.addEventListener('abort', onAbort, { once: true });

            timer = setTimeout(() => {
                cleanup();
                reject(new Error(`Timeout waiting for element: ${selector}`));
            }, timeoutMs);

            observer = new MutationObserver(() => {
                const el = check();
                if (el) { cleanup(); resolve(el); }
            });

            observer.observe(scope.body || scope, { childList: true, subtree: true });
        });
    }

    // 3. Humanized Interaction Dispatcher (Synthetic vs CDP isTrusted)
    const HumanActions = {
        async click(element, options = {}) {
            const { useCdp = false, signal = null } = options;
            if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');

            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            const dwell = 60 + Math.floor(Math.random() * 80);
            await new Promise(r => setTimeout(r, dwell));

            if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');

            if (useCdp) {
                const rect = element.getBoundingClientRect();
                const coords = {
                    x: Math.round(rect.left + rect.width / 2),
                    y: Math.round(rect.top + rect.height / 2)
                };
                const res = await sendToWorker({ action: 'CDP_CLICK', coords });
                if (!res?.ok) throw new Error(res?.error || 'CDP Click failed');
                return res;
            }

            if (typeof element.focus === 'function') element.focus();
            element.click();
            return { success: true, synthetic: true };
        },

        async type(element, text, options = {}) {
            const { useCdp = false, signal = null } = options;
            if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');

            element.focus();
            if (useCdp) {
                const res = await sendToWorker({ action: 'CDP_TYPE', text });
                if (!res?.ok) throw new Error(res?.error || 'CDP Type failed');
                return res;
            }

            // Synthetic character-by-character input
            element.value = '';
            for (const char of text) {
                if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
                element.value += char;
                element.dispatchEvent(new Event('input', { bubbles: true }));
                await new Promise(r => setTimeout(r, 20 + Math.floor(Math.random() * 30)));
            }
            element.dispatchEvent(new Event('change', { bubbles: true }));
            return { success: true, synthetic: true };
        }
    };

    // 4. In-Page Token & Storage Harvester
    function harvestWebStorage() {
        const local = {};
        const session = {};
        const jwtCandidates = [];

        try {
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                const val = localStorage.getItem(key);
                local[key] = val;
                if (typeof val === 'string' && val.startsWith('ey') && val.split('.').length === 3) {
                    jwtCandidates.push({ source: 'localStorage', key, token: val });
                }
            }
        } catch (_) {}

        try {
            for (let i = 0; i < sessionStorage.length; i++) {
                const key = sessionStorage.key(i);
                const val = sessionStorage.getItem(key);
                session[key] = val;
                if (typeof val === 'string' && val.startsWith('ey') && val.split('.').length === 3) {
                    jwtCandidates.push({ source: 'sessionStorage', key, token: val });
                }
            }
        } catch (_) {}

        return {
            url: location.href,
            localStorage: local,
            sessionStorage: session,
            tokens: jwtCandidates
        };
    }

    // 5. HTML5 Media Fast-Forward Controller
    const MediaController = {
        mute(video) {
            if (!video) return;
            video.defaultMuted = true;
            video.muted = true;
            video.volume = 0;
            video.playsInline = true;
        },
        async seek(seconds, videoSelector = 'video') {
            const video = document.querySelector(videoSelector);
            if (!video) throw new Error('Video element not found');
            this.mute(video);
            video.currentTime = seconds;
            await new Promise(resolve => {
                const check = () => {
                    if (!video.seeking && Math.abs(video.currentTime - seconds) <= 2) resolve();
                    else setTimeout(check, 200);
                };
                check();
            });
            return { currentTime: video.currentTime, duration: video.duration };
        }
    };

    // 6. IndexedDB Engine (Safe & Fast Session Extraction for E2EE apps like Zalo, Telegram, WhatsApp)
    const NON_AUTH_STORE_REGEX = /message|conversation|chat|sticker|emoji|attachment|media|cache|file|log|telemetry|offline_sync|history|download|thread|draft/i;
    const MAX_RECORDS_PER_STORE = 50;
    const MAX_VALUE_SIZE_BYTES = 32768; // 32KB per record max
    const DB_TIMEOUT_MS = 2500;

    const IndexedDbEngine = {
        async dumpAll() {
            if (typeof indexedDB === 'undefined' || !indexedDB.databases) return [];
            try {
                const dbs = await indexedDB.databases();
                const dump = [];
                for (const dbInfo of dbs) {
                    if (!dbInfo.name) continue;
                    try {
                        const dbPromise = new Promise((resolve) => {
                            const req = indexedDB.open(dbInfo.name);
                            req.onerror = () => resolve(null);
                            req.onsuccess = async () => {
                                const db = req.result;
                                const storeNames = Array.from(db.objectStoreNames);
                                // Filter out massive media/chat history stores to avoid OOM
                                const targetStores = storeNames.filter(name => !NON_AUTH_STORE_REGEX.test(name));
                                if (!targetStores.length) {
                                    db.close();
                                    return resolve({ name: dbInfo.name, version: db.version, stores: {} });
                                }
                                const stores = {};
                                const tx = db.transaction(targetStores, 'readonly');
                                for (const sName of targetStores) {
                                    try {
                                        const store = tx.objectStore(sName);
                                        const records = await new Promise(rStore => {
                                            const cursorReq = store.openCursor();
                                            const items = [];
                                            cursorReq.onsuccess = (e) => {
                                                const cursor = e.target.result;
                                                if (cursor && items.length < MAX_RECORDS_PER_STORE) {
                                                    try {
                                                        const val = cursor.value;
                                                        // Guard against huge binary blobs / non-cloneable objects
                                                        if (val && typeof val === 'object') {
                                                            if (val instanceof Blob && val.size > MAX_VALUE_SIZE_BYTES) {
                                                                cursor.continue();
                                                                return;
                                                            }
                                                            if (val instanceof ArrayBuffer && val.byteLength > MAX_VALUE_SIZE_BYTES) {
                                                                cursor.continue();
                                                                return;
                                                            }
                                                        }
                                                        items.push({ key: cursor.key, value: val });
                                                    } catch (_) {}
                                                    cursor.continue();
                                                } else {
                                                    rStore(items);
                                                }
                                            };
                                            cursorReq.onerror = () => rStore([]);
                                        });
                                        stores[sName] = {
                                            keyPath: store.keyPath,
                                            autoIncrement: store.autoIncrement,
                                            records
                                        };
                                    } catch (_) {
                                        stores[sName] = { records: [] };
                                    }
                                }
                                db.close();
                                resolve({ name: dbInfo.name, version: db.version, stores });
                            };
                        });

                        const timeoutPromise = new Promise(r => setTimeout(() => r(null), DB_TIMEOUT_MS));
                        const dbData = await Promise.race([dbPromise, timeoutPromise]);
                        if (dbData) dump.push(dbData);
                    } catch (_) {}
                }
                return dump;
            } catch (_) {
                return [];
            }
        },

        async restoreAll(dbList) {
            if (!Array.isArray(dbList) || !dbList.length || typeof indexedDB === 'undefined') return 0;
            let restoredCount = 0;
            for (const dbItem of dbList) {
                if (!dbItem.name || !dbItem.stores) continue;
                try {
                    await new Promise((resolve) => {
                        const storeEntries = Object.entries(dbItem.stores);
                        const openReq = indexedDB.open(dbItem.name, dbItem.version || 1);
                        openReq.onupgradeneeded = (e) => {
                            const db = e.target.result;
                            for (const [sName, sData] of storeEntries) {
                                if (!db.objectStoreNames.contains(sName)) {
                                    const opts = {};
                                    if (sData.keyPath) opts.keyPath = sData.keyPath;
                                    if (sData.autoIncrement !== undefined) opts.autoIncrement = sData.autoIncrement;
                                    db.createObjectStore(sName, opts);
                                }
                            }
                        };
                        openReq.onsuccess = async () => {
                            const db = openReq.result;
                            const existingStores = Array.from(db.objectStoreNames);
                            const validStores = storeEntries.filter(([sName]) => existingStores.includes(sName)).map(([sName]) => sName);
                            if (validStores.length) {
                                const tx = db.transaction(validStores, 'readwrite');
                                for (const [sName, sData] of storeEntries) {
                                    if (!validStores.includes(sName)) continue;
                                    const store = tx.objectStore(sName);
                                    for (const rec of (sData.records || [])) {
                                        try {
                                            if (store.keyPath) {
                                                store.put(rec.value);
                                            } else {
                                                store.put(rec.value, rec.key);
                                            }
                                        } catch (_) {}
                                    }
                                }
                                tx.oncomplete = () => { db.close(); resolve(); };
                                tx.onerror = () => { db.close(); resolve(); };
                            } else {
                                db.close();
                                resolve();
                            }
                        };
                        openReq.onerror = () => resolve();
                    });
                    restoredCount++;
                } catch (_) {}
            }
            return restoredCount;
        }
    };

    // 7. Video Link Harvester (TikTok / Douyin / Shorts / Reels)
    function harvestVideoLinks() {
        const foundUrls = new Set();
        const hostname = (typeof window !== 'undefined' && window.location?.hostname)
            ? window.location.hostname.toLowerCase()
            : '';
        const currentUrl = (typeof window !== 'undefined' && window.location?.href)
            ? window.location.href
            : '';
        let platform = 'generic';

        // 1. Current URL check (if user is directly on a video/reel/shorts page)
        if (currentUrl.includes('/video/') && /\/video\/\d+/.test(currentUrl)) {
            foundUrls.add(currentUrl.split('?')[0]);
        } else if (currentUrl.includes('/shorts/')) {
            foundUrls.add(currentUrl.split('?')[0]);
        } else if (currentUrl.includes('/reel/')) {
            foundUrls.add(currentUrl.split('?')[0]);
        }

        if (hostname.includes('tiktok.com') || hostname.includes('douyin.com')) {
            platform = hostname.includes('douyin.com') ? 'douyin' : 'tiktok';

            // Strategy A: All anchor tags with /video/
            if (typeof document !== 'undefined') {
                document.querySelectorAll('a[href*="/video/"]').forEach(a => {
                    const href = a.href || a.getAttribute('href');
                    if (href && /\/video\/\d+/.test(href)) {
                        const full = href.startsWith('http') ? href : `https://www.tiktok.com${href.startsWith('/') ? '' : '/'}${href}`;
                        foundUrls.add(full.split('?')[0]);
                    }
                });

                // Strategy B: Full URLs in raw HTML
                const bodyHtml = document.body ? document.body.innerHTML : '';
                const fullUrlMatches = bodyHtml.matchAll(/https?:\/\/(?:www\.)?tiktok\.com\/@[a-zA-Z0-9_.-]+\/video\/\d+/g);
                for (const m of fullUrlMatches) {
                    foundUrls.add(m[0].split('?')[0]);
                }

                // Strategy C: Relative /@user/video/ID paths in raw HTML
                const relUrlMatches = bodyHtml.matchAll(/\/@[a-zA-Z0-9_.-]+\/video\/\d+/g);
                for (const m of relUrlMatches) {
                    foundUrls.add(`https://www.tiktok.com${m[0]}`);
                }

                // Strategy D: Player wrapper elements (id="xgwrapper-0-7106594312292453675")
                document.querySelectorAll('[id^="xgwrapper-"]').forEach(el => {
                    const idMatch = el.id.match(/\d{15,22}/);
                    if (idMatch) {
                        foundUrls.add(`https://www.tiktok.com/@tiktok/video/${idMatch[0]}`);
                    }
                });

                // Strategy E: Script hydration tags (__UNIVERSAL_DATA_FOR_REHYDRATION__, SIGI_STATE)
                document.querySelectorAll('script[type="application/json"], script#__UNIVERSAL_DATA_FOR_REHYDRATION__, script#SIGI_STATE').forEach(s => {
                    try {
                        const txt = s.textContent || '';
                        // Extract aweme_id / itemId / video_id
                        const idMatches = txt.matchAll(/"(?:video_id|itemId|item_id|aweme_id)":\s*"?(\d{15,22})"?/g);
                        for (const m of idMatches) {
                            foundUrls.add(`https://www.tiktok.com/@tiktok/video/${m[1]}`);
                        }
                    } catch (_) {}
                });
            }
        } else if (hostname.includes('youtube.com')) {
            platform = 'youtube_shorts';
            if (typeof document !== 'undefined') {
                document.querySelectorAll('a[href*="/shorts/"]').forEach(a => {
                    const href = a.href || a.getAttribute('href');
                    if (href && /\/shorts\/[a-zA-Z0-9_-]+/.test(href)) {
                        const full = href.startsWith('http') ? href : `https://www.youtube.com${href}`;
                        foundUrls.add(full.split('?')[0]);
                    }
                });
                const bodyHtml = document.body ? document.body.innerHTML : '';
                const shortsMatches = bodyHtml.matchAll(/\/shorts\/([a-zA-Z0-9_-]{8,15})/g);
                for (const m of shortsMatches) {
                    foundUrls.add(`https://www.youtube.com/shorts/${m[1]}`);
                }
            }
        } else if (hostname.includes('instagram.com') || hostname.includes('facebook.com')) {
            platform = 'reels';
            if (typeof document !== 'undefined') {
                document.querySelectorAll('a[href*="/reel/"], a[href*="/reels/"]').forEach(a => {
                    const href = a.href || a.getAttribute('href');
                    if (href) {
                        const full = href.startsWith('http') ? href : `https://www.instagram.com${href}`;
                        foundUrls.add(full.split('?')[0]);
                    }
                });
            }
        } else if (typeof document !== 'undefined') {
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href || a.getAttribute('href');
                if (href && (href.endsWith('.mp4') || /\/(video|shorts|reel)\//i.test(href))) {
                    foundUrls.add(href.split('?')[0]);
                }
            });
        }

        return {
            platform,
            hostname,
            count: foundUrls.size,
            urls: Array.from(foundUrls)
        };
    }

    // 8. Listener for UI Inquiries (Popup RPC)
    if (typeof chrome !== 'undefined' && chrome.runtime?.onMessage) {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            if (message.action === 'DUMP_TOKENS') {
                sendResponse({ ok: true, data: harvestWebStorage() });
                return true;
            }
            if (message.action === 'DUMP_INDEXEDDB') {
                IndexedDbEngine.dumpAll()
                    .then(data => sendResponse({ ok: true, data }))
                    .catch(err => sendResponse({ ok: false, error: err.message }));
                return true;
            }
            if (message.action === 'RESTORE_INDEXEDDB') {
                IndexedDbEngine.restoreAll(message.databases)
                    .then(count => sendResponse({ ok: true, count }))
                    .catch(err => sendResponse({ ok: false, error: err.message }));
                return true;
            }
            if (message.action === 'MEDIA_SEEK') {
                MediaController.seek(message.seconds, message.selector)
                    .then(res => sendResponse({ ok: true, res }))
                    .catch(err => sendResponse({ ok: false, error: err.message }));
                return true;
            }
            if (message.action === 'HARVEST_VIDEO_LINKS') {
                try {
                    const result = harvestVideoLinks();
                    sendResponse({ ok: true, data: result });
                } catch (err) {
                    sendResponse({ ok: false, error: err.message });
                }
                return true;
            }
            if (message.action === 'AUTO_UPLOAD_TIKTOK') {
                executeTikTokUpload(message)
                    .then(res => sendResponse({ ok: true, data: res }))
                    .catch(err => sendResponse({ ok: false, error: err.message }));
                return true;
            }
            if (message.action === 'GET_SNIFFED_APIS') {
                sendResponse({ ok: true, data: localSniffQueue });
                return true;
            }
            if (message.action === 'CLEAR_SNIFFED_APIS') {
                localSniffQueue.length = 0;
                sendResponse({ ok: true });
                return true;
            }
            return false;
        });
    }

    // 9. TikTok Auto-Uploader Engine (Hardened for 2026 TikTok Studio / Creator Center)
    async function executeTikTokUpload(options) {
        const {
            fileName,
            fileBase64,
            caption = '',
            autoPost = false,
            checkCopyright = true,
            scheduleMinutes = 0,
            findInputTimeoutMs = 12000
        } = options;

        function findDeepElement(selector, root = document) {
            let el = root.querySelector(selector);
            if (el) return el;
            // Check shadow roots
            const allNodes = root.querySelectorAll('*');
            for (const n of allNodes) {
                if (n.shadowRoot) {
                    const found = findDeepElement(selector, n.shadowRoot);
                    if (found) return found;
                }
            }
            // Check iframes
            const iframes = root.querySelectorAll('iframe');
            for (const f of iframes) {
                try {
                    const doc = f.contentDocument || f.contentWindow?.document;
                    if (doc) {
                        const found = findDeepElement(selector, doc);
                        if (found) return found;
                    }
                } catch (_) {}
            }
            return null;
        }

        function findFileInput() {
            return findDeepElement('input[type="file"][accept*="video"], input[type="file"]');
        }

        let fileInput = findFileInput();
        if (!fileInput) {
            const startTime = Date.now();
            while (!fileInput && Date.now() - startTime < findInputTimeoutMs) {
                await new Promise(r => setTimeout(r, 100));
                fileInput = findFileInput();
            }
        }

        if (!fileInput) {
            const curHref = (typeof window !== 'undefined' && window.location?.href || '').toLowerCase();
            if (curHref && !curHref.includes('/upload')) {
                if (typeof sessionStorage !== 'undefined') {
                    sessionStorage.setItem('relay_auto_running', 'true');
                }
                if (typeof window !== 'undefined' && window.location) {
                    window.location.href = 'https://www.tiktok.com/tiktokstudio/upload';
                }
                return { success: false, redirected: true };
            }
            throw new Error('Không tìm thấy khung tải video trên trang TikTok. Hãy đảm bảo bạn đang mở tiktok.com/tiktokstudio/upload');
        }

        // Convert base64 to File object
        const binary = atob(fileBase64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        const file = new File([bytes], fileName || 'reup_mutated.mp4', { type: 'video/mp4' });

        const dt = new DataTransfer();
        dt.items.add(file);

        // Assign to input
        fileInput.files = dt.files;
        fileInput.dispatchEvent(new Event('input', { bubbles: true }));
        fileInput.dispatchEvent(new Event('change', { bubbles: true }));

        // Also dispatch DragEvent drop on dropzone container
        const dropTarget = fileInput.closest('[class*="drop"], [class*="upload"], [class*="stage"]') || fileInput.parentElement;
        if (dropTarget) {
            try {
                dropTarget.dispatchEvent(new DragEvent('dragenter', { bubbles: true, cancelable: true, dataTransfer: dt }));
                dropTarget.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }));
                dropTarget.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
            } catch (_) {}
        }

        // Wait for caption editor to appear (polling up to 60s while video initializes)
        const CAPTION_SELECTORS = [
            'div[contenteditable="true"]',
            '.public-DraftEditor-content',
            'div[data-e2e="video-caption-editor"]',
            'div[data-placeholder]',
            'textarea[placeholder*="caption"]',
            'div.notranslate[contenteditable]',
            'div[role="textbox"]'
        ];

        let editorEl = null;
        const captionWaitStart = Date.now();
        while (!editorEl && Date.now() - captionWaitStart < 60000) {
            await new Promise(r => setTimeout(r, 800));
            for (const sel of CAPTION_SELECTORS) {
                const el = findDeepElement(sel);
                if (el && (el.offsetWidth > 0 || el.offsetHeight > 0 || el.getClientRects().length > 0)) {
                    editorEl = el;
                    break;
                }
            }
        }

        if (editorEl && caption) {
            editorEl.focus();
            try {
                // Fully select DraftJS contents and delete old text (e.g. auto-filled filename)
                const sel = (typeof window !== 'undefined' && window.getSelection) ? window.getSelection() : null;
                if (sel && typeof document.createRange === 'function') {
                    const range = document.createRange();
                    range.selectNodeContents(editorEl);
                    sel.removeAllRanges();
                    sel.addRange(range);
                }
                document.execCommand('delete', false, null);
                // Insert the clean caption once
                document.execCommand('insertText', false, caption);
            } catch (_) {
                if (editorEl.tagName === 'TEXTAREA') {
                    editorEl.value = caption;
                } else {
                    editorEl.innerText = caption;
                }
            }
            // Trigger change event without duplicate synthetic insertText inputEvent
            editorEl.dispatchEvent(new Event('change', { bubbles: true }));

            // Dispatch space key to trigger hashtag chip conversion
            try {
                editorEl.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', code: 'Space', keyCode: 32, which: 32, bubbles: true }));
                editorEl.dispatchEvent(new KeyboardEvent('keyup', { key: ' ', code: 'Space', keyCode: 32, which: 32, bubbles: true }));
            } catch (_) {}
        }

        // Handle Copyright Check Toggle if requested
        if (checkCopyright) {
            try {
                const copyrightToggles = [...document.querySelectorAll('input[type="checkbox"], [role="switch"]')];
                const crToggle = copyrightToggles.find(el => {
                    const parent = el.closest('div, label, tr');
                    return parent && /copyright|bản quyền/i.test(parent.textContent || '');
                });
                if (crToggle && !crToggle.checked && crToggle.getAttribute('aria-checked') !== 'true') {
                    crToggle.click();
                    // Wait and confirm the "Turn on" confirmation modal
                    await new Promise(r => setTimeout(r, 700));
                    const confirmButtons = [...document.querySelectorAll('button')];
                    const turnOnBtn = confirmButtons.find(b => 
                        /^(Turn on|Bật)$/i.test((b.textContent || '').trim()) && !b.disabled
                    );
                    if (turnOnBtn) turnOnBtn.click();
                }
            } catch (_) {}
        }

        // Handle Schedule Post if requested
        let scheduled = false;
        if (scheduleMinutes > 0) {
            try {
                const scheduleToggles = [...document.querySelectorAll('input[type="checkbox"], [role="switch"], [role="radio"]')];
                const schedToggle = scheduleToggles.find(el => {
                    const parent = el.closest('div, label, tr');
                    return parent && /schedule|lên lịch|hẹn giờ/i.test(parent.textContent || '');
                });
                if (schedToggle && !schedToggle.checked && schedToggle.getAttribute('aria-checked') !== 'true') {
                    schedToggle.click();
                    scheduled = true;
                }
            } catch (_) {}
        }

        // Wait for upload progress to finish (up to 120s)
        const uploadProgressStart = Date.now();
        while (Date.now() - uploadProgressStart < 120000) {
            const progressEl = findDeepElement('[class*="progress"], [role="progressbar"], [class*="upload-status"]');
            const progressText = progressEl ? (progressEl.textContent || '') : '';
            // If uploading percentage is still shown and not 100%
            const pctMatch = progressText.match(/(\d+)%/);
            if (pctMatch && parseInt(pctMatch[1], 10) < 100) {
                await new Promise(r => setTimeout(r, 1000));
                continue;
            }
            break;
        }

        function dismissExitDialog() {
            const dialogs = [...document.querySelectorAll('[role="dialog"], [class*="modal"]')];
            for (const d of dialogs) {
                if (/exit|rời khỏi/i.test(d.textContent || '')) {
                    const cancelBtn = [...d.querySelectorAll('button')].find(b => /cancel|hủy/i.test(b.textContent || ''));
                    if (cancelBtn) cancelBtn.click();
                }
            }
        }

        function findPostButton() {
            // 1. Direct data-e2e selector on TikTok Studio
            const e2eBtn = document.querySelector('button[data-e2e="post_video_button"], button[data-e2e="post_btn"]');
            if (e2eBtn && !e2eBtn.disabled && e2eBtn.getAttribute('aria-disabled') !== 'true') {
                return e2eBtn;
            }

            // 2. Strict matching on candidate buttons, strictly excluding sidebar/navigation/modals
            const allButtons = [...document.querySelectorAll('button')];
            return allButtons.find(b => {
                if (b.closest('nav, aside, [class*="sidebar"], [class*="menu"], header, [role="dialog"], [class*="modal"]')) {
                    return false;
                }
                if (b.disabled || b.getAttribute('aria-disabled') === 'true') return false;

                const text = (b.textContent || '').trim();
                // CRITICAL PENTEST FIX: NEVER match plural "Posts" (the sidebar navigation item!)
                if (/^posts$/i.test(text)) return false;
                if (/exit|rời|cancel|hủy|discard|bỏ qua|replace|thay thế/i.test(text)) return false;

                // Match exact button text Post / Đăng / Schedule / Lên lịch
                return /^(post|đăng|schedule|lên lịch)$/i.test(text);
            });
        }

        let postClicked = false;
        if (autoPost) {
            const postWaitStart = Date.now();
            while (Date.now() - postWaitStart < 60000) {
                await new Promise(r => setTimeout(r, 1000));
                dismissExitDialog();

                // Confirm Turn On copyright if still pending
                const turnOnBtn = [...document.querySelectorAll('button')].find(b => 
                    /^(Turn on|Bật)$/i.test((b.textContent || '').trim()) && !b.disabled
                );
                if (turnOnBtn) turnOnBtn.click();

                const postBtn = findPostButton();
                if (postBtn) {
                    postBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    await new Promise(r => setTimeout(r, 300));
                    postBtn.click();
                    postClicked = true;
                    break;
                }
            }
        }

        return {
            success: true,
            fileName: file.name,
            fileSize: file.size,
            captionFilled: !!(editorEl && caption),
            scheduled: scheduled,
            postClicked: postClicked
        };
    }

    // 10. In-Page Floating Auto-Upload HUD (Zero-Flake, Direct DOM Runner)
    function initUploadHud() {
        if (typeof window === 'undefined' || typeof document === 'undefined') return;
        if (window.top !== window) return; // STRICT: Only run HUD & uploader in top window, never iframes
        const href = (window.location?.href || '').toLowerCase();
        if (!href.includes('tiktok.com')) return;
        if (document.getElementById('relay-upload-hud')) return;

        const isUploadPage = href.includes('/creator-center/upload') || href.includes('/tiktokstudio/upload') || href.includes('/upload');

        const hud = document.createElement('div');
        hud.id = 'relay-upload-hud';
        hud.style.cssText = `
            position: fixed !important;
            bottom: 24px !important;
            right: 24px !important;
            z-index: 2147483647 !important;
            background: #0f172a !important;
            color: #f8fafc !important;
            border: 2px solid #38bdf8 !important;
            border-radius: 10px !important;
            padding: 14px 16px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 15px rgba(56,189,248,0.3) !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            width: 320px !important;
            box-sizing: border-box !important;
            line-height: 1.4 !important;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            pointer-events: auto !important;
        `;

        hud.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: bold; font-size: 13px; color: #38bdf8;">⚡ RelayKit Auto-Upload</span>
                <span id="relay-hud-badge" style="background: #334155; color: #94a3b8; font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold;">Checking...</span>
            </div>
            <div id="relay-hud-stats" style="font-size: 11px; color: #94a3b8; margin-bottom: 4px;">Đang kết nối Engine 127.0.0.1:8765...</div>
            <div id="relay-hud-next" style="font-size: 10.5px; color: #34d399; font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 8px;">--</div>
            <div style="display: flex; gap: 6px;">
                <button id="relay-hud-start" style="flex: 1; background: #059669; color: white; border: none; padding: 8px 10px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11.5px;">${isUploadPage ? '▶️ Bắt Đầu Auto Đăng' : '🚀 Mở Trang Upload & Auto Đăng'}</button>
                <button id="relay-hud-stop" style="flex: 1; background: #dc2626; color: white; border: none; padding: 8px 10px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11.5px; display: none;">⏹️ Dừng Lại</button>
            </div>
            <div id="relay-hud-log" style="margin-top: 8px; font-size: 10px; color: #94a3b8; font-family: monospace; max-height: 70px; overflow-y: auto; background: #090d16; padding: 6px; border-radius: 4px;">Sẵn sàng.</div>
        `;

        (document.body || document.documentElement).appendChild(hud);

        const badge = hud.querySelector('#relay-hud-badge');
        const stats = hud.querySelector('#relay-hud-stats');
        const nextEl = hud.querySelector('#relay-hud-next');
        const startBtn = hud.querySelector('#relay-hud-start');
        const stopBtn = hud.querySelector('#relay-hud-stop');
        const logEl = hud.querySelector('#relay-hud-log');

        function log(msg) {
            if (!logEl) return;
            const t = new Date().toLocaleTimeString('vi-VN');
            logEl.innerHTML += `<div>[${t}] ${msg}</div>`;
            logEl.scrollTop = logEl.scrollHeight;
        }

        async function syncStudioPostedVideos() {
            try {
                const rows = [...document.querySelectorAll('div[class*="table"], div[class*="row"], tr, div[class*="item"], div[class*="cell"]')];
                const titles = [];
                for (const r of rows) {
                    const titleEl = r.querySelector('[class*="title"], [class*="desc"], [class*="caption"], a, span');
                    if (titleEl) {
                        const text = (titleEl.textContent || '').trim();
                        if (text && text.length > 5 && !/views|likes|comments|actions|privacy|everyone/i.test(text)) {
                            titles.push(text);
                        }
                    }
                }
                if (titles.length > 0) {
                    await fetch('http://127.0.0.1:8765/api/sync-posted', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ titles })
                    });
                }
            } catch (_) {}
        }

        async function pollStatus() {
            try {
                // Auto-sync existing studio posts to prevent duplicate uploads
                syncStudioPostedVideos();
                const res = await fetch('http://127.0.0.1:8765/api/status');
                if (res.ok) {
                    const data = await res.json();
                    badge.textContent = '🟢 Online';
                    badge.style.background = '#065f46';
                    badge.style.color = '#34d399';
                    stats.textContent = `Hàng đợi: ${data.pending} chờ / ${data.uploaded} đã đăng`;
                    nextEl.textContent = data.next_file || 'Hết video!';
                    return data;
                }
            } catch (_) {}
            badge.textContent = '🔴 Offline';
            badge.style.background = '#991b1b';
            badge.style.color = '#fca5a5';
            stats.textContent = 'Chưa bật python upload-server';
            return null;
        }

        pollStatus();
        setInterval(pollStatus, 4000);

        let running = false;

        startBtn.addEventListener('click', async () => {
            const curHref = (window.location?.href || '').toLowerCase();
            const onUploadPage = curHref.includes('/tiktokstudio/upload') || curHref.includes('/creator-center/upload') || curHref.includes('/upload');
            if (!onUploadPage) {
                sessionStorage.setItem('relay_auto_running', 'true');
                const uploadBtn = [...document.querySelectorAll('button, a')].find(b => 
                    /^\s*\+?\s*Upload\s*$/i.test(b.textContent || '') &&
                    b.offsetWidth > 0 &&
                    !b.closest('#relay-upload-hud')
                );
                if (uploadBtn) {
                    uploadBtn.click();
                    log('Đang chuyển sang trang Upload...');
                    return;
                }
                window.location.href = 'https://www.tiktok.com/tiktokstudio/upload';
                return;
            }
            const status = await pollStatus();
            if (!status || status.pending === 0) {
                log('Hàng đợi trống hoặc server chưa bật.');
                sessionStorage.removeItem('relay_auto_running');
                return;
            }
            running = true;
            sessionStorage.setItem('relay_auto_running', 'true');
            startBtn.style.display = 'none';
            stopBtn.style.display = 'block';
            log(`🚀 Bắt đầu auto đăng ${status.pending} video...`);

            while (running) {
                log('Đang lấy video tiếp theo từ engine...');
                let item;
                try {
                    const res = await fetch('http://127.0.0.1:8765/api/next');
                    item = await res.json();
                } catch (e) {
                    log('Lỗi kết nối engine: ' + e.message);
                    break;
                }

                if (!item || !item.ok || !item.video_id) {
                    log('🎉 ĐÃ HOÀN TẤT TOÀN BỘ VIDEO!');
                    sessionStorage.removeItem('relay_auto_running');
                    break;
                }

                log(`Nạp video: ${item.file_name} (${(item.file_size/1048576).toFixed(1)} MB)...`);
                try {
                    const uploadRes = await executeTikTokUpload({
                        fileName: item.file_name,
                        fileBase64: item.file_base64,
                        caption: item.caption,
                        autoPost: true,
                        checkCopyright: true,
                        scheduleMinutes: item.schedule_minutes || 0
                    });

                    log(`✅ Đã đăng xong: ${item.file_name}`);
                    await fetch('http://127.0.0.1:8765/api/complete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ video_id: item.video_id, details: uploadRes })
                    });
                } catch (err) {
                    log(`⚠️ Lỗi upload (${err.message}). Bỏ qua video này để tránh đăng trùng!`);
                    await fetch('http://127.0.0.1:8765/api/fail', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ video_id: item.video_id, error: err.message })
                    });
                }

                await pollStatus();
                if (!running) break;

                log('⏳ Giãn cách an toàn 90s trước video tiếp theo...');
                for (let s = 90; s > 0; s--) {
                    if (!running) break;
                    if (s % 15 === 0 || s <= 5) log(`  ... Còn ${s}s`);
                    await new Promise(r => setTimeout(r, 1000));
                }

                if (!running) break;

                // Reset upload form for next video in queue
                const uploadAnotherBtn = [...document.querySelectorAll('button')].find(b => 
                    /upload another|tải lên video khác/i.test(b.textContent || '')
                );
                if (uploadAnotherBtn) {
                    uploadAnotherBtn.click();
                    await new Promise(r => setTimeout(r, 2500));
                } else {
                    sessionStorage.setItem('relay_auto_running', 'true');
                    window.location.href = 'https://www.tiktok.com/tiktokstudio/upload';
                    return;
                }
            }

            running = false;
            sessionStorage.removeItem('relay_auto_running');
            startBtn.style.display = 'block';
            stopBtn.style.display = 'none';
        });

        stopBtn.addEventListener('click', () => {
            running = false;
            sessionStorage.removeItem('relay_auto_running');
            log('⏹️ Đã nhận lệnh dừng.');
            startBtn.style.display = 'block';
            stopBtn.style.display = 'none';
        });

        // Auto-resume if coming from another page
        if (isUploadPage && sessionStorage.getItem('relay_auto_running') === 'true') {
            setTimeout(() => {
                if (startBtn && !running) startBtn.click();
            }, 1800);
        }
    }

    // 11. In-Page Zero-Cert API Sniffer Engine
    const localSniffQueue = [];

    function injectApiSniffer() {
        if (typeof window === 'undefined' || typeof document === 'undefined') return;
        if (window.__relay_api_sniffer_injected) return;
        window.__relay_api_sniffer_injected = true;

        if (typeof document.createElement === 'function') {
            const script = document.createElement('script');
            script.textContent = `
            (function() {
                if (window.__relay_sniffer_hooked) return;
                window.__relay_sniffer_hooked = true;

                const emitSniff = (data) => {
                    window.postMessage({ type: 'RELAY_SNIFF_EVENT', payload: data }, '*');
                };

                // 1. Hook window.fetch
                if (window.fetch) {
                    const origFetch = window.fetch;
                    window.fetch = async function(...args) {
                        const reqUrl = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
                        const options = args[1] || (typeof args[0] === 'object' ? args[0] : {});
                        const method = (options.method || 'GET').toUpperCase();
                        let body = '';
                        try {
                            if (options.body) {
                                body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
                            }
                        } catch(_) {}

                        try {
                            const response = await origFetch.apply(this, args);
                            const cloned = response.clone();
                            cloned.text().then(resText => {
                                emitSniff({
                                    url: reqUrl,
                                    method: method,
                                    headers: options.headers || {},
                                    body: body,
                                    response_status: response.status,
                                    response_body: resText ? resText.substring(0, 1024) : '',
                                    source: 'desktop'
                                });
                            }).catch(() => {});
                            return response;
                        } catch(err) {
                            emitSniff({
                                url: reqUrl,
                                method: method,
                                headers: options.headers || {},
                                body: body,
                                response_status: 0,
                                response_body: err.message,
                                source: 'desktop'
                            });
                            throw err;
                        }
                    };
                }

                // 2. Hook XMLHttpRequest
                if (window.XMLHttpRequest) {
                    const origOpen = XMLHttpRequest.prototype.open;
                    const origSend = XMLHttpRequest.prototype.send;
                    const origSetReqHeader = XMLHttpRequest.prototype.setRequestHeader;

                    XMLHttpRequest.prototype.open = function(method, url) {
                        this.__relay_sniff = { method: (method || 'GET').toUpperCase(), url: url, headers: {} };
                        return origOpen.apply(this, arguments);
                    };
                    XMLHttpRequest.prototype.setRequestHeader = function(k, v) {
                        if (this.__relay_sniff) this.__relay_sniff.headers[k] = v;
                        return origSetReqHeader.apply(this, arguments);
                    };
                    XMLHttpRequest.prototype.send = function(body) {
                        if (this.__relay_sniff) {
                            const sniffData = this.__relay_sniff;
                            let bodyStr = '';
                            try {
                                bodyStr = typeof body === 'string' ? body : JSON.stringify(body);
                            } catch(_) {}
                            sniffData.body = bodyStr;
                            this.addEventListener('load', function() {
                                emitSniff({
                                    url: sniffData.url,
                                    method: sniffData.method,
                                    headers: sniffData.headers,
                                    body: sniffData.body,
                                    response_status: this.status,
                                    response_body: (this.responseText || '').substring(0, 1024),
                                    source: 'desktop'
                                });
                            });
                        }
                        return origSend.apply(this, arguments);
                    };
                }
            })();
            `;
            try {
                (document.head || document.documentElement).appendChild(script);
                script.remove();
            } catch (_) {}
        }
    }

    if (typeof window !== 'undefined') {
        window.addEventListener('message', (e) => {
            if (e.data && e.data.type === 'RELAY_SNIFF_EVENT' && e.data.payload) {
                const item = e.data.payload;
                localSniffQueue.unshift(item);
                if (localSniffQueue.length > 100) localSniffQueue.pop();

                // 1. Forward via extension runtime (Bypasses Mixed Content / HTTPS host restrictions)
                try {
                    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
                        chrome.runtime.sendMessage({ action: 'SNIFFER_INGEST', payload: item }).catch(() => {});
                    }
                } catch (_) {}

                // 2. Fallback direct local fetch if allowed
                try {
                    fetch('http://127.0.0.1:8999/api/ingest', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(item)
                    }).catch(() => {});
                } catch(_) {}
            }
        });

        // Capture HTML form submissions before navigation/unload
        window.addEventListener('submit', (e) => {
            try {
                const form = e.target;
                if (!form || !(form instanceof HTMLFormElement)) return;
                if (form.hasAttribute('data-relay-cs-sniffed')) return;
                form.setAttribute('data-relay-cs-sniffed', String(Date.now()));
                setTimeout(() => {
                    try { form.removeAttribute('data-relay-cs-sniffed'); } catch (_) {}
                }, 2000);

                const rawAction = form.getAttribute('action') || '';
                let actionUrl = window.location.href;
                try {
                    actionUrl = new URL(rawAction || window.location.href, window.location.href).href;
                } catch (_) {}

                const method = (form.method || 'POST').toUpperCase();
                const entries = {};
                const urlParams = [];

                if (typeof FormData !== 'undefined') {
                    try {
                        const fd = new FormData(form);
                        for (const [k, v] of fd.entries()) {
                            if (typeof v === 'string') {
                                entries[k] = v;
                                urlParams.push(encodeURIComponent(k) + '=' + encodeURIComponent(v));
                            }
                        }
                    } catch (_) {}
                }

                const bodyStr = method === 'GET' ? '' : (urlParams.length > 0 ? urlParams.join('&') : JSON.stringify(entries));
                const finalUrl = method === 'GET' && urlParams.length > 0
                    ? (actionUrl.includes('?') ? `${actionUrl}&${urlParams.join('&')}` : `${actionUrl}?${urlParams.join('&')}`)
                    : actionUrl;

                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"], button:not([type])');
                const btnText = submitBtn ? (submitBtn.innerText || submitBtn.value || submitBtn.textContent || '').trim() : '';
                const triggerAction = btnText || ('Form Submit: ' + (form.id || form.name || 'HTML Form'));

                const payload = {
                    id: 'req_form_' + Math.random().toString(36).substring(2, 10),
                    url: finalUrl,
                    method: method,
                    headers: {
                        'content-type': method === 'POST' ? 'application/x-www-form-urlencoded' : 'application/json',
                        'referer': window.location.href
                    },
                    body: bodyStr,
                    response_status: 200,
                    response_body: JSON.stringify({ form_inputs: entries }),
                    trigger_action: triggerAction,
                    source: 'desktop',
                    tags: ['FORM', 'AUTH', 'API'],
                    is_important: true,
                    highlight_reason: `Form Submit: ${triggerAction}`,
                    timestamp: Date.now()
                };

                if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
                    chrome.runtime.sendMessage({ action: 'SNIFFER_INGEST', payload }).catch(() => {});
                }
            } catch (_) {}
        }, true);
    }

    if (typeof window !== 'undefined' && typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                initUploadHud();
                injectApiSniffer();
            });
        } else {
            setTimeout(() => {
                initUploadHud();
                injectApiSniffer();
            }, 1000);
        }
    }

    // Expose for unit tests
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = {
            waitFor,
            HumanActions,
            harvestWebStorage,
            MediaController,
            IndexedDbEngine,
            harvestVideoLinks,
            executeTikTokUpload,
            injectApiSniffer,
            localSniffQueue
        };
    }
})();
