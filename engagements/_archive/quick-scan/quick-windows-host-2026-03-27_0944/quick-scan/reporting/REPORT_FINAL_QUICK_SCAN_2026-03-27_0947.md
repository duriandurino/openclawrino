# Penetration Test Report — 192.168.0.112 (Quick Scan)

**Date:** 2026-03-27
**Target:** 192.168.0.112 (Quick Scan)
**Findings:** 12

---

## 1. Executive Summary

This assessment identified **12 findings** across the target:

| Severity | Count |
|----------|-------|
| High | 12 |

### Priority Actions

1. **5985 — http: Apache HTTP Server 2.4.49 - Path Traversal & Remote Code Execution** (High) — If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access
2. **3306 — mysql: Active Calendar 1.2 - '/data/mysqlevents.php?css' Cross-Site** (High) — If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access
3. **3306 — mysql: Advanced Poll 2.0 - 'mysql_host' Cross-Site Scripting** (High) — If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access

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

### QS-001 — 5985 — http: Apache HTTP Server 2.4.49 - Path Traversal & Remote Code Execution

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 5985 — http: Apache HTTP Server 2.4.49 - Path Traversal & Remote Code Execution (RCE)
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 5985 — http: Apache HTTP Server 2.4.49 - Path Traversal & Remote Code Execution (RCE)
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict WinRM to trusted administration networks, prefer HTTPS/5986 where possible, and verify only intended admin groups can use remote management.
- **Hardening:** Maintain a patching cadence for web-facing components, reduce banner leakage, and monitor for unexpected management endpoints on non-standard hosts.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-002 — 3306 — mysql: Active Calendar 1.2 - '/data/mysqlevents.php?css' Cross-Site

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 3306 — mysql: Active Calendar 1.2 - '/data/mysqlevents.php?css' Cross-Site Scripting
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 3306 — mysql: Active Calendar 1.2 - '/data/mysqlevents.php?css' Cross-Site Scripting
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict MySQL to approved application hosts only, disable public exposure where unnecessary, and verify account/network ACLs for the service.
- **Hardening:** Keep database services on dedicated application/admin networks, monitor for unexpected remote logins, and document the expected client set.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-003 — 3306 — mysql: Advanced Poll 2.0 - 'mysql_host' Cross-Site Scripting

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 3306 — mysql: Advanced Poll 2.0 - 'mysql_host' Cross-Site Scripting
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 3306 — mysql: Advanced Poll 2.0 - 'mysql_host' Cross-Site Scripting
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict MySQL to approved application hosts only, disable public exposure where unnecessary, and verify account/network ACLs for the service.
- **Hardening:** Keep database services on dedicated application/admin networks, monitor for unexpected remote logins, and document the expected client set.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-004 — 3306 — mysql: Agora 1.4 RC1 - 'MysqlfinderAdmin.php' Remote File Inclusion

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 3306 — mysql: Agora 1.4 RC1 - 'MysqlfinderAdmin.php' Remote File Inclusion
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 3306 — mysql: Agora 1.4 RC1 - 'MysqlfinderAdmin.php' Remote File Inclusion
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict MySQL to approved application hosts only, disable public exposure where unnecessary, and verify account/network ACLs for the service.
- **Hardening:** Keep database services on dedicated application/admin networks, monitor for unexpected remote logins, and document the expected client set.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-005 — 3306 — mysql: Asterisk 'asterisk-addons' 1.2.7/1.4.3 - CDR_ADDON_MYSQL Module

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 3306 — mysql: Asterisk 'asterisk-addons' 1.2.7/1.4.3 - CDR_ADDON_MYSQL Module SQL Injection
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 3306 — mysql: Asterisk 'asterisk-addons' 1.2.7/1.4.3 - CDR_ADDON_MYSQL Module SQL Injection
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict MySQL to approved application hosts only, disable public exposure where unnecessary, and verify account/network ACLs for the service.
- **Hardening:** Keep database services on dedicated application/admin networks, monitor for unexpected remote logins, and document the expected client set.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-006 — 3306 — mysql: Banex PHP MySQL Banner Exchange 2.21 - 'admin.php' Multiple SQL

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 3306 — mysql: Banex PHP MySQL Banner Exchange 2.21 - 'admin.php' Multiple SQL Injections
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 3306 — mysql: Banex PHP MySQL Banner Exchange 2.21 - 'admin.php' Multiple SQL Injections
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict MySQL to approved application hosts only, disable public exposure where unnecessary, and verify account/network ACLs for the service.
- **Hardening:** Keep database services on dedicated application/admin networks, monitor for unexpected remote logins, and document the expected client set.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-007 — 3306/tcp — mysql

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the enum phase: 3306/tcp — mysql
- **Evidence:** ```
Quick scan candidate finding (observed) from enum: 3306/tcp — mysql
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict MySQL to approved application hosts only, disable public exposure where unnecessary, and verify account/network ACLs for the service.
- **Hardening:** Keep database services on dedicated application/admin networks, monitor for unexpected remote logins, and document the expected client set.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-008 — 5985 — http: Apache 1.0/1.2/1.3 - Server Address Disclosure

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 5985 — http: Apache 1.0/1.2/1.3 - Server Address Disclosure
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 5985 — http: Apache 1.0/1.2/1.3 - Server Address Disclosure
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict WinRM to trusted administration networks, prefer HTTPS/5986 where possible, and verify only intended admin groups can use remote management.
- **Hardening:** Maintain a patching cadence for web-facing components, reduce banner leakage, and monitor for unexpected management endpoints on non-standard hosts.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-009 — 5985 — http: Apache 1.1 / NCSA HTTPd 1.5.2 / Netscape Server 1.12/1.1/2.0 - a

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 5985 — http: Apache 1.1 / NCSA HTTPd 1.5.2 / Netscape Server 1.12/1.1/2.0 - a nph-test-cgi
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 5985 — http: Apache 1.1 / NCSA HTTPd 1.5.2 / Netscape Server 1.12/1.1/2.0 - a nph-test-cgi
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict WinRM to trusted administration networks, prefer HTTPS/5986 where possible, and verify only intended admin groups can use remote management.
- **Hardening:** Maintain a patching cadence for web-facing components, reduce banner leakage, and monitor for unexpected management endpoints on non-standard hosts.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-010 — 5985 — http: Apache 1.3/2.0.x - Server Side Include Cross-Site Scripting

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 5985 — http: Apache 1.3/2.0.x - Server Side Include Cross-Site Scripting
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 5985 — http: Apache 1.3/2.0.x - Server Side Include Cross-Site Scripting
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict WinRM to trusted administration networks, prefer HTTPS/5986 where possible, and verify only intended admin groups can use remote management.
- **Hardening:** Maintain a patching cadence for web-facing components, reduce banner leakage, and monitor for unexpected management endpoints on non-standard hosts.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-011 — 5985 — http: Apache Geronimo 2.1.x - '/console/portal/Server/Monitoring'

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the vuln phase: 5985 — http: Apache Geronimo 2.1.x - '/console/portal/Server/Monitoring' Multiple Cross-Site Scripting Vulnerabilities
- **Evidence:** ```
Quick scan candidate finding (observed) from vuln: 5985 — http: Apache Geronimo 2.1.x - '/console/portal/Server/Monitoring' Multiple Cross-Site Scripting Vulnerabilities
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict WinRM to trusted administration networks, prefer HTTPS/5986 where possible, and verify only intended admin groups can use remote management.
- **Hardening:** Maintain a patching cadence for web-facing components, reduce banner leakage, and monitor for unexpected management endpoints on non-standard hosts.
- **References:** Quick scan profile: windows-host, Execution mode: safe

### QS-012 — 5985/tcp — http

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** 192.168.0.112
- **Description:** Quick scan candidate from the enum phase: 5985/tcp — http
- **Evidence:** ```
Quick scan candidate finding (observed) from enum: 5985/tcp — http
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Restrict WinRM to trusted administration networks, prefer HTTPS/5986 where possible, and verify only intended admin groups can use remote management.
- **Hardening:** Maintain a patching cadence for web-facing components, reduce banner leakage, and monitor for unexpected management endpoints on non-standard hosts.
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
| QS-001 | 5985 — http: Apache HTTP Server 2.4.49 - Path Traversal & Remote Code Execution | High | Immediate |
| QS-002 | 3306 — mysql: Active Calendar 1.2 - '/data/mysqlevents.php?css' Cross-Site | High | Immediate |
| QS-003 | 3306 — mysql: Advanced Poll 2.0 - 'mysql_host' Cross-Site Scripting | High | Immediate |
| QS-004 | 3306 — mysql: Agora 1.4 RC1 - 'MysqlfinderAdmin.php' Remote File Inclusion | High | Immediate |
| QS-005 | 3306 — mysql: Asterisk 'asterisk-addons' 1.2.7/1.4.3 - CDR_ADDON_MYSQL Module | High | Immediate |
| QS-006 | 3306 — mysql: Banex PHP MySQL Banner Exchange 2.21 - 'admin.php' Multiple SQL | High | Immediate |
| QS-007 | 3306/tcp — mysql | High | Immediate |
| QS-008 | 5985 — http: Apache 1.0/1.2/1.3 - Server Address Disclosure | High | Immediate |
| QS-009 | 5985 — http: Apache 1.1 / NCSA HTTPd 1.5.2 / Netscape Server 1.12/1.1/2.0 - a | High | Immediate |
| QS-010 | 5985 — http: Apache 1.3/2.0.x - Server Side Include Cross-Site Scripting | High | Immediate |
| QS-011 | 5985 — http: Apache Geronimo 2.1.x - '/console/portal/Server/Monitoring' | High | Immediate |
| QS-012 | 5985/tcp — http | High | Immediate |

---

## 6. Appendices

### A. Tools Used

- nmap, masscan (enumeration)
- Metasploit, custom scripts (exploitation)
- Shodan, crt.sh (OSINT)
- Burp Suite, curl (web testing)

### B. Scope Boundaries

All testing was conducted within the authorized scope. No denial-of-service attacks were performed without explicit permission.
