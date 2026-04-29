# PlayerV2 Phoenix — Appendix Draft

Date: 2026-04-29
Target: playerv2-phoenix
Status: Draft

## Appendix purpose

This appendix is the holding area for detailed supporting material that is useful for reviewers but too dense for the executive or main technical narrative.

## Recommended appendix sections

### A. Engagement metadata
- target name
- assessment window
- tester name
- scope summary
- testing posture notes

### B. Evidence references
- recon summary path
- enum summary path
- vuln summary path
- vulnerability evidence index path
- live validation plan path for PHX-V05

### C. Key observed local strings and states
Include exact observed values that matter to credibility, for example:
- exposed hostnames
- login prompts
- boot-stage strings
- service names
- crash messages

### D. Key script-review excerpts
Summarize the most relevant logic from:
- `repairman.sh`
- `nctv-watchdog.sh`
- `hardware_lock.py`
- `unlock_vault.py`

### E. CVSS and finding-status table
Recommended columns:
- finding ID
- title
- validation status
- CVSS label
- CVSS score
- severity
- report role

Suggested current mapping:
- PHX-V01 — Verified — CVSS-B 6.8 — Medium — Main finding
- PHX-V02 — Verified — CVSS-B 7.3 — High — Main finding
- PHX-V03 — Verified — CVSS-B 7.1 — High — Main finding
- PHX-V04 — Supported — Unscored — Medium direction — Supporting root cause
- PHX-V05 — Supported — Unscored — Medium direction — Candidate pending live replay
- PHX-V06 — Supported / partially observed — Unscored — Secondary candidate, not reproducible enough yet for scoring
- PHX-V07 — Supported — Unscored — Low-severity candidate or hardening note
- PHX-V08 — Not applicable as standalone vuln — Unscored — Context only

### F. Retest checklist
- trusted-media identity checks across native-slot and USB-presented paths
- fail-closed behavior on hardware-check exceptions
- shell-history secret handling cleanup
- recovery-path authenticity validation
- PHX-V06 repeated boot-cycle timing validation if exploit feasibility is revisited
- PHX-V07 exact shutdown/disruption replay if availability impact is revisited

## Recommended linked artifacts
- `engagements/playerv2-phoenix/vuln/vuln-summary.md`
- `engagements/playerv2-phoenix/vuln/vuln-evidence-index.md`
- `engagements/playerv2-phoenix/vuln/PHX-V05_LIVE_VALIDATION_PLAN_2026-04-29.md`
- `engagements/playerv2-phoenix/reporting/technical-report.md`
- `engagements/playerv2-phoenix/reporting/executive-report.md`
