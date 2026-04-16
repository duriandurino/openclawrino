# Manual Bundle Checklist

Use this as the hand-carry package for the new PC.

## Must-copy from workspace
- `memory/`
- `credentials.json`
- `.google-creds`
- `logs/` only if you care about historical local logs
- any untracked deliverables you want to keep
- any ignored evidence files you intentionally want preserved

## Must-copy from home/config outside workspace
- `~/.ssh/`
- `~/.gitconfig`
- `~/.git-credentials` if present
- `~/.config/gh/` if you use GitHub CLI
- `~/.openclaw/` relevant config and state
- `~/.opencode/` relevant config/session state
- `~/.config/nvm/` only if you want a like-for-like toolchain carryover
- `~/.ollama/` only if you want local models migrated instead of re-downloading

## Google / gog auth
Bring whatever the current machine is actually using:
- workspace `credentials.json`
- workspace `.google-creds`
- any keyring-backed gog/google tokens if they are not reproducible from just those files
- note the preferred passphrase in `TOOLS.md` and `MEMORY.md`: `hatlesswhite`

## Git auth
Bring one of:
- SSH keys in `~/.ssh/`
- HTTPS PAT stored in credential helper / `~/.git-credentials`
- GitHub CLI auth in `~/.config/gh/`

## OpenClaw continuity
Bring:
- repo clone of this workspace
- `~/.openclaw/` configs that define gateway/session/runtime behavior
- any service/unit files if the always-on PC will run OpenClaw as a service

## Large or awkward files to zip manually
Recommended archive groups:

### 1. Daily memory and local state
- `memory/`
- `state/` if you want a separate backup in addition to git

### 2. Credential bundle
- `credentials.json`
- `.google-creds`
- `~/.ssh/`
- `~/.gitconfig`
- `~/.git-credentials`
- `~/.config/gh/`

### 3. Optional model/tool cache bundle
- `~/.ollama/`
- `~/.opencode/`
- `~/.config/nvm/`

### 4. Evidence and bulky artifacts you do not want in git
See `second-life/LARGE_FILE_INVENTORY.md`.

## Restore order on new PC
1. clone repo
2. restore workspace manual bundle items
3. restore home-directory auth/config items
4. reinstall missing system packages if needed
5. run validation checklist from `second-life/MIGRATION_MANIFEST.md`
