---
name: gworkspace
description: "Create and manage Google Docs, Slides, Sheets, Gmail, Calendar, and Contacts via the gog CLI. Use when the user asks to create a document, presentation, spreadsheet, send email, or manage calendar events in Google Workspace."
metadata:
  openclaw:
    emoji: "📊"
    priority: 50
author: Hatless White
dependencies: [gog]
---

# Google Workspace CLI (gog)

Create Google Docs, Slides, Sheets, Gmail, Calendar, and Contacts using the `gog` CLI.

## Account & Authentication

```bash
gog auth list                              # Show all authed accounts
gog auth add <email> --services <services> # Auth a new account
```

The account's consent screen must be configured via Google Cloud Console and OAuth credentials loaded via `gog auth credentials <path>`.

## ⚡ Quick Reference

| Task | Command |
|------|---------|
| **Search emails** | `gog gmail search 'subject:report newer_than:2d' --json` |
| **Send email** | `gog gmail send --to a@b.com --subject Hi --body Hello` |
| **List Drive files** | `gog drive search 'root' --json` |
| **Upload to Drive** | `gog drive upload /path/to/file` |
| **Create presentation** | `gog slides create-from-markdown 'Title' --content-file report.md` |
| **Export presentation** | `gog slides export <id> -o out.pptx` |
| **Create spreadsheet** | `gog sheets create 'My Sheet'` |
| **Read spreadsheet** | `gog sheets read <sheet-id> 'Sheet1'` |
| **Contacts lookup** | `gog contacts search 'john' --json` |

## 🎯 Creating Slides from Markdown

**This is the primary use case for pentest reports.** Use the simple command — it already handles headers, bullets, and slide breaks correctly.

```bash
gog slides create-from-markdown "Pentest Report" \
  --content-file /path/to/report.md \
  --account hatlesswhite@gmail.com
```

**What gog handles natively:**
- `# Title` → Slide title
- `## Subtitle` → Subtitle
- `- item` → Bullet points
- `**bold**` → Bold text
- `---` → New slide break

**Do NOT pre-process markdown** — the simple command produces better results than complex HTML conversion.

## Creating Google Docs from Markdown

gog doesn't support direct Docs creation from markdown. Alternatives:

1. **Use gog slides** (renders all content beautifully, can be exported as PDF)
2. **Upload HTML to Drive** → Open with Google Docs (manual conversion step)
3. **Paste content** directly into Google Docs via browser

## Gmail

```bash
gog gmail search 'subject:report newer_than:1d' --json
gog gmail send --to a@b.com --subject "Report" --body "See attached" --attachments /path/to/file.pdf
gog gmail attachments download <msg-id> <attachment-id> --output /tmp/
```

## Calendar

```bash
gog calendar events --json
gog calendar create "Pentest Debrief" --start "2026-03-20T14:00:00" --end "2026-03-20T15:00:00"
```

## Drive Operations

```bash
gog drive search "'root' and name contains 'report'" --json
gog drive download <file-id> --output /tmp/
gog drive upload /path/to/file.pdf
```

## Reporting Workflow

When generating pentest reports:

1. Write markdown report in workspace (`engagements/<target>/report/REPORT_FINAL_YYYY-MM-DD_HHMM.md`)
2. Run: `gog slides create-from-markdown "Title" --content-file <report.md>`
3. Share the Google Slides URL with stakeholders
4. Export as PDF if needed: `gog slides export <id> -o report.pdf`
