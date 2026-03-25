# Portability Notes

## Portable with caution
These are usually useful to move, but may contain secrets:
- `openclaw.json`
- Telegram credential files
- cron job definitions
- `.google-creds`
- `credentials.json`
- helper scripts used by report publishing

## Machine-specific or node-specific
These may not be safe to reuse blindly on a new PC:
- `identity/device.json`
- `identity/device-auth.json`
- `devices/paired.json`
- `devices/pending.json`

Why:
- they may bind the environment to a specific machine, pairing state, or node identity
- reusing them may be desirable for continuity, or undesirable if the new PC should be treated as a new node

## Recommendation
If the goal is:

### A. "Clone this exact life onto another PC"
Reuse most copied files, including identity/pairing state, but do it carefully.

### B. "Create a fresh OpenClaw machine using this workspace"
Reuse the workspace repo, methodology skills, and selected credentials/config only.
Do not blindly restore device identity or pairing files.

## Security warning
This folder now contains sensitive setup materials.
Do not publish it publicly unless you first remove or rotate secrets.
