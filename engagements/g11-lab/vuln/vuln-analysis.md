Vulnerability Analysis – Target: G11 (192.168.0.226)
Engagement: Recon + Enum + Vuln Analysis (No exploitation)
Domain: NCTV360
Target OS: Windows (likely multiple layers/VMs inside)

Scope reminder: G11 may be running virtual machines (port 2179 open). This expands the attack surface and may expose guest VMs via VMRDVP.

Findings overview (active ports and services from enum):
- RPC 135/tcp – msrpc endpoint (authenticated RPC; may enumerate services/users with proper credentials)
- SMB 139/445 – SMBv2/SMBv3 with signing enabled but not required; anonymous access denied
- RDP 3389 – Network Level Authentication (NLA) enabled; CredSSP/Early User Auth supported
- WinRM 5985 – HTTP WinRM, requires authentication
- VMRDVP 2179 – VMware Remote Display / Hyper-V display protocol (VM surface present)
- UPnP 5357 – WSDAPI; HTTP 503 / service unavailable observed in enumeration

For each finding: CVE ID(s) (if applicable), affected Windows versions, severity, exploitable likelihood, remediation.

1) SMB (139/445) – SMBv1/v2/v3 exposure concerns; EternalBlue risk mitigated by patching.
- CVE: CVE-2017-0144 (MS17-010) – EternalBlue-like exploitation against SMBv1; note: SME/v1 usage; modern Windows patches mitigate.
- CVE: CVE-2017-0145 (MS17-010) – SMBv1 vulnerabilites used in other exploits; patched in supported OSes.
- Affected: Windows OS versions with SMBv1 enabled and unpatched. If patched, risk mitigated.
- Severity: High if unpatched, otherwise Medium/Low depending on exposure.
- Exploitable: Likely if unpatched, requires network access to SMB; can be via anonymous/credentialed vectors depending on configuration. Given SMB signing is not required but access denied, exposure exists but less likely to be exploited anonymously.
- Remediation: Disable SMBv1 if not required; ensure MS17-010 patches applied; enable SMB signing; restrict SMB exposure to trusted networks; implement firewall rules; monitor for SMB-related activity.

2) RPC (135) – Windows RPC endpoints can be used for enumeration and lateral movement with credentials.
- CVE: Not a single CVE; RPC endpoints are often vectors when combined with other vulnerabilities. CVEs exist for RPC-related flaws in Windows (various CVEs across years). Specific exploitation commonly requires credentials or other footholds.
- Affected: Windows RPC-enabled hosts; dependent on service versions and patch state.
- Severity: Medium to High depending on exposed RPC services and credentials.
- Exploitable: Requires authentication; some RPC vulnerabilities exist (e.g., CVE-2017-0145 family via MSRPC), but current finding is enumeration surface. Not easily exploitable without credentials.
- Remediation: Keep systems patched; restrict RPC to internal networks; use firewalls; enforce least privilege and credential hygiene; monitor RPC endpoints for unusual calls.

3) RDP (3389) – Remote Desktop Protocol surface with NLA enabled.
- CVE: CVE-2019-0708 (BlueKeep) – historic RDP vulnerability, but requires unpatched systems vulnerable to memory corruption; many modern Windows patches mitigate.
- DejaBlue family (CVE-set) – affected Windows versions pre-patch; exact CVEs vary by vendor; guidance remains apply patches.
- Affected: Windows servers/desktops with RDP exposure; patched versions minimize risk; legacy systems remain at risk.
- Severity: Medium to High for unpatched systems; with NLA and modern hardening, risk is reduced.
- Exploitable: Less likely if patched; still potential via brute-force attempts (though NLA protects with credentials). External exposure could be abused if credentials leaked or misconfigurations.
- Remediation: Ensure patching to mitigate BlueKeep/DejaBlue; enforce strong password policies; monitor RDP traffic; consider remote access gateways; disable RDP from untrusted networks if not needed.

4) WinRM (5985) – Windows Remote Management exposed; authentication required.
- CVE: Not a single CVE; there are several Windows WinRM-related CVEs in various years (e.g., CVE-2020-13379 mentions PowerShell/PAC for WinRM; but patch guidance often covers authentication weaknesses).
- Affected: Systems with WinRM enabled and reachable; likely patched in modern Windows builds; authentication-based access depends on credentials and policy.
- Severity: Low to Medium for default configurations; could be higher if misconfigurations exist (e.g., allowed access to non-admins or exposed PowerShell endpoints).
- Exploitable: Generally requires valid credentials; RAM-based weaknesses exist but often require an authenticated user.
- Remediation: Restrict WinRM to trusted hosts; disable if not required; enforce strong authentication; apply latest patches; monitor WinRM events.

5) VMRDVP (2179) – VMware Remote Display / Hyper-V display protocol surface.
- CVE: Various VMware/Hyper-V vulnerabilities exist across versions (guest VM escape vectors); exact CVEs depend on the virtualization platform exposed by G11. Example CVEs include memory corruption, escape vulnerabilities, and VMEscape paths.
- Affected: Hosts running VMware/Hyper-V hypervisor with exposed VMRDVP interface; guest VMs could be exposed to management vectors.
- Severity: Medium to High depending on virtualization exposure and segment protections.
- Exploitable: Potential VM escape or guest VM compromise if virtualization stack is misconfigured or outdated; requires network reachability and privileges within hypervisor context.
- Remediation: Isolate virtualization interfaces; patch virtualization hosts; restrict access to hypervisor management networks; monitor virtualization traffic; disable or constrain VMRDVP exposure if not required.

6) UPnP (5357) – WSDAPI service shows HTTP 503 in enumeration; potential information disclosure risks exist in UPnP/WSD.
- CVE: Various UPnP-related CVEs exist (e.g., CVE-2017-10271 for Oracle/UPnP, but Windows-specific UPnP CVEs exist like CVE-2015-0012 in services). Specific risk on Windows may be limited depending on service exposure.
- Affected: Windows systems exposing UPnP/WSD endpoints.
- Severity: Low to Medium depending on disclosed information and misconfigurations.
- Exploitable: Typically requires discovery and crafted requests; information disclosure is more common; direct exploitation less common in modern patched systems.
- Remediation: Disable UPnP where not needed; ensure service hardening; monitor UPnP/WSD endpoints; apply patches for UPnP-related vulnerabilities if they exist in the platform version.

Observations and risk notes
- G11 open ports include 135, 445, 3389, 5985, 2179, 5357. The presence of 2179 indicates VM-related services; G11 may host VMs; this expands risk surface.
- SMB signing is enabled but not required; anonymous access denied; however, unsigned sessions could be susceptible to relay attacks in some configurations. Consider ensuring SMB signing is required (not just allowed).
- RDP shows NLA is enabled, which mitigates many brute-force or unauthenticated attacks, but public exposure still warrants hardening and monitoring.
- WinRM requires authentication; ensure policies enforce least privilege and audited access.
- RPC endpoints on 135 could be a foothold for enumeration or lateral movement if credentials exist.
- UPnP exposure may reveal internal topology; if possible, disable the service or restrict to trusted networks.

Remediation checklist (apply as appropriate to environment)
- Patch management: verify that Windows Security Updates are applied, including MS17-010 patches for SMB, BlueKeep/DejaBlue patches for RDP, and WinRM-related fixes.
- Disable SMBv1 if not needed; enable SMB signing as required, and configure firewall rules to limit SMB exposure.
- Harden RDP: enforce MFA or just disable RDP to untrusted networks; implement Network Level Access control; use RD Gateway or VPN.
- Lock down WinRM: limit to authorized hosts; use Just Enough Administration (JEA); enable auditing; consider HTTPS transport and certificate validation.
- VM security: isolate hypervisor interfaces; apply patches to VMware/Hyper-V; confirm VM escape risk mitigations; monitor hypervisor logs.
- UPnP: disable if not required; minimize exposure; patch per vendor guidance.

Conclusion
- G11 presents a multi-surface Windows host with RPC, SMB, RDP, WinRM, VMRDVP, and UPnP exposure. Some services show best practices (NLA for RDP, SMB signing optional). The most actionable risks are potential EternalBlue-like exposure if systems are unpatched (MS17-010 family) and potential VM escape surfaces via VMRDVP. Prioritize patching, network segmentation, least-privilege credentials, and active monitoring. No exploitation was performed in this task.
