# Migration Guide

## Goal
Recreate the current OpenClaw pentest workspace on another PC with the least missing state.

## 1. Prepare the new machine
Install the baseline stack first:
- OpenClaw
- git
- Python 3
- any local dependencies used by the workspace
- optional Google/Telegram tooling if you want publishing and messaging continuity

Then clone the repo.

## 2. Restore the workspace repo
Clone this repository into the new workspace location.

Expected result:
- agents/
- skills/
- engagements/
- reporting/
- scripts/
- README.md
- AGENTS.md and other root context files

## 3. Restore local OpenClaw config
Copy the contents of:
- `second-life/copies-private/openclaw-home/`
into the appropriate places under the new machine’s `~/.openclaw/` directory.

Main files to restore first:
- `openclaw.json`
- `credentials/`
- `cron/jobs.json`

Use caution with:
- `devices/`
- `identity/`

These may be machine-linked or session-linked and may need regeneration depending on how the new node is intended to behave.

## 4. Restore workspace-untracked files
Copy these back into the workspace if they are still needed:
- `copies/workspace-untracked/root/.google-creds`
- `copies/workspace-untracked/root/credentials.json`
- `copies/workspace-untracked/scripts/upload_pptx_to_drive.py`
- `copies/workspace-untracked/scripts/pentest_slides_generator.py`
- `copies/workspace-untracked/scripts/auto_slides_pipeline.py`

These matter especially for:
- Google publishing
- branded report/presentation generation
- slide pipeline experiments and helpers

## 5. Re-check git identity
This repo currently uses git author config set locally in the workspace repo.
After migration, verify:
```bash
git config user.name
git config user.email
```

## 6. Validate OpenClaw behavior
Check:
- OpenClaw config loads
- messaging credentials still work
- report publishing still works
- custom skills are present
- specter agents still read their identity files
- branded reporting path still works

## 7. Validate the methodology stack
Make sure these skills exist:
- `pentest-essentials`
- `preengagement-essentials`
- `enum-phase-essentials`
- `vuln-phase-essentials`
- `exploit-phase-essentials`
- `post-phase-essentials`
- `report-phase-essentials`

## 8. Final caution
Do **not** blindly reuse machine identity and device pairing files if the new PC is intended to be a clean logical node. Review `PORTABILITY_NOTES.md` first.
w `PORTABILITY_NOTES.md` first.
