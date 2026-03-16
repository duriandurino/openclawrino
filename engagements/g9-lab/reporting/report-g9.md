# Penetration Testing Report: Target G9

## 1. Executive Summary

This report documents the reconnaissance and active enumeration findings for the target host designated “G9” (IP 192.168.0.214) within the NCTV360 domain. The engagement was conducted on 2026-03-16 with verbal authorization from the G9 owner. No exploits were performed; this engagement focuses on identifying exposed services and security weaknesses to guide remediation and hardening efforts.

Key takeaway: SMB signing is enabled but not required, exposing the system to relay-type threats. WinRM is exposed on the network and should be firewalled. RDP with Network Level Authentication is enabled and properly configured, but strong credential hygiene and network access controls are essential.

## 2. Scope & Authorization

- Target: G9 (HOSTNAME: G9), IP: 192.168.0.214
- Domain/Workgroup: NCTV360
- Operating System: Microsoft Windows (exact version not identified)
- Engagement Date: 2026-03-16
- Authorization: Verbal confirmation from G9 owner
- Scope: Reconnaissance + Active enumeration only; NO exploitation
- Methods: Standard port scanning, service identification, SMB/RDP/WinRM configuration checks, and NetBIOS enumeration

## 3. Target Profile

- Hostname: G9
- IP Address: 192.168.0.214
- Domain: NCTV360
- OS: Microsoft Windows (exact version not identified)
- Exposed Services: SMB (139/445), RDP (3389), WinRM (5985), NetBIOS (139)

## 4. Methodology

- Passive Reconnaissance: Information gathering about domain and network context (NCTV360).
- Active Enumeration: Port scanning, service detection, SMB signing status, RDP configuration, and NetBIOS disclosure.
- No exploitation: No attempts to gain unauthorized access or run exploits.

## 5. Findings

### 5.1 SMB Signing Enabled But Not Required
- Severity: Medium
- Description: SMB signing is supported but not enforced, allowing unsigned SMB packets and potentially enabling relay attacks.
- Evidence: SMBv2 Security Mode: 3:1:1 — Message signing enabled but NOT required.
- Remediation: Enforce SMB signing for all communications. In Group Policy: Microsoft network server: Digitally sign communications (always) → Enabled.
- Hardening: Apply GPOs to require signing on all domain-joined and standalone Windows machines; monitor for unsigned SMB traffic.

### 5.2 RDP with NLA Enabled
- Severity: Info
- Description: RDP is accessible with Network Level Authentication, reducing unauthenticated exposure. Brute-force remains possible but is mitigated by NLA.
- Evidence: NLA Status: ENABLED; CredSSP (NLA); Brute force potential noted.
- Remediation: No changes required for this finding, but strengthen controls with VPN-only access or IP whitelisting and strong password policies.
- Hardening: Consider VPN isolation or firewall rules to limit RDP exposure; enable account lockout thresholds.

### 5.3 WinRM Exposed on Network
- Severity: Low
- Description: WinRM (HTTP, port 5985) is exposed on the network. Although authenticated access is required, the service increases the attack surface.
- Evidence: Port 5985/tcp Open: http — WinRM
- Remediation: Restrict access to WinRM to trusted admin hosts/networks via firewalls. Prefer HTTPS (5986) where possible and disable WinRM if not in use.
- Hardening: If remote management is needed, configure WinRM over HTTPS and ensure proper certificate configuration.

### 5.4 No Anonymous Access to SMB Shares
- Severity: Good Finding (Informational)
- Description: Anonymous access to SMB shares is denied.
- Evidence: Anonymous Access: DENIED; Null Session: DENIED.
- Remediation: Maintain current configuration.
- Hardening: N/A

### 5.5 Domain Information Disclosure via NetBIOS
- Severity: Info
- Description: NetBIOS reveals domain name NCTV360, which can aid reconnaissance.
- Evidence: NetBIOS: NCTV360 <00> - <GROUP> B <ACTIVE> Domain/Workgroup Name
- Remediation: If NetBIOS is not required, disable TCP/IP NetBIOS Helper or minimize exposure; segment networks to reduce risk.
- Hardening: Review necessity of NetBIOS; limit exposure on sensitive interfaces.

## 6. Attack Surface Map

Visual summary (textual):
- SMB (139/445): Auth required? No anonymous access; Signing enabled but not required.
- RDP (3389): NLA enabled; brute-force possible but mitigated by credentials and rate-limiting.
- WinRM (5985): Exposed HTTP; authenticated access required; consider HTTPS.
- NetBIOS: Domain disclosed as NCTV360.

## 7. Risk Summary

| Finding | Severity | Type | Observed Risk |
|---|---|---|---|
| SMB Signing Enabled But Not Required | Medium | Relay Attack | Potential credential interception via SMB relay
| WinRM Exposed on Network | Low | Information Exposure | Increased attack surface; potential remote execution with valid creds
| RDP with NLA Enabled | Info | Configuration | Brute-force risk mitigated by NLA; ensure strong credentials
| Domain Information Disclosure via NetBIOS | Info | Information Leak | Domain name disclosure can aid attackers
| No Anonymous Access to SMB Shares | Good Finding | Configuration | Proper access controls in place

## 8. Recommendations (Prioritized Action Items)

- Immediate/High Priority
  - Enforce SMB signing: Enable Microsoft network server: Digitally sign communications (always).
  - Firewalize WinRM: Restrict 5985 access to trusted admin hosts; consider moving to 5986 with HTTPS.
- Medium Priority
  - RDP access controls: Use VPN or IP whitelisting; enforce strong passwords and account lockout.
  - Review NetBIOS usage: Disable NetBIOS where not required; segment networks if necessary.
- Low Priority
  - Patch management: Keep Windows up to date with security patches.
  - Maintain audit logging for RDP/WinRM attempts.

## 9. Appendix

- Enumeration data and service details are referenced in engagements/g9-lab/recon/enum-results.md.
- This report contains no exploitation data; it is a reconnaissance-focused deliverable.
