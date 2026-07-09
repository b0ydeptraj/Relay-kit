# Relay-Kit V5 Upgrade Guide

Welcome to Relay-Kit V5! This guide will help you upgrade your existing V4 workspaces or install a fresh V5 setup.

## Upgrading from V4
1. **Pull the latest changes** for Relay-Kit.
2. **Install missing dependencies** required for semantic search and FastAPI:
   ```bash
   pip install "relay-kit[embeddings]" fastapi uvicorn
   ```
3. **Run the Migration Doctor**:
   ```bash
   relay-kit release doctor .
   ```
   If all gates pass, your workspace has successfully adapted to V5!

## Fresh Install for V5 (Codex / Claude / Antigravity)
1. Clone the repository and setup the environment.
2. The CLI is now fully modularized. Access standard commands like `relay-kit context search` or `relay-kit lane run`.
3. To enable AI automation safely, only install verified extensions:
   ```bash
   relay-kit extension install <path_to_pack> --trust reviewed
   ```

## Troubleshooting
- **Missing Lane Table**: If your lane audit fails, ensure `.relay-kit/state/team-board.md` contains the proper markdown table.
- **Lock Conflicts**: V5 introduces strict file locks. If agents fail to start, check `relay-kit pulse build .` or the live dashboard for locked files.
- **Stale Context Index**: Run `relay-kit context search . --allow-stale` if you need immediate results without reindexing.
