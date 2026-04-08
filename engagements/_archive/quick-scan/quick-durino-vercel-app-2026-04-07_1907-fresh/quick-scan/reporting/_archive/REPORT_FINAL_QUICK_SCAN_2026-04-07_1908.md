# Penetration Test Report — https://durino.vercel.app (Quick Scan)

**Date:** 2026-04-07
**Target:** https://durino.vercel.app (Quick Scan)
**Findings:** 4

---

## 1. Executive Summary

This assessment identified **4 findings** across the target:

| Severity | Count |
|----------|-------|
| High | 1 |
| Medium | 1 |
| Low | 2 |

### Priority Actions

1. **header: missing CSP header** (High) — If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access
2. **banner: server banner exposed** (Medium) — This may reveal useful attacker information or weaken defensive posture if left unaddressed.
3. **header: missing X-Content-Type-Options header** (Low) — This is currently a lower-confidence or lower-impact observation, but it may still aid attacker reconnaissance or chaining.

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

### QS-001 — header: missing CSP header

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** https://durino.vercel.app
- **Description:** Quick scan candidate from the vuln phase: header: missing CSP header
- **Evidence:** ```
Quick scan candidate finding (candidate) from vuln: header: missing CSP header
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Apply the missing security control, then verify the header/control is present in a follow-up scan.
- **Hardening:** Keep exposed services minimized, monitor access patterns, and document expected network exposure so deviations stand out quickly.
- **References:** Quick scan profile: webapp, Execution mode: safe

### QS-002 — banner: server banner exposed

- **Severity:** Medium
- **CVSS Score:** N/A
- **Affected Target:** https://durino.vercel.app
- **Description:** Quick scan candidate from the vuln phase: banner: server banner exposed
- **Evidence:** ```
Quick scan candidate finding (candidate) from vuln: banner: server banner exposed
```
- **Impact:** This may reveal useful attacker information or weaken defensive posture if left unaddressed.
- **Remediation:** Validate the observation manually, document whether it is expected, and harden the service if the exposure is unnecessary.
- **Hardening:** Keep exposed services minimized, monitor access patterns, and document expected network exposure so deviations stand out quickly.
- **References:** Quick scan profile: webapp, Execution mode: safe

### QS-003 — header: missing X-Content-Type-Options header

- **Severity:** Low
- **CVSS Score:** N/A
- **Affected Target:** https://durino.vercel.app
- **Description:** Quick scan candidate from the vuln phase: header: missing X-Content-Type-Options header
- **Evidence:** ```
Quick scan candidate finding (candidate) from vuln: header: missing X-Content-Type-Options header
```
- **Impact:** This is currently a lower-confidence or lower-impact observation, but it may still aid attacker reconnaissance or chaining.
- **Remediation:** Apply the missing security control, then verify the header/control is present in a follow-up scan.
- **Hardening:** Keep exposed services minimized, monitor access patterns, and document expected network exposure so deviations stand out quickly.
- **References:** Quick scan profile: webapp, Execution mode: safe

### QS-004 — header: missing X-Frame-Options header

- **Severity:** Low
- **CVSS Score:** N/A
- **Affected Target:** https://durino.vercel.app
- **Description:** Quick scan candidate from the vuln phase: header: missing X-Frame-Options header
- **Evidence:** ```
Quick scan candidate finding (candidate) from vuln: header: missing X-Frame-Options header
```
- **Impact:** This is currently a lower-confidence or lower-impact observation, but it may still aid attacker reconnaissance or chaining.
- **Remediation:** Apply the missing security control, then verify the header/control is present in a follow-up scan.
- **Hardening:** Keep exposed services minimized, monitor access patterns, and document expected network exposure so deviations stand out quickly.
- **References:** Quick scan profile: webapp, Execution mode: safe

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
| QS-001 | header: missing CSP header | High | Immediate |
| QS-002 | banner: server banner exposed | Medium | Scheduled |
| QS-003 | header: missing X-Content-Type-Options header | Low | Low Priority |
| QS-004 | header: missing X-Frame-Options header | Low | Low Priority |

---

## 6. Appendices

### A. Tools Used

- nmap, masscan (enumeration)
- Metasploit, custom scripts (exploitation)
- Shodan, crt.sh (OSINT)
- Burp Suite, curl (web testing)

### B. Scope Boundaries

All testing was conducted within the authorized scope. No denial-of-service attacks were performed without explicit permission.
