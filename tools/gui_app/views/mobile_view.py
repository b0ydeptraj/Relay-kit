import os
import shutil
import subprocess
import threading
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk

from tools.api_interceptor.mobile_helper import (
    FRIDA_UNIVERSAL_SSL_BYPASS,
    get_connected_adb_devices,
    prepare_system_ca_cert,
)


class MobileView(ctk.CTkFrame):
    """Mobile ADB Certificate & Frida SSL Pinning Helper View."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.selected_cert_path = None
        self._build_ui()
        self._refresh_adb()

    def _build_ui(self):
        # Header Banner
        banner = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=10, border_width=1, border_color="#1e293b")
        banner.pack(fill="x", padx=16, pady=(16, 10))

        title = ctk.CTkLabel(
            banner, text="📱 MOBILE APP API INTERCEPTOR & BYPASS HELPER",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#f472b6"
        )
        title.pack(side="left", padx=16, pady=10)

        self.lbl_adb_status = ctk.CTkLabel(
            banner, text="ADB: Đang quét...",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#cbd5e1"
        )
        self.lbl_adb_status.pack(side="right", padx=16)

        self.btn_refresh_adb = ctk.CTkButton(
            banner, text="🔄 Quét Lại Thiết Bị", width=120, height=28,
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#1e293b", hover_color="#334155",
            command=self._refresh_adb
        )
        self.btn_refresh_adb.pack(side="right", padx=6)

        # Main Layout
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Left Column: ADB CA Cert Installer
        left_col = ctk.CTkFrame(content_frame, fg_color="#0d1322", corner_radius=10, border_width=1, border_color="#1e293b")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ctk.CTkLabel(left_col, text="1. Cài Đặt System CA Certificate (Xuyên Thủng Android 7+)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=14, pady=(14, 6))

        cert_select_frame = ctk.CTkFrame(left_col, fg_color="#090d16", corner_radius=8)
        cert_select_frame.pack(fill="x", padx=14, pady=6)

        self.lbl_cert_name = ctk.CTkLabel(cert_select_frame, text="Chưa chọn file chứng chỉ (.pem / .crt)", font=ctk.CTkFont(size=11), text_color="#94a3b8")
        self.lbl_cert_name.pack(side="left", padx=12, pady=8, fill="x", expand=True)

        btn_browse = ctk.CTkButton(
            cert_select_frame, text="📁 Chọn Cert", width=90, height=28,
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#0284c7", hover_color="#0369a1",
            command=self._browse_cert
        )
        btn_browse.pack(side="right", padx=8, pady=6)

        self.btn_push_cert = ctk.CTkButton(
            left_col, text="⚡ Đẩy Vào /system/etc/security/cacerts Bằng ADB", height=32,
            font=ctk.CTkFont(size=12, weight="bold"), fg_color="#059669", hover_color="#047857",
            command=self._push_cert_adb
        )
        self.btn_push_cert.pack(fill="x", padx=14, pady=6)

        ctk.CTkLabel(left_col, text="Lệnh ADB Tương Đương:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=14, pady=(8, 2))
        self.txt_adb_log = ctk.CTkTextbox(left_col, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#050811", height=150)
        self.txt_adb_log.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # Right Column: Frida SSL Pinning Bypass
        right_col = ctk.CTkFrame(content_frame, fg_color="#0d1322", corner_radius=10, border_width=1, border_color="#1e293b")
        right_col.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_col, text="2. Frida Script Bypass SSL Pinning (TikTok libsscronet.so)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#f472b6").pack(anchor="w", padx=14, pady=(14, 6))

        btn_row = ctk.CTkFrame(right_col, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=4)

        btn_copy_frida = ctk.CTkButton(
            btn_row, text="📋 Copy Frida Script", width=140, height=28,
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#0284c7", hover_color="#0369a1",
            command=self._copy_frida
        )
        btn_copy_frida.pack(side="left")

        btn_save_frida = ctk.CTkButton(
            btn_row, text="💾 Lưu Thành File .js", width=130, height=28,
            font=ctk.CTkFont(size=11, weight="bold"), fg_color="#334155", hover_color="#475569",
            command=self._save_frida
        )
        btn_save_frida.pack(side="left", padx=6)

        self.txt_frida = ctk.CTkTextbox(right_col, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#050811")
        self.txt_frida.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        self.txt_frida.insert("end", FRIDA_UNIVERSAL_SSL_BYPASS)

    def _refresh_adb(self):
        devices = get_connected_adb_devices()
        if devices:
            self.lbl_adb_status.configure(text=f"🟢 Đã kết nối: {', '.join(devices)}", text_color="#34d399")
        else:
            self.lbl_adb_status.configure(text="🔴 Không tìm thấy thiết bị ADB", text_color="#f87171")

    def _browse_cert(self):
        f = filedialog.askopenfilename(filetypes=[("Certificate Files", "*.pem *.crt *.cer"), ("All Files", "*.*")])
        if f:
            self.selected_cert_path = Path(f)
            self.lbl_cert_name.configure(text=self.selected_cert_path.name, text_color="#38bdf8")
            res = prepare_system_ca_cert(self.selected_cert_path)
            self.txt_adb_log.delete("1.0", "end")
            self.txt_adb_log.insert("end", res["adb_instructions"])

    def _push_cert_adb(self):
        if not self.selected_cert_path:
            self.txt_adb_log.delete("1.0", "end")
            self.txt_adb_log.insert("end", "[!] Vui lòng chọn 1 file chứng chỉ (.pem) trước!\n")
            return

        def run():
            res = prepare_system_ca_cert(self.selected_cert_path)
            hash_name = res["system_hash"]
            out_file = res["output_file"]

            self.txt_adb_log.delete("1.0", "end")
            self.txt_adb_log.insert("end", f"[*] Đang thực thi ADB root & remount...\n")

            adb = shutil.which("adb")
            if not adb:
                self.txt_adb_log.insert("end", "[!] Không tìm thấy lệnh 'adb'. Hãy chắc chắn bạn đã cài ADB hoặc bật cổng giả lập.\n")
                return

            try:
                subprocess.run([adb, "root"], capture_output=True, timeout=5)
                subprocess.run([adb, "remount"], capture_output=True, timeout=5)
                push_res = subprocess.run([adb, "push", out_file, f"/system/etc/security/cacerts/{hash_name}"], capture_output=True, text=True, timeout=10)
                self.txt_adb_log.insert("end", push_res.stdout + push_res.stderr + "\n")
                subprocess.run([adb, "shell", f"chmod 644 /system/etc/security/cacerts/{hash_name}"], capture_output=True, timeout=5)
                self.txt_adb_log.insert("end", f"[+] ĐÃ ĐẨY THÀNH CÔNG: /system/etc/security/cacerts/{hash_name}!\n[+] Hãy khởi động lại thiết bị hoặc giả lập để áp dụng.\n")
            except Exception as e:
                self.txt_adb_log.insert("end", f"[!] Lỗi ADB: {e}\n")

        threading.Thread(target=run, daemon=True).start()

    def _copy_frida(self):
        self.clipboard_clear()
        self.clipboard_append(FRIDA_UNIVERSAL_SSL_BYPASS)

    def _save_frida(self):
        f = filedialog.asksaveasfilename(defaultextension=".js", filetypes=[("JavaScript", "*.js")])
        if f:
            Path(f).write_text(FRIDA_UNIVERSAL_SSL_BYPASS, encoding="utf-8")
