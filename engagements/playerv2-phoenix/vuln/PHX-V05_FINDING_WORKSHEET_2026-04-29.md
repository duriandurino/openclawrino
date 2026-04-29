# PHX-V05 — Finding Worksheet

Date: 2026-04-29
Target: playerv2-phoenix
Finding: PHX-V05 — Recovery-path abuse potential via `repairman.sh`

## Current state

- **Validation status:** Supported
- **Reportability:** Candidate-stage report inclusion is justified
- **Scoring state:** CVSS fields remain intentionally unscored pending live acceptance proof
- **Why:** Code-backed recovery logic and restore behavior are evidenced, but attacker-controlled recovery content acceptance has not yet been demonstrated live on target or sacrificial media.

## Finding contract

- **finding_id:** PHX-V05
- **title:** Recovery-path abuse potential via `repairman.sh`
- **severity:** Medium
- **validation_status:** Supported
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** null
- **cvss_vector:** null
- **cvss_severity:** Medium
- **cvss_rationale:** Supported candidate. Recovered Phoenix recovery scripts show an automatic USB recovery path that performs direct SD repair and `rsync` mirroring from the USB runtime onto protected media without a visible cryptographic authenticity gate in the reviewed script body. This is enough to treat the issue as a stronger supported candidate, but not enough to assign a defensible final CVSS score until live acceptance of attacker-controlled recovery content is proven or disproven.
- **cvss_assumptions:** The current assessment intentionally stops before assigning exploitability metrics because the required repair image or alternate test image was unavailable during this pass. Threat and Environmental metrics are also not enriched yet. Publish as candidate-stage only unless a later validation run confirms that operator-controlled or attacker-controlled recovery content is accepted before write actions.
- **cve_ids:** []
- **cwe_ids:** ["CWE-494", "CWE-829"]

## Root cause summary

The Phoenix recovery design appears to trust a USB-booted repair environment enough to:
- enter a recovery workflow automatically when expected device conditions are present
- run repair actions against the SD card
- mirror content from the USB runtime onto the SD card using `rsync`
- restore configuration and service state before reboot

In the recovered script review, no visible signature verification, bundle authenticity check, or operator-authentication gate was identified before restore actions proceed.

## Evidence baseline

### Script-backed observations
- `repairman.sh` is designed to run automatically in the Phoenix USB recovery context
- in surgery mode it performs `fsck` on `/dev/mmcblk0p1` and `/dev/mmcblk0p2`
- it mounts the SD root and mirrors `/` from the USB runtime onto the SD root via `rsync`
- it rebuilds `fstab`, restores firmware config, forces graphical target/lightdm, toggles services, and reboots
- no visible signature or authenticity check was observed in the reviewed restore path before the copy/restore logic

### Current evidentiary limit
What is not yet proven:
- that the real target will accept attacker-controlled recovery content in practice
- that no hidden validation step exists outside the recovered script body
- that benign operator-controlled marker content can be written to sacrificial media through the real workflow

## Impact statement

If later verified, PHX-V05 would represent a high-confidence integrity weakness in the recovery path: an attacker with appropriate physical access and recovery-path control could potentially restore attacker-chosen content to protected media without passing a meaningful authenticity gate.

At the current state, the finding should be presented as a supported candidate with meaningful concern, not a completed exploit.

## Decision rule for later promotion

Promote PHX-V05 toward verified only if one of the following is demonstrated in controlled validation:
- the target accepts operator-controlled recovery-script logic up to a trusted marker point without a signature/auth gate
- the target reaches recovery write stages from an operator-controlled Phoenix-style USB source without hidden trust validation
- benign marker content is copied onto sacrificial media through the recovery workflow

## Provisional scoring direction after verification

If Phase A or Phase B validation succeeds, likely next scoring posture:
- **Label:** start with `CVSS-B`
- **Then consider:** `CVSS-BT` or `CVSS-BTE` only if threat/environment enrichment is intentionally added
- **Likely impact direction:** integrity-heavy finding, possibly with availability impact depending on overwrite behavior
- **Likely attack narrative:** physically local attacker controls recovery medium and abuses trusted recovery path to influence protected system state

Do not lock a final vector until live acceptance evidence exists.

## Recommended next step

Use the existing live-validation package:
- `engagements/playerv2-phoenix/vuln/PHX-V05_LIVE_VALIDATION_PLAN_2026-04-29.md`
- `engagements/playerv2-phoenix/vuln/PHX-V05_OPERATOR_RUNBOOK_2026-04-29.md`
- `engagements/playerv2-phoenix/vuln/PHX-V05_SAFE_MARKERS_2026-04-29.md`
- `engagements/playerv2-phoenix/vuln/PHX-V05_RESULT_TEMPLATE_2026-04-29.md`

Until that run happens, keep PHX-V05 in the report as:
- supported
- unscored
- candidate-stage only
