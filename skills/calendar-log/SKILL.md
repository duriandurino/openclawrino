---
name: calendar-log
description: Log daily activities to Google Calendar as concise EOD summaries. Use when creating end-of-day summaries, logging milestones to calendar, tracking pentest progress, or when asked to "log to calendar" or "create EOD entry". Creates clean, scannable calendar events.
---

# Calendar Log

Create concise, well-formatted calendar entries for daily activity tracking.

## Quick Start

```bash
gog calendar create "primary" \
  --summary "EOD — [Topic] ([Date])" \
  --from "YYYY-MM-DDTHH:MM:00+08:00" \
  --to "YYYY-MM-DDTHH:MM:00+08:00" \
  --account hatlesswhite@gmail.com \
  --description "[formatted summary]" \
  --all-day
```

## Format Rules

### Event Title Pattern
```
EOD — [Topic/Project] (YYYY-MM-DD)
```
Examples:
- `EOD — Vault Pentest (2026-03-18)`
- `EOD — GWorkspace Setup (2026-03-18)`

### Description Format (Concise)
Use this exact structure — **MAX 15 lines**:

```
🎯 [Main Achievement]

📦 Deliverables
• [Item 1]
• [Item 2]

🔍 Key Findings
• [Finding 1]
• [Finding 2]

📊 Status: [In Progress / Complete / Blocked]
```

### Alternative: Milestone Log
For logging specific events (not EOD):
```
[Milestone Type] — [Brief Description]
• What: [One line]
• Status: ✅ Done / 🔄 In Progress / ❌ Blocked
```

## Time Options

| Type | Flags |
|------|-------|
| All-day event | `--all-day --from "YYYY-MM-DD" --to "YYYY-MM-DD"` |
| Specific time | `--from "YYYY-MM-DDTHH:MM:00+08:00" --to "..."` |
| End of day | `--from "...T18:00:00" --to "...T18:30:00"` |

## Workflow

```
1. COLLECT activities from session/memory
2. FORMAT using template above
3. CREATE calendar event with gog
4. CONFIRM event link returned
```

## Example: Pentagon Test EOD

```bash
gog calendar create "primary" \
  —summary "EOD — Vault Pentest (2026-03-18)" \
  —all-day \
  —from "2026-03-18" \
  —to "2026-03-18" \
  —account hatlesswhite@gmail.com \
  —description "🎯 Vault decrypted (15 min)
📦 Full report, slides, 9 findings
🔍 V-012: Hardcoded key (CRITICAL)
📊 Status: Complete"
```

## Guidelines

1. **Keep it under 15 lines** — calendar should be scannable
2. **Use emojis sparingly** — 🎯📦🔍📊 for section headers only
3. **No timestamps** — just high-level activities
4. **One event per day per project** — don't clutter
5. **Bullet points over paragraphs** — always
