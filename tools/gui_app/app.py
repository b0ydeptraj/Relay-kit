import os
import sys
from pathlib import Path
import customtkinter as ctk

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from tools.gui_app.views.mobile_view import MobileView
from tools.gui_app.views.reup_view import ReupView
from tools.gui_app.views.sniffer_view import SnifferView
from tools.gui_app.views.uploader_view import UploaderView

# Set default theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class RelayKitStudioApp(ctk.CTk):
    """Main Desktop Window for RelayKit Studio."""

    def __init__(self):
        super().__init__()

        self.title("RelayKit Studio — Unified MMO & API Operator")
        self.geometry("1140x740")
        self.minsize(980, 640)

        # Configure 2-column grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # Default view
        self._switch_view("sniffer")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#090d16")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        # App Brand
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 24))

        ctk.CTkLabel(
            brand_frame, text="⚡ RelayKit Studio",
            font=ctk.CTkFont(size=16, weight="bold"), text_color="#38bdf8"
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_frame, text="Enterprise MMO & API Suite",
            font=ctk.CTkFont(size=11), text_color="#64748b"
        ).pack(anchor="w", pady=(2, 0))

        # Navigation Buttons
        self.nav_buttons = {}

        nav_items = [
            ("sniffer", "📡 API Sniffer & Replay"),
            ("mobile", "📱 Mobile & Frida Helper"),
            ("reup", "🎬 Video Reup Engine"),
            ("uploader", "🚀 TikTok Auto-Upload"),
        ]

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w", height=38,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent", text_color="#94a3b8",
                hover_color="#1e293b", corner_radius=8,
                command=lambda k=key: self._switch_view(k)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[key] = btn

        # Bottom Info
        bot_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bot_frame.pack(side="bottom", fill="x", padx=16, pady=16)

        ctk.CTkLabel(
            bot_frame, text="🟢 Local Daemon Active",
            font=ctk.CTkFont(size=11, weight="bold"), text_color="#34d399"
        ).pack(anchor="w")

        ctk.CTkLabel(
            bot_frame, text="v1.0.0 • 100% Free & Open",
            font=ctk.CTkFont(size=10), text_color="#475569"
        ).pack(anchor="w", pady=(2, 0))

    def _build_content_area(self):
        self.container = ctk.CTkFrame(self, corner_radius=0, fg_color="#030712")
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.pack_propagate(False)

        self.views = {
            "sniffer": SnifferView(self.container),
            "mobile": MobileView(self.container),
            "reup": ReupView(self.container),
            "uploader": UploaderView(self.container),
        }

    def _switch_view(self, view_key: str):
        # Update button highlights
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(fg_color="#1e293b", text_color="#38bdf8")
            else:
                btn.configure(fg_color="transparent", text_color="#94a3b8")

        # Hide all views and show selected
        for k, view in self.views.items():
            if k == view_key:
                view.pack(fill="both", expand=True)
            else:
                view.pack_forget()


def launch_app():
    app = RelayKitStudioApp()
    app.mainloop()


if __name__ == "__main__":
    launch_app()
