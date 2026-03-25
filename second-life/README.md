# Second Life

This directory is the **migration and resurrection kit** for bringing this OpenClaw setup onto another PC.

It exists because the git repo alone does **not** contain everything needed to recreate the current working environment.

## What this folder is for

Use this folder when you want to:
- move this OpenClaw setup to a new machine
- rebuild the current pentest workspace after reinstalling
- understand what is stored in-repo vs only on the local machine
- preserve important local config and credentials that are not fully represented in git

## What is included

### Guides
- `MIGRATION_GUIDE.md` — step-by-step migration flow
- `EXTERNAL_FILES_INVENTORY.md` — what lives outside repo tracking and why it matters
- `PORTABILITY_NOTES.md` — what is portable, sensitive, or machine-specific

### Copied local files
These are snapshots of important files that were not safely preserved by repo history alone.

#### OpenClaw home config snapshot
Under `copies/openclaw-home/`:
- `openclaw.json`
- `credentials/telegram-default-allowFrom.json`
- `credentials/telegram-pairing.json`
- `cron/jobs.json`
- `devices/paired.json`
- `devices/pending.json`
- `identity/device-auth.json`
- `identity/device.json`

#### Workspace untracked essentials
Sensitive/untracked local copies are under `copies-private/workspace-untracked/`.
- `.google-creds`
- `credentials.json`
- `scripts/upload_pptx_to_drive.py`
- `scripts/pentest_slides_generator.py`
- `scripts/auto_slides_pipeline.py`

## Important warning
This directory contains **sensitive material**.
It may include:
- provider credentials
- Telegram/OpenClaw identity or pairing data
- local publishing credentials
- machine-linked identity files

Handle it like secrets, not normal docs.

## Migration philosophy
The repo gives you the **workspace logic**.
This folder helps preserve the **local machine reality**.
You usually need both.
hy
The repo gives you the **workspace logic**.
This folder helps preserve the **local machine reality**.
You usually need both.
