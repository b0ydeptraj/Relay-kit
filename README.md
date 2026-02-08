# Python Kit v2.1

Generate AI agent skills from Python and Flutter project analysis, plus template skills from Antigravity, ClaudeKit, and UI/UX Pro Max.

## Prerequisites

- Python 3.10+ (`python --version`)
- Git (for cloning/updating this repo)
- The AI CLI you plan to target:
  - Claude: `claude`
  - Antigravity/Gemini: `gemini`
  - Codex: Codex app with `.codex/skills` support

## Quick Start

```bash
python python_kit.py /path/to/project               # Python skill set (default)
python python_kit.py /path/to/project --kit flutter # Flutter skill set
python python_kit.py /path/to/project --kit antigravity
python python_kit.py /path/to/project --kit claudekit
python python_kit.py /path/to/project --kit ui-ux
python python_kit.py /path/to/project --kit full
python python_kit.py /path/to/project --ai gemini   # Gemini output
python python_kit.py /path/to/project --ai codex    # Codex output
python python_kit.py /path/to/project --ai all      # Both Claude + Gemini
python python_kit.py /path/to/project --ai generic  # Prompts for any AI
```

## Run For Each Tool

Use the same command shape and change only `--ai`.

```bash
python C:/Users/b0ydeptrai/OneDrive/Documents/python-kit/python_kit.py <project_path> --ai claude --kit full
python C:/Users/b0ydeptrai/OneDrive/Documents/python-kit/python_kit.py <project_path> --ai gemini --kit full
python C:/Users/b0ydeptrai/OneDrive/Documents/python-kit/python_kit.py <project_path> --ai codex --kit full
```

Outputs by tool:

- `claude` -> `<project_path>/.claude/skills/`
- `gemini` -> `<project_path>/.agent/skills/`
- `codex` -> `<project_path>/.codex/skills/`

Notes:

- `--ai all` currently means `claude + gemini` only.
- On Windows, `aux` is a reserved name, so Codex support assets are written to `.codex/support/`.

## AI Adapters & Output Folders

| `--ai` | Folder | Auto-read? |
|--------|--------|------------|
| `claude` | `.claude/skills/` | Yes (Claude Code) |
| `gemini` | `.agent/skills/` | Yes (Gemini/Antigravity) |
| `codex` | `.codex/skills/` | Yes (Codex skills) |
| `all` | Both folders | Yes (Claude + Gemini) |
| `generic` | `.python-kit-prompts/` | No (copy-paste) |

## Skill Sets

| Set | What it includes |
|-----|------------------|
| `python` | 19 analysis skills for Python projects |
| `flutter` | 8 analysis skills for Flutter projects |
| `antigravity` | Template skills for frontend/backend/devops/testing/database |
| `claudekit` | Template skills for tooling, docs, MCP, frontend/backends |
| `ui-ux` | UI/UX Pro Max skill (scripts + data included) |
| `full` | All skills combined |

Use `--list-skills` to see the full list.

## Extra Assets

Extra assets by adapter:

- `gemini`/`all`: `.agent/` receives Antigravity `rules/`, `workflows/`, and `.shared/`
- `claude`/`all`: `.claude/` receives ClaudeKit `agents/` and `commands/`
- `codex`: `.codex/support/antigravity/` receives `rules/`, `workflows/`, `.shared/`; `.codex/support/claude/` receives `agents/`, `commands/` (paths rewritten for Codex)

## Publish To GitHub

From the `python-kit` folder:

```bash
git init
git add .
git commit -m "feat: add codex adapter and multi-tool install docs"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

For later upgrades:

```bash
git add -A
git commit -m "feat: ..."
git push
```

## Credits

- [claudekit-skills](https://github.com/anthropics/claudekit-skills)
- [antigravity-kit](https://github.com/vudovn/antigravity-kit)
- [ui-ux-pro-max-skill](https://ui-ux-pro-max-skill.nextlevelbuilder.io/)