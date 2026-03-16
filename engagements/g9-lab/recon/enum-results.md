# G9 (192.168.0.214) — Enumeration Results

> **Target:** Windows PC "G9"  
> **Engagement Date:** 2026-03-16  
> **Operator:** Hatless White 🎯  
> **Authorization:** Verbal confirmed from G9 owner  
> **Scope:** Recon + Enum only — NO exploitation

---

## Target Identity

| Field | Value |
|-------|-------|
| Hostname | G9 |
| IP Address | 192.168.0.214 |
| MAC Address | 58:02:05:2B:BD:60 |
| Workgroup/Domain | NCTV360 |
| OS | Microsoft Windows (unknown exact version) |
| Services | File Server, Workstation |

---

## Open Ports & Services

| Port | State | Service | Version/Details |
|------|-------|---------|-----------------|
| 139/tcp | Open | netbios-ssn | Microsoft NetBIOS Session Service |
| 445/tcp | Open | microsoft-ds | SMB (SMBv2/SMBv3) |
| 1236/tcp | Filtered | bvcontrol | Unknown — filtered |
| 3389/tcp | Open | ms-wbt-server | Remote Desktop Protocol |
| 5357/tcp | Open | wsdapi | Microsoft HTTPAPI / SSDP/UPnP |
| 5985/tcp | Open | http | WinRM (Windows Remote Management) |

---

## Service Analysis

### SMB (Ports 139/445)
- **SMBv2 Security Mode:** 3:1:1 — Message signing enabled but NOT required
- **Anonymous Access:** DENIED (NT_STATUS_ACCESS_DENIED)
- **Null Session:** DENIED (rpcclient failed)
- **Shares:** Could not enumerate without authentication
- **Vulnerability Check:** MS17-010 (EternalBlue) check returned inconclusive (needs auth)

### RDP (Port 3389)
- **Security Layers Supported:**
  - ✅ CredSSP (NLA) — Network Level Authentication required
  - ✅ CredSSP with Early User Auth
  - ✅ RDSTLS
- **NLA Status:** ENABLED — prevents unauthenticated RDP access
- **Implication:** RDP brute-force possible but rate-limited; NLA blocks credential-less attacks

### WinRM (Port 5985)
- **Status:** Responding (HTTP 404 on root, Microsoft-HTTPAPI/2.0)
- **Auth Required:** Yes — no anonymous access
- **Potential:** Valid credentials = PowerShell remote access

### UPnP/WSD (Port 5357)
- **Status:** Service Unavailable (HTTP 503)
- **Info Disclosure:** Minimal — no useful data returned

---

## NetBIOS Enumeration

```
G9              <20> - B <ACTIVE>  File Server Service
G9              <00> - B <ACTIVE>  Workstation Service
NCTV360         <00> - <GROUP> B <ACTIVE>  Domain/Workgroup Name
```

---

## Attack Surface Summary

```
┌─────────────────────────────────────────────────┐
│                 G9 (Windows)                    │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │   SMB    │  │   RDP    │  │    WinRM     │  │
│  │ 139/445  │  │   3389   │  │    5985      │  │
│  │          │  │          │  │              │  │
│  │ Auth req │  │ NLA ON   │  │ Auth req     │  │
│  │ No anon  │  │ CredSSP  │  │ PS remote    │  │
│  │ Sign nrq │  │ Brute ok │  │ Creds needed │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                                                 │
│  Domain: NCTV360                                │
│  Signing: Enabled but NOT required (SMB)        │
└─────────────────────────────────────────────────┘
```

---

## Potential Attack Vectors (Not Exploited)

| Vector | Feasibility | Method | Risk to Target |
|--------|-------------|--------|----------------|
| **SMB Brute Force** | 🟡 Medium | hydra, crackmapexec with wordlist | Account lockout possible |
| **RDP Brute Force** | 🟡 Medium | hydra, rdp-sec-check | Account lockout, logs generated |
| **WinRM Access** | 🟡 Medium | evil-winrm with valid creds | PowerShell access if creds found |
| **SMB Signing Disabled** | 🟡 Medium | NTLM relay attack (requires second host) | Credential interception |
| **MS17-010** | ❓ Unknown | Needs auth or deeper probe | System compromise if vulnerable |

### What We COULD Do With Valid Credentials:
- SMB → enumerate shares, read/write files
- RDP → full GUI desktop access
- WinRM → PowerShell command execution
- Lateral movement to other hosts in NCTV360 domain

---

## Recommendations for G9 Owner (Security Hardening)

1. **Enable SMB Signing** — Currently disabled, vulnerable to relay attacks
   - Group Policy: `Microsoft network server: Digitally sign communications (always)` → Enabled
2. **Restrict RDP** — Consider IP whitelisting or VPN-only access
3. **Firewall Port 5985** — WinRM should only be accessible from trusted admin hosts
4. **Account Lockout Policy** — Protect against brute force (if not already enabled)
5. **Check Windows Update** — Ensure latest patches to prevent SMB exploits

---

## Next Steps

- [ ] If credentials are obtained: SMB share enumeration, WinRM shell, RDP login
- [ ] Scan G6 (192.168.0.74) when ready
- [ ] Domain enumeration if NCTV360 has a domain controller

---

*No exploitation performed. This is a reconnaissance report only.*
