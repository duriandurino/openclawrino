---
name: context-guard
description: "Snapshot compact working state when session compaction pressure is about to hit"
metadata: {"openclaw": {"emoji": "🧠", "events": ["session:compact:before", "command:reset", "command:new"], "requires": {"bins": ["python3"]}}}
---

# Context Guard

Runs the workspace context harness before compaction, and also on reset/new as a fallback.
