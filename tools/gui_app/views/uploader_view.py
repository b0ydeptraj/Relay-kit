import json
import threading
import urllib.request
import customtkinter as ctk


class UploaderView(ctk.CTkFrame):
    """TikTok Auto-Upload Queue & Ledger Dashboard View."""

    def __init__(self, master, bridge_port: int = 8765, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bridge_port = bridge_port
        self.is_polling = True

        self._build_ui()
        self._poll_status()

    def _build_ui(self):
        # Header Banner
        banner = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=10, border_width=1, border_color="#1e293b")
        banner.pack(fill="x", padx=16, pady=(16, 10))

        title = ctk.CTkLabel(
            banner, text="🚀 TIKTOK AUTO-UPLOAD QUEUE & SYNC MANAGER",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#38bdf8"
        )
        title.pack(side="left", padx=16, pady=10)

        self.lbl_server_status = ctk.CTkLabel(
            banner, text="Bridge 127.0.0.1:8765: Kiểm tra...",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8"
        )
        self.lbl_server_status.pack(side="right", padx=16)

        self.btn_reset_failed = ctk.CTkButton(
            banner, text="🔄 Reset Failed", width=110, height=28,
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#334155", hover_color="#475569",
            command=self._reset_failed
        )
        self.btn_reset_failed.pack(side="right", padx=6)

        # Metric Cards Row
        cards_row = ctk.CTkFrame(self, fg_color="transparent")
        cards_row.pack(fill="x", padx=16, pady=(0, 10))

        self.card_total = self._create_card(cards_row, "Tổng Video", "0", "#38bdf8")
        self.card_pending = self._create_card(cards_row, "Đang Chờ", "0", "#facc15")
        self.card_uploaded = self._create_card(cards_row, "Đã Đăng", "0", "#34d399")
        self.card_failed = self._create_card(cards_row, "Lỗi / Bỏ Qua", "0", "#f87171")

        # Video Queue Table
        ctk.CTkLabel(self, text="Danh Sách Video Trong Hàng Đợi Upload:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=20, pady=(6, 2))

        self.queue_scroll = ctk.CTkScrollableFrame(self, fg_color="#0d1322", corner_radius=10, border_width=1, border_color="#1e293b")
        self.queue_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _create_card(self, parent, title: str, val: str, text_color: str):
        card = ctk.CTkFrame(parent, fg_color="#0d1322", corner_radius=8, border_width=1, border_color="#1e293b", height=70)
        card.pack(side="left", fill="both", expand=True, padx=4)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w", padx=12, pady=(8, 0))
        val_lbl = ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=20, weight="bold"), text_color=text_color)
        val_lbl.pack(anchor="w", padx=12, pady=(0, 6))
        return val_lbl

    def _poll_status(self):
        if not self.is_polling:
            return

        def fetch():
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.bridge_port}/api/status", timeout=0.8) as resp:
                    status_data = json.loads(resp.read().decode())
                with urllib.request.urlopen(f"http://127.0.0.1:{self.bridge_port}/api/queue", timeout=0.8) as resp:
                    queue_data = json.loads(resp.read().decode())
                return status_data, queue_data.get("items", [])
            except Exception:
                return None, None

        def callback(status_data, items):
            if status_data:
                self.lbl_server_status.configure(text="🟢 Bridge Online", text_color="#34d399")
                self.card_total.configure(text=str(status_data.get("total_videos", 0)))
                self.card_pending.configure(text=str(status_data.get("pending", 0)))
                self.card_uploaded.configure(text=str(status_data.get("uploaded", 0)))
                self.card_failed.configure(text=str(status_data.get("failed", 0) + status_data.get("skipped", 0)))
            else:
                self.lbl_server_status.configure(text="🔴 Bridge Offline", text_color="#f87171")

            if items is not None:
                self._render_queue(items)

            self.after(2000, self._poll_status)

        def thread_target():
            s, q = fetch()
            self.after(0, lambda: callback(s, q))

        threading.Thread(target=thread_target, daemon=True).start()

    def _render_queue(self, items):
        for w in self.queue_scroll.winfo_children():
            w.destroy()

        if not items:
            lbl = ctk.CTkLabel(self.queue_scroll, text="Hàng đợi trống hoặc thư mục chưa có video.", text_color="#64748b")
            lbl.pack(pady=30)
            return

        for idx, item in enumerate(items, 1):
            row = ctk.CTkFrame(self.queue_scroll, fg_color="#141c2e", corner_radius=6, height=36)
            row.pack(fill="x", padx=4, pady=2)
            row.pack_propagate(False)

            status = item.get("status", "PENDING")
            st_color = "#34d399" if status == "UPLOADED" else ("#facc15" if status == "PENDING" else "#f87171")
            st_bg = "#065f46" if status == "UPLOADED" else ("#713f12" if status == "PENDING" else "#7f1d1d")

            ctk.CTkLabel(row, text=f"#{idx}", width=35, font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748b").pack(side="left", padx=4)

            badge = ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=10, weight="bold"), text_color=st_color, fg_color=st_bg, corner_radius=4, padx=6)
            badge.pack(side="left", padx=4)

            name_lbl = ctk.CTkLabel(row, text=item.get("file_name", ""), font=ctk.CTkFont(size=11), text_color="#cbd5e1", anchor="w")
            name_lbl.pack(side="left", fill="x", expand=True, padx=8)

            size_mb = item.get("file_size", 0) / 1048576
            ctk.CTkLabel(row, text=f"{size_mb:.1f} MB", font=ctk.CTkFont(size=10), text_color="#94a3b8").pack(side="right", padx=10)

    def _reset_failed(self):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{self.bridge_port}/api/retry-failed", data=b"{}", headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=1)
        except Exception:
            pass

    def destroy(self):
        self.is_polling = False
        super().destroy()
