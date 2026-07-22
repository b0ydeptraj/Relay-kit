---
name: terminal-operator-ui
description: Use when building a rich terminal UI (TUI) for operator control panels, automation dashboards, or CLI tools: Rich, Textual, blessed, curses, prompt_toolkit, or similar.
---

# Mission
Build functional, navigable terminal UIs with correct layout, input handling, and live update discipline.

## Mandatory scope
1. Declare framework: Rich (static), Textual (reactive TUI), blessed, curses, prompt_toolkit.
2. Layout: define panels, tables, progress bars, and input areas with explicit dimensions and overflow behavior.
3. Live updates: use Live context (Rich) or reactive state (Textual) — never print() to a live TUI.
4. Input handling: define keyboard shortcuts, navigation, and exit path explicitly.
5. Color and styling: define palette and use named styles, not inline ANSI codes.
6. Error display: show error state visually in a status bar or panel, not as raw exception text.

## Evidence contract
- framework declared
- layout documented (panels, tables, inputs)
- live update mechanism specified
- keyboard shortcuts documented
- runs in target terminal (Windows cmd/PowerShell/Linux term)

## Role
- tui-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- UI spec or wireframe
- framework preference
- Python version

## Outputs
- TUI implementation
- keyboard shortcut map
- live update docs

## Reference skills and rules
- Never mix print() with a live TUI — it corrupts the layout.
- Define explicit terminal size handling — TUIs break when terminal is too narrow.
- Input blocking operations must run in threads with TUI-safe update callbacks.
- Test in the actual target terminal (Windows Terminal vs xterm differ).
- Open `references/terminal-operator-ui-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/terminal-operator-ui-good-output.md` and `examples/terminal-operator-ui-bad-output.md` to calibrate output quality.
- Use `evals/terminal-operator-ui-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/terminal-operator-ui-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- advanced-python-engineering
- desktop-python-ui
- test-hub
- field-journal-evolution
