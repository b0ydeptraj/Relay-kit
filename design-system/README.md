# Relay-kit Design System

Warm-minimal identity, one source of truth, portable across web, desktop and mobile.

## Source of truth
- `tokens/tokens.json` — colors (light+dark), type, spacing, radius, elevation, motion.
- Edit that file, then run:  `python build_tokens.py`  → regenerates every export below.

## Exports (generated — do not hand-edit)
- `web/tokens.css` — CSS variables, light + dark.
- `qt/relay_kit_theme.py` + `relay_kit_light.qss` / `relay_kit_dark.qss` — PySide6/PyQt6.
- `imgui/relay_kit_theme.h` — `ApplyRelayKitTheme()` for Dear ImGui (C++).
- `flutter/relay_kit_theme.dart` — `RelayKit.theme(dark: false)` ThemeData.
- `react-native/relayKitTheme.ts` — typed theme object.

## Reference
- `design-system.html` — style guide (tokens, type, platform mapping).
- `mock/` — example screens: `desktop_qt.html`, `imgui.html`, `mobile.html` (+ PNG/JPG).

## Re-theme in one move
Change `color.light.primary` / `color.dark.primary` (and their deep/tint) in tokens.json,
re-run build_tokens.py — web, Qt, ImGui, Flutter and RN all follow.

## Fonts
Web pulls Fraunces + Inter + JetBrains Mono from Google Fonts. Desktop/mobile must
**bundle** the .ttf files (drop them in each platform's fonts/ dir) or fall back to
Georgia / system-sans / system-mono. Font files are not redistributed here for licensing.

## Theme layer (multi-identity)
`tokens.json` is the *base architecture*. `themes/*.json` are *presets* — one per domain:
- relay-editorial (dev-tool), nocturne-ops (security/terminal), cobalt-fintech (crypto),
  sunset-social (content), slate-enterprise (SaaS), verdant-commerce (e-commerce).
Each preset = palette + font pairing + shape scale + surface style + density + mode.
See `theme-gallery.html` for the same screen in all six. Render/add themes with
`mock/render_themes.py` over `mock/app-parametric.html`.
