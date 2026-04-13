# Findings Register

| Finding ID | Status | Title | Affected asset | Evidence | Impact | Likelihood | Risk | CVSS | Remediation |
|---|---|---|---|---|---|---|---|---|---|
| F-001 | validated | Local authorization config can be altered via hardware-lock.env | hardwareLockV2 | EVI-003, EVI-004, EVI-005 | Gate check can be aligned to current hardware without the original authorized tuple | high with local file edit access | medium | N/A | Protect config integrity, restrict write access, and bind authorization to tamper-evident state |
| F-002 | validated | Secure payload remains protected by independent LUKS vault key | hardwareLockV2 | EVI-004, EVI-005, EVI-006 | Edited authorization values do not unlock the real vault or expose player runtime files | high | medium | N/A | Keep cryptographic separation and add secure provenance checks for unlock logic |
