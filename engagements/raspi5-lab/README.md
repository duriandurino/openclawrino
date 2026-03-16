# Raspberry Pi 5B Penetration Testing — Master Guide

> **Target:** Raspberry Pi 5 Model B  
> **Engagement Date:** 2026-03-16  
> **Operator:** Hatless White 🎯  
> **Authorization:** Confirmed (physical + network access in scope)

---

## ⚠️ CRITICAL CONSTRAINT: Storage Device Lock

The Raspberry Pi 5B's storage device (SD card / NVMe HAT) is **locked to the device ID**. This means:

- ❌ **Cannot clone** the SD card or NVMe on another machine
- ❌ **Cannot image** the storage for offline analysis
- ❌ **Cannot swap** storage between Pi units — it won't boot
- ✅ **All storage-level attacks MUST happen on the device itself**
- ✅ **Physical access is required** for storage manipulation
- ✅ **Booting from external media** (USB/NVMe) is still possible if configured

**This fundamentally changes the pentest approach.** We can't pull the SD card, mount it on our Kali box, and analyze it offline. We need to:
1. Gain physical access
2. Get a shell (network or hardware)
3. Exfiltrate data live, or
4. Manipulate the running system in-place

---

## Engagement Directory Structure

```
engagements/raspi5-lab/
├── README.md              ← This file (master guide)
├── recon/                 ← Passive recon & OSINT docs
├── enum/                  ← Active enumeration docs
├── exploit/               ← Hardware attacks & exploitation
├── vuln/                  ← Vulnerability analysis
├── post-exploit/          ← Post-exploitation, storage lock bypass
├── reporting/             ← Final report & remediation
├── evidence/              ← Raw scan outputs, captures, hashes
└── loot/                  ← Exfiltrated data, configs, keys
```

---

## Attack Surface Summary

```
┌─────────────────────────────────────────────────────────┐
│                   RASPBERRY PI 5B                       │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐    │
│  │ NETWORK  │  │ PHYSICAL │  │     WIRELESS       │    │
│  │          │  │          │  │                    │    │
│  │ • SSH    │  │ • GPIO   │  │ • WiFi (802.11ac) │    │
│  │ • HTTP   │  │ • UART   │  │ • Bluetooth 5.0   │    │
│  │ • Samba  │  │ • JTAG*  │  │ • BLE             │    │
│  │ • NFS    │  │ • USB    │  │                    │    │
│  │ • VNC    │  │ • HDMI   │  │                    │    │
│  │ • mDNS   │  │ • SD Card│  │                    │    │
│  └──────────┘  │ • Power  │  └────────────────────┘    │
│                └──────────┘                             │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │               STORAGE (LOCKED)                   │   │
│  │  • SD Card (microSD) — device-bound              │   │
│  │  • NVMe (via HAT) — device-bound                 │   │
│  │  • USB boot possible (if configured)             │   │
│  │  • Cannot image/clone to another machine         │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              BCM2712 SoC (Pi 5)                  │   │
│  │  • ARM Cortex-A76 quad-core @ 2.4GHz            │   │
│  │  • RP1 I/O controller (new in Pi 5)             │   │
│  │  • VideoCore VII GPU                            │   │
│  │  • Hardware crypto engine                        │   │
│  │  * JTAG not exposed on standard headers          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Methodology Overview

### Phase 1: Passive Recon
- Network discovery (who's on the LAN?)
- mDNS/Avahi enumeration
- Service fingerprinting from the network
- OSINT on the Pi's public-facing surface (if any)

### Phase 2: Active Enumeration
- Targeted nmap scans
- Service version detection
- SSH configuration analysis
- Web service discovery (if running)
- Samba/NFS enumeration

### Phase 3: Hardware Attacks
- **UART console access** (primary hardware vector)
- GPIO manipulation
- USB attack vectors (BadUSB, HID injection)
- HDMI/display output analysis
- Power side-channel analysis
- NVMe/SD card physical inspection

### Phase 4: Storage Lock Exploitation
- On-device forensics (live system)
- Boot sequence manipulation
- Alternative boot media attacks
- Config file extraction
- Key/certificate recovery from live memory

### Phase 5: Vulnerability Analysis
- OS version → CVE matching
- Kernel exploit assessment
- Service misconfiguration checks
- Default credential testing
- Firmware analysis

### Phase 6: Exploitation
- Network-based attacks
- Local privilege escalation
- Physical access exploits
- Credential attacks

### Phase 7: Post-Exploitation
- Persistence mechanisms
- Data exfiltration
- Lateral movement to other hosts
- Evidence collection

---

## Pi 5B-Specific Notes

### What's New vs Pi 4
- **RP1 I/O chip** — new southbridge, different GPIO handling
- **BCM2712 SoC** — different from BCM2711 (Pi 4), some kernel drivers differ
- **PCIe 2.0 x1** — enables NVMe HAT (fast storage = new attack surface)
- **True Gigabit Ethernet** — no longer USB-shared, different network behavior
- **2x USB 3.0 + 2x USB 2.0** — USB attack surface remains
- **5-pin UART header** — broken out for debug (prime hardware vector)
- **Power button** — new physical interaction point
- **RTC battery connector** — new surface for persistence?

### What's the Same
- Still runs Raspberry Pi OS (Debian-based)
- SSH, VNC, and default service landscape unchanged
- Boot from SD/NVMe/USB still uses same config.txt mechanisms
- User management, sudo, group membership — standard Linux

---

## Quick Start Checklist

- [ ] Confirm target IP (nmap -sn on local subnet)
- [ ] Identify OS version (SSH banner, service fingerprint)
- [ ] Check for default credentials (pi/raspberry, or custom?)
- [ ] Map open ports and services
- [ ] Assess physical access vectors (UART pins, USB ports)
- [ ] Check boot configuration (config.txt, cmdline.txt)
- [ ] Test for storage lock (can we image the SD? no.)
- [ ] Plan on-device vs off-device attack strategy

---

*This is a living document. Update as the engagement progresses.*
