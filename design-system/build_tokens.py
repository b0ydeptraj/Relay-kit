#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Relay-kit design tokens -> platform exports.
Edit tokens/tokens.json, then run:  python build_tokens.py
Writes: web/tokens.css, qt/*, imgui/*, flutter/*, react-native/*
"""
import json, os, io
ROOT = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(ROOT, "tokens", "tokens.json"), encoding="utf-8"))
CL, CD = T["color"]["light"], T["color"]["dark"]
F, S, R = T["font"], T["space"], T["radius"]

def w(rel, s):
    p = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8").write(s if s.endswith("\n") else s + "\n")
    print("wrote", rel)

def hx(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ---------- WEB : tokens.css ----------
def css():
    def vars(c):
        L = [f"  --rk-{k}: {v};" for k, v in c.items()]
        L += [f"  --rk-font-display: '{F['family']['display']['web']}', {F['family']['display']['fallback']};",
              f"  --rk-font-sans: '{F['family']['sans']['web']}', {F['family']['sans']['fallback']};",
              f"  --rk-font-mono: '{F['family']['mono']['web']}', {F['family']['mono']['fallback']};"]
        for k, v in F["size"].items():   L.append(f"  --rk-size-{k}: {v}px;")
        for k, v in S.items():           L.append(f"  --rk-space-{k}: {v}px;")
        for k, v in R.items():           L.append(f"  --rk-radius-{k}: {v}px;")
        L.append(f"  --rk-elev-1: {T['elevation']['e1']};")
        L.append(f"  --rk-elev-2: {T['elevation']['e2']};")
        L.append(f"  --rk-ease: {T['motion']['ease']};")
        return "\n".join(L)
    return f"""/* Relay-kit design tokens — generated from tokens.json. Do not edit by hand. */
:root, [data-theme="light"] {{
{vars(CL)}
}}
[data-theme="dark"] {{
{chr(10).join(f'  --rk-{k}: {v};' for k,v in CD.items())}
}}
"""
w("web/tokens.css", css())

# ---------- QT / PySide6 ----------
def qss(c):
    return f"""/* Relay-kit — Qt stylesheet (generated). Pair with relay_kit_theme.py */
* {{ font-family: "{F['family']['sans']['web']}", "Segoe UI", sans-serif; font-size: {F['size']['body']}px; color: {c['ink']}; }}
QMainWindow, QWidget {{ background: {c['bg']}; }}
QFrame#Card, QGroupBox {{ background: {c['surface']}; border: 1px solid {c['line']}; border-radius: {R['md']}px; }}
QLabel#H1 {{ font-family: "{F['family']['display']['web']}", Georgia, serif; font-size: {F['size']['h1']}px; color: {c['ink']}; }}
QLabel#Eyebrow {{ color: {c['primary']}; font-weight: 700; letter-spacing: 1px; }}
QLabel#Muted {{ color: {c['muted']}; }}
QPushButton {{ background: {c['surface']}; border: 1px solid {c['line']}; border-radius: {R['sm']}px; padding: 8px 16px; }}
QPushButton:hover {{ border-color: {c['primary']}; color: {c['primary']}; }}
QPushButton#Primary {{ background: {c['primary']}; color: {c['onPrimary']}; border: none; font-weight: 600; }}
QPushButton#Primary:hover {{ background: {c['primaryDeep']}; }}
QLineEdit, QComboBox, QPlainTextEdit {{ background: {c['surface']}; border: 1px solid {c['line']}; border-radius: {R['sm']}px; padding: 8px 10px; selection-background-color: {c['primaryTint']}; }}
QLineEdit:focus, QComboBox:focus {{ border: 1.5px solid {c['primary']}; }}
QListWidget#Nav {{ background: {c['surface2']}; border: none; border-right: 1px solid {c['line']}; padding: 8px; }}
QListWidget#Nav::item {{ padding: 9px 12px; border-radius: {R['sm']}px; color: {c['inkSoft']}; }}
QListWidget#Nav::item:selected {{ background: {c['primaryTint']}; color: {c['primaryDeep']}; }}
QProgressBar {{ background: {c['surface2']}; border: none; border-radius: {R['pill']}px; height: 8px; text-align: center; }}
QProgressBar::chunk {{ background: {c['primary']}; border-radius: {R['pill']}px; }}
QHeaderView::section {{ background: {c['surface2']}; color: {c['muted']}; border: none; padding: 8px; }}
QStatusBar {{ background: {c['surface2']}; color: {c['muted']}; }}
"""
w("qt/relay_kit_light.qss", qss(CL))
w("qt/relay_kit_dark.qss", qss(CD))
w("qt/relay_kit_theme.py", f'''"""Relay-kit Qt theme loader (PySide6 / PyQt6).  Generated helper.
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
LIGHT = {json.dumps(CL, ensure_ascii=False)}
DARK  = {json.dumps(CD, ensure_ascii=False)}

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
''')

# ---------- IMGUI (C++) ----------
def v4(hexc, a=1.0):
    r, g, b = hx(hexc); return f"ImVec4({r/255:.3f}f, {g/255:.3f}f, {b/255:.3f}f, {a:.2f}f)"
def imgui():
    c = CD  # ImGui panels read best dark
    return f"""// Relay-kit — Dear ImGui theme (generated). C++11.
// Call ApplyRelayKitTheme() once after ImGui::CreateContext().
// Load fonts (optional) for full fidelity:
//   io.Fonts->AddFontFromFileTTF("fonts/Inter.ttf", 16.0f);
//   io.Fonts->AddFontFromFileTTF("fonts/JetBrainsMono.ttf", 15.0f);
#pragma once
#include "imgui.h"

inline void ApplyRelayKitTheme() {{
    ImGuiStyle& s = ImGui::GetStyle();
    s.WindowRounding    = {R['md']}.0f;
    s.ChildRounding     = {R['sm']}.0f;
    s.FrameRounding     = {R['sm']}.0f;
    s.PopupRounding     = {R['sm']}.0f;
    s.GrabRounding      = {R['sm']}.0f;
    s.TabRounding       = {R['sm']}.0f;
    s.WindowPadding     = ImVec2({S['4']}, {S['4']});
    s.FramePadding      = ImVec2({S['3']}, {S['2']});
    s.ItemSpacing       = ImVec2({S['3']}, {S['2']});
    s.ScrollbarSize     = 12.0f;
    s.WindowBorderSize  = 1.0f;
    s.FrameBorderSize   = 1.0f;

    ImVec4* col = s.Colors;
    col[ImGuiCol_WindowBg]        = {v4(c['bg'])};
    col[ImGuiCol_ChildBg]         = {v4(c['surface'])};
    col[ImGuiCol_PopupBg]         = {v4(c['surface2'])};
    col[ImGuiCol_Border]          = {v4(c['line'])};
    col[ImGuiCol_Text]            = {v4(c['ink'])};
    col[ImGuiCol_TextDisabled]    = {v4(c['muted'])};
    col[ImGuiCol_FrameBg]         = {v4(c['surface2'])};
    col[ImGuiCol_FrameBgHovered]  = {v4(c['line'])};
    col[ImGuiCol_FrameBgActive]   = {v4(c['primaryTint'])};
    col[ImGuiCol_TitleBg]         = {v4(c['surface2'])};
    col[ImGuiCol_TitleBgActive]   = {v4(c['surface2'])};
    col[ImGuiCol_Button]          = {v4(c['primary'], 0.14)};
    col[ImGuiCol_ButtonHovered]   = {v4(c['primary'], 0.30)};
    col[ImGuiCol_ButtonActive]    = {v4(c['primary'])};
    col[ImGuiCol_Header]          = {v4(c['primary'], 0.18)};
    col[ImGuiCol_HeaderHovered]   = {v4(c['primary'], 0.32)};
    col[ImGuiCol_HeaderActive]    = {v4(c['primary'])};
    col[ImGuiCol_CheckMark]       = {v4(c['primary'])};
    col[ImGuiCol_SliderGrab]      = {v4(c['primary'])};
    col[ImGuiCol_SliderGrabActive]= {v4(c['primaryDeep'])};
    col[ImGuiCol_Tab]             = {v4(c['surface2'])};
    col[ImGuiCol_TabActive]       = {v4(c['primary'], 0.28)};
    col[ImGuiCol_TabHovered]      = {v4(c['primary'], 0.20)};
    col[ImGuiCol_PlotLines]       = {v4(c['primary'])};
    col[ImGuiCol_PlotHistogram]   = {v4(c['primary'])};
    col[ImGuiCol_Separator]       = {v4(c['line'])};
    col[ImGuiCol_ScrollbarBg]     = {v4(c['bg'])};
    col[ImGuiCol_ScrollbarGrab]   = {v4(c['line'])};
}}
"""
w("imgui/relay_kit_theme.h", imgui())

# ---------- FLUTTER ----------
def dart():
    def C(h): r,g,b=hx(h); return f"Color(0xFF{r:02X}{g:02X}{b:02X})"
    def scheme(c, bright):
        return f"""  static const ColorScheme {'light' if bright else 'dark'} = ColorScheme(
    brightness: Brightness.{'light' if bright else 'dark'},
    surface: {C(c['bg'])}, onSurface: {C(c['ink'])},
    primary: {C(c['primary'])}, onPrimary: {C(c['onPrimary'])},
    secondary: {C(c['primaryDeep'])}, onSecondary: {C(c['onPrimary'])},
    error: {C(c['danger'])}, onError: {C('#FFFFFF')},
    outline: {C(c['line'])},
  );"""
    return f"""// Relay-kit — Flutter theme (generated). Requires google_fonts (or bundle fonts).
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class RelayKit {{
{scheme(CL, True)}
{scheme(CD, False)}

  static ThemeData theme({{bool dark = false}}) {{
    final cs = dark ? RelayKit.dark : RelayKit.light;
    final base = ThemeData(useMaterial3: true, colorScheme: cs, scaffoldBackgroundColor: cs.surface);
    return base.copyWith(
      textTheme: GoogleFonts.interTextTheme(base.textTheme).copyWith(
        displaySmall: GoogleFonts.fraunces(fontSize: {F['size']['display']}, fontWeight: FontWeight.w500, color: cs.onSurface),
        headlineSmall: GoogleFonts.fraunces(fontSize: {F['size']['h2']}, fontWeight: FontWeight.w500, color: cs.onSurface),
      ),
      cardTheme: CardTheme(color: {C(CL['surface'])}, elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular({R['md']}),
          side: BorderSide(color: cs.outline))),
      filledButtonTheme: FilledButtonThemeData(style: FilledButton.styleFrom(
        backgroundColor: cs.primary, foregroundColor: cs.onPrimary,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular({R['sm']})))),
    );
  }}
}}
"""
w("flutter/relay_kit_theme.dart", dart())

# ---------- REACT NATIVE ----------
def rn():
    return f"""// Relay-kit — React Native theme (generated). Bundle fonts via expo-font / react-native.config.js.
export const relayKit = {{
  color: {{ light: {json.dumps(CL)}, dark: {json.dumps(CD)} }},
  font: {{
    display: 'Fraunces', sans: 'Inter', mono: 'JetBrains Mono',
    size: {json.dumps(F['size'])}, weight: {json.dumps(F['weight'])},
  }},
  space: {json.dumps(S)},
  radius: {json.dumps(R)},
}} as const;

// Example:
// const c = relayKit.color[scheme];  // scheme = 'light' | 'dark'
// <View style={{{{ backgroundColor: c.surface, borderColor: c.line, borderRadius: relayKit.radius.md }}}} />
// <Text style={{{{ color: c.primary, fontFamily: relayKit.font.display }}}} />
"""
w("react-native/relayKitTheme.ts", rn())

print("== all exports generated ==")
