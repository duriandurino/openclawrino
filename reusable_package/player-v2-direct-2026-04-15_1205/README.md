# Player V2 Direct Pentest Package

This package is for checking a Player V2 Raspberry Pi when you have **physical access** to the device.

## Fast beginner path
If you want the simplest path, use these scripts in order:

```bash
bash scripts/01-player-v2-setup.sh
bash scripts/03-make-work-folder.sh
bash scripts/04-check-device.sh
bash scripts/05-check-network.sh <target-ip>
bash scripts/06-find-local-files.sh
bash scripts/07-find-secrets.sh
bash scripts/08-make-final-package.sh
```

## If tools are missing
Shared installer:
```bash
sudo bash ../_common/scripts/01-common-install.sh
```

Player V2 installer:
```bash
sudo bash scripts/02-install-player-v2-tools.sh
```

## What each easy script does
- `01-player-v2-setup.sh` = first step, checks whether your tools are ready
- `02-install-player-v2-tools.sh` = installs the shared and Player V2 tools
- `03-make-work-folder.sh` = creates your working folder for this run
- `04-check-device.sh` = collects basic system info from the device
- `05-check-network.sh` = checks the target from the network side
- `06-find-local-files.sh` = looks for local app files and services
- `07-find-secrets.sh` = looks for secrets, encrypted files, and clue files
- `08-make-final-package.sh` = creates the final report bundle

## Old advanced scripts still exist
The original scripts are still here if you want them:
- `00-bootstrap-engagement.sh`
- `10-live-baseline.sh`
- `20-network-check.sh`
- `30-local-surface-enum.sh`
- `40-secret-and-artifact-triage.sh`
- `95-export-bundle.sh`

The new numbered beginner scripts are just easier wrappers around those.

## Important docs
- `docs/operator-checklist.md` = shortest checklist
- `docs/assessment-profile.md` = scope and assumptions
- `docs/handoff-notes.md` = prior context and continuation notes
- `docs/export-bundle-explained.md` = simple explanation of the final package script

## Shared setup scripts
Shared check script:
```bash
bash ../../_common/scripts/00-common-setup.sh "$(pwd)"
```

Shared install script:
```bash
sudo bash ../_common/scripts/01-common-install.sh
```

## Reminder
This package helps organize the work.
It does not replace live validation.
Only report what you can still prove now.
