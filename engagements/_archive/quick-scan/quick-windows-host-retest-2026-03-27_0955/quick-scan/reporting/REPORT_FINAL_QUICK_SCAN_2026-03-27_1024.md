# Penetration Test Report — 192.168.0.112 (Quick Scan)

**Date:** 2026-03-27
**Target:** 192.168.0.112 (Quick Scan)
**Findings:** 4

---

## 1. Executive Summary

This assessment identified **4 findings** across the target:

| Severity | Count |
|----------|-------|
| High | 4 |

### Priority Actions

1. **RDP exposed** (High) — If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access
2. **SMB exposed** (High) — If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access
3. **WinRM/HTTP management surface exposed** (High) — If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access

---

## 2. Methodology

The assessment followed a structured penetration testing methodology:

1. **Reconnaissance** — Passive information gathering (DNS, WHOIS, OSINT)
2. **Enumeration** — Active service discovery and fingerprinting
3. **Vulnerability Analysis** — CVE matching and manual testing
4. **Exploitation** — Proof-of-concept exploitation of confirmed vulnerabilities
5. **Post-Exploitation** — Privilege escalation and impact assessment
6. **Reporting** — Documented findings with remediation guidance

---

## 3. Findings

### QS-001 — RDP exposed

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the enum phase: RDP exposed
- **Evidence:** ```
Quick scan candidate finding (observed) from enum: RDP exposed
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict RDP to approved admin hosts, require MFA/VPN in front of remote access, and verify Network Level Authentication plus account lockout controls are enforced.
- **Hardening:** Segment management services away from user networks, monitor remote administration events centrally, and enforce least-privilege access for all admin paths.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-002 — SMB exposed

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the enum phase: SMB exposed
- **Evidence:** ```
Quick scan candidate finding (observed) from enum: SMB exposed
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Perform targeted validation immediately, patch or reconfigure the exposed service, and verify the issue is no longer reachable from the current network segment.
- **Hardening:** Segment management services away from user networks, monitor remote administration events centrally, and enforce least-privilege access for all admin paths.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-003 — WinRM/HTTP management surface exposed

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the enum phase: WinRM/HTTP management surface exposed
- **Evidence:** ```
Quick scan candidate finding (observed) from enum: WinRM/HTTP management surface exposed
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict WinRM to trusted administration networks, prefer HTTPS/5986 where possible, and verify only intended admin groups can use remote management.
- **Hardening:** Segment management services away from user networks, monitor remote administration events centrally, and enforce least-privilege access for all admin paths.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-004 — MySQL service exposed

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the enum phase: MySQL service exposed
- **Evidence:** ```
Quick scan candidate finding (observed) from enum: MySQL service exposed
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict MySQL to approved application hosts only, disable public exposure where unnecessary, and verify account/network ACLs for the service.
- **Hardening:** Keep database services on dedicated application/admin networks, monitor for unexpected remote logins, and document the expected client set.
- **References:** Quick scan profile: windows-host, Execution mode: safe

---

## 4. Security Enhancement Recommendations

### Exposure Management

Use quick scan as triage only, then validate high-risk candidates manually before operational changes or client delivery.

### Administrative Surface Reduction

Restrict exposed management services to trusted administration paths, segment them from user networks, and monitor for unexpected remote-access activity.

### Patch and Validation Workflow

For candidate version-based matches, verify the real product/version before remediation, then patch and re-scan to confirm closure.

---

## 5. Risk Summary Matrix

| ID | Finding | Severity | Remediation Priority |
|----|---------|----------|---------------------|
| QS-001 | RDP exposed | High | Immediate |
| QS-002 | SMB exposed | High | Immediate |
| QS-003 | WinRM/HTTP management surface exposed | High | Immediate |
| QS-004 | MySQL service exposed | High | Immediate |

---

## 6. Appendices

### A. Tools Used

- nmap, masscan (enumeration)
- Metasploit, custom scripts (exploitation)
- Shodan, crt.sh (OSINT)
- Burp Suite, curl (web testing)

### B. Scope Boundaries

All testing was conducted within the authorized scope. No denial-of-service attacks were performed without explicit permission.
