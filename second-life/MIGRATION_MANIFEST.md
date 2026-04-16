# Hatless White Migration Manifest

## Goal
Move this OpenClaw workspace to another PC where the session stays active and available full-time, while preserving Hatless White's identity, memory, skills, sub-agents, and operator workflow.

## Migration Strategy

### Push to git
Push the workspace repo with:
- identity and persona files
- agent definitions
- skill folders and packaged skill artifacts
- scripts, docs, templates, state files that are safe to version
- engagement notes and lightweight deliverables that are already tracked
- migration docs in `second-life/`

### Carry manually outside git
Bring these separately:
- Google auth and token material
- Git credentials / SSH keys / PATs
- any local OpenClaw config outside the workspace
- session/runtime state that lives outside this repo
- large or ignored files you do not want in git

## Core files that define Hatless White

### Primary identity
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `AGENTS.md`
- `TOOLS.md`
- `MEMORY.md`

### Active working memory and state
- `STATE.md`
- `WORKING.md`
- `OPEN_LOOPS.md`
- `DECISIONS.md`
- `HEARTBEAT.md`
- `state/`
- `memory/` (gitignored, copy manually)

### Sub-agent identity files
- `agents/specter-coder.md`
- `agents/specter-recon.md`
- `agents/specter-enum.md`
- `agents/specter-vuln.md`
- `agents/specter-exploit.md`
- `agents/specter-post.md`
- `agents/specter-report.md`
- `agents/specter-skillcrafter.md`

### Skill sources and packaged artifacts
- `skills/`
- `skillcrafter/`
- `recon/`
- `enum/`
- `exploit/`
- `post/`
- `reporting/`
- `vuln/`
- `dist/`
- `*.skill`

### Workspace automation and docs
- `scripts/`
- `docs/`
- `templates/`
- `README.md`
- `GIT_SETUP.md`
- `GIT_SETUP_WIN11.md`
- `OLLAMA_SETUP.md`
- `workspace-structure.md`

## Sensitive credentials and auth to carry manually
These should NOT be relied on through git sync.

### Workspace-local sensitive files already excluded
- `credentials.json`
- `.google-creds`
- `memory/`
- `*.log`
- `*.key`
- `*.pem`
- `*.cred`
- `*.pcap`
- `*.pcapng`
- `*.cap`
- `*.hash`
- `*.john`

### Likely external auth/config locations to export from the old PC
Check and migrate as needed:
- `~/.ssh/`
- `~/.gitconfig`
- `~/.config/git/` if used
- Git credential helper storage, for example:
  - `~/.git-credentials`
  - desktop keyring / libsecret entries
  - GitHub CLI auth such as `~/.config/gh/`
- OpenClaw config/state outside workspace, for example:
  - `~/.openclaw/` except large caches you do not need
  - gateway or node config if used on host
- OpenCode config if you want continuity:
  - `~/.opencode/` minus reinstallable deps/cache if desired
- npm/nvm context if needed for tools:
  - `~/.config/nvm/`
- Ollama models and config if you want local models ready immediately:
  - `~/.ollama/`
- Google auth material used by gog or related tooling:
  - confirm token/cache/keyring-backed auth on the source machine

## Important session continuity notes

### What git will preserve well
- Hatless White's persona, instructions, and workflow conventions
- sub-agent definitions
- skill source files
- scripts and automation logic
- curated long-term memory in `MEMORY.md`
- tracked engagement artifacts and notes

### What git will NOT preserve by itself
- live session threads
- provider logins and browser-backed auth sessions
- OS keyring entries
- gitignored daily memory files
- external model downloads
- local CLI installs outside repo

## Recommended migration procedure
1. Clean and commit the workspace repo.
2. Push all safe changes to remote git.
3. Copy the manual bundle items listed in `second-life/MANUAL_BUNDLE_CHECKLIST.md`.
4. On the new PC, install system prerequisites and clone the repo.
5. Restore credentials and external configs.
6. Restore `memory/` and other gitignored state.
7. Validate OpenClaw, gog, git, OpenCode, and optional Ollama.
8. Run a small smoke test with main agent plus one sub-agent.

## Validation checklist on the new PC
- repo cloned successfully
- `openclaw status` works
- workspace opens at `/home/dukali/.openclaw/workspace` or intended new path
- git push/pull works
- Google auth works for gog workflows
- OpenCode is available if desired
- required models/tools are installed
- `MEMORY.md` and `memory/` are present
- sub-agent files exist under `agents/`
- skill files exist under `skills/`
- state files restored under `state/`

## Notes
- `BOOTSTRAP.md` still exists in repo. Keep or remove intentionally.
- `memory/` is currently gitignored, so manual copy is mandatory if you want full recall continuity.
- `.opencode/node_modules/` is reinstallable and should not be treated as a critical artifact.
