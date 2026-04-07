# Reusable Utilities

This directory contains stable, reusable utilities for use across the workspace.

## CVE Lookup

**File:** `cve_lookup.py`

A stable wrapper entrypoint for CVE lookups that delegates to the existing implementation in `vuln/scripts/cve_lookup.py`.

### Usage

```bash
# Single service lookup
python3 scripts/opencode/reusable/cve_lookup.py --service openssh --version "8.2p1"

# Batch analyze enum JSON
python3 scripts/opencode/reusable/cve_lookup.py --file engagements/<target>/enum/parsed/nmap-service-*.json

# Specific CVE lookup
python3 scripts/opencode/reusable/cve_lookup.py --cve CVE-2024-6387

# Local exploit database only
python3 scripts/opencode/reusable/cve_lookup.py --service apache --version "2.4.49" --searchsploit-only

# Show wrapper info
python3 scripts/opencode/reusable/cve_lookup.py --wrapper-info
```

### Purpose

This wrapper provides:
- A stable, discoverable entrypoint under `scripts/opencode/reusable/`
- Delegation to the existing `vuln/scripts/cve_lookup.py` implementation
- Additional `--wrapper-info` flag for debugging

## OpenCode Watcher

**File:** `opencode_watch.py`

A reusable wrapper for supervising `opencode run` in a more reliable way. This is the foundation for "nested vibe coding" workflows, where Hatless White or a subagent uses OpenCode as a live coding helper and wants structured progress/outcome handling instead of blind fire-and-forget execution.

### Usage

```bash
# Minimal run with JSON result
python3 scripts/opencode/reusable/opencode_watch.py \
  --prompt "Reply with exactly: OK" \
  --json

# Run in workspace with fallback model and saved result
python3 scripts/opencode/reusable/opencode_watch.py \
  --cwd /home/dukali/.openclaw/workspace \
  --model opencode/minimax-m2.5-free \
  --fallback-model opencode/gpt-5-nano \
  --prompt "Build a tiny argparse example and summarize it" \
  --save engagements/tmp/opencode-watch-result.json
```

### What it does

- launches `opencode run --format json`
- parses OpenCode JSON events
- tracks step/text progress
- detects stall timeout and hard timeout
- can retry once with a fallback model
- returns a structured result for the caller

### Why it exists

This keeps OpenCode use:
- observable
- easier to automate safely
- less brittle for nested coding workflows

## OpenCode Task Wrapper

**File:** `opencode_task.py`

A thin wrapper on top of `opencode_watch.py` for repeatable nested coding workflows.

### Usage

```bash
# Plan a reusable utility
python3 scripts/opencode/reusable/opencode_task.py \
  --mode plan \
  --utility-class reusable \
  --task "Design a small parser for this JSON output and explain the structure"

# Build with watcher-backed execution
python3 scripts/opencode/reusable/opencode_task.py \
  --mode build \
  --utility-class reusable \
  --task "Build a tiny argparse-based helper and summarize usage" \
  --json
```

### What it does

- wraps a task into a coding-oriented OpenCode prompt
- loads project-local mode guidance
- calls `opencode_watch.py` underneath
- keeps invocation more consistent for main-session and subagent use

## Adding New Utilities

When adding new reusable utilities:
1. Place them in this directory
2. Add usage documentation to this README
3. Ensure they have proper `--help` output
4. Test with safe, non-destructive validation
