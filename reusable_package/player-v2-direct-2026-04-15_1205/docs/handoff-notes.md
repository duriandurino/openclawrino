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
- [Add current state here]
- [Add blocked paths here]
- [Add high-value file paths here]
- [Add services already checked here]
