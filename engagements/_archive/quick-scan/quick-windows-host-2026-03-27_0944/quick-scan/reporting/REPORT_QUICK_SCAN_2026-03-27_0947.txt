# Penetration Test Report (Quick Scan) — 192.168.0.112

- Profile: `windows-host`
- Mode: `safe`
- Engagement: `quick-windows-host-2026-03-27_0944`
- Steps executed: `3`
- Generated: `2026-03-27 09:47 PST`

## Scope
- Rapid triage / hygiene / exposure assessment
- Safe or low-impact checks where possible unless a profile explicitly broadens coverage
- This is not a substitute for a full pentest

## Executive Summary

- Quick scan profile `windows-host` ran against `192.168.0.112` in `safe` mode and captured 12 meaningful candidate observations, with highest provisional severity `Critical`.
- These results are triage-oriented and should be manually validated before being treated as confirmed vulnerabilities.

## Severity Buckets

- Critical: 1
- High: 6
- Medium: 0
- Low: 0
- Info: 5

## Candidate Findings

| Severity | Source | Confidence | Finding |
|---|---|---|---|
| High | enum | candidate | 3306/tcp — mysql |
| Info | enum | candidate | 5985/tcp — http |
| High | vuln | candidate | 3306 — mysql: Active Calendar 1.2 - '/data/mysqlevents.php?css' Cross-Site Scripting |
| High | vuln | candidate | 3306 — mysql: Advanced Poll 2.0 - 'mysql_host' Cross-Site Scripting |
| High | vuln | candidate | 3306 — mysql: Agora 1.4 RC1 - 'MysqlfinderAdmin.php' Remote File Inclusion |
| High | vuln | candidate | 3306 — mysql: Asterisk 'asterisk-addons' 1.2.7/1.4.3 - CDR_ADDON_MYSQL Module SQL Injection |
| High | vuln | candidate | 3306 — mysql: Banex PHP MySQL Banner Exchange 2.21 - 'admin.php' Multiple SQL Injections |
| Info | vuln | candidate | 5985 — http: Apache 1.0/1.2/1.3 - Server Address Disclosure |
| Info | vuln | candidate | 5985 — http: Apache 1.1 / NCSA HTTPd 1.5.2 / Netscape Server 1.12/1.1/2.0 - a nph-test-cgi |
| Info | vuln | candidate | 5985 — http: Apache 1.3/2.0.x - Server Side Include Cross-Site Scripting |
| Info | vuln | candidate | 5985 — http: Apache Geronimo 2.1.x - '/console/portal/Server/Monitoring' Multiple Cross-Site Scripting Vulnerabilities |
| Critical | vuln | candidate | 5985 — http: Apache HTTP Server 2.4.49 - Path Traversal & Remote Code Execution (RCE) |

## What Needs Manual Validation

- Validate: 3306/tcp — mysql
- Validate: 5985/tcp — http
- Validate: 3306 — mysql: Active Calendar 1.2 - '/data/mysqlevents.php?css' Cross-Site Scripting
- Validate: 3306 — mysql: Advanced Poll 2.0 - 'mysql_host' Cross-Site Scripting
- Validate: 3306 — mysql: Agora 1.4 RC1 - 'MysqlfinderAdmin.php' Remote File Inclusion
- Validate: 3306 — mysql: Asterisk 'asterisk-addons' 1.2.7/1.4.3 - CDR_ADDON_MYSQL Module SQL Injection
- Validate: 3306 — mysql: Banex PHP MySQL Banner Exchange 2.21 - 'admin.php' Multiple SQL Injections
- Validate: 5985 — http: Apache 1.0/1.2/1.3 - Server Address Disclosure
- Validate: 5985 — http: Apache 1.1 / NCSA HTTPd 1.5.2 / Netscape Server 1.12/1.1/2.0 - a nph-test-cgi
- Validate: 5985 — http: Apache 1.3/2.0.x - Server Side Include Cross-Site Scripting
- Validate: 5985 — http: Apache Geronimo 2.1.x - '/console/portal/Server/Monitoring' Multiple Cross-Site Scripting Vulnerabilities
- Validate: 5985 — http: Apache HTTP Server 2.4.49 - Path Traversal & Remote Code Execution (RCE)

## Recommended Next Action

- Escalate to a full pentest workflow or targeted manual validation immediately for the highest-risk candidates.

## Recon Summary

- No summary generated for this phase.

## Enumeration Summary

# Phase Complete: Enumeration

**Engagement:** quick-windows-host-2026-03-27_0944
**Phase:** enum
**Agent:** specter-enum
**Date:** 2026-03-27 09:47 PST
**Status:** complete

## Found

- 82/tcp — xfer
- 135/tcp — msrpc
- 139/tcp — netbios-ssn
- 445/tcp — microsoft-ds
- 1236/tcp — bvcontrol
- 3306/tcp — mysql
- 3389/tcp — ms-wbt-server
- 5985/tcp — wsman
- 7070/tcp — realserver
- 49153/tcp — unknown
- 82/tcp — xfer?
- 445/tcp — microsoft-ds?
- 1236/tcp — tcpwrapped
- 5985/tcp — http
- 7070/tcp — ssl|realserver?
- 49153/tcp — tcpwrapped
- 3389/tcp open
- 5985/tcp open

## Not Found

## Vulnerability Summary

# Phase Complete: Vulnerability Analysis

**Engagement:** quick-windows-host-2026-03-27_0944
**Phase:** vuln
**Agent:** specter-vuln
**Date:** 2026-03-27 09:47 PST
**Status:** complete

## Found

- 3306 — mysql: Active Calendar 1.2 - '/data/mysqlevents.php?css' Cross-Site Scripting
- 3306 — mysql: Advanced Poll 2.0 - 'mysql_host' Cross-Site Scripting
- 3306 — mysql: Agora 1.4 RC1 - 'MysqlfinderAdmin.php' Remote File Inclusion
- 3306 — mysql: Asterisk 'asterisk-addons' 1.2.7/1.4.3 - CDR_ADDON_MYSQL Module SQL Injection
- 3306 — mysql: Banex PHP MySQL Banner Exchange 2.21 - 'admin.php' Multiple SQL Injections
- 5985 — http: Apache 1.0/1.2/1.3 - Server Address Disclosure
- 5985 — http: Apache 1.1 / NCSA HTTPd 1.5.2 / Netscape Server 1.12/1.1/2.0 - a nph-test-cgi
- 5985 — http: Apache 1.3/2.0.x - Server Side Include Cross-Site Scripting
- 5985 — http: Apache Geronimo 2.1.x - '/console/portal/Server/Monitoring' Multiple Cross-Site Scripting Vulnerabilities
- 5985 — http: Apache HTTP Server 2.4.49 - Path Traversal & Remote Code Execution (RCE)

## Not Found

- Checked: current automated artifacts → Result: no additional negative results explicitly captured

## Recommended Next

- **Next Phase:** specter-exploit
- **Vector:** network
- **Reason:** Automated vuln artifacts produced reusable evidence for the next phase.

## Recommendations

- Validate candidate findings manually before escalation or reporting as confirmed issues.
- Escalate to a full pentest workflow if exposed services, weak posture, or high-risk candidates are found.
- Preserve engagement artifacts for follow-up analysis and retesting.
