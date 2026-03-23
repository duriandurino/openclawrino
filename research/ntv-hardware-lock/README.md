# NTV Phoenix & Hardware Lock

Dedicated workspace for pass-down docs about the NTV360 Hardware Lock and Phoenix (player repair tool).

## Purpose

This folder is the clean local knowledge base for learning, reverse-engineering, and maintaining the turnover material left by the previous developer.

## Structure

- `source/drive/root/` — files downloaded from the shared Google Drive root
- `source/drive/kent_turnover/` — files from the unorganized turnover folder
- `notes/ARCHITECTURE_SUMMARY.md` — distilled technical summary
- `notes/LEARNING_PATH.md` — suggested study order and what to validate next
- `notes/OPEN_QUESTIONS.md` — gaps, assumptions, and things to confirm live

## High-level understanding

There are 3 major moving parts:

1. **Player stack** — Raspberry Pi signage runtime (`player-server`, UI, Chromium kiosk, PM2, NGINX)
2. **Hardware Lock** — verifies device identity before allowing the secure player stack to run
3. **Phoenix** — field recovery model for repairing or temporarily reviving broken players from USB

## Important caution

Some docs contain secrets-like material (for example device identifiers / config keys). Treat this folder as sensitive internal documentation.
