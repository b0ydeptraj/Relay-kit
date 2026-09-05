# Restore local Git refs

After reinstalling Windows:

```powershell
git clone --branch codex/pre-windows-reinstall-backup https://github.com/b0ydeptraj/Relay-kit.git relay-kit-backup
cd relay-kit-backup
git bundle verify backups/relay-kit-all-local-refs-2026-09-05.bundle
git fetch backups/relay-kit-all-local-refs-2026-09-05.bundle "refs/heads/*:refs/heads/*" "refs/tags/*:refs/tags/*"
git switch main
git remote set-url origin https://github.com/b0ydeptraj/Relay-kit.git
```

The bundle contains the complete history of 48 local branches and 6 tags as captured before the Windows reinstall.
