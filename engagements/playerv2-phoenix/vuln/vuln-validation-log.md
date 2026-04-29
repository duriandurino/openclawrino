# PlayerV2 Phoenix — Vulnerability Validation Log

Date: 2026-04-29

## Analyst decisions captured

- Decision: **PHX-V01 and PHX-V02 should remain separate**
- Reason: keeping trigger and fail-open effect separate will make scoring, remediation, and reporting cleaner and avoids muddy remediation ownership.

- Decision: **PHX-V03 should be treated as still useful in a real attack if defenders miss it**
- Reason: even when not proven universal across all builds, exposed provisioning commands, passphrases, and workflow details are realistic chaining material in real local compromise paths.

## Validation-state ledger

### PHX-V01
- State: Verified
- Score state: populated as CVSS-B
- Confidence: High
- Note: scoped to the authorization-bypass condition caused by storage-interface-dependent identity handling

### PHX-V02
- State: Verified
- Score state: populated as CVSS-B
- Confidence: High
- Note: scoped to fail-open preserved local access after authorization-check crash

### PHX-V03
- State: Verified
- Score state: populated as CVSS-B
- Confidence: High for exposure, medium-high for exploitation relevance
- Note: current analyst direction treats the exposed provisioning material as operationally useful enough to justify stronger impact framing

### PHX-V04
- State: Supported
- Score state: provisional only
- Confidence: Medium-high
- Note: likely root-cause/supporting architecture unless distinct attacker leverage is proven

### PHX-V05
- State: Supported
- Score state: provisional only
- Confidence: Medium-high
- Note: recovered Phoenix `repairman.sh` and setup artifacts show a real USB recovery path with no visible authenticity gate before restore actions, but live acceptance of attacker-controlled content is not yet proven

### PHX-V06
- State: Supported / partially observed
- Score state: unscored
- Confidence: Medium
- Note: requires reproducibility and action-window validation

### PHX-V07
- State: Supported
- Score state: unscored
- Confidence: Medium
- Note: likely availability or kiosk-hardening finding if retained

### PHX-V08
- State: Not Applicable as standalone vulnerability
- Score state: unscored by design
- Confidence: High as context
- Note: retain only as environment context unless linked to a concrete weakness
