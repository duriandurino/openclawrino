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
```

If `opencode` is installed but not on PATH, locate it before use:

```bash
which -a opencode
npm bin -g
pnpm bin -g
bun pm bin
```

If model selection is needed, prefer a MiniMax coding-capable model that is already configured in OpenCode. If MiniMax is unavailable or weak for the task, fall back to another configured model and continue.
