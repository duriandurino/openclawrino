# CVE Severity Reference

## CVSS v3.1 Score Ranges

| Score | Severity | Color | Action |
|-------|----------|-------|--------|
| 9.0–10.0 | Critical | 🔴 | Immediate remediation, prioritize exploitation |
| 7.0–8.9 | High | 🟠 | Fast-track fix, high-value target |
| 4.0–6.9 | Medium | 🟡 | Schedule remediation |
| 0.1–3.9 | Low | 🟢 | Address when convenient |
| 0.0 | None | ⚪ | Informational only |

## Common Critical CVEs (Raspberry Pi / Linux Targets)

| CVE | Service | Impact | Exploit |
|-----|---------|--------|---------|
| CVE-2024-6387 | OpenSSH 8.2p1–9.6p1 | Unauth RCE as root | Public, reliable |
| CVE-2021-41773 | Apache 2.4.49 | Path traversal, RCE | Public |
| CVE-2017-0144 | SMBv1 (EternalBlue) | Remote code exec | Metasploit |
| CVE-2021-44228 | Log4j 2.x | Remote code exec (log injection) | Public, reliable |
| CVE-2020-1472 | Samba/AD (Zerologon) | Domain admin | Metasploit |
| CVE-2024-21762 | Fortinet SSL VPN | Out-of-bounds write, RCE | Public |
| CVE-2023-44487 | HTTP/2 impls | Rapid Reset DoS | Public |

## CVSS Vector Components

| Component | Values |
|-----------|--------|
| Attack Vector (AV) | Network (N), Adjacent (A), Local (L), Physical (P) |
| Attack Complexity (AC) | Low (L), High (H) |
| Privileges Required (PR) | None (N), Low (L), High (H) |
| User Interaction (UI) | None (N), Required (R) |
| Scope (S) | Unchanged (U), Changed (C) |
| Impact: Confidentiality (C) | High (H), Low (L), None (N) |
| Impact: Integrity (I) | High (H), Low (L), None (N) |
| Impact: Availability (A) | High (H), Low (L), None (N) |

Example: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` → Score 10.0 (Critical)

## Research Workflow

```
Service + Version
    │
    ├── searchsploit → Has exploit?
    │     ├── YES → Check EDB-ID, download to loot/
    │     └── NO  → Continue
    │
    ├── NVD API → Matches CVEs?
    │     ├── YES → Check CVSS, confirm version match
    │     └── NO  → Continue
    │
    └── Manual research
          ├── vendor advisory
          ├── GitHub issues
          └── exploit-db, packetstorm
```
