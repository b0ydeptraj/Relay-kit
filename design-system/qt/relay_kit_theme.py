"""Relay-kit Qt theme loader (PySide6 / PyQt6).  Generated helper.
Usage:
    from relay_kit_theme import apply_relay_kit
    app = QApplication([]); apply_relay_kit(app, dark=False)
Bundle Fraunces/Inter/JetBrainsMono .ttf next to this file for full fidelity;
falls back to Georgia / Segoe UI / system mono if missing.
"""
import os
from PySide6.QtWidgets import QApplication          # swap to PyQt6 if needed
from PySide6.QtGui import QFontDatabase, QPalette, QColor

_HERE = os.path.dirname(os.path.abspath(__file__))
LIGHT = {"bg": "#FAF6EF", "surface": "#FFFFFF", "surface2": "#F3ECDF", "ink": "#22201C", "inkSoft": "#4A443B", "muted": "#6E665A", "line": "#E8DFCF", "lineSoft": "#F0E9DB", "primary": "#059669", "primaryDeep": "#047857", "primaryTint": "#DBF3EA", "onPrimary": "#FFFFFF", "success": "#059669", "warning": "#B7791F", "danger": "#C0392B", "info": "#2F6DB0", "band": "#14120D", "onBand": "#F3ECDD"}
DARK  = {"bg": "#15140F", "surface": "#201E17", "surface2": "#26231B", "ink": "#F2EBDD", "inkSoft": "#D6CDBB", "muted": "#9C9284", "line": "#332C22", "lineSoft": "#2A241B", "primary": "#34D399", "primaryDeep": "#6EE7B7", "primaryTint": "#0E241C", "onPrimary": "#08130D", "success": "#34D399", "warning": "#E0A94B", "danger": "#E1685A", "info": "#7FA8DA", "band": "#0E0C09", "onBand": "#F3ECDD"}

def _load_fonts():
    for f in ("Fraunces.ttf", "Inter.ttf", "JetBrainsMono.ttf"):
        p = os.path.join(_HERE, "fonts", f)
        if os.path.exists(p):
            QFontDatabase.addApplicationFont(p)

def apply_relay_kit(app: QApplication, dark: bool = False):
    c = DARK if dark else LIGHT
    _load_fonts()
    pal = QPalette()
    pal.setColor(QPalette.Window,     QColor(c["bg"]))
    pal.setColor(QPalette.Base,       QColor(c["surface"]))
    pal.setColor(QPalette.Text,       QColor(c["ink"]))
    pal.setColor(QPalette.WindowText, QColor(c["ink"]))
    pal.setColor(QPalette.Highlight,  QColor(c["primary"]))
    pal.setColor(QPalette.HighlightedText, QColor(c["onPrimary"]))
    app.setPalette(pal)
    qss = "relay_kit_dark.qss" if dark else "relay_kit_light.qss"
    with open(os.path.join(_HERE, qss), encoding="utf-8") as fh:
        app.setStyleSheet(fh.read())
