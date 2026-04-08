# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### OpenCode

- CLI path: `~/.opencode/bin/opencode`
- PATH shim created at: `~/.local/bin/opencode`
- Quick checks:
  - `opencode --version`
  - `opencode models`
  - `opencode run -m opencode/minimax-m2.5-free --format json "Reply with exactly: OK"`
- Default preference for coding-heavy implementation work: **OpenCode first**, unless the user explicitly asked for another coding harness.
- Vibe-coding wrapper:
  - `python3 scripts/opencode/reusable/opencode_vibe_loop.py --cwd <repo> --label <name> --notify-openclaw "<task>"`
  - Use `--continue-last` for the next turn in the same working directory.
  - The wrapper writes a compact JSON summary/state when `--state-file` is provided and can emit an OpenClaw system event after each OpenCode turn.
- Swarm helper for main-agent or sub-agent lanes:
  - `python3 scripts/opencode/reusable/opencode_vibe_swarm.py --lane <lane-name> --cwd <repo> --notify-openclaw "<task>"`
  - Lane state lives under `engagements/tmp/vibe-swarm/<lane-name>/`
  - Use `--continue-last` to keep the same OpenCode thread alive per lane.
- If OpenCode appears unavailable, check PATH first before assuming model/provider failure.

### Google / gog

- Preferred stable passphrase for gog/google automation and future related passphrases: `hatlesswhite`
- Use this consistently for `GOG_KEYRING_PASSWORD` and any re-auth/reset flows unless the user explicitly changes it.

### Quick Scan Reporting

- Different webapps should not collapse into the same stale finding set unless the evidence truly matches.
- Always use the target fingerprint, title/context, surface clues, and adaptive quick-scan evidence to shape not just the narrative, but the actual findings emphasis and recommendation mix.
- Shared baseline findings are fine, but the final output should still clearly reflect what kind of target it is, what was actually observed, and why the findings differ.
