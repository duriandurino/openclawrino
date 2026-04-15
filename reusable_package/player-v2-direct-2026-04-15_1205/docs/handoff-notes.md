# Handoff Notes

## Start here
1. Read `README.md`
2. Review `docs/assessment-profile.md`
3. Run `bash scripts/00-bootstrap-engagement.sh`
4. Run `bash scripts/10-live-baseline.sh`
5. Decide quickly whether the network is worth deeper work or whether to pivot local

## Safe first scripts
- `scripts/00-bootstrap-engagement.sh`
- `scripts/10-live-baseline.sh`
- `scripts/20-network-check.sh <target-ip>`
- `scripts/30-local-surface-enum.sh`
- `scripts/40-secret-and-artifact-triage.sh`

These are collection-oriented and non-destructive by default.

## Areas that require extra caution
- decrypting or modifying live artifacts
- restarting services
- interacting with production ad or sync workflows
- actions that could rotate logs or alter timestamps
- hardware disassembly or storage extraction

## Prior evidence worth keeping in mind
- Similar Player V2 network posture was previously very locked down
- Related work across Phoenix / Hardware Lock / setup.enc suggests local artifact analysis matters more than blind network persistence
- A blocked path is still valuable if it rules out a tempting but unsupported claim

## Assumptions made in this package
- operator has shell access on-box or can open a terminal locally
- bash is available
- basic GNU userland tools exist: `find`, `grep`, `ss`, `ps`, `ip`, `sha256sum`
- optional tools may not exist and scripts should degrade gracefully

## If the original operator stopped midway
- check `logs/`
- check `results/runs/` for the latest timestamped run
- continue writing into `reports/evidence-log.md`
- update `reports/findings.md` only after re-validation
- add your own next actions at the bottom of this file

## Continuation notes
- Package was scaffolded on 2026-04-15 but the working report set was still mostly template text when the prior session was interrupted.
- Prior evidence indicates the highest-yield path is direct local assessment on the Pi, not blind network persistence.
- Treat this package as a reusable direct-assessment kit seeded with prior Player V2 and Hardware Lock evidence.

## Current state
- Prior related evidence across `engagements/player-v2/`, `engagements/playerv2-artifacts/`, and `engagements/playerv2-setup-enc*` was reviewed before building this package.
- Known prior result: `setup.enc` was confirmed as an OpenSSL salted encrypted container and remained unauditable without legitimate decryption knowledge.
- Known prior result: related Hardware Lock V2 work indicates the local box was exhausted as a self-contained recovery source and likely depends on missing external Phoenix or repair artifacts.
- This package currently assumes a fresh direct-on-device run still needs to be performed, but it now carries concrete context so the next operator does not restart from zero.

## Blocked paths already worth preserving
- Network-only attack path looked low-yield in prior evidence, with minimal exposed services and no meaningful passive capture.
- Repeated `setup.enc` decryption hypothesis testing did not produce validated plaintext and should not be reported as a success.
- Restoring player functionality from local placeholders alone is unsupported by current evidence when Phoenix or repair payloads are absent.

## High-value file paths from prior evidence
- `engagements/player-v2/recon/RECON_SUMMARY_2026-03-18_1053.md`
- `engagements/player-v2/enum/ENUM_SUMMARY_2026-03-18_1053.md`
- `engagements/player-v2/vuln/VULN_SUMMARY_2026-03-18_1053.md`
- `engagements/playerv2-artifacts/inbound/setup.enc`
- `engagements/playerv2-artifacts/quick-scan-setup-enc/QUICK_SCAN_SETUP_ENC_2026-04-08_1706.md`
- `engagements/playerv2-setup-enc-final/reporting/REPORT_FINAL_2026-04-09_1420.md`
- `engagements/hardwarelockv2/04-exploit/exploit-summary.md`

## Services and themes already checked in prior evidence
- rpcbind and mDNS level network exposure
- SSH rejection / no usable SSH entry
- Electron, Python service, Player, Phoenix, Hardware Lock, and encrypted artifact workflow
- shell history, service definitions, installer scripts, and encrypted payload recovery clues

## Recommended continuation order
1. Run the package scripts on the live target only if a fresh direct console session is available.
2. Re-validate whether the current device still matches the prior minimal network posture.
3. Prioritize local startup chain, service units, secrets, and artifact workflow over speculative brute force.
4. Preserve negative results and blocked paths in the report, because they materially shape the risk story.
