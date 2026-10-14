/**
 * sniffer_inject.js - Runs in MAIN world (page context) at document_start
 * Hooks window.fetch and window.XMLHttpRequest without CSP restrictions.
 * Auto-correlates user clicks ("Xem hồ sơ", "Lưu thông tin") with requests,
 * and auto-inspects JSON response bodies to spotlight important data.
 */
(function() {
    'use strict';
    if (window.__relay_sniffer_hooked) return;
    window.__relay_sniffer_hooked = true;

    // 1. User Action Tracker (Click / Submit correlation)
    let lastUserAction = null;

    if (typeof window !== 'undefined') {
        window.addEventListener('click', (e) => {
            try {
                const target = e.target;
                if (!target) return;
                const clickable = target.closest('button, a, [role="button"], input[type="submit"], input[type="button"], tr, li, div[onclick]') || target;
                let text = (clickable.innerText || clickable.textContent || clickable.value || clickable.getAttribute('aria-label') || clickable.title || clickable.name || '').trim();
                if (text.length > 35) {
                    text = text.substring(0, 35).split('\n')[0].trim() + '...';
                }
                if (!text && clickable.id) text = '#' + clickable.id;
                if (!text && clickable.className) text = '.' + String(clickable.className).split(' ')[0];

                if (text) {
                    lastUserAction = {
                        text: text,
                        tag: (clickable.tagName || '').toLowerCase(),
                        timestamp: Date.now()
                    };
                }
            } catch (_) {}
        }, true);
    }

    function resolveUrl(url) {
        if (!url) return '';
        try {
            if (typeof window !== 'undefined' && window.location) {
                return new URL(url, window.location.href).href;
            }
        } catch (_) {}
        return String(url);
    }

    function isIgnored(url) {
        if (!url) return true;
        const u = String(url).toLowerCase();
        // Prevent infinite self-capture loop of Sniffer Hub & Extension
        if (u.includes('127.0.0.1:8999') || u.includes('localhost:8999') || u.includes(':8998') || u.includes(':8999')) return true;
        if (u.includes('/api/feed') || u.includes('/api/request/') || u.includes('/api/ingest')) return true;
        if (window.location && (window.location.port === '8999' || window.location.port === '8998')) return true;

        // Ignore static media/css/fonts assets
        if (/\.(png|jpe?g|gif|svg|webp|css|woff2?|ttf|eot|ico|map)(\?.*)?$/i.test(u)) return true;

        // Ignore telemetry & analytics noise (including Chrome background internal services)
        if (/(google-analytics\.com|doubleclick\.net|clarity\.ms|connect\.facebook\.net|\/telemetry|\/log_event|\/collect\?|adtrafficquality\.google\.com|play\.google\.com\/log|accounts\.google\.com\/rotatecookies|validationasyncservice|async\/bgasy)/i.test(u)) return true;

        return false;
    }

    function autoTag(url, method, body, triggerAction, responseText) {
        const tags = [];
        const u = String(url).toLowerCase();
        const m = String(method || 'GET').toUpperCase();
        const b = String(body || '').toLowerCase();

        if (triggerAction) {
            tags.push('ACTION');
        }
        if (/(auth|login|signin|register|signup|logout|token|session|oauth|passwd|password|taikhoan|matkhau|dangnhap)/i.test(u) ||
            /(username|password|pass|user|email|taikhoan|matkhau|dangnhap)/i.test(b)) {
            tags.push('AUTH');
        }
        if (/(user|profile|account|member|\bme\b|my-)/i.test(u)) {
            tags.push('USER');
        }
        if (/([?&/](id|uid|user_id|account_id|order_id|item_id)=\d+)|(\/[a-z_-]+\/\d{2,})/i.test(u)) {
            tags.push('IDOR');
        }
        if (/(\/api\/|\/v\d+\/|graphql|\/rpc|\/ajax\/)/i.test(u) || m === 'POST' || m === 'PUT' || m === 'DELETE') {
            tags.push('API');
        }
        return tags;
    }

    function inspectResponseJson(text) {
        if (!text || typeof text !== 'string') return null;
        const trimmed = text.trim();
        if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) return null;
        try {
            const data = JSON.parse(trimmed);
            const obj = Array.isArray(data) ? (data[0] || {}) : data;
            if (typeof obj !== 'object' || !obj) return null;

            const targets = ['username', 'user_id', 'id', 'name', 'email', 'phone', 'nickname', 'profile', 'role', 'status', 'token'];
            const found = {};
            for (const key of Object.keys(obj)) {
                const kLow = key.toLowerCase();
                if (targets.includes(kLow) || targets.some(t => kLow.includes(t))) {
                    const val = obj[key];
                    if (typeof val === 'string' || typeof val === 'number') {
                        found[key] = String(val).substring(0, 50);
                    }
                }
            }
            if (Object.keys(found).length > 0) {
                return found;
            }
        } catch (_) {}
        return null;
    }

    function emitSniff(data) {
        if (isIgnored(data.url)) return;
        data.tags = autoTag(data.url, data.method, data.body, data.trigger_action, data.response_body);
        const preview = inspectResponseJson(data.response_body);
        if (preview) {
            data.preview_summary = JSON.stringify(preview);
            if (!data.tags.includes('USER')) data.tags.push('USER');
            data.is_important = true;
        }
        try {
            window.postMessage({ type: 'RELAY_SNIFF_EVENT', payload: data }, '*');
        } catch (_) {}
    }

    // 2. Hook window.fetch
    if (window.fetch) {
        const origFetch = window.fetch;
        window.fetch = async function(...args) {
            const rawUrl = typeof args[0] === 'string' ? args[0] : (args[0]?.url || '');
            const reqUrl = resolveUrl(rawUrl);
            if (isIgnored(reqUrl)) {
                return origFetch.apply(this, args);
            }

            let triggerAction = null;
            if (lastUserAction && (Date.now() - lastUserAction.timestamp < 3500)) {
                triggerAction = lastUserAction.text;
            }

            const options = args[1] || (typeof args[0] === 'object' && !(args[0] instanceof Request) ? args[0] : {});
            const method = (options.method || (args[0] instanceof Request ? args[0].method : 'GET') || 'GET').toUpperCase();
            let body = '';
            try {
                if (options.body) {
                    body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
                }
            } catch (_) {}

            try {
                const response = await origFetch.apply(this, args);
                try {
                    const cloned = response.clone();
                    cloned.text().then(resText => {
                        emitSniff({
                            url: reqUrl,
                            method: method,
                            headers: options.headers || {},
                            body: body,
                            response_status: response.status,
                            response_body: resText ? resText.substring(0, 2048) : '',
                            trigger_action: triggerAction,
                            source: 'desktop',
                            timestamp: Date.now()
                        });
                    }).catch(() => {});
                } catch (_) {}
                return response;
            } catch (err) {
                emitSniff({
                    url: reqUrl,
                    method: method,
                    headers: options.headers || {},
                    body: body,
                    response_status: 0,
                    response_body: err.message,
                    trigger_action: triggerAction,
                    source: 'desktop',
                    timestamp: Date.now()
                });
                throw err;
            }
        };
    }

    // 3. Hook XMLHttpRequest
    if (window.XMLHttpRequest) {
        const origOpen = XMLHttpRequest.prototype.open;
        const origSend = XMLHttpRequest.prototype.send;
        const origSetReqHeader = XMLHttpRequest.prototype.setRequestHeader;

        XMLHttpRequest.prototype.open = function(method, url) {
            const fullUrl = resolveUrl(typeof url === 'string' ? url : String(url || ''));
            if (isIgnored(fullUrl)) {
                this.__relay_sniff = null;
                return origOpen.apply(this, arguments);
            }

            let triggerAction = null;
            if (lastUserAction && (Date.now() - lastUserAction.timestamp < 3500)) {
                triggerAction = lastUserAction.text;
            }

            this.__relay_sniff = {
                method: (method || 'GET').toUpperCase(),
                url: fullUrl,
                trigger_action: triggerAction,
                headers: {}
            };
            return origOpen.apply(this, arguments);
        };

        XMLHttpRequest.prototype.setRequestHeader = function(k, v) {
            if (this.__relay_sniff) {
                this.__relay_sniff.headers[k] = v;
            }
            return origSetReqHeader.apply(this, arguments);
        };

        XMLHttpRequest.prototype.send = function(body) {
            if (this.__relay_sniff) {
                const sniffData = this.__relay_sniff;
                let bodyStr = '';
                try {
                    bodyStr = typeof body === 'string' ? body : JSON.stringify(body);
                } catch (_) {}
                sniffData.body = bodyStr;

                this.addEventListener('load', function() {
                    emitSniff({
                        url: sniffData.url,
                        method: sniffData.method,
                        headers: sniffData.headers,
                        body: sniffData.body,
                        trigger_action: sniffData.trigger_action,
                        response_status: this.status,
                        response_body: (this.responseText || '').substring(0, 2048),
                        source: 'desktop',
                        timestamp: Date.now()
                    });
                });
            }
            return origSend.apply(this, arguments);
        };
    }

    // 4. Hook HTML Form Submissions (Traditional login/portal forms that do not use fetch/XHR)
    function captureFormSubmission(form, source) {
        if (!form || !(form instanceof HTMLFormElement)) return;
        try {
            if (form.hasAttribute('data-relay-sniffed')) return;
            form.setAttribute('data-relay-sniffed', String(Date.now()));
            setTimeout(() => {
                try { form.removeAttribute('data-relay-sniffed'); } catch (_) {}
            }, 2000);

            const rawAction = form.getAttribute('action') || '';
            const actionUrl = resolveUrl(rawAction || (typeof window !== 'undefined' ? window.location.href : ''));
            if (isIgnored(actionUrl)) return;

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
                        } else if (v && typeof v === 'object' && v.name) {
                            entries[k] = `[File: ${v.name}]`;
                        }
                    }
                } catch (_) {}
            }

            if (form.elements) {
                for (let i = 0; i < form.elements.length; i++) {
                    const el = form.elements[i];
                    if (!el.name || el.disabled || entries[el.name] !== undefined) continue;
                    if ((el.type === 'radio' || el.type === 'checkbox') && !el.checked) continue;
                    if (el.type === 'file') {
                        entries[el.name] = el.files && el.files[0] ? `[File: ${el.files[0].name}]` : '';
                    } else if (el.value !== undefined) {
                        entries[el.name] = el.value;
                        urlParams.push(encodeURIComponent(el.name) + '=' + encodeURIComponent(el.value));
                    }
                }
            }

            const bodyStr = method === 'GET' ? '' : (urlParams.length > 0 ? urlParams.join('&') : JSON.stringify(entries));
            const finalUrl = method === 'GET' && urlParams.length > 0
                ? (actionUrl.includes('?') ? `${actionUrl}&${urlParams.join('&')}` : `${actionUrl}?${urlParams.join('&')}`)
                : actionUrl;

            let triggerAction = null;
            if (lastUserAction && (Date.now() - lastUserAction.timestamp < 4000)) {
                triggerAction = lastUserAction.text;
            } else {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"], button:not([type])');
                if (submitBtn) {
                    triggerAction = (submitBtn.innerText || submitBtn.value || submitBtn.textContent || '').trim();
                }
                if (!triggerAction) triggerAction = 'Form Submit: ' + (form.id || form.name || 'HTML Form');
            }

            const formDataPayload = {
                id: 'req_form_' + Math.random().toString(36).substring(2, 10),
                url: finalUrl,
                method: method,
                headers: {
                    'content-type': method === 'POST' ? 'application/x-www-form-urlencoded' : 'application/json',
                    'referer': typeof window !== 'undefined' ? window.location.href : ''
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

            // 1. Post to extension content script
            emitSniff(formDataPayload);

            // 2. navigator.sendBeacon (immune to page unload/navigation)
            try {
                if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
                    const blob = new Blob([JSON.stringify(formDataPayload)], { type: 'application/json' });
                    navigator.sendBeacon('http://127.0.0.1:8999/api/ingest', blob);
                }
            } catch (_) {}

            // 3. Fetch with keepalive: true
            try {
                if (typeof fetch !== 'undefined') {
                    fetch('http://127.0.0.1:8999/api/ingest', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formDataPayload),
                        keepalive: true
                    }).catch(() => {});
                }
            } catch (_) {}
        } catch (_) {}
    }

    if (typeof window !== 'undefined') {
        window.addEventListener('submit', (e) => {
            if (e.target && (e.target.tagName === 'FORM' || e.target instanceof HTMLFormElement)) {
                captureFormSubmission(e.target, 'event_submit');
            }
        }, true);
    }

    if (typeof HTMLFormElement !== 'undefined') {
        const origFormSubmit = HTMLFormElement.prototype.submit;
        HTMLFormElement.prototype.submit = function() {
            try {
                captureFormSubmission(this, 'js_submit');
            } catch (_) {}
            return origFormSubmit.apply(this, arguments);
        };
    }

    // 5. Hook Document Page Load (for SSR apps like ASP.NET / PHP where pages load without AJAX)
    function recordPageDocument() {
        if (typeof window === 'undefined' || !window.location) return;
        const u = window.location.href;
        if (isIgnored(u) || u.startsWith('chrome') || u.startsWith('about:') || u.startsWith('edge:') || u.startsWith('devtools:')) return;
        if (window.__relay_page_recorded) return;
        window.__relay_page_recorded = true;

        const title = (typeof document !== 'undefined' ? (document.title || '') : '').trim();
        const pathPart = window.location.pathname.split('/').pop() || window.location.pathname;
        const actionName = title ? `Trang: "${title}"` : `Xem trang: ${pathPart}`;

        // 1. Headers & Cookies
        const headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'referer': typeof document !== 'undefined' ? (document.referrer || '') : ''
        };
        if (typeof document !== 'undefined' && document.cookie) {
            headers['cookie'] = document.cookie;
        }

        // 2. Hidden ASP.NET / CSRF state tokens
        const hiddenTokens = {};
        if (typeof document !== 'undefined') {
            document.querySelectorAll('input[type="hidden"]').forEach(inp => {
                if (inp.name && inp.value) {
                    hiddenTokens[inp.name] = inp.value;
                }
            });
        }

        // 3. Page data extraction (Grades, stats, student details)
        let pageDataSummary = '';
        if (typeof document !== 'undefined') {
            const summaryParts = [];
            if (title) summaryParts.push(`📌 Tiêu đề: ${title}`);

            const stats = Array.from(document.querySelectorAll('div, span, td, p'))
                .map(el => (el.innerText || '').trim())
                .filter(t => t.length > 3 && t.length < 50 && (t.includes('TBC') || t.includes('tích lũy') || t.includes('học lực') || t.includes('Mã SV') || t.includes('Sinh viên')))
                .slice(0, 6);
            if (stats.length > 0) {
                summaryParts.push('📊 Thống kê: ' + stats.join(' | '));
            }

            const tables = document.querySelectorAll('table');
            if (tables.length > 0) {
                const sampleRows = [];
                tables[0].querySelectorAll('tr').forEach((tr, idx) => {
                    if (idx < 10) {
                        const cells = Array.from(tr.querySelectorAll('th, td')).map(c => (c.innerText || '').trim().replace(/\s+/g, ' ')).filter(Boolean);
                        if (cells.length > 0) sampleRows.push(cells.join(' | '));
                    }
                });
                if (sampleRows.length > 0) {
                    summaryParts.push('📋 Bảng dữ liệu trích xuất:\n' + sampleRows.join('\n'));
                }
            }

            pageDataSummary = summaryParts.join('\n\n') || (document.body ? document.body.innerText.substring(0, 1500) : '');
        }

        const bodyStr = Object.keys(hiddenTokens).length > 0
            ? Object.entries(hiddenTokens).map(([k, v]) => `${k}=${encodeURIComponent(v.substring(0, 50)) + (v.length > 50 ? '...' : '')}`).join('&')
            : '';

        const tags = ['PAGE', 'USER', 'API'];
        if (/([?&/](id|uid|masv|user_id)=\d+)|(\/[a-z_-]+\/\d{2,})/i.test(u) || /ketquahoctap|diem|soyeu/i.test(u)) {
            tags.push('IDOR');
        }

        const pageData = {
            id: 'req_page_' + Math.random().toString(36).substring(2, 10),
            url: u,
            method: 'GET',
            headers: headers,
            body: bodyStr,
            response_status: 200,
            response_body: pageDataSummary,
            trigger_action: actionName,
            source: 'desktop',
            tags: tags,
            is_important: true,
            highlight_reason: actionName,
            timestamp: Date.now()
        };

        emitSniff(pageData);

        try {
            if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
                const blob = new Blob([JSON.stringify(pageData)], { type: 'application/json' });
                navigator.sendBeacon('http://127.0.0.1:8999/api/ingest', blob);
            }
        } catch (_) {}
    }

    if (typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', recordPageDocument);
        } else {
            recordPageDocument();
        }
    }

    // 5. WebSocket / SignalR frame capture
    if (window.WebSocket) {
        const OrigWS = window.WebSocket;
        window.WebSocket = function(url, protocols) {
            const ws = protocols ? new OrigWS(url, protocols) : new OrigWS(url);
            const wsUrl = String(url);
            if (isIgnored(wsUrl)) return ws;

            let frameIndex = 0;

            // Outgoing frames (send)
            const origSend = ws.send.bind(ws);
            ws.send = function(data) {
                try {
                    let body = '';
                    if (typeof data === 'string') body = data;
                    else if (data instanceof ArrayBuffer) body = '[ArrayBuffer ' + data.byteLength + 'B]';
                    else if (data instanceof Blob) body = '[Blob ' + data.size + 'B]';
                    emitSniff({
                        id: 'ws_send_' + Math.random().toString(36).substring(2, 9),
                        url: wsUrl,
                        method: 'WS_SEND',
                        headers: {},
                        body: body,
                        response_status: 101,
                        response_body: '',
                        source: 'desktop',
                        tags: ['API', 'WS'],
                        is_important: body.length > 10,
                        trigger_action: lastUserAction && (Date.now() - lastUserAction.timestamp < 3500) ? lastUserAction.text : null,
                        timestamp: Date.now()
                    });
                } catch (_) {}
                return origSend(data);
            };

            // Incoming frames (message)
            ws.addEventListener('message', (event) => {
                try {
                    const body = typeof event.data === 'string' ? event.data : '[Binary frame]';
                    // SignalR keepalive filter
                    if (body === '{}' || body === 'ping' || body.length < 3) return;
                    emitSniff({
                        id: 'ws_recv_' + (frameIndex++) + '_' + Math.random().toString(36).substring(2, 7),
                        url: wsUrl,
                        method: 'WS_RECV',
                        headers: {},
                        body: '',
                        response_status: 101,
                        response_body: body.substring(0, 4096),
                        source: 'desktop',
                        tags: ['API', 'WS'],
                        is_important: body.length > 20,
                        trigger_action: null,
                        timestamp: Date.now()
                    });
                } catch (_) {}
            });

            return ws;
        };
        // Copy static properties (CONNECTING, OPEN, etc.)
        Object.assign(window.WebSocket, OrigWS);
        window.WebSocket.prototype = OrigWS.prototype;
    }
})();
