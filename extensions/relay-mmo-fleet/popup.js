/**
 * popup.js - RelayKit MMO Fleet Operator UI Controller
 * 
 * Features:
 *   - Error boundary (prevents black screen / renderer crash)
 *   - Safe IndexedDB extraction (filters heavy media/messages, caps records, timeout circuit-breaker)
 *   - RFC 6265bis compliant cookie injection
 *   - Multi-domain SSO ecosystem support
 *   - Diagnostic result banner & storage clear
 */
'use strict';

// 0. Global Error Boundary to prevent black screen / popup renderer crash
window.addEventListener('error', (e) => {
    const banner = document.getElementById('injection-result');
    if (banner) {
        banner.className = 'result-banner result-error';
        banner.innerHTML = `<b>❌ Lỗi giao diện:</b> ${e.message}`;
        banner.style.display = 'block';
    }
});

window.addEventListener('unhandledrejection', (e) => {
    const banner = document.getElementById('injection-result');
    if (banner) {
        banner.className = 'result-banner result-error';
        banner.innerHTML = `<b>❌ Lỗi async:</b> ${e.reason?.message || e.reason}`;
        banner.style.display = 'block';
    }
});

let activeExportedBundle = null;

document.addEventListener('DOMContentLoaded', async () => {
    const $ = id => document.getElementById(id);

    // Tab Navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            $(btn.dataset.tab)?.classList.add('active');

            if (btn.dataset.tab === 'tab-sniffer') {
                checkSnifferHub();
                refreshSnifferList();
            }
        });
    });

    // Helpers: Tab & Status
    async function getActiveTab() {
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        return tabs[0] || null;
    }

    function setStatus(text, isBusy = false) {
        $('status-text').textContent = text;
        $('status-dot').className = 'status-dot' + (isBusy ? ' busy' : '');
    }

    function showResultBanner(type, htmlContent) {
        const banner = $('injection-result');
        if (!banner) return;
        banner.className = `result-banner result-${type}`;
        banner.innerHTML = htmlContent;
        banner.style.display = 'block';
    }

    function hideResultBanner() {
        const banner = $('injection-result');
        if (banner) banner.style.display = 'none';
    }

    // 1. Export Full Bundle (Safe IndexedDB + Multi-domain Cookies + Web Storage)
    $('btn-export-full').addEventListener('click', async () => {
        hideResultBanner();
        setStatus('Bundling session...', true);
        const tab = await getActiveTab();
        if (!tab || !tab.url) return setStatus('No active tab');

        chrome.runtime.sendMessage({ action: 'EXPORT_COOKIES', url: tab.url }, async (cookieRes) => {
            const cookies = cookieRes?.ok ? cookieRes.data.cookies : [];
            let storage = { localStorage: {}, sessionStorage: {} };
            let indexedDbDump = [];

            // Extract LocalStorage & SessionStorage
            try {
                const storageRes = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: () => {
                        const local = {};
                        const session = {};
                        try {
                            for (let i = 0; i < localStorage.length; i++) {
                                local[localStorage.key(i)] = localStorage.getItem(localStorage.key(i));
                            }
                        } catch (_) {}
                        try {
                            for (let i = 0; i < sessionStorage.length; i++) {
                                session[sessionStorage.key(i)] = sessionStorage.getItem(sessionStorage.key(i));
                            }
                        } catch (_) {}
                        return { local, session };
                    }
                });
                if (storageRes?.[0]?.result) {
                    storage.localStorage = storageRes[0].result.local;
                    storage.sessionStorage = storageRes[0].result.session;
                }
            } catch (_) {}

            // Extract IndexedDB (Auth/Session stores ONLY, with record caps & 2.5s circuit breaker)
            try {
                const idbRes = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: async () => {
                        if (typeof indexedDB === 'undefined' || !indexedDB.databases) return [];
                        const NON_AUTH_STORE_REGEX = /message|conversation|chat|sticker|emoji|attachment|media|cache|file|log|telemetry|offline_sync|history|download|thread|draft/i;
                        const MAX_RECORDS = 50;
                        const MAX_BYTES = 32768; // 32KB max per record
                        const DB_TIMEOUT = 2500;

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
                                            // Blacklist massive non-auth chat/attachment stores
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
                                                            if (cursor && items.length < MAX_RECORDS) {
                                                                try {
                                                                    const val = cursor.value;
                                                                    // Skip giant binary blobs
                                                                    if (val && typeof val === 'object') {
                                                                        if (val instanceof Blob && val.size > MAX_BYTES) {
                                                                            cursor.continue();
                                                                            return;
                                                                        }
                                                                        if (val instanceof ArrayBuffer && val.byteLength > MAX_BYTES) {
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

                                    const timeoutPromise = new Promise(r => setTimeout(() => r(null), DB_TIMEOUT));
                                    const dbData = await Promise.race([dbPromise, timeoutPromise]);
                                    if (dbData) dump.push(dbData);
                                } catch (_) {}
                            }
                            return dump;
                        } catch (_) {
                            return [];
                        }
                    }
                });
                indexedDbDump = idbRes?.[0]?.result || [];
            } catch (_) {}

            const bundle = {
                domain: new URL(tab.url).hostname,
                url: tab.url,
                exportedAt: new Date().toISOString(),
                cookies,
                localStorage: storage.localStorage,
                sessionStorage: storage.sessionStorage,
                indexedDB: indexedDbDump
            };

            activeExportedBundle = bundle;
            try {
                await chrome.storage.local.set({ lastExportedBundle: bundle });
            } catch (_) {}

            // Prevent DOM Renderer OOM crash: if bundle JSON is > 300KB, show clean preview
            const fullJson = JSON.stringify(bundle, null, 2);
            if (fullJson.length > 300000) {
                const preview = {
                    domain: bundle.domain,
                    url: bundle.url,
                    exportedAt: bundle.exportedAt,
                    cookiesCount: cookies.length,
                    localStorageKeys: Object.keys(storage.localStorage).length,
                    indexedDbDatabases: indexedDbDump.length,
                    _note: "Bundle kích thước lớn đã lưu an toàn trong bộ nhớ extension. Bấm nút Copy để lấy toàn bộ hoặc Inject trực tiếp!"
                };
                $('output-area').value = JSON.stringify(preview, null, 2);
            } else {
                $('output-area').value = fullJson;
            }

            $('output-meta').textContent = `${cookies.length} cookies, ${Object.keys(storage.localStorage).length} keys, ${indexedDbDump.length} DBs`;
            setStatus('Ready');
        });
    });

    // 2. Export Cookies Only (JSON)
    $('btn-export-cookies-json').addEventListener('click', async () => {
        hideResultBanner();
        setStatus('Exporting cookies...', true);
        const tab = await getActiveTab();
        if (!tab || !tab.url) return setStatus('No active tab');

        chrome.runtime.sendMessage({ action: 'EXPORT_COOKIES', url: tab.url }, response => {
            if (response?.ok) {
                activeExportedBundle = { cookies: response.data.cookies };
                $('output-area').value = JSON.stringify(response.data.cookies, null, 2);
                $('output-meta').textContent = `${response.data.total} cookies (${response.data.domain})`;
                setStatus('Ready');
            } else {
                $('output-area').value = `Error: ${response?.error || 'Failed'}`;
                setStatus('Error');
            }
        });
    });

    // 3. Scan Tokens & Storage
    $('btn-scan-tokens').addEventListener('click', async () => {
        hideResultBanner();
        setStatus('Scanning storage...', true);
        const tab = await getActiveTab();
        if (!tab || !tab.id) return setStatus('No active tab');

        try {
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => {
                    const local = {};
                    const session = {};
                    const keyCredentials = [];
                    try {
                        for (let i = 0; i < localStorage.length; i++) {
                            const k = localStorage.key(i);
                            const v = localStorage.getItem(k);
                            local[k] = v;
                            if (typeof v === 'string' && (
                                (v.startsWith('ey') && v.split('.').length === 3) ||
                                k.includes('token') || k.includes('zpw') || k.includes('uuid') || k.includes('key')
                            )) {
                                keyCredentials.push({ source: 'localStorage', key: k, value: v });
                            }
                        }
                    } catch (_) {}
                    try {
                        for (let i = 0; i < sessionStorage.length; i++) {
                            const k = sessionStorage.key(i);
                            const v = sessionStorage.getItem(k);
                            session[k] = v;
                            if (typeof v === 'string' && (
                                (v.startsWith('ey') && v.split('.').length === 3) ||
                                k.includes('token') || k.includes('zpw') || k.includes('uuid') || k.includes('key')
                            )) {
                                keyCredentials.push({ source: 'sessionStorage', key: k, value: v });
                            }
                        }
                    } catch (_) {}
                    return {
                        url: location.href,
                        totalKeys: Object.keys(local).length + Object.keys(session).length,
                        keyCredentials,
                        localStorage: local,
                        sessionStorage: session
                    };
                }
            });
            const data = results?.[0]?.result;
            if (data) {
                $('output-area').value = JSON.stringify(data, null, 2);
                $('output-meta').textContent = `${data.keyCredentials.length} credentials (${data.totalKeys} keys)`;
                setStatus('Ready');
            } else {
                throw new Error('No storage accessible on this page');
            }
        } catch (err) {
            $('output-area').value = `Error: ${err.message}`;
            setStatus('Error');
        }
    });

    // 4. Copy Output (Clipboard Safe)
    $('btn-copy').addEventListener('click', async () => {
        try {
            if (activeExportedBundle) {
                await navigator.clipboard.writeText(JSON.stringify(activeExportedBundle, null, 2));
            } else {
                await navigator.clipboard.writeText($('output-area').value);
            }
            $('btn-copy').textContent = 'Copied!';
            setTimeout(() => { $('btn-copy').textContent = 'Copy'; }, 1500);
        } catch (_) {
            $('output-area').select();
            document.execCommand('copy');
            $('btn-copy').textContent = 'Copied!';
            setTimeout(() => { $('btn-copy').textContent = 'Copy'; }, 1500);
        }
    });

    // Helper: Parse Netscape formatted cookies
    function parseNetscapeCookies(text) {
        const lines = text.split('\n');
        const cookies = [];
        for (const rawLine of lines) {
            const line = rawLine.trim();
            if (!line || line.startsWith('#')) continue;
            const parts = line.split('\t');
            if (parts.length >= 7) {
                cookies.push({
                    domain: parts[0],
                    hostOnly: parts[1] !== 'TRUE',
                    path: parts[2],
                    secure: parts[3] === 'TRUE',
                    expirationDate: parseInt(parts[4], 10) || 0,
                    name: parts[5],
                    value: parts[6]
                });
            }
        }
        return cookies;
    }

    // Helper: Resilient Session Parser
    function parseSessionInput(text) {
        text = text.trim();
        if (!text && activeExportedBundle) {
            return activeExportedBundle;
        }
        if (!text) throw new Error('Dữ liệu đang trống! Hãy dán JSON hoặc Netscape cookies vào ô.');

        // If preview was rendered and user hasn't typed anything else
        if (text.includes('_note') && activeExportedBundle) {
            return activeExportedBundle;
        }

        // Netscape format detection
        if (text.startsWith('# Netscape') || (text.includes('\t') && !text.startsWith('{') && !text.startsWith('['))) {
            const cookies = parseNetscapeCookies(text);
            if (cookies.length) return { cookies, localStorage: {}, sessionStorage: {}, indexedDB: [] };
        }

        // Auto-fix missing brackets or trailing commas from copy-paste
        let sanitized = text;
        if (!sanitized.startsWith('[') && sanitized.endsWith(']')) {
            sanitized = '[' + sanitized;
        }
        if (sanitized.startsWith('[') && !sanitized.endsWith(']')) {
            sanitized = sanitized + ']';
        }
        sanitized = sanitized.replace(/,\s*([\]}])/g, '$1');

        let parsed;
        try {
            parsed = JSON.parse(sanitized);
        } catch (_) {
            parsed = JSON.parse(text);
        }

        if (parsed && typeof parsed === 'object') {
            if (Array.isArray(parsed)) {
                return { cookies: parsed, localStorage: {}, sessionStorage: {}, indexedDB: [] };
            }
            if (parsed.cookies || parsed.localStorage || parsed.indexedDB) {
                return {
                    cookies: Array.isArray(parsed.cookies) ? parsed.cookies : [],
                    localStorage: parsed.localStorage || {},
                    sessionStorage: parsed.sessionStorage || {},
                    indexedDB: Array.isArray(parsed.indexedDB) ? parsed.indexedDB : []
                };
            }
            if (parsed.name && (parsed.value !== undefined)) {
                return { cookies: [parsed], localStorage: {}, sessionStorage: {}, indexedDB: [] };
            }
        }

        throw new Error('Dữ liệu JSON không nhận diện được cấu trúc cookie hoặc bundle session.');
    }

    // Helper: Inject Single Cookie with strict RFC 6265bis and Chrome MV3 rules
    async function injectSingleCookie(c, tabHostname, storeId) {
        if (!c || !c.name) return { ok: false, name: '(empty)', error: 'Missing cookie name' };

        const isHost = c.name.startsWith('__Host-');
        const isSecurePrefix = c.name.startsWith('__Secure-');

        // Clean domain: strip leading dot
        let cleanDomain = (c.domain || '').replace(/^\./, '');
        if (!cleanDomain) cleanDomain = tabHostname;

        const shouldBeSecure = Boolean(c.secure || isHost || isSecurePrefix);
        const protocol = shouldBeSecure ? 'https://' : 'http://';
        const path = isHost ? '/' : (c.path || '/');
        const cookieUrl = `${protocol}${cleanDomain}${path}`;

        const details = {
            url: cookieUrl,
            name: c.name,
            value: typeof c.value === 'string' ? c.value : String(c.value || ''),
            path: path,
            secure: shouldBeSecure,
            httpOnly: Boolean(c.httpOnly)
        };

        // RFC 6265bis: __Host- cookies MUST NOT have a domain attribute
        // Host-only cookies MUST NOT have a domain attribute
        if (!isHost && !c.hostOnly && cleanDomain) {
            details.domain = cleanDomain;
        }

        if (storeId) {
            details.storeId = storeId;
        }

        // Expiration date (in seconds, must be in future)
        if (typeof c.expirationDate === 'number' && !c.session && c.expirationDate > Math.floor(Date.now() / 1000)) {
            details.expirationDate = Math.round(c.expirationDate);
        }

        // SameSite configuration
        if (c.sameSite) {
            const ss = String(c.sameSite).toLowerCase();
            if (ss === 'no_restriction' || ss === 'none') {
                details.sameSite = 'no_restriction';
                details.secure = true;
            } else if (ss === 'lax') {
                details.sameSite = 'lax';
            } else if (ss === 'strict') {
                details.sameSite = 'strict';
            }
        }

        try {
            const res = await chrome.cookies.set(details);
            if (res) {
                return { ok: true, name: c.name };
            } else {
                const err = chrome.runtime?.lastError?.message || 'Rejected by browser policy';
                return { ok: false, name: c.name, error: err, details };
            }
        } catch (err) {
            return { ok: false, name: c.name, error: err.message, details };
        }
    }

    // 5. Inject Session into Current Tab (Cookies + LocalStorage + SessionStorage + IndexedDB)
    $('btn-inject-session').addEventListener('click', async () => {
        hideResultBanner();
        const rawText = $('output-area').value.trim();
        setStatus('Injecting session...', true);
        const tab = await getActiveTab();
        if (!tab || !tab.url) {
            setStatus('Error: No tab');
            showResultBanner('error', '❌ Không tìm thấy tab đang kích hoạt!');
            return;
        }

        let bundle;
        try {
            bundle = parseSessionInput(rawText);
        } catch (err) {
            setStatus('Lỗi định dạng');
            showResultBanner('error', `❌ ${err.message}`);
            return;
        }

        const tabHostname = new URL(tab.url).hostname;

        // Resolve storeId (Incognito vs Standard)
        let storeId;
        try {
            const stores = await chrome.cookies.getAllCookieStores();
            const currentStore = stores.find(s => s.tabIds.includes(tab.id));
            if (currentStore) storeId = currentStore.id;
        } catch (_) {}

        // A. Inject Cookies
        let cookieSuccess = 0;
        const failedCookies = [];
        for (const c of (bundle.cookies || [])) {
            const res = await injectSingleCookie(c, tabHostname, storeId);
            if (res.ok) {
                cookieSuccess++;
            } else {
                failedCookies.push(res);
            }
        }

        // B. Inject LocalStorage & SessionStorage
        let localCount = 0;
        let sessionCount = 0;
        try {
            const storageRes = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: (localData, sessionData) => {
                    let lCount = 0;
                    let sCount = 0;
                    if (localData && typeof localData === 'object') {
                        for (const [k, v] of Object.entries(localData)) {
                            localStorage.setItem(k, typeof v === 'string' ? v : JSON.stringify(v));
                            lCount++;
                        }
                    }
                    if (sessionData && typeof sessionData === 'object') {
                        for (const [k, v] of Object.entries(sessionData)) {
                            sessionStorage.setItem(k, typeof v === 'string' ? v : JSON.stringify(v));
                            sCount++;
                        }
                    }
                    return { lCount, sCount };
                },
                args: [bundle.localStorage, bundle.sessionStorage]
            });
            if (storageRes?.[0]?.result) {
                localCount = storageRes[0].result.lCount;
                sessionCount = storageRes[0].result.sCount;
            }
        } catch (_) {}

        // C. Inject IndexedDB (Deep session restore)
        let idbCount = 0;
        if (bundle.indexedDB && Array.isArray(bundle.indexedDB) && bundle.indexedDB.length) {
            try {
                const idbRes = await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: async (databases) => {
                        let restored = 0;
                        for (const dbItem of databases) {
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
                                restored++;
                            } catch (_) {}
                        }
                        return restored;
                    },
                    args: [bundle.indexedDB]
                });
                idbCount = idbRes?.[0]?.result || 0;
            } catch (_) {}
        }

        // Build Diagnostic Report
        const totalItemsInjected = cookieSuccess + localCount + idbCount;
        const totalCookies = (bundle.cookies || []).length;
        $('output-meta').textContent = `${cookieSuccess}/${totalCookies} cookies, ${localCount} keys, ${idbCount} DBs`;

        if (totalItemsInjected === 0 && failedCookies.length > 0) {
            setStatus('Lỗi nạp');
            const errList = failedCookies.slice(0, 3).map(f => `<li><code>${f.name}</code>: ${f.error}</li>`).join('');
            showResultBanner('error', `
                <b>❌ Nạp thất bại (0 item thành công):</b>
                <ul>${errList}</ul>
                <div style="margin-top:4px;">Tab chưa được reload để bạn kiểm tra lỗi.</div>
            `);
            return;
        }

        if (failedCookies.length > 0) {
            setStatus('Cảnh báo một phần');
            const errList = failedCookies.slice(0, 3).map(f => `<li><code>${f.name}</code>: ${f.error}</li>`).join('');
            showResultBanner('warning', `
                <b>⚠️ Nạp thành công ${cookieSuccess}/${totalCookies} cookies (${failedCookies.length} bị từ chối):</b>
                <ul>${errList}</ul>
                <div>Đã nạp ${localCount} khóa LocalStorage, ${idbCount} IndexedDB.</div>
                <button class="result-btn" id="btn-reload-now">🔄 Reload Tab Ngay</button>
            `);
        } else {
            setStatus('Thành công!');
            showResultBanner('success', `
                <b>✅ Nạp thành công toàn bộ:</b>
                <div>• Cookies: ${cookieSuccess}/${totalCookies}</div>
                <div>• LocalStorage: ${localCount} keys</div>
                <div>• IndexedDB: ${idbCount} databases</div>
                <button class="result-btn" id="btn-reload-now">🔄 Reload Tab Ngay (tự reload sau 3s...)</button>
            `);
        }

        // Hook Reload Button
        document.getElementById('btn-reload-now')?.addEventListener('click', () => {
            chrome.tabs.reload(tab.id);
        });

        // Auto-reload after 3.5s only if injection was successful
        setTimeout(() => {
            chrome.tabs.reload(tab.id);
        }, 3500);
    });

    // 6. Clear Session on Current Tab (Wipe Cookies + LocalStorage + SessionStorage + IndexedDB)
    $('btn-clear-session')?.addEventListener('click', async () => {
        hideResultBanner();
        const tab = await getActiveTab();
        if (!tab || !tab.url) return;

        setStatus('Clearing tab session...', true);
        const parsedUrl = new URL(tab.url);
        const hostname = parsedUrl.hostname;

        // 1. Remove cookies for this URL and domain
        let removedCookies = 0;
        try {
            const cookies = await chrome.cookies.getAll({ domain: hostname });
            for (const c of cookies) {
                const protocol = c.secure ? 'https://' : 'http://';
                const domainClean = c.domain.replace(/^\./, '');
                const url = `${protocol}${domainClean}${c.path}`;
                await chrome.cookies.remove({ url, name: c.name });
                removedCookies++;
            }
        } catch (_) {}

        // 2. Clear LocalStorage, SessionStorage & IndexedDB
        try {
            await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: async () => {
                    localStorage.clear();
                    sessionStorage.clear();
                    if (typeof indexedDB !== 'undefined' && indexedDB.databases) {
                        try {
                            const dbs = await indexedDB.databases();
                            for (const db of dbs) {
                                if (db.name) indexedDB.deleteDatabase(db.name);
                            }
                        } catch (_) {}
                    }
                }
            });
        } catch (_) {}

        setStatus('Session Cleared');
        showResultBanner('success', `🧹 Đã xóa sạch session trên tab ${hostname}! (${removedCookies} cookies đã xóa).`);
        setTimeout(() => {
            chrome.tabs.reload(tab.id);
        }, 1500);
    });

    // 7. Test Click (CDP vs Synthetic)
    $('btn-test-click').addEventListener('click', async () => {
        const selector = $('input-selector').value.trim();
        if (!selector) {
            $('cdp-log').textContent = 'Please enter a target selector.';
            return;
        }

        const tab = await getActiveTab();
        if (!tab || !tab.id) return;

        const useCdp = $('chk-use-cdp').checked;
        $('cdp-log').textContent = `Targeting: ${selector} (mode: ${useCdp ? 'CDP isTrusted' : 'Synthetic'})...`;
        setStatus('Executing click...', true);

        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: (sel, cdp) => {
                const el = document.querySelector(sel);
                if (!el) return { found: false };
                const rect = el.getBoundingClientRect();
                return {
                    found: true,
                    coords: { x: Math.round(rect.left + rect.width / 2), y: Math.round(rect.top + rect.height / 2) }
                };
            },
            args: [selector, useCdp]
        }, async results => {
            const res = results?.[0]?.result;
            if (!res?.found) {
                $('cdp-log').textContent = `Element not found: ${selector}`;
                setStatus('Ready');
                return;
            }

            if (useCdp) {
                chrome.runtime.sendMessage({ action: 'CDP_CLICK', tabId: tab.id, coords: res.coords }, cdpRes => {
                    if (cdpRes?.ok) {
                        $('cdp-log').textContent = `[CDP] Dispatched isTrusted click at (${res.coords.x}, ${res.coords.y}) in ${cdpRes.dwell}ms`;
                    } else {
                        $('cdp-log').textContent = `[CDP Error] ${cdpRes?.error}`;
                    }
                    setStatus('Ready');
                });
            } else {
                chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    func: sel => { document.querySelector(sel)?.click(); },
                    args: [selector]
                });
                $('cdp-log').textContent = `[DOM] Dispatched synthetic click on ${selector}`;
                setStatus('Ready');
            }
        });
    });

    // 8. Fast-Forward Video
    $('btn-seek-video').addEventListener('click', async () => {
        const tab = await getActiveTab();
        if (!tab || !tab.id) return;
        $('cdp-log').textContent = 'Seeking active video forward +60s...';
        chrome.tabs.sendMessage(tab.id, { action: 'MEDIA_SEEK', seconds: 60, selector: 'video' }, res => {
            if (res?.ok) {
                $('cdp-log').textContent = `Video seeked to ${Math.round(res.res.currentTime)}s / ${Math.round(res.res.duration)}s`;
            } else {
                $('cdp-log').textContent = `Media seek failed: ${res?.error || 'No video element'}`;
            }
        });
    });

    // 9. Task Runner Start / Stop
    $('btn-start-run').addEventListener('click', async () => {
        $('btn-start-run').disabled = true;
        $('btn-stop-run').disabled = false;
        $('runner-state').textContent = 'RUNNING';
        $('progress-bar').style.width = '50%';
        $('current-step').textContent = '1/2';
        await chrome.runtime.sendMessage({
            action: 'UPDATE_STATE',
            state: { status: 'running', currentStep: 1, totalSteps: 2 }
        });
    });

    $('btn-stop-run').addEventListener('click', async () => {
        $('btn-start-run').disabled = false;
        $('btn-stop-run').disabled = true;
        $('runner-state').textContent = 'STOPPED';
        $('progress-bar').style.width = '0%';
        await chrome.runtime.sendMessage({
            action: 'UPDATE_STATE',
            state: { status: 'stopped' }
        });
    });

    // 10. Video Reup Link Harvester
    let harvestedUrlsList = [];

    function showHarvestBanner(type, htmlContent) {
        const banner = $('harvest-result-banner');
        if (!banner) return;
        banner.className = `result-banner result-${type}`;
        banner.innerHTML = htmlContent;
        banner.style.display = 'block';
    }

    $('btn-harvest-links')?.addEventListener('click', async () => {
        const tab = await getActiveTab();
        if (!tab || !tab.id) {
            showHarvestBanner('error', 'Không tìm thấy tab trình duyệt đang hoạt động.');
            return;
        }

        setStatus('Đang quét link video...', true);
        $('btn-harvest-links').disabled = true;
        showHarvestBanner('info', '⏳ Đang quét video trên tab hiện tại...');

        async function queryTab(tabId) {
            try {
                return await new Promise((resolve, reject) => {
                    chrome.tabs.sendMessage(tabId, { action: 'HARVEST_VIDEO_LINKS' }, res => {
                        if (chrome.runtime.lastError) {
                            return reject(new Error(chrome.runtime.lastError.message));
                        }
                        resolve(res);
                    });
                });
            } catch (err) {
                // If content script was not injected yet (pre-existing tab), inject it on the fly!
                if (chrome.scripting) {
                    await chrome.scripting.executeScript({
                        target: { tabId },
                        files: ['content.js']
                    });
                    return await new Promise((resolve, reject) => {
                        chrome.tabs.sendMessage(tabId, { action: 'HARVEST_VIDEO_LINKS' }, res => {
                            if (chrome.runtime.lastError) {
                                return reject(new Error(chrome.runtime.lastError.message));
                            }
                            resolve(res);
                        });
                    });
                }
                throw err;
            }
        }

        try {
            const res = await queryTab(tab.id);
            $('btn-harvest-links').disabled = false;
            setStatus('Standby');

            if (!res || !res.ok) {
                showHarvestBanner('error', `Không thể quét link: ${res?.error || 'Trang không phản hồi'}. Hãy tải lại tab TikTok rồi thử lại.`);
                return;
            }

            const data = res.data;
            harvestedUrlsList = data.urls || [];
            $('harvest-meta').textContent = `${data.count} video (${data.platform})`;
            $('harvest-output-area').value = harvestedUrlsList.join('\n');

            if (harvestedUrlsList.length > 0) {
                $('btn-copy-links').disabled = false;
                $('btn-download-links').disabled = false;
                showHarvestBanner('success', `<b>✅ Thành công:</b> Đã gom được <b>${data.count}</b> link video từ ${data.hostname}! Bấm nút bên dưới để tải hoặc sao chép.`);
            } else {
                $('btn-copy-links').disabled = true;
                $('btn-download-links').disabled = true;
                showHarvestBanner('error', 'Chưa tìm thấy video nào. Hãy chắc chắn bạn đang ở trang TikTok (For You, Search, hoặc Profile) và cuộn chuột xuống 1 lần để video tải ra!');
            }
        } catch (err) {
            $('btn-harvest-links').disabled = false;
            setStatus('Standby');
            showHarvestBanner('error', `Lỗi: ${err.message}. Hãy tải lại trang TikTok (F5) rồi bấm quét lại.`);
        }
    });

    $('btn-copy-links')?.addEventListener('click', async () => {
        if (!harvestedUrlsList.length) return;
        try {
            await navigator.clipboard.writeText(harvestedUrlsList.join('\n'));
            const originalText = $('btn-copy-links').textContent;
            $('btn-copy-links').textContent = '✅ Đã chép!';
            setTimeout(() => { $('btn-copy-links').textContent = originalText; }, 2000);
        } catch (err) {
            $('harvest-output-area').select();
            document.execCommand('copy');
        }
    });

    $('btn-download-links')?.addEventListener('click', () => {
        if (!harvestedUrlsList.length) return;
        const blob = new Blob([harvestedUrlsList.join('\n')], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'links.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // 11. TikTok Auto-Upload Studio & Batch Engine Bridge
    const ENGINE_URL = 'http://127.0.0.1:8765';
    let isBatchRunning = false;
    let selectedUploadFile = null;

    function appendBatchLog(msg) {
        const area = $('batch-log-area');
        if (!area) return;
        const time = new Date().toLocaleTimeString('vi-VN');
        area.value += `[${time}] ${msg}\n`;
        area.scrollTop = area.scrollHeight;
    }

    function showUploadBanner(type, htmlContent) {
        const banner = $('upload-result-banner');
        if (!banner) return;
        banner.className = `result-banner result-${type}`;
        banner.innerHTML = htmlContent;
        banner.style.display = 'block';
    }

    // Subtab Switching
    $('btn-subtab-batch')?.addEventListener('click', () => {
        const bSection = $('section-upload-batch');
        const mSection = $('section-upload-manual');
        if (bSection) bSection.style.display = 'block';
        if (mSection) mSection.style.display = 'none';
        $('btn-subtab-batch').style.fontWeight = 'bold';
        $('btn-subtab-batch').style.background = '#334155';
        $('btn-subtab-manual').style.fontWeight = 'normal';
        $('btn-subtab-manual').style.background = 'transparent';
        checkEngineStatus();
    });

    $('btn-subtab-manual')?.addEventListener('click', () => {
        const bSection = $('section-upload-batch');
        const mSection = $('section-upload-manual');
        if (bSection) bSection.style.display = 'none';
        if (mSection) mSection.style.display = 'block';
        $('btn-subtab-manual').style.fontWeight = 'bold';
        $('btn-subtab-manual').style.background = '#334155';
        $('btn-subtab-batch').style.fontWeight = 'normal';
        $('btn-subtab-batch').style.background = 'transparent';
    });

    // Engine Status Checker
    async function checkEngineStatus() {
        const badge = $('engine-status-badge');
        const stats = $('engine-queue-stats');
        const nextEl = $('engine-next-file');
        if (!badge) return null;

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000);
            const res = await fetch(`${ENGINE_URL}/api/status`, { signal: controller.signal });
            clearTimeout(timeoutId);

            if (res.ok) {
                const data = await res.json();
                badge.textContent = '🟢 Đang kết nối';
                badge.style.background = '#065f46';
                badge.style.color = '#34d399';
                if (stats) stats.textContent = `${data.pending} chờ / ${data.uploaded} đã đăng (Tổng: ${data.total_videos})`;
                if (nextEl) nextEl.textContent = data.next_file || 'Hết video!';
                return data;
            }
        } catch (_) {}

        badge.textContent = '🔴 Chưa bật server';
        badge.style.background = '#991b1b';
        badge.style.color = '#fca5a5';
        if (stats) stats.textContent = 'Chưa bật server engine';
        if (nextEl) nextEl.textContent = '--';
        return null;
    }

    // Auto-check on load or tab switch
    document.querySelector('[data-tab="tab-upload"]')?.addEventListener('click', () => {
        checkEngineStatus();
    });

    // Helper: Find or open TikTok upload tab
    async function ensureTikTokUploadTab() {
        const tabs = await chrome.tabs.query({ url: '*://*.tiktok.com/*' });
        let targetTab = tabs.find(t => t.url && (t.url.includes('/creator-center/upload') || t.url.includes('/tiktokstudio/upload')));

        if (targetTab) {
            await chrome.tabs.update(targetTab.id, { active: true });
            return targetTab;
        }

        if (tabs.length > 0) {
            targetTab = tabs[0];
            await chrome.tabs.update(targetTab.id, { url: 'https://www.tiktok.com/creator-center/upload', active: true });
        } else {
            targetTab = await chrome.tabs.create({ url: 'https://www.tiktok.com/creator-center/upload' });
        }

        // Wait for tab to complete loading
        await new Promise((resolve) => {
            const check = () => {
                chrome.tabs.get(targetTab.id, (t) => {
                    if (t && t.status === 'complete') resolve();
                    else setTimeout(check, 800);
                });
            };
            setTimeout(check, 1000);
        });

        // Extra grace period for TikTok React scripts
        await new Promise(r => setTimeout(r, 2000));
        return targetTab;
    }

    // Helper: Inject content script safely
    async function injectContentScript(tabId) {
        if (chrome.scripting) {
            try {
                await chrome.scripting.executeScript({
                    target: { tabId },
                    files: ['content.js']
                });
            } catch (_) {}
        }
    }

    // 11.A Batch Upload Loop
    $('btn-start-batch-upload')?.addEventListener('click', async () => {
        const engineData = await checkEngineStatus();
        if (!engineData) {
            appendBatchLog('❌ Chưa phát hiện Python Local Engine!');
            appendBatchLog('💡 Mở terminal chạy lệnh: python scripts/video_reup.py upload-server');
            showUploadBanner('error', 'Chưa kết nối Engine! Hãy mở terminal và chạy: <code>python scripts/video_reup.py upload-server</code>');
            return;
        }

        if (engineData.pending === 0) {
            appendBatchLog('⚠️ Không còn video nào đang chờ trong mutated_videos/!');
            showUploadBanner('warning', 'Hàng đợi trống! Bạn hãy tải thêm video hoặc kiểm tra upload_ledger.json.');
            return;
        }

        isBatchRunning = true;
        $('btn-start-batch-upload').style.display = 'none';
        $('btn-stop-batch-upload').style.display = 'block';
        appendBatchLog(`🚀 BẮT ĐẦU AUTO PIPELINE: Còn ${engineData.pending} video cần đăng...`);

        while (isBatchRunning) {
            // 1. Fetch next video from engine
            appendBatchLog('⏳ Đang lấy video tiếp theo từ engine...');
            let nextItem;
            try {
                const res = await fetch(`${ENGINE_URL}/api/next`);
                nextItem = await res.json();
            } catch (err) {
                appendBatchLog(`❌ Lỗi kết nối engine: ${err.message}`);
                break;
            }

            if (!nextItem || !nextItem.ok || !nextItem.video_id) {
                appendBatchLog('🎉 HOÀN THÀNH: Đã đăng xong toàn bộ video trong mutated_videos/!');
                showUploadBanner('success', '🎉 <b>Xong Toàn Bộ:</b> Tất cả video trong mutated_videos/ đã được đăng lên kênh TikTok!');
                break;
            }

            appendBatchLog(`🎬 [Video] ${nextItem.file_name} (${(nextItem.file_size / 1048576).toFixed(1)} MB)`);
            appendBatchLog(`📝 [Caption] "${nextItem.caption}"`);

            // 2. Open or switch to TikTok tab
            let tab;
            try {
                tab = await ensureTikTokUploadTab();
                await injectContentScript(tab.id);
            } catch (err) {
                appendBatchLog(`❌ Lỗi mở tab TikTok: ${err.message}`);
                break;
            }

            // 3. Dispatch upload via content.js
            appendBatchLog('⚡ Đang nạp video vào trình duyệt TikTok & chờ tải lên...');
            const autoPost = $('batch-auto-post')?.checked ?? true;

            const uploadResult = await new Promise((resolve) => {
                chrome.tabs.sendMessage(tab.id, {
                    action: 'AUTO_UPLOAD_TIKTOK',
                    fileName: nextItem.file_name,
                    fileBase64: nextItem.file_base64,
                    caption: nextItem.caption,
                    autoPost: autoPost,
                    checkCopyright: true,
                    scheduleMinutes: nextItem.schedule_minutes || 0
                }, res => {
                    resolve(res);
                });
            });

            if (uploadResult && uploadResult.ok) {
                appendBatchLog(`✅ ĐĂNG THÀNH CÔNG: ${nextItem.file_name}`);
                // Report to engine
                try {
                    await fetch(`${ENGINE_URL}/api/complete`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ video_id: nextItem.video_id, details: uploadResult.data })
                    });
                } catch (_) {}
            } else {
                appendBatchLog(`❌ LỖI ĐĂNG: ${uploadResult?.error || 'Trang không phản hồi'}`);
                try {
                    await fetch(`${ENGINE_URL}/api/fail`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ video_id: nextItem.video_id, error: uploadResult?.error || 'Unknown' })
                    });
                } catch (_) {}
            }

            await checkEngineStatus();

            if (!isBatchRunning) break;

            // 4. Cooldown before next video (Anti-Spam Pentest Rule)
            const cooldownSec = parseInt($('batch-cooldown')?.value, 10) || 90;
            appendBatchLog(`⏳ Giãn cách an toàn ${cooldownSec}s trước video tiếp theo...`);
            for (let s = cooldownSec; s > 0; s--) {
                if (!isBatchRunning) break;
                if (s % 15 === 0 || s <= 5) {
                    appendBatchLog(`  ... Còn ${s}s`);
                }
                await new Promise(r => setTimeout(r, 1000));
            }
        }

        isBatchRunning = false;
        $('btn-start-batch-upload').style.display = 'block';
        $('btn-stop-batch-upload').style.display = 'none';
        setStatus('Standby');
    });

    $('btn-stop-batch-upload')?.addEventListener('click', () => {
        isBatchRunning = false;
        appendBatchLog('⏹️ Đã nhận lệnh dừng từ người dùng.');
        $('btn-start-batch-upload').style.display = 'block';
        $('btn-stop-batch-upload').style.display = 'none';
        setStatus('Standby');
    });

    // 11.B Manual Single Upload
    $('btn-browse-video')?.addEventListener('click', () => {
        $('upload-file-input')?.click();
    });

    $('upload-file-input')?.addEventListener('change', (e) => {
        const file = e.target.files?.[0];
        if (file) {
            selectedUploadFile = file;
            $('upload-filename-display').textContent = `${file.name} (${(file.size / 1048576).toFixed(1)} MB)`;
            $('upload-filename-display').style.color = '#34d399';
            showUploadBanner('info', `Đã chọn file: <b>${file.name}</b>. Điền caption rồi bấm nút Đăng bên dưới.`);
        }
    });

    $('btn-execute-upload')?.addEventListener('click', async () => {
        if (!selectedUploadFile) {
            showUploadBanner('error', 'Vui lòng chọn 1 file video (.mp4) trước khi bấm đăng.');
            return;
        }

        const tab = await ensureTikTokUploadTab();
        await injectContentScript(tab.id);

        const caption = $('upload-caption-text')?.value || '';
        const autoPost = $('chk-auto-click-post')?.checked ?? true;

        setStatus('Đang tải video lên TikTok...', true);
        $('btn-execute-upload').disabled = true;
        showUploadBanner('info', `⏳ Đang đọc file và nạp vào khung đăng TikTok (${(selectedUploadFile.size / 1048576).toFixed(1)} MB)...`);

        const reader = new FileReader();
        reader.onerror = () => {
            $('btn-execute-upload').disabled = false;
            setStatus('Standby');
            showUploadBanner('error', 'Lỗi đọc file video cục bộ.');
        };

        reader.onload = async () => {
            const base64Data = reader.result.split(',')[1];
            chrome.tabs.sendMessage(tab.id, {
                action: 'AUTO_UPLOAD_TIKTOK',
                fileName: selectedUploadFile.name,
                fileBase64: base64Data,
                caption: caption,
                autoPost: autoPost,
                checkCopyright: true,
                scheduleMinutes: 0
            }, res => {
                $('btn-execute-upload').disabled = false;
                setStatus('Standby');

                if (!res || !res.ok) {
                    showUploadBanner('error', `Lỗi đăng: ${res?.error || 'Trang upload không phản hồi'}. Vui lòng thử lại.`);
                    return;
                }

                const data = res.data;
                if (data.postClicked) {
                    showUploadBanner('success', `<b>🎉 THÀNH CÔNG RỰC RỠ:</b> Video <b>${data.fileName}</b> đã được tự động tải lên và bấm nút Đăng lên kênh!`);
                } else {
                    showUploadBanner('success', `<b>✅ Nạp Video Thành Công:</b> Video <b>${data.fileName}</b> và caption đã được điền sẵn vào trang. Bạn có thể xem lại và bấm Đăng!`);
                }
            });
        };

        reader.readAsDataURL(selectedUploadFile);
    });

    // 12. API Sniffer Controller
    const SNIFFER_HUB_URL = 'http://127.0.0.1:8999';
    let latestCapturedReqId = null;

    async function checkSnifferHub() {
        const ind = $('sniffer-hub-indicator');
        if (!ind) return;
        try {
            const res = await fetch(`${SNIFFER_HUB_URL}/api/status`);
            if (res.ok) {
                const data = await res.json();
                ind.textContent = `🟢 Hub Online (${data.total_captured})`;
                ind.style.background = '#065f46';
                ind.style.color = '#34d399';
                return data;
            }
        } catch (_) {}
        ind.textContent = '🟡 Hub Offline (Lưu Cục Bộ)';
        ind.style.background = '#854d0e';
        ind.style.color = '#fef08a';
        return null;
    }

    let currentSnifferTag = '';

    document.querySelectorAll('.sniffer-tag-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.sniffer-tag-btn').forEach(b => {
                b.style.background = '#334155';
                b.style.color = '#94a3b8';
                b.classList.remove('active');
            });
            btn.classList.add('active');
            btn.style.background = '#0284c7';
            btn.style.color = '#fff';
            currentSnifferTag = btn.dataset.tag || '';
            refreshSnifferList();
        });
    });

    $('btn-auto-tab')?.addEventListener('click', async () => {
        const tab = await getActiveTab();
        if (tab?.url) {
            try {
                const domain = new URL(tab.url).hostname.replace('www.', '');
                const input = $('sniffer-filter');
                if (input) {
                    input.value = domain;
                    refreshSnifferList();
                }
            } catch (_) {}
        }
    });

    async function refreshSnifferList() {
        const listEl = $('sniffer-list');
        const countEl = $('sniffer-count');
        if (!listEl) return;

        const filterVal = ($('sniffer-filter')?.value || '').trim().toLowerCase();
        let requests = [];

        // 1. Try getting from Sniffer Hub first
        try {
            const res = await fetch(`${SNIFFER_HUB_URL}/api/feed?filter=${encodeURIComponent(filterVal)}&tag=${encodeURIComponent(currentSnifferTag)}&auto_clean=1&limit=40`);
            if (res.ok) {
                const data = await res.json();
                requests = data.requests || [];
            }
        } catch (_) {}

        // 2. Query Background Service Worker feed (Memory buffer in extension)
        if (requests.length === 0 && typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
            try {
                const bgRes = await new Promise(r => {
                    chrome.runtime.sendMessage({ action: 'GET_SNIFFER_FEED' }, r);
                });
                if (bgRes?.ok && Array.isArray(bgRes.requests)) {
                    requests = bgRes.requests.filter(r => !filterVal || (r.url || '').toLowerCase().includes(filterVal));
                }
            } catch (_) {}
        }

        // 3. Fallback: If Hub & Background offline, query active tab local content script queue
        if (requests.length === 0) {
            try {
                const tab = await getActiveTab();
                if (tab?.id) {
                    const res = await new Promise(r => {
                        chrome.tabs.sendMessage(tab.id, { action: 'GET_SNIFFED_APIS' }, r);
                    });
                    if (res?.ok && Array.isArray(res.data)) {
                        requests = res.data.filter(r => !filterVal || (r.url || '').toLowerCase().includes(filterVal));
                    }
                }
            } catch (_) {}
        }

        if (currentSnifferTag) {
            requests = requests.filter(r => {
                if (currentSnifferTag === 'IMPORTANT') return r.is_important || (r.tags || []).includes('IMPORTANT') || Boolean(r.trigger_action);
                return (r.tags || []).includes(currentSnifferTag);
            });
        }

        if (countEl) countEl.textContent = requests.length;

        if (requests.length === 0) {
            listEl.innerHTML = '<div style="color: #64748b; padding: 12px; text-align: center;">Chưa có request nào khớp. Thao tác trên web để bắt API...</div>';
            return;
        }

        latestCapturedReqId = requests[0]?.id || null;

        listEl.innerHTML = requests.map(r => {
            const methodColor = r.method === 'POST' ? '#4ade80' : '#38bdf8';
            const statusColor = (r.response_status && r.response_status < 400) ? '#34d399' : '#f87171';
            const srcBadge = r.source === 'mobile' ? '<span style="background:#701a75;color:#f472b6;padding:1px 3px;border-radius:2px;font-size:8px;">MOB</span>' : '<span style="background:#1e3a8a;color:#93c5fd;padding:1px 3px;border-radius:2px;font-size:8px;">PC</span>';
            const actionBadge = r.trigger_action ? `<span style="background:#0284c7;color:#fff;padding:1px 4px;border-radius:2px;font-size:8px;font-weight:bold;">🖱️ ${r.trigger_action}</span>` : '';
            const previewText = r.preview_summary ? `<div style="font-size:8.5px;color:#34d399;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">✨ Khớp: ${r.preview_summary}</div>` : '';
            const borderStyle = r.is_important ? 'border-left: 2px solid #f59e0b; background: rgba(245,158,11,0.06);' : '';

            return `
            <div style="padding: 5px 6px; border-bottom: 1px solid #141c2e; display: flex; flex-direction: column; gap: 2px; ${borderStyle}">
                <div style="display: flex; gap: 4px; align-items: center; flex-wrap: wrap;">
                    ${srcBadge}
                    <span style="font-weight: bold; color: ${methodColor}; font-size: 9.5px;">${r.method}</span>
                    <span style="color: ${statusColor}; font-size: 9.5px;">${r.response_status || '--'}</span>
                    ${actionBadge}
                    <span style="color: #64748b; margin-left: auto; font-size: 8.5px;">${r.timestamp ? new Date(r.timestamp * 1000).toLocaleTimeString() : 'now'}</span>
                </div>
                <div style="color: #cbd5e1; word-break: break-all; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${r.url}">${r.url}</div>
                ${previewText}
            </div>
            `;
        }).join('');
    }

    $('btn-open-web-hub')?.addEventListener('click', () => {
        chrome.tabs.create({ url: 'http://127.0.0.1:8999' });
    });

    $('btn-clear-sniffer')?.addEventListener('click', async () => {
        try { await fetch(`${SNIFFER_HUB_URL}/api/clear`, { method: 'POST' }); } catch (_) {}
        try {
            const tab = await getActiveTab();
            if (tab?.id) chrome.tabs.sendMessage(tab.id, { action: 'CLEAR_SNIFFED_APIS' });
        } catch (_) {}
        refreshSnifferList();
    });

    $('sniffer-filter')?.addEventListener('input', refreshSnifferList);

    $('btn-copy-latest-py')?.addEventListener('click', async () => {
        if (!latestCapturedReqId) {
            alert('Chưa có request nào được bắt để tạo code Python!');
            return;
        }
        try {
            const res = await fetch(`${SNIFFER_HUB_URL}/api/codegen/${latestCapturedReqId}`);
            const data = await res.json();
            if (data?.python) {
                navigator.clipboard.writeText(data.python);
                alert('Đã copy mã Python Requests vào Clipboard!');
            }
        } catch (_) {
            alert('Không thể kết nối tới Sniffer Hub 8999 để sinh code.');
        }
    });

    $('btn-copy-latest-curl')?.addEventListener('click', async () => {
        if (!latestCapturedReqId) {
            alert('Chưa có request nào được bắt để tạo cURL!');
            return;
        }
        try {
            const res = await fetch(`${SNIFFER_HUB_URL}/api/codegen/${latestCapturedReqId}`);
            const data = await res.json();
            if (data?.curl) {
                navigator.clipboard.writeText(data.curl);
                alert('Đã copy lệnh cURL vào Clipboard!');
            }
        } catch (_) {
            alert('Không thể kết nối tới Sniffer Hub 8999 để sinh code.');
        }
    });

    // Auto-refresh sniffer tab
    setInterval(async () => {
        if ($('tab-sniffer')?.classList.contains('active')) {
            await checkSnifferHub();
            await refreshSnifferList();
        }
    }, 2000);
});
