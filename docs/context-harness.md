# Context Harness

A durable, low-noise session continuity harness for this workspace.

## Goals

- detect rising session pressure using real OpenClaw session metadata when possible
- snapshot compact, high-value working state before context compaction
- stage only narrow state files
- commit only when the snapshot changed
- push safely without destroying the local checkpoint on failure
- make future sessions read the saved state explicitly

## Pressure source

Primary source:
- `openclaw status --json`
- read `sessions.recent[*].percentUsed` for the current session key when available

Fallback source:
- `~/.openclaw/agents/main/sessions/sessions.json`
- read the current session entry and derive percent from `percentUsed`, or from `totalTokens/contextTokens`

Fallback heuristic:
- if neither surface is available, use transcript file size growth only as a weak warning signal, never as authoritative threshold truth

## Thresholds

- warning: 40%
- snapshot: 48%
- cooldown: 20 minutes between automatic snapshots for the same session state
- debounce: skip snapshot if content hash is unchanged

## Files updated by the harness

- `WORKING.md`
- `STATE.md`
- `DECISIONS.md`
- `OPEN_LOOPS.md`
- `state/context-pressure.json`
- `state/session-reset-handoff.json`
- optional append to `memory/YYYY-MM-DD.md`
- `logs/context-harness.log`

## Safety

The harness redacts obvious secrets and never stages:

- `credentials.json`
- `.google-creds`
- `*.pem`, `*.key`, `*.pcap`, `*.hash`, `loot/`, `evidence/`
- transcript files under `~/.openclaw/agents/*/sessions/`
- raw config files outside the tracked workspace snapshot set

## Bootstrap continuity

Future sessions should explicitly read:

1. `WORKING.md`
2. `STATE.md`
3. `OPEN_LOOPS.md`
4. `DECISIONS.md`

This complements, not replaces, the normal memory files.

## Dry run

```bash
python3 scripts/context_harness.py snapshot --current-task "..." --objective "..." --next-step "..." --dry-run
```

## Real snapshot

```bash
python3 scripts/context_harness.py snapshot --current-task "..." --objective "..." --next-step "..." --commit --push
```

## Manual remember checkpoint

Use this when the user wants an immediate post-reset memory pin, even if compaction pressure is low.

```bash
python3 scripts/context_harness.py snapshot --current-task "..." --objective "..." --next-step "..." --trigger manual-remember --force --commit
```

## Check pressure only

```bash
python3 scripts/context_harness.py pressure
```

## Hook integration

A workspace hook can call the harness on `session:compact:before` so the snapshot runs right before compaction pressure bites.
