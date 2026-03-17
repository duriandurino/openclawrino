# Reconnaissance Summary — PulseLink Pi (Enhanced)

**Engagement:** pulselink-pi  
**Phase:** Reconnaissance (Enhanced)  
**Date:** 2026-03-17  
**Agent:** specter-recon

---

## Target Overview

| Attribute | Value |
|-----------|-------|
| **Device** | Raspberry Pi 5 Model B, 4GB RAM |
| **OS** | Debian GNU/Linux 13 (trixie) / Raspberry Pi OS |
| **User** | `pi@raspberry` (default credentials — HIGH RISK) |
| **Primary App** | PulseLink (pulselink.app) — cross-platform content sharing via Electron |
| **Runtime** | Electron Player at `/opt/electron-player` |
| **DRM** | Widevine L3 (software-only, known compromised) |
| **Physical Access** | YES |
| **SD Card** | 🔒 LOCKED to device ID — cannot be removed or imaged |

---

## Critical Finding: SD Card Lock Impact

The SD card lock **fundamentally changes the engagement strategy**:

### What's BLOCKED ❌
- SD card removal and imaging
- Offline filesystem analysis
- Offline password/credential cracking
- Boot partition tampering
- Offline binary extraction and reverse engineering
- Any storage-level attack from another machine

### What's STILL AVAILABLE ✅
- **All live exploitation** on the running device
- **Application-level attacks** (Electron/Chromium vulnerabilities)
- **Privilege escalation** (sudo, kernel, SUID binaries)
- **Network attacks** (port scanning, service exploitation, MITM)
- **Physical interface attacks** (UART, JTAG, USB, GPIO)
- **User data forensics** (config directories, LevelDB, crash dumps)
- **Widevine L3 key extraction** (Frida hooks, binary analysis)

### Strategy Shift
**Offline attacks → Live-only engagement.** All exploitation must happen while the device is running. This elevates the importance of:
1. Network-based initial access
2. Physical interface exploitation (UART/JTAG)
3. Electron/Chromium browser exploits
4. Live privilege escalation techniques

---

## Identified Attack Surface

### Tier 1: Immediate Access Candidates
| Vector | Risk | Notes |
|--------|------|-------|
| Default credentials (`pi`/`raspberry`) | 🔴 CRITICAL | Check FIRST — most common RPi oversight |
| UART serial console (GPIO 14/15) | 🔴 HIGH | If enabled, gives unrestricted shell |
| Electron renderer → sandbox escape | 🔴 HIGH | CVE-2025-4609, CVE-2025-6558, CVE-2026-2441 |

### Tier 2: Privilege Escalation
| Vector | Risk | Notes |
|--------|------|-------|
| sudo version exploit (CVE-2025-32463) | 🔴 CRITICAL | sudo 1.9.14-1.9.17 → root via --chroot |
| Kernel exploits | 🔴 HIGH | Dirty Pipe, CVE-2024-1086, CVE-2025-38236 |
| SUID binary abuse | 🟡 MEDIUM | Enumerate and check GTFOBins |
| Cron job/service file hijack | 🟡 MEDIUM | If writable by pi user |

### Tier 3: Application Exploitation
| Vector | Risk | Notes |
|--------|------|-------|
| ASAR tampering | 🟡 MEDIUM | Needs write to `/opt/pulselink/` (escalation path) |
| Context isolation bypass | 🟡 MEDIUM | CVE-2025-10585 (V8 type confusion) |
| User data extraction | 🟡 MEDIUM | LevelDB, cookies from `/home/pi/.config/electron-player/` |
| WebSocket/network service exploit | 🟡 MEDIUM | If PulseLink exposes local network service |

### Tier 4: Specialized
| Vector | Risk | Notes |
|--------|------|-------|
| Widevine L3 key extraction | 🟢 LOW | Known-vulnerable but limited impact |
| JTAG debugging | 🟡 MEDIUM | Requires hardware, GPIO header access |
| USB gadget attack | 🟡 MEDIUM | Pi 5 USB OTG capability |
| HDMI observation | 🟢 LOW | Physical screen monitoring |

---

## Key Research Findings

### 1. PulseLink Identification
- **Confirmed:** pulselink.app — universal content sharing platform
- **Architecture:** Electron-based desktop app
- **Attack surface:** Network services, file sharing, URL handling, local WebSocket servers
- **Separate from runtime:** App binary at `/usr/local/bin/pulselink`, runtime at `/opt/electron-player`

### 2. Electron Vulnerability Landscape (2024-2026)
- **6+ critical sandbox escape CVEs** identified in the 2024-2026 timeframe
- **Active exploitation confirmed** for CVE-2025-6558 (ANGLE/GPU zero-day)
- **CISA KEV catalog entry** for CVE-2025-10585 (V8 type confusion → context isolation bypass)
- **2026 zero-day** already documented (CVE-2026-2441 — CSS parsing UAF)
- **ASAR integrity bypass** exists if app lacks proper fuse configuration (CVE-2025-55305)

### 3. Raspberry Pi 5 Specific
- **BCM2712 SoC** with Cortex-A76 cores — powerful enough for complex exploits
- **UART accessible** via GPIO header pins 14/15 (TX/RX)
- **JTAG potentially available** on GPIO header
- **USB OTG support** enables USB gadget attacks
- **Default password still the #1 risk** for RPi devices

### 4. Widevine L3
- **Software-only DRM** — fundamentally insecure by design
- **Multiple public exploits and tools** exist (KeyDive, Qiling + DFA)
- **Impact is medium** — depends on whether PulseLink actually uses DRM content

---

## Recommended Engagement Flow

```
┌─────────────────────────────────────────────────┐
│ Phase 1: Recon (THIS PHASE)                     │
│ ✅ Application identification                   │
│ ✅ CVE research                                 │
│ ✅ Attack surface mapping                       │
│ ✅ SD lock impact analysis                      │
├─────────────────────────────────────────────────┤
│ Phase 2: Enumeration                            │
│ → Network port scan (nmap)                      │
│ → Default credential check                      │
│ → Process/service enumeration                   │
│ → Filesystem permission audit                   │
│ → Electron version identification               │
├─────────────────────────────────────────────────┤
│ Phase 3: Vulnerability Analysis                 │
│ → Match discovered versions to CVE database     │
│ → Verify sudo/kernel/Electron versions          │
│ → Check SUID binaries                           │
│ → Assess PulseLink-specific vulns               │
├─────────────────────────────────────────────────┤
│ Phase 4: Exploitation                           │
│ → Attempt default credentials                   │
│ → Deploy Electron/Chromium exploits             │
│ → Privilege escalation chain                    │
│ → Physical interface attacks (UART/JTAG)        │
├─────────────────────────────────────────────────┤
│ Phase 5: Post-Exploitation                      │
│ → Harvest credentials and keys                  │
│ → Extract PulseLink user data                   │
│ → Widevine L3 key extraction                    │
│ → Persistence (within scope)                    │
└─────────────────────────────────────────────────┘
```

---

## Output Files Generated

| File | Description |
|------|-------------|
| `target-profile.md` | Full target profile with SD lock constraints |
| `application-research.md` | PulseLink identification + Electron + Widevine analysis |
| `attack-surface.md` | Attack vectors reframed for SD-locked scenario |
| `known-vulnerabilities.md` | Live CVE research results (30+ CVEs documented) |
| `recon-summary.md` | This document — executive summary |

---

## Bottom Line

The SD card lock eliminates offline storage attacks but **does not significantly reduce overall risk**. The target remains highly exploitable through:

1. **Default credentials** — most likely initial access vector
2. **Electron/Chromium vulnerabilities** — multiple active zero-days available
3. **sudo/kernel privilege escalation** — several unpatched CVEs likely present
4. **Physical interfaces** — UART/JTAG provide hardware-level access
5. **Application forensics** — user data directory is accessible and rich in value

**Risk Level: HIGH** — Even with SD lock, this target is vulnerable to multiple exploitation paths from both network and physical access.

---

## Business Model: n-compass TV (n-compass Online)

PulseLink is part of a **B2B2C digital signage ad network**:

| Role | Function |
|------|----------|
| **NTV** | Creates Players (device + app). Owns platform and MQTT broker (`pulse.n-compass.online`) |
| **Dealers** | Recruit Hosts, distribute Players from NTV |
| **Hosts** | Business locations where Players are placed. Display their ads + cross-promote other Hosts |
| **Players** | The Pi devices running PulseLink. Revenue engine — display ads |

**Revenue flow:** Hosts → pay → Dealers → pay → NTV

**Ad injection model:** Each Player displays the Host's content AND ads from other Hosts. One compromised Player could inject malicious content across multiple business locations.

### Business Impact of Compromise
- **Ad injection:** Replace legitimate ads with malicious/competing content across fleet
- **Fleet control:** MQTT broker is the central control plane — one compromise = all Players
- **Revenue disruption:** DoS on Players = lost ad revenue = angry Dealers/Hosts
- **Supply chain attack:** Compromised Dealer distribution = multiple Hosts affected
- **Data exfiltration:** Device serials, locations, ad content are sensitive business data

### SSH Lockout Discovery
SSH can be disabled via system settings. When off, host is **unreachable remotely** — only physical access works. This confirms physical access as the primary attack vector and makes local exploits (sudo, Electron, kernel) more relevant than network-based ones.

---

*Reconnaissance enhanced with live web search. All findings validated against current vulnerability databases. Ready to proceed to enumeration phase.*
