# Penetration Test Report — hardwareLockV2

**Status:** Final
**Date:** 2026-04-14
**Target:** hardwareLockV2
**Overall Risk:** Medium
**Findings:** 3

---

## 1. Executive Summary

This assessment identified **3 findings** across the target:

| Severity | Count |
|----------|-------|
| Medium | 3 |

### Priority Actions

1. **Local authorization configuration can be altered via hardware-lock.env** (Medium) — A local attacker with sufficient write access can weaken trust in the first-layer hardware authorization mechanism and make the device
2. **Encrypted vault remained the effective security boundary** (Medium) — The secure runtime could not be recovered or executed from the surviving local artifacts, limiting compromise despite the weaker
3. **Phoenix recovery chain is critical but missing from the current image** (Medium) — Runtime recovery on the current box is blocked because the device lacks the original Phoenix installer context or equivalent restore source.

---

## 2. Scope, ROE, and Methodology

- Assessment type: structured penetration test
- Methodology: Reconnaissance, Enumeration, Vulnerability Analysis, Exploitation, Post-Exploitation, Reporting

---

## 3. Findings Summary

| ID | Finding | Severity | Asset |
|----|---------|----------|-------|
| F-001 | Local authorization configuration can be altered via hardware-lock.env | Medium | hardwareLockV2 local authorization layer |
| F-002 | Encrypted vault remained the effective security boundary | Medium | /var/lib/nctv-phoenix/vault.img |
| F-003 | Phoenix recovery chain is critical but missing from the current image | Medium | hardwareLockV2 guarded runtime recovery path |

---

## 4. Attack Path / Engagement Story

- Primary engagement story: Local authorization configuration can be altered via hardware-lock.env was the strongest triage signal during this assessment.
- Strongest observed impact: A local attacker with sufficient write access can weaken trust in the first-layer hardware authorization mechanism and make the device appear authorized even when the original tuple has changed.
- This path remains a triage hypothesis until validated through deeper manual testing.

---

## 5. Detailed Findings

### F-001 — Local authorization configuration can be altered via hardware-lock.env

- **Severity:** Medium
- **CVSS Score:** N/A
- **Affected Target:** hardwareLockV2 local authorization layer
- **Description:** The device authorization decision depends on values stored in /etc/nctv-phoenix/hardware-lock.env. Testing showed these values can be changed locally, allowing the current hardware tuple to satisfy the initial authorization gate.
- **Evidence:** ```
Reviewed hardware_lock.py, unlock_vault.py, and hardware-lock.env; confirmed gate success once env values were aligned to current hardware.
```
- **Impact:** A local attacker with sufficient write access can weaken trust in the first-layer hardware authorization mechanism and make the device appear authorized even when the original tuple has changed.
- **Remediation:** Protect hardware-lock.env with stronger integrity controls, minimize who can modify it, and remove reliance on mutable plaintext authorization values as the primary trust anchor.
- **Hardening:** Bind authorization to tamper-evident state such as signed metadata, sealed secrets, or secure hardware-backed attestation rather than editable local config alone.
- **References:** EVI-003, EVI-004, EVI-005

### F-002 — Encrypted vault remained the effective security boundary

- **Severity:** Medium
- **CVSS Score:** N/A
- **Affected Target:** /var/lib/nctv-phoenix/vault.img
- **Description:** Even after the authorization layer was aligned to the current hardware tuple, the LUKS-backed vault did not unlock and the secure runtime was not exposed. This shows the encrypted vault remained the effective protection boundary in the tested state.
- **Evidence:** ```
Observed cryptsetup failure from unlock_vault.py and absence of mounted secure runtime paths.
```
- **Impact:** The secure runtime could not be recovered or executed from the surviving local artifacts, limiting compromise despite the weaker authorization layer.
- **Remediation:** Preserve the cryptographic separation, review the unlock/provisioning workflow for secure provenance, and maintain recoverable records for original authorized tuples and guarded runtime provenance.
- **Hardening:** Keep vault unlocking dependent on stronger secrets or device-bound material, and add signed provenance checks for restore/install artifacts.
- **References:** EVI-004, EVI-005, EVI-006, EVI-007

### F-003 — Phoenix recovery chain is critical but missing from the current image

- **Severity:** Medium
- **CVSS Score:** N/A
- **Affected Target:** hardwareLockV2 guarded runtime recovery path
- **Description:** Recovered installer evidence showed that setup.enc is only a bootstrap. It installs nctv-player, then downloads and decrypts phoenix.enc and runs phoenix_install.sh --guard. Those second-stage Phoenix artifacts were not present locally during the assessment.
- **Evidence:** ```
Decrypted setup.enc locally and reviewed install flow; searched local paths for Phoenix artifacts; reviewed repairman dependency on external nctv-phoenix tree.
```
- **Impact:** Runtime recovery on the current box is blocked because the device lacks the original Phoenix installer context or equivalent restore source.
- **Remediation:** Treat Phoenix installer artifacts, recovery media, and provenance records as critical assets. Store them securely, version them, and ensure legitimate recovery paths are available for authorized maintenance and incident response.
- **Hardening:** Use signed recovery packages, audited retention of restore media, and explicit inventory of the guarded artifact chain so recovery does not depend on undocumented external residue.
- **References:** EVI-008, EVI-009, EVI-010, EVI-011, EVI-012, EVI-013

---

## 6. Remediation Roadmap

**Immediate**
- No immediate remediation items captured

**Short-term**
- F-001 — Remediate the issue and confirm the fix in a follow-up validation scan
- F-002 — Remediate the issue and confirm the fix in a follow-up validation scan
- F-003 — Treat Phoenix installer artifacts, recovery media, and provenance records as critical assets

**Medium-term hardening**
- No medium-term hardening items captured

---

## 7. Security Enhancement Recommendations

### Authorization Integrity

Replace editable plaintext authorization tuples with tamper-evident or hardware-backed authorization data.

### Recovery Provenance

Maintain secure, documented, and recoverable copies of Phoenix installer artifacts and approved repair media.

### Operational Resilience

Record original hardware-binding values and guarded recovery dependencies in a controlled maintenance process so legitimate support does not depend on ad hoc external artifacts.

### Monitoring

Alert on repeated repair-loop behavior, missing runtime trees, and failed guarded restore attempts to shorten time-to-diagnosis.

---

## 8. Cleanup / Restoration Status

- Tester-created artifacts introduced: none captured by this reporting workflow
- Cleanup performed: not applicable for markdown report generation artifacts
- Remaining changes on target: unknown from quick-scan triage alone, validate during deeper follow-up if needed
- Residual risk: candidate findings may still indicate meaningful exposure until manually validated and remediated

---

## 9. Retest Guidance / Recommended Next Action

- Re-test after remediation by rerunning the same profile and manually validating whether the previously observed exposure still reproduces.

---

## 10. Appendices

### A. Risk Summary Matrix

| ID | Finding | Severity | Remediation Priority |
|----|---------|----------|---------------------|
| F-001 | Local authorization configuration can be altered via hardware-lock.env | Medium | Scheduled |
| F-002 | Encrypted vault remained the effective security boundary | Medium | Scheduled |
| F-003 | Phoenix recovery chain is critical but missing from the current image | Medium | Scheduled |

### B. Tools Used

- nmap, masscan (enumeration)
- Metasploit, custom scripts (exploitation)
- Shodan, crt.sh (OSINT)
- Burp Suite, curl (web testing)

### C. Scope Boundaries

All testing was conducted within the authorized scope. No denial-of-service attacks were performed without explicit permission.
