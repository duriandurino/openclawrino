# OpenCode CLI Notes

Project-local prep for this workspace assumes these documented capabilities:

- `opencode run <prompt>` for non-interactive execution
- built-in `build` mode for file changes and shell use
- built-in `plan` mode for planning without edits
- MCP management via `opencode mcp add|list|auth`
- project-scoped custom modes via `.opencode/modes/*.md`

Quick verification commands:

```bash
command -v opencode
opencode --version
opencode models
opencode mcp list
python3 scripts/opencode/reusable/opencode_watch.py --prompt "Reply with exactly: OK" --json
```

If `opencode` is installed but not on PATH, locate it before use:

```bash
which -a opencode
npm bin -g
pnpm bin -g
bun pm bin
```

If model selection is needed, prefer a MiniMax coding-capable model that is already configured in OpenCode. If MiniMax is unavailable or weak for the task, fall back to another configured model and continue.

Preferred watcher-backed invocation for non-trivial work:

```bash
python3 scripts/opencode/reusable/opencode_task.py \
  --mode build \
  --utility-class reusable \
  --task "Build this coding utility for an authorized workflow and summarize the result"
```

This wrapper uses `opencode_watch.py` underneath so the run is supervised and can fall back cleanly.
