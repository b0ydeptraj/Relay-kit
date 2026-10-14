import os
import threading
from pathlib import Path
from tkinter import filedialog
import customtkinter as ctk

from tools.video_reup_engine.filter_pipeline import PRESETS
from tools.video_reup_engine.mutation_engine import mutate_video


class ReupView(ctk.CTkFrame):
    """Video Mutation & Reup Engine Control View."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.raw_dir = Path("C:/Users/Hiep/raw_videos") if Path("C:/Users/Hiep/raw_videos").is_dir() else Path.cwd()
        self.out_dir = Path("c:/Users/Hiep/Documents/Relay-kit/mutated_videos")
        self.is_running = False

        self._build_ui()

    def _build_ui(self):
        # Header Banner
        banner = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=10, border_width=1, border_color="#1e293b")
        banner.pack(fill="x", padx=16, pady=(16, 10))

        title = ctk.CTkLabel(
            banner, text="🎬 VIDEO MUTATION & ANTI-COPYRIGHT ENGINE",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#38bdf8"
        )
        title.pack(side="left", padx=16, pady=10)

        # Settings Box
        cfg_frame = ctk.CTkFrame(self, fg_color="#0d1322", corner_radius=10, border_width=1, border_color="#1e293b")
        cfg_frame.pack(fill="x", padx=16, pady=(0, 10))

        # Row 1: Directories
        r1 = ctk.CTkFrame(cfg_frame, fg_color="transparent")
        r1.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(r1, text="Thư mục Video Gốc:", font=ctk.CTkFont(size=11, weight="bold"), width=130, anchor="w").pack(side="left")
        self.entry_raw = ctk.CTkEntry(r1, font=ctk.CTkFont(size=11), fg_color="#1e293b", border_color="#334155")
        self.entry_raw.insert(0, str(self.raw_dir))
        self.entry_raw.pack(side="left", fill="x", expand=True, padx=6)

        btn_browse_raw = ctk.CTkButton(
            r1, text="📁 Chọn", width=70, height=28,
            font=ctk.CTkFont(size=11), fg_color="#334155",
            command=self._browse_raw
        )
        btn_browse_raw.pack(side="left")

        # Row 2: Preset & Action
        r2 = ctk.CTkFrame(cfg_frame, fg_color="transparent")
        r2.pack(fill="x", padx=14, pady=(0, 12))

        ctk.CTkLabel(r2, text="Cấu hình Preset:", font=ctk.CTkFont(size=11, weight="bold"), width=130, anchor="w").pack(side="left")
        self.preset_combo = ctk.CTkComboBox(
            r2, values=["balanced (Khuyên dùng - Chữ xuôi chuẩn)", "light (Nhẹ)", "aggressive (Mạnh)"],
            width=300, font=ctk.CTkFont(size=11), fg_color="#1e293b", border_color="#334155"
        )
        self.preset_combo.set("balanced (Khuyên dùng - Chữ xuôi chuẩn)")
        self.preset_combo.pack(side="left", padx=6)

        self.btn_run_mutate = ctk.CTkButton(
            r2, text="▶️ Bắt Đầu Đột Biến Toàn Bộ", height=32,
            font=ctk.CTkFont(size=12, weight="bold"), fg_color="#059669", hover_color="#047857",
            command=self._start_batch_mutation
        )
        self.btn_run_mutate.pack(side="right")

        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(cfg_frame, height=8, progress_color="#38bdf8")
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=14, pady=(0, 12))

        # Output Log Box
        ctk.CTkLabel(self, text="Nhật Ký Quá Trình Đột Biến (Perceptual Hash & Disruption):", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=20, pady=(4, 2))
        self.txt_log = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#050811")
        self.txt_log.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def _browse_raw(self):
        d = filedialog.askdirectory(initialdir=self.raw_dir)
        if d:
            self.raw_dir = Path(d)
            self.entry_raw.delete(0, "end")
            self.entry_raw.insert(0, str(self.raw_dir))

    def _log(self, text: str):
        self.txt_log.insert("end", text + "\n")
        self.txt_log.see("end")

    def _start_batch_mutation(self):
        if self.is_running:
            return

        raw_path = Path(self.entry_raw.get().strip())
        if not raw_path.is_dir():
            self._log(f"[!] Thư mục không tồn tại: {raw_path}")
            return

        videos = sorted(list(raw_path.glob("*.mp4")))
        if not videos:
            self._log(f"[!] Không tìm thấy video .mp4 nào trong: {raw_path}")
            return

        self.is_running = True
        self.btn_run_mutate.configure(state="disabled", text="⏳ Đang xử lý...")
        self.out_dir.mkdir(parents=True, exist_ok=True)

        preset_choice = "balanced"
        if "light" in self.preset_combo.get().lower():
            preset_choice = "light"
        elif "aggressive" in self.preset_combo.get().lower():
            preset_choice = "aggressive"

        cfg = PRESETS[preset_choice]

        def worker():
            total = len(videos)
            self._log(f"\n{'='*55}\n🚀 Bắt đầu đột biến {total} video (Preset: {cfg.preset_name}, Lật gương: {cfg.mirror_horizontal})...")
            success_count = 0

            for idx, raw in enumerate(videos, 1):
                mut_name = f"{raw.stem}_mutated{raw.suffix}"
                out_file = self.out_dir / mut_name
                self._log(f"[{idx}/{total}] Đang xử lý: {raw.name}...")

                try:
                    res = mutate_video(raw, output_file=out_file, config=cfg)
                    elapsed = res.get("elapsed_seconds", 0)
                    size = res.get("output", {}).get("size_bytes", 0)
                    self._log(f"  -> Xong trong {elapsed:.2f}s | Kích thước: {(size/1048576):.2f} MB | Hash MD5 đổi thành công.")
                    success_count += 1
                except Exception as e:
                    self._log(f"  [X] Lỗi: {e}")

                self.progress_bar.set(idx / total)

            self._log(f"\n🎉 HOÀN THÀNH: {success_count}/{total} video đã được chuyển vào {self.out_dir}\n{'='*55}\n")
            self.is_running = False
            self.btn_run_mutate.configure(state="normal", text="▶️ Bắt Đầu Đột Biến Toàn Bộ")

        threading.Thread(target=worker, daemon=True).start()
