# G11 (192.168.0.226) — Enumeration Results

> **Target:** Windows PC "G11"  
> **Engagement Date:** 2026-03-16  
> **Operator:** Hatless White 🎯  
> **Authorization:** Verbal confirmed from G11 owner (same pal)  
> **Scope:** Recon + Enum + Vuln analysis — NO exploitation

---

## Target Identity

| Field | Value |
|-------|-------|
| Hostname | G11 |
| IP Address | 192.168.0.226 |
| MAC Address | 10:FF:E0:70:23:FB (Giga-byte Technology) |
| Workgroup/Domain | NCTV360 |
| OS | Microsoft Windows |
| Hardware | Gigabyte motherboard (possibly custom build) |

---

## Open Ports & Services

| Port | State | Service | Version/Details |
|------|-------|---------|-----------------|
| 135/tcp | Open | msrpc | Microsoft Windows RPC |
| 139/tcp | Open | netbios-ssn | NetBIOS Session Service |
| 445/tcp | Open | microsoft-ds | SMB (SMBv2/SMBv3) |
| 2179/tcp | Open | vmrdp | VMware Remote Display / Hyper-V |
| 3389/tcp | Open | ms-wbt-server | Remote Desktop Protocol |
| 5357/tcp | Open | wsdapi | Microsoft HTTPAPI (SSDP/UPnP) |
| 5985/tcp | Open | http | WinRM (Windows Remote Management) |

**⚠️ G11 has 2 MORE ports than G9:**
- **135/tcp (RPC)** — Windows RPC endpoint, can enumerate services/users
- **2179/tcp (vmrdp)** — VMware/Hyper-V remote display — suggests G11 may be running virtual machines

---

## Service Analysis

### SMB (Ports 139/445)
- **SMBv2 Security Mode:** 3:1:1 — Message signing enabled but NOT required
- **Anonymous Access:** DENIED
- **Null Session:** DENIED
- **MS17-010 (EternalBlue):** Check returned inconclusive (likely patched or needs auth)

### RPC (Port 135)
- Open and responding
- Could enumerate services, users, and shares via RPC endpoints
- Requires authentication for detailed enumeration

### RDP (Port 3389)
- **Security Layers Supported:**
  - ✅ CredSSP (NLA) — Network Level Authentication enabled
  - ✅ CredSSP with Early User Auth
  - ✅ RDSTLS
- **NLA Status:** ENABLED

### WinRM (Port 5985)
- **Status:** Responding (HTTP 404, Microsoft-HTTPAPI/2.0)
- **Auth Required:** Yes

### VMRDVP (Port 2179)
- **Service:** VMware Remote Display Protocol or Hyper-V VMRDVP
- **Implication:** G11 may host virtual machines
- **Risk:** If VMs are accessible, could pivot to guest VMs

### UPnP/WSD (Port 5357)
- **Status:** Service Unavailable (HTTP 503)

---

## NetBIOS Enumeration

```
G11             <00> - B <ACTIVE>  Workstation Service
NCTV360         <00> - <GROUP> B <ACTIVE>  Domain/Workgroup Name
G11             <20> - B <ACTIVE>  File Server Service
```

---

## Comparison: G9 vs G11

| Feature | G9 (192.168.0.214) | G11 (192.168.0.226) |
|---------|---------------------|----------------------|
| SMB (139/445) | ✅ | ✅ |
| SMB Signing | Enabled, not required | Enabled, not required |
| RDP (3389) | ✅ NLA | ✅ NLA |
| WinRM (5985) | ✅ | ✅ |
| UPnP (5357) | ✅ | ✅ |
| RPC (135) | ❌ | ✅ **NEW** |
| VMRDVP (2179) | ❌ | ✅ **NEW** |
| Domain | NCTV360 | NCTV360 |
| MAC Vendor | Unknown | Giga-byte Technology |

---

## Attack Surface Summary

```
┌─────────────────────────────────────────────────┐
│                G11 (Windows)                    │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │   RPC    │  │   SMB    │  │  VMRDVP     │  │
│  │   135    │  │  139/445 │  │    2179     │  │
│  │          │  │          │  │              │  │
│  │ Enum svc │  │ Auth req │  │ VM access?  │  │
│  │ Users?   │  │ Sign nrq │  │ Hyper-V/VM  │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │   RDP    │  │  WinRM   │  │   UPnP      │  │
│  │   3389   │  │   5985   │  │    5357     │  │
│  │          │  │          │  │              │  │
│  │ NLA ON   │  │ Auth req │  │ 503 error   │  │
│  │ Brute ok │  │ PS remte │  │ Info leak?  │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                                                 │
│  Domain: NCTV360                                │
│  Hardware: Gigabyte motherboard                 │
│  Virtualization: LIKELY (VMRDVP port open)      │
└─────────────────────────────────────────────────┘
```

---

## Potential Attack Vectors (Not Exploited)

| Vector | Feasibility | Method | Notes |
|--------|-------------|--------|-------|
| **RPC Enumeration** | 🟡 Medium | rpcclient, impacket | Enumerate users, services, shares |
| **SMB Brute Force** | 🟡 Medium | hydra, crackmapexec | Account lockout risk |
| **RDP Brute Force** | 🟡 Medium | hydra | NLA enabled, noisy |
| **WinRM Access** | 🟡 Medium | evil-winrm with creds | PowerShell access |
| **VM Escape** | 🔴 High Impact | VMRDVP (2179) | If VMs running, could pivot to guest OS |
| **SMB Relay** | 🟡 Medium | Responder + ntlmrelayx | Signing not required |

---

## Findings Summary

| # | Finding | Severity |
|---|---------|----------|
| 1 | SMB Signing not required | 🟡 Medium |
| 2 | RPC port exposed (135) | 🟢 Low |
| 3 | VMRDVP port exposed (2179) — possible VMs | 🟡 Medium |
| 4 | WinRM exposed on network | 🟢 Low |
| 5 | RDP with NLA enabled | ℹ️ Info |
| 6 | NetBIOS discloses domain (NCTV360) | ℹ️ Info |
| 7 | No anonymous SMB access | ✅ Good |
| 8 | Giga-byte hardware — custom build | ℹ️ Info |

---

*No exploitation performed. Recon + Enum + Vuln analysis only.*
