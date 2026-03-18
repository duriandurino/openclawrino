# Calendar Log Examples

## Example 1: Pentest EOD (All-day)

```bash
gog calendar create "primary" \
  --summary "EOD — Vault Pentest (2026-03-18)" \
  --all-day \
  --from "2026-03-18" \
  --to "2026-03-18" \
  --account hatlesswhite@gmail.com \
  --description "🎯 Vault decrypted via hardcoded Pi serial (15 min)
📦 Deliverables: Report (28KB), Slides (9 slides), 9 findings
🔍 V-012: Hardcoded key (CRITICAL 9.1)
🛡️ pentest-slides skill created
📊 Status: Complete"
```

## Example 2: Milestone Log (Specific Time)

```bash
gog calendar create "primary" \
  --summary "Milestone — gog CLI Auth Complete" \
  --from "2026-03-18T14:00:00+08:00" \
  --to "2026-03-18T14:15:00+08:00" \
  --account hatlesswhite@gmail.com \
  --description "✅ Google Cloud project created
✅ OAuth credentials configured
✅ Gmail, Drive, Docs, Sheets APIs enabled
📊 Status: Complete"
```

## Example 3: FULL DAY Capture (Recommended)

```bash
gog calendar create "primary" \
  --summary "EOD — Full Day (2026-03-18)" \
  --all-day \
  --from "2026-03-18" \
  --to "2026-03-18" \
  --account hatlesswhite@gmail.com \
  --description "🎯 Vault decrypted via hardcoded Pi serial (15 min)
📦 Report (28KB), Google Docs, Slides (9 slides)
🔍 V-012: Hardcoded key (CRITICAL 9.1), 9 total findings
🛠️ Built: pentest-slides + calendar-log skills
🛠️ Configured: gog CLI, Google Cloud project, OAuth
📊 Status: Complete"
```

### How to Capture Full Day

Before creating the event:
1. Check `memory/YYYY-MM-DD.md` for all entries
2. Run `git log --oneline --since="2026-03-18"` for commits
3. Review sessions/sub-agents spawned
4. List all skills created or modified

Then compile into single comprehensive entry.

## Example 4: In-Progress Day

```bash
gog calendar create "primary" \
  --summary "EOD — Network Recon (2026-03-19)" \
  --all-day \
  --from "2026-03-19" \
  --to "2026-03-19" \
  --account hatlesswhite@gmail.com \
  --description "🎯 Port scanning complete, 3 services found
📦 Deliverables: nmap results, service enumeration
🔍 SSH open on port 22, HTTP on 80
📊 Status: In Progress (vuln analysis next)"
```
