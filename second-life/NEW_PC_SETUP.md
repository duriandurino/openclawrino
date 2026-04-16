# New PC Setup for Hatless White

## 1. Base system
Install on the new always-on PC:
- git
- node + npm
- nvm if you want the same Node management flow
- Python 3
- OpenClaw
- optional: Ollama
- optional: tmux

## 2. Clone the workspace
```bash
git clone <your-workspace-repo-url> ~/.openclaw/workspace
cd ~/.openclaw/workspace
```

## 3. Restore manual bundle
Copy back:
- `memory/`
- `credentials.json`
- `.google-creds`
- any wanted logs/evidence
- external config directories from your home folder

## 4. Restore identity and agent continuity
These should already come from git, but verify:
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `AGENTS.md`
- `MEMORY.md`
- `agents/`
- `skills/`
- `state/`

## 5. Restore auth
### Git
Either restore SSH keys or PAT-backed credentials.

### Google / gog
Restore the workspace auth files and any token/keyring material needed by the current flow.
Preferred passphrase note in workspace docs: `hatlesswhite`.

### OpenClaw
Restore any config under `~/.openclaw/` required for gateway/session behavior.

## 6. Reinstall lightweight dependencies
In workspace-local tool folders, reinstall what is safe to regenerate.
Example:
```bash
cd ~/.openclaw/workspace/.opencode
npm install
```

## 7. Optional local models
If you are not copying `~/.ollama/`, re-pull required models manually.

## 8. Smoke test
Run:
```bash
openclaw status
git status
```
Then verify:
- the workspace opens correctly
- agent files are present
- memory files are present
- Google-dependent workflows can authenticate
- one skill and one sub-agent workflow behave normally

## 9. Always-on readiness
For the new PC, prefer:
- stable network
- persistent OpenClaw service/runtime
- auto-start on boot if desired
- backups for both repo and manual bundle archive

## 10. Suggested first migration commit on source PC
Before moving, commit the migration docs and any wanted pending workspace changes so the repo itself becomes the primary portable brain.
