/**
 * browser_media_bridge.js - Cross-Origin Iframe RPC & HTML5 Media Automation Engine
 * 
 * Reusable client-side driver for Playwright/Puppeteer evaluate() and Extension content scripts.
 * Provides:
 *   1. Html5MediaController: Autoplay policy bypass, resilient seeking, and playback state tracking.
 *   2. FrameRpcBridge: Bi-directional cross-origin postMessage RPC between parent page and embedded iframes.
 *   3. ResilientStepRunner: AbortController-driven step pipeline with bounded timeouts and graceful skip.
 */
(function (root, factory) {
    if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.BrowserMediaBridge = factory();
    }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    const RPC_REQ = 'FRAME_RPC_REQ';
    const RPC_RES = 'FRAME_RPC_RES';

    /**
     * Module 1: HTML5 Media Controller
     */
    const Html5MediaController = {
        muteForPlayback(video) {
            if (!video) return;
            video.defaultMuted = true;
            video.muted = true;
            video.volume = 0;
            video.playsInline = true;
        },

        clickPlayOverlay(scope = document) {
            const selectors = [
                'button.ytp-large-play-button',
                'button.ytmCuedOverlayPlayButton',
                '.ytp-cued-thumbnail-overlay button',
                'button[aria-label*="Play"]',
                '.vjs-big-play-button',
                '.play-button'
            ];
            for (const sel of selectors) {
                const btn = scope.querySelector(sel);
                if (btn && btn.getClientRects().length) {
                    btn.click();
                    return true;
                }
            }
            return false;
        },

        getVideoElement(selector = 'video', scope = document) {
            const list = [...scope.querySelectorAll(selector)].filter(v => v.isConnected);
            return list.find(v => v.getClientRects().length > 0) || list[0] || null;
        },

        getState(video) {
            if (typeof video === 'string') video = this.getVideoElement(video);
            return {
                ready: !!video && video.readyState >= 1,
                currentTime: video ? video.currentTime : 0,
                duration: video && Number.isFinite(video.duration) ? video.duration : 0,
                paused: video ? video.paused : true,
                ended: video ? video.ended : false,
                seeking: video ? video.seeking : false,
                error: video && video.error ? video.error.message : null
            };
        },

        async play(options = {}) {
            const { selector = 'video', timeoutMs = 15000, signal = null, scope = document } = options;
            const self = this;
            const deadline = Date.now() + timeoutMs;
            let attempts = 0;

            this.clickPlayOverlay(scope);

            while (Date.now() < deadline) {
                if (signal?.aborted) throw new DOMException('Playback aborted', 'AbortError');
                const video = self.getVideoElement(selector, scope);
                if (video) {
                    self.muteForPlayback(video);
                    if (!video.paused && video.readyState >= 1) {
                        return self.getState(video);
                    }
                    try {
                        attempts++;
                        await video.play();
                        if (!video.paused) return self.getState(video);
                    } catch (err) {
                        if (err.name === 'NotAllowedError') {
                            self.muteForPlayback(video);
                            self.clickPlayOverlay(scope);
                        }
                    }
                }
                await new Promise(r => setTimeout(r, 250));
            }
            throw new Error(`Timeout waiting for media playback after ${attempts} attempts`);
        },

        async seek(seconds, options = {}) {
            const { selector = 'video', tolerance = 2, timeoutMs = 20000, signal = null, scope = document } = options;
            const self = this;
            const deadline = Date.now() + timeoutMs;

            if (!Number.isFinite(seconds) || seconds < 0) {
                throw new Error(`Invalid seek target seconds: ${seconds}`);
            }

            let video = self.getVideoElement(selector, scope);
            if (!video) throw new Error(`Video element not found for selector: ${selector}`);

            self.muteForPlayback(video);
            video.currentTime = seconds;

            while (Date.now() < deadline) {
                if (signal?.aborted) throw new DOMException('Seek aborted', 'AbortError');

                // Handle dynamic element swap during player transitions
                const current = self.getVideoElement(selector, scope);
                if (current && current !== video) {
                    video = current;
                    self.muteForPlayback(video);
                    video.currentTime = seconds;
                }

                if (!video.seeking && Math.abs(video.currentTime - seconds) <= tolerance) {
                    return self.getState(video);
                }

                if (!video.seeking && Math.abs(video.currentTime - seconds) > tolerance) {
                    video.currentTime = seconds;
                }

                await new Promise(r => setTimeout(r, 200));
            }
            throw new Error(`Timeout seeking video to ${seconds}s (current: ${video?.currentTime}s)`);
        }
    };

    /**
     * Module 2: Frame RPC Bridge (Cross-Origin postMessage protocol)
     */
    const FrameRpcBridge = {
        sessions: new Map(),

        send(targetWindow, targetOrigin, message, options = {}) {
            const { timeoutMs = 15000, signal = null, session = 'default' } = options;
            const requestId = 'req_' + Math.random().toString(36).slice(2, 10) + '_' + Date.now();

            return new Promise((resolve, reject) => {
                let timer = null;

                function cleanup() {
                    if (timer) clearTimeout(timer);
                    window.removeEventListener('message', onMessage);
                    signal?.removeEventListener('abort', onAbort);
                }

                function onAbort() {
                    cleanup();
                    reject(new DOMException('Frame RPC request aborted', 'AbortError'));
                }

                function onMessage(event) {
                    if (targetOrigin !== '*' && event.origin !== targetOrigin) return;
                    const data = event.data;
                    if (!data || data.type !== RPC_RES || data.requestId !== requestId) return;
                    cleanup();
                    if (data.ok) {
                        resolve(data.result);
                    } else {
                        reject(new Error(data.error || 'Frame RPC request failed'));
                    }
                }

                if (signal?.aborted) return onAbort();
                signal?.addEventListener('abort', onAbort, { once: true });

                window.addEventListener('message', onMessage);

                timer = setTimeout(() => {
                    cleanup();
                    reject(new Error(`Timeout waiting for Frame RPC response (${options.command || 'unknown'})`));
                }, timeoutMs);

                const payload = {
                    type: RPC_REQ,
                    session,
                    requestId,
                    command: options.command,
                    data: message
                };

                try {
                    targetWindow.postMessage(payload, targetOrigin);
                } catch (err) {
                    cleanup();
                    reject(err);
                }
            });
        },

        attachFrameReceiver(allowedOrigins, commandHandlers) {
            function onReceive(event) {
                if (allowedOrigins !== '*' && Array.isArray(allowedOrigins) && !allowedOrigins.includes(event.origin)) {
                    return;
                }
                const data = event.data;
                if (!data || data.type !== RPC_REQ || typeof data.command !== 'string') return;

                const { session, requestId, command } = data;
                const handler = commandHandlers[command];

                const reply = (ok, result, error) => {
                    if (!event.source || !event.source.postMessage) return;
                    event.source.postMessage({
                        type: RPC_RES,
                        session,
                        requestId,
                        ok,
                        result,
                        error: error ? (error.message || String(error)) : null
                    }, event.origin === 'null' ? '*' : event.origin);
                };

                if (typeof handler !== 'function') {
                    reply(false, null, `Unknown command: ${command}`);
                    return;
                }

                Promise.resolve()
                    .then(() => handler(data.data, session))
                    .then(res => reply(true, res, null))
                    .catch(err => reply(false, null, err));
            }

            window.addEventListener('message', onReceive);
            return () => window.removeEventListener('message', onReceive);
        }
    };

    /**
     * Module 3: Resilient Step Runner
     */
    class ResilientStepRunner {
        constructor() {
            this.activeController = null;
        }

        async withStepTimeout(stepFn, timeoutMs = 15000, options = {}) {
            const { isCritical = false, stepLabel = 'unnamed-step', onSkip = null } = options;
            const controller = new AbortController();
            this.activeController = controller;

            let timer = null;
            let timedOut = false;

            const timeoutPromise = new Promise((_, reject) => {
                timer = setTimeout(() => {
                    timedOut = true;
                    controller.abort();
                    reject(new Error(`Step [${stepLabel}] timed out after ${timeoutMs}ms`));
                }, timeoutMs);
            });

            try {
                const result = await Promise.race([
                    stepFn(controller.signal),
                    timeoutPromise
                ]);
                return { success: true, result, skipped: false };
            } catch (error) {
                if (timedOut && !isCritical) {
                    console.warn(`[BrowserMediaBridge] Non-critical step [${stepLabel}] timed out; skipping gracefully.`);
                    if (typeof onSkip === 'function') {
                        try { onSkip(error); } catch (_) {}
                    }
                    return { success: false, skipped: true, reason: error.message };
                }
                throw error;
            } finally {
                if (timer) clearTimeout(timer);
                if (this.activeController === controller) {
                    this.activeController = null;
                }
            }
        }

        cancel() {
            if (this.activeController) {
                this.activeController.abort();
                this.activeController = null;
            }
        }
    }

    return {
        Html5MediaController,
        FrameRpcBridge,
        ResilientStepRunner,
        createRunner: () => new ResilientStepRunner()
    };
});
