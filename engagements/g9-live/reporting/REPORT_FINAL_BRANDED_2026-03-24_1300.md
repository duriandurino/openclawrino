# Penetration Test Report — G9 (192.168.0.227)

**Date:** 2026-03-24
**Target:** G9 (192.168.0.227)
**Findings:** 1

---

## 1. Executive Summary

This assessment identified **1 findings** across the target:

| Severity | Count |
|----------|-------|
| Low | 1 |

### Priority Actions

1. **RDP supports legacy TLS 1.0 and TLS 1.1** (Low) — An attacker positioned to intercept or downgrade traffic may benefit from weaker legacy cryptographic settings. While th

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

### G9-001 — RDP supports legacy TLS 1.0 and TLS 1.1

- **Severity:** Low
- **CVSS Score:** 3.1
- **Affected Target:** 192.168.0.227:3389 (RDP)
- **Description:** The Remote Desktop service on G9 supports deprecated TLS protocol versions 1.0 and 1.1 in addition to modern versions. Legacy TLS support weakens transport security posture and may expose the service to downgrade and compatibility risks.
- **Evidence:** ```
Live verification via Nmap SSL/TLS enumeration confirmed TLSv1.0 and TLSv1.1 support on 3389/tcp.
```
- **Impact:** An attacker positioned to intercept or downgrade traffic may benefit from weaker legacy cryptographic settings. While this did not result in direct compromise during testing, it represents avoidable exposure on a management service.
- **Remediation:** Disable TLS 1.0 and TLS 1.1 for RDP via Group Policy or SCHANNEL registry settings. Enforce TLS 1.2 or higher and validate with a repeat SSL/TLS enumeration scan after the change.
- **Hardening:** Restrict RDP access to dedicated administration hosts, require MFA for remote administration, and continuously monitor remote-access events for unusual activity.
- **References:** Microsoft SCHANNEL/TLS hardening guidance, RDP service configuration review

---

## 4. Security Enhancement Recommendations

### Remote Administration Exposure

Limit exposure of RDP and WinRM to approved administrator systems or a management VLAN. If remote administration is needed across sites, require VPN or a bastion host instead of exposing management ports broadly on the local LAN.

### Legacy Protocol Reduction

Disable NetBIOS over TCP/IP if no legacy dependency exists, review SMB protocol configuration, and remove older protocol support that is no longer operationally required.

### Monitoring and Detection

Create alerting for repeated RDP/WinRM access attempts, unusual authentication patterns, and new inbound management connections from non-administrative endpoints.

---

## 5. Risk Summary Matrix

| ID | Finding | Severity | Remediation Priority |
|----|---------|----------|---------------------|
| G9-001 | RDP supports legacy TLS 1.0 and TLS 1.1 | Low | Low Priority |

---

## 6. Appendices

### A. Tools Used

- nmap, masscan (enumeration)
- Metasploit, custom scripts (exploitation)
- Shodan, crt.sh (OSINT)
- Burp Suite, curl (web testing)

### B. Scope Boundaries

All testing was conducted within the authorized scope. No denial-of-service attacks were performed without explicit permission.
