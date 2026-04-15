# Operator Checklist

Use this checklist inside the package while working on the Raspberry Pi.

## Pre-run
- [ ] Confirm authorization and scope still apply
- [ ] Confirm stop conditions are understood
- [ ] Confirm you are inside the package root
- [ ] Run `bash scripts/00-prereq-check.sh`
- [ ] Review `docs/assessment-profile.md`
- [ ] Review `docs/handoff-notes.md`

## Live run order
- [ ] Run `bash scripts/00-bootstrap-engagement.sh`
- [ ] Run `bash scripts/10-live-baseline.sh`
- [ ] Record screenshots or photos of live UI if relevant
- [ ] Run `bash scripts/20-network-check.sh <target-ip>` from an authorized same-segment host
- [ ] Run `bash scripts/30-local-surface-enum.sh`
- [ ] Run `bash scripts/40-secret-and-artifact-triage.sh`

## Validation discipline
- [ ] Do not claim a finding unless it is reproducible now
- [ ] Prefer copies of artifacts over originals for testing
- [ ] Preserve hashes before validation attempts
- [ ] Record exact commands, outputs, and file paths
- [ ] Preserve blocked paths and negative results

## Reporting
- [ ] Update `reports/evidence-log.md` continuously
- [ ] Promote only validated findings into `reports/findings.md`
- [ ] Keep `reports/report.md` as the source of truth
- [ ] Update `docs/handoff-notes.md` before stopping

## Export
- [ ] Run `bash scripts/95-export-bundle.sh`
- [ ] If export tooling is missing, review `reports/BUNDLE_NOTES_*.md`
- [ ] Confirm final report and slide markdown outputs were generated
