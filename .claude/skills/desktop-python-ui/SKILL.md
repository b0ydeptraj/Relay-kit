---
name: desktop-python-ui
description: Use when building a desktop Python GUI: PyQt6/PySide6, Tkinter, wxPython, or customtkinter for operator tools, automation dashboards, or config panels.
---

# Mission
Build clean, functional Python desktop UIs with correct event loop integration, threading discipline, and packaging.

## Mandatory scope
1. Declare framework: PyQt6/PySide6, Tkinter, customtkinter — each has different signal/slot or callback model.
2. Threading: UI updates must happen on main thread; background work in QThread/threading.Thread with signals.
3. Layout: use layout managers (QVBoxLayout, QHBoxLayout, grid) — never fixed pixel positioning.
4. Packaging: specify PyInstaller or cx_Freeze spec for standalone executable if needed.
5. State management: separate model from view — no business logic in widget callbacks.
6. Error handling: show user-friendly error dialogs for all recoverable exceptions.

## Evidence contract
- framework declared
- threading model documented (background work separated from UI thread)
- layout uses layout managers
- packaging spec documented if needed
- runs without console window if GUI-only

## Role
- python-ui-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- UI spec
- Python framework preference
- target OS (Windows/Linux/macOS)
- MMO operation live state (from mmo-cloud-operations, mmo-proxy-network-ops) for control panel data

## Outputs
- Python UI implementation
- threading model docs
- packaging spec

## Reference skills and rules
- Never block the main UI thread with slow operations.
- Signals/slots for PyQt — never call UI methods directly from background threads.
- Use layout managers — absolute positioning breaks on different screen sizes.
- Provide packaging spec if operator needs a standalone .exe.
- Open `references/desktop-python-ui-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/desktop-python-ui-good-output.md` and `examples/desktop-python-ui-bad-output.md` to calibrate output quality.
- Use `evals/desktop-python-ui-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/desktop-python-ui-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- advanced-python-engineering
- terminal-operator-ui
- test-hub
- field-journal-evolution
