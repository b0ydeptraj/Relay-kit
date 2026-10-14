import json
import threading
import urllib.parse
import urllib.request
import webbrowser
import customtkinter as ctk

from tools.api_interceptor.codegen import generate_curl_command, generate_python_script
from tools.api_interceptor.models import CapturedRequest
from tools.api_interceptor.sniffer_hub import run_sniffer_hub


class SnifferView(ctk.CTkFrame):
    """Modern Dark-Mode API Sniffer & Inspector View."""

    def __init__(self, master, hub_port: int = 8999, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.hub_port = hub_port
        self.hub_server = None
        self.hub_thread = None
        self.active_request_id = None
        self.requests_cache = []
        self.is_polling = True

        self._build_ui()
        self._auto_start_hub()
        self._poll_feed()

    def _build_ui(self):
        # Top Control Banner
        self.banner = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=10, border_width=1, border_color="#1e293b")
        self.banner.pack(fill="x", padx=16, pady=(16, 10))

        self.title_label = ctk.CTkLabel(
            self.banner, text="📡 UNIFIED API SNIFFER & REVERSE HUB",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#38bdf8"
        )
        self.title_label.pack(side="left", padx=16, pady=10)

        self.status_badge = ctk.CTkLabel(
            self.banner, text="🟢 Hub: 127.0.0.1:8999",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#34d399",
            fg_color="#065f46", corner_radius=6, padx=8, pady=2
        )
        self.status_badge.pack(side="left", padx=6)

        self.btn_web = ctk.CTkButton(
            self.banner, text="🌐 Mở Web Hub", width=100, height=28,
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#1e293b", hover_color="#334155",
            command=lambda: webbrowser.open(f"http://127.0.0.1:{self.hub_port}")
        )
        self.btn_web.pack(side="right", padx=10)

        self.btn_clear = ctk.CTkButton(
            self.banner, text="🧹 Xóa Bộ Nhớ", width=90, height=28,
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#dc2626", hover_color="#b91c1c",
            command=self._clear_feed
        )
        self.btn_clear.pack(side="right", padx=6)

        # Split Content Pane (Left: Request List, Right: Request Inspector)
        self.split_pane = ctk.CTkFrame(self, fg_color="transparent")
        self.split_pane.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Left Column: Request List & Search
        self.left_col = ctk.CTkFrame(self.split_pane, width=380, fg_color="#0d1322", corner_radius=10, border_width=1, border_color="#1e293b")
        self.left_col.pack(side="left", fill="y", padx=(0, 8))
        self.left_col.pack_propagate(False)

        self.search_entry = ctk.CTkEntry(
            self.left_col, placeholder_text="🔍 Lọc URL (ví dụ: upload, item, tiktok)...",
            height=32, fg_color="#1e293b", border_color="#334155", font=ctk.CTkFont(size=11)
        )
        self.search_entry.pack(fill="x", padx=10, pady=10)

        self.list_scroll = ctk.CTkScrollableFrame(self.left_col, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True, padx=4, pady=(0, 6))

        # Right Column: Inspector
        self.right_col = ctk.CTkFrame(self.split_pane, fg_color="#0d1322", corner_radius=10, border_width=1, border_color="#1e293b")
        self.right_col.pack(side="right", fill="both", expand=True)

        self.inspect_header = ctk.CTkFrame(self.right_col, fg_color="#090d16", corner_radius=8, height=44)
        self.inspect_header.pack(fill="x", padx=12, pady=12)

        self.req_summary_label = ctk.CTkLabel(
            self.inspect_header, text="Chọn 1 request bên trái để kiểm tra & trích xuất",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#f8fafc", anchor="w"
        )
        self.req_summary_label.pack(side="left", padx=12, fill="x", expand=True)

        self.btn_copy_py = ctk.CTkButton(
            self.inspect_header, text="📋 Copy Python Requests", width=150, height=28,
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#0284c7", hover_color="#0369a1",
            command=self._copy_python
        )
        self.btn_copy_py.pack(side="right", padx=6)

        self.btn_copy_curl = ctk.CTkButton(
            self.inspect_header, text="📋 Copy cURL", width=100, height=28,
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#334155", hover_color="#475569",
            command=self._copy_curl
        )
        self.btn_copy_curl.pack(side="right", padx=6)

        # Tabview Inspector
        self.tabs = ctk.CTkTabview(self.right_col, fg_color="#090d16", segmented_button_selected_color="#0284c7")
        self.tabs.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.tab_tokens = self.tabs.add("🔑 Tokens & Signatures")
        self.tab_headers = self.tabs.add("📋 Headers")
        self.tab_payload = self.tabs.add("📦 Payload (Body)")
        self.tab_resp = self.tabs.add("📥 Response Preview")

        self.txt_tokens = ctk.CTkTextbox(self.tab_tokens, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#050811")
        self.txt_tokens.pack(fill="both", expand=True, padx=6, pady=6)

        self.txt_headers = ctk.CTkTextbox(self.tab_headers, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#050811")
        self.txt_headers.pack(fill="both", expand=True, padx=6, pady=6)

        self.txt_payload = ctk.CTkTextbox(self.tab_payload, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#050811")
        self.txt_payload.pack(fill="both", expand=True, padx=6, pady=6)

        self.txt_resp = ctk.CTkTextbox(self.tab_resp, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#050811")
        self.txt_resp.pack(fill="both", expand=True, padx=6, pady=6)

    def _auto_start_hub(self):
        """Ensure Sniffer Hub server is running in background thread."""
        try:
            req = urllib.request.urlopen(f"http://127.0.0.1:{self.hub_port}/api/status", timeout=0.8)
            if req.status == 200:
                return  # Already running
        except Exception:
            pass

        def run():
            try:
                self.hub_server = run_sniffer_hub(port=self.hub_port, host="127.0.0.1")
                self.hub_server.serve_forever()
            except Exception:
                pass

        self.hub_thread = threading.Thread(target=run, daemon=True)
        self.hub_thread.start()

    def _poll_feed(self):
        """Poll captured requests from local hub without blocking GUI."""
        if not self.is_polling:
            return

        def fetch():
            filter_kw = ""
            try:
                filter_kw = self.search_entry.get().strip()
            except Exception:
                pass
            url = f"http://127.0.0.1:{self.hub_port}/api/feed?filter={urllib.parse.quote(filter_kw)}&limit=40"
            try:
                with urllib.request.urlopen(url, timeout=0.8) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode())
                        return data.get("requests", [])
            except Exception:
                return None

        def callback(reqs):
            if reqs is not None:
                # Update list if changed
                if [r["id"] for r in reqs] != [r["id"] for r in self.requests_cache]:
                    self.requests_cache = reqs
                    self._render_list()

            self.after(1200, self._poll_feed)

        def thread_target():
            res = fetch()
            self.after(0, lambda: callback(res))

        threading.Thread(target=thread_target, daemon=True).start()

    def _render_list(self):
        for widget in self.list_scroll.winfo_children():
            widget.destroy()

        if not self.requests_cache:
            lbl = ctk.CTkLabel(self.list_scroll, text="Chưa có request nào.\nHãy thao tác trên web/app...", text_color="#64748b", font=ctk.CTkFont(size=11))
            lbl.pack(pady=40)
            return

        for req in self.requests_cache:
            is_active = (req["id"] == self.active_request_id)
            bg_color = "#1e293b" if is_active else "#141c2e"
            item_frame = ctk.CTkFrame(self.list_scroll, fg_color=bg_color, corner_radius=6)
            item_frame.pack(fill="x", pady=2, padx=2)

            meta_row = ctk.CTkFrame(item_frame, fg_color="transparent")
            meta_row.pack(fill="x", padx=6, pady=(4, 2))

            src_color = "#93c5fd" if req["source"] == "desktop" else "#f472b6"
            src_bg = "#1e3a8a" if req["source"] == "desktop" else "#701a75"
            src_badge = ctk.CTkLabel(
                meta_row, text=req["source"].upper()[:3],
                font=ctk.CTkFont(size=9, weight="bold"), text_color=src_color,
                fg_color=src_bg, corner_radius=3, padx=4, pady=1
            )
            src_badge.pack(side="left")

            method_color = "#4ade80" if req["method"] == "POST" else "#38bdf8"
            m_label = ctk.CTkLabel(
                meta_row, text=req["method"],
                font=ctk.CTkFont(size=10, weight="bold"), text_color=method_color
            )
            m_label.pack(side="left", padx=6)

            st_color = "#34d399" if req["response_status"] < 400 else "#f87171"
            st_label = ctk.CTkLabel(
                meta_row, text=str(req["response_status"]),
                font=ctk.CTkFont(size=10), text_color=st_color
            )
            st_label.pack(side="left")

            url_label = ctk.CTkLabel(
                item_frame, text=req["url"],
                font=ctk.CTkFont(size=11), text_color="#cbd5e1",
                anchor="w"
            )
            url_label.pack(fill="x", padx=6, pady=(0, 4))

            # Bind clicks
            item_frame.bind("<Button-1>", lambda e, r_id=req["id"]: self._select_request(r_id))
            url_label.bind("<Button-1>", lambda e, r_id=req["id"]: self._select_request(r_id))
            meta_row.bind("<Button-1>", lambda e, r_id=req["id"]: self._select_request(r_id))

    def _select_request(self, req_id):
        self.active_request_id = req_id
        self._render_list()

        selected = next((r for r in self.requests_cache if r["id"] == req_id), None)
        if not selected:
            return

        self.req_summary_label.configure(text=f"{selected['method']} {selected['url']}")

        # 1. Tokens
        tokens = selected.get("extracted_tokens", {})
        self.txt_tokens.delete("1.0", "end")
        if tokens:
            self.txt_tokens.insert("end", json.dumps(tokens, indent=2, ensure_ascii=False))
        else:
            self.txt_tokens.insert("end", "(Không phát hiện auth/signature token đặc thù)")

        # 2. Headers
        self.txt_headers.delete("1.0", "end")
        self.txt_headers.insert("end", json.dumps(selected.get("headers", {}), indent=2, ensure_ascii=False))

        # 3. Payload
        self.txt_payload.delete("1.0", "end")
        body = selected.get("body", "")
        try:
            body = json.dumps(json.loads(body), indent=2, ensure_ascii=False)
        except Exception:
            pass
        self.txt_payload.insert("end", body or "(Empty body)")

        # 4. Response
        self.txt_resp.delete("1.0", "end")
        resp_b = selected.get("response_body", "")
        try:
            resp_b = json.dumps(json.loads(resp_b), indent=2, ensure_ascii=False)
        except Exception:
            pass
        self.txt_resp.insert("end", resp_b or "(Empty response)")

    def _copy_python(self):
        if not self.active_request_id:
            return
        selected = next((r for r in self.requests_cache if r["id"] == self.active_request_id), None)
        if selected:
            req_obj = CapturedRequest.from_dict(selected)
            py_code = generate_python_script(req_obj)
            self.clipboard_clear()
            self.clipboard_append(py_code)
            self.btn_copy_py.configure(text="✅ Đã Copy Python!")
            self.after(1500, lambda: self.btn_copy_py.configure(text="📋 Copy Python Requests"))

    def _copy_curl(self):
        if not self.active_request_id:
            return
        selected = next((r for r in self.requests_cache if r["id"] == self.active_request_id), None)
        if selected:
            req_obj = CapturedRequest.from_dict(selected)
            curl_cmd = generate_curl_command(req_obj)
            self.clipboard_clear()
            self.clipboard_append(curl_cmd)
            self.btn_copy_curl.configure(text="✅ Đã Copy cURL!")
            self.after(1500, lambda: self.btn_copy_curl.configure(text="📋 Copy cURL"))

    def _clear_feed(self):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{self.hub_port}/api/clear", data=b"{}", headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=1)
        except Exception:
            pass
        self.active_request_id = None
        self.requests_cache = []
        self._render_list()

    def destroy(self):
        self.is_polling = False
        super().destroy()
