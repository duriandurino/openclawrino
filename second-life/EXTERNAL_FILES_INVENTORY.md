# External Files Inventory

These are important files that are **not fully preserved by the git repo alone**.

## Outside workspace / outside repo root

### `~/.openclaw/openclaw.json`
Why it matters:
- main OpenClaw configuration
- likely includes node/runtime/provider settings

### `~/.openclaw/credentials/telegram-default-allowFrom.json`
Why it matters:
- Telegram allowlist behavior

### `~/.openclaw/credentials/telegram-pairing.json`
Why it matters:
- Telegram pairing/config state

### `~/.openclaw/cron/jobs.json`
Why it matters:
- scheduled jobs/reminders/automation state

### `~/.openclaw/devices/*`
Why it matters:
- paired/pending device state

### `~/.openclaw/identity/*`
Why it matters:
- local device/node identity
- may be machine-specific

## Inside workspace but currently untracked / not safely preserved by repo

### `.google-creds`
Why it matters:
- local Google integration credentials/config

### `credentials.json`
Why it matters:
- Google/API/service auth material used by workspace flows

### `scripts/upload_pptx_to_drive.py`
Why it matters:
- helper for Drive upload / presentation publishing workflow

### `scripts/pentest_slides_generator.py`
Why it matters:
- branded slide/pptx generation support

### `scripts/auto_slides_pipeline.py`
Why it matters:
- slide pipeline helper / PoC path

## Not copied intentionally
Some files were **not** included as part of the Second Life snapshot because they are not core setup state or are too transient/noisy:
- logs/
- media/inbound/
- sqlite memory databases
- command/update offset files
- transient run state

Those may still matter for forensics/history, but they are not primary setup dependencies.
