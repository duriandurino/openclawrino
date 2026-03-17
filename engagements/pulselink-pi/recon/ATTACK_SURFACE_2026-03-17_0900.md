# Attack Surface Analysis — PulseLink Pi (SD-Locked Scenario)

## Executive Summary

With the SD card cryptographically locked to the device ID, the attack surface is **significantly altered**. Offline storage attacks (imaging, mounting, offline password cracking) are **completely eliminated**. All exploitation must occur on the **live, running device**. This reframes the engagement around live privilege escalation, application exploitation, network attacks, and physical interface access.

---

## 🚫 BLOCKED by SD Card Lock

These classic Raspberry Pi attack vectors are **NO LONGER AVAILABLE**:

| Attack | Method | Status |
|--------|--------|--------|
| **SD card imaging** | Remove card → `dd` image → analyze offline | ❌ BLOCKED |
| **Offline filesystem mount** | Mount ext4 partition on attack machine | ❌ BLOCKED |
| **Offline shadow file cracking** | Extract `/etc/shadow` → hashcat/john | ❌ BLOCKED |
| **Offline credential harvesting** | Read SSH keys, config files from mounted FS | ❌ BLOCKED |
| **Filesystem modification** | Plant backdoors, modify configs offline | ❌ BLOCKED |
| **Boot partition tampering** | Modify `/boot/config.txt`, inject kernel params | ❌ BLOCKED |
| **Offline binary analysis** | Copy and reverse-engineer binaries offline | ❌ BLOCKED |
| **SD card cloning** | Create identical copy for sandbox testing | ❌ BLOCKED |

---

## ✅ STILL AVAILABLE — Live Attack Vectors

### Category 1: Application-Level Attacks (HIGH PRIORITY)

| Vector | Description | Entry Point | Impact |
|--------|-------------|-------------|--------|
| **Electron renderer exploit** | XSS → sandbox escape → RCE | PulseLink UI vulnerabilities | Full user compromise |
| **ASAR tampering** | Modify `/opt/pulselink/resources/app.asar` | Write access to `/opt/pulselink` (if escalated) | Persistent backdoor |
| **Context isolation bypass** | Break out of Electron's security context | Renderer process exploit | Node.js API access |
| **Chromium sandbox escape** | CVE-2025-4609, CVE-2025-6558, CVE-2026-2441 | Malicious content in renderer | Kernel-level access |
| **WebSocket injection** | Inject into PulseLink's local WebSocket server | Local network/localhost | Data manipulation |
| **Protocol handler exploit** | Abuse PulseLink's custom URL scheme | User interaction or automated | Code execution |
| **User data extraction** | Read Local Storage, cookies from config dir | `/home/pi/.config/electron-player/` | Credential theft |

### Category 2: Privilege Escalation (pi → root)

| Vector | CVE/Technique | Description | Status |
|--------|---------------|-------------|--------|
| **Default password** | CVE-2021-38759 | If password still "raspberry" | ⚠️ Check first |
| **sudo chroot exploit** | CVE-2025-32463 | sudo 1.9.14-1.9.17 root via --chroot | 🔴 If unpatched |
| **sudo host option** | CVE-2025-32462 | Privilege escalation via host restrictions | 🟡 Config-dependent |
| **SUID binary abuse** | GTFOBins | Find and exploit SUID binaries | 🟡 Standard technique |
| **Kernel exploit** | CVE-2024-1086, Dirty Pipe CVE-2022-0847 | Linux kernel privilege escalation | 🔴 If unpatched |
| **RaspAP exploit** | CVE-2024-41637 | www-data → root via restapi.service | 🔴 If RaspAP installed |
| **Cron job hijack** | Manual analysis | Modify root-run scripts | 🟡 If writable |
| **Writable service files** | Manual analysis | Modify systemd service configs | 🟡 If misconfigured |
| **PAM/udisks chain** | CVE-2025-6018 + CVE-2025-6019 | Chain to root | 🔴 If unpatched |
| **below LPE** | CVE-2025-27591 | Root via sudo access to `below` | 🟡 If installed |

### Category 3: Network Attacks

| Vector | Description | Requirements | Impact |
|--------|-------------|--------------|--------|
| **Port scanning** | Identify listening services | Network access to Pi | Service discovery |
| **PulseLink network service** | Exploit exposed WebSocket/HTTP server | Pi on same network | App compromise |
| **Man-in-the-middle** | ARP spoof between Pi and paired devices | Local network access | Data interception |
| **SSH brute force** | If SSH enabled with default creds | Network access | User compromise |
| **mDNS/Bonjour discovery** | Discover PulseLink via zero-config | Same subnet | Service enumeration |
| **API endpoint exploitation** | If PulseLink exposes REST/GraphQL API | Network access | Data extraction |
| **Update mechanism interception** | CVE-2024-39698 — electron-updater improper cert validation | Network access + write to launch dir | Malicious update |

### Category 3.5: Physical Keyboard/Mouse Access (CRITICAL — CONFIRMED)

| Vector | Description | Impact |
|--------|-------------|--------|
| **Direct terminal access** | Open terminal on Pi directly — BYPASSES SSH password entirely | Full user shell without credentials |
| **Task Manager access** | `htop`/Task Manager to view processes, CPU, memory, ports | Live system reconnaissance |
| **Ctrl+Q / Ctrl+W** | Quits PulseLink player briefly; auto-restarts after short delay | Temporary app disruption for analysis |
| **Ctrl+R** | Restarts player by **synchronizing content to cloud** | Triggers network activity — MITM opportunity |
| **GUI exploration** | Browse directories, open files, inspect configs via GUI file manager | Full filesystem access as `pi` user |
| **Browser access** | Open Chromium on Pi to research/verify versions online | No need for remote tools |

**This is the highest-value attack vector** — physical keyboard + mouse gives full `pi` user shell access without needing SSH, UART, or any credentials. Simply open a terminal application on the Pi desktop.

### Category 4: Physical Interface Attacks

| Interface | Attack | Difficulty | Notes |
|-----------|--------|------------|-------|
| **UART (GPIO 14/15)** | Serial console access → root shell | Easy | If UART enabled in `/boot/config.txt` |
| **JTAG (GPIO)** | Hardware debugging → full memory access | Medium | BCM2712 JTAG pins on GPIO header |
| **USB ports** | USB gadget attack (Raspberry Pi acts as HID) | Medium | Pi 5 supports USB OTG |
| **USB injection** | Malicious USB device → keystroke injection | Easy | If USB ports accessible |
| **HDMI** | Connect display to observe screen output | Trivial | Physical observation |
| **GPIO sensors** | Side-channel analysis via GPIO | Hard | Power analysis, timing attacks |
| **SPI/I2C buses** | Intercept peripheral communication | Medium | If devices on these buses |
| **Power glitching** | Voltage glitching for fault injection | Hard | Requires specialized hardware |

### Category 5: Widevine L3 DRM Attacks

| Vector | Description | Impact |
|--------|-------------|--------|
| **CDM binary analysis** | Reverse engineer `/opt/WidevineCdm` | Key extraction |
| **Frida hooking** | Inject into Widevine process at runtime | Content key theft |
| **Content decryption** | Extract decrypted media streams | DRM bypass |
| **Device key extraction** | Recover L3 device private key | Full DRM compromise |

---

## Recommended Attack Strategy (SD-Locked + Physical Access)

### Phase 1: Initial Access (CRITICAL — Use Physical Terminal!)
1. **Open terminal directly on Pi** — bypasses SSH password entirely
2. Run `whoami` / `id` / `pwd` to confirm `pi` user shell
3. Check SSH rejection reason: was default password changed, or SSH key-only?
4. Enumerate from shell: `sudo -l`, `ps aux`, `crontab -l`, `ls -la /opt/`
5. **Monitor Ctrl+R behavior** — sync-to-cloud triggers network traffic for capture
6. **Test Ctrl+Q/Ctrl+W** — brief app pause = window for file inspection

### Phase 2: Active Enumeration
1. Enumerate from shell: `sudo -l`, `ps aux`, `systemctl status pulselink`
2. Extract secrets: `.env`, certificates, registration data
3. Analyze MQTT broker communication
4. Map the n-compass TV business model (NTV → Dealers → Hosts → Players)
5. If SSH is disabled, all interaction must be physical — adjust methodology accordingly

### Phase 3: Privilege Escalation
1. Exploit Electron/Chromium vulnerabilities (CVE-2025-4609, CVE-2025-6558)
2. Check sudo version for CVE-2025-32463
3. Enumerate SUID binaries and kernel version
4. Look for writable service files, cron jobs

### Phase 4: Post-Exploitation
1. Extract PulseLink app data from user config
2. Harvest credentials and API keys
3. Analyze WidevineCdm for DRM key material
4. Establish persistence (if within scope)

### Phase 5: Physical (if permitted)
1. UART console access for unrestricted shell
2. JTAG debugging for memory forensics
3. USB gadget attacks for covert access

---

## Risk Matrix

| Vector | Likelihood | Impact | Risk | Priority |
|--------|-----------|--------|------|----------|
| **Physical keyboard/mouse terminal** | **CONFIRMED** | **CRITICAL** | 🔴 | **P0 — USE NOW** |
| Default credentials | BLOCKED (changed) | CRITICAL | ❌ | Blocked |
| Electron renderer RCE | HIGH | HIGH | 🔴 | P0 |
| sudo privilege escalation | MEDIUM | CRITICAL | 🔴 | P1 |
| Kernel exploit | MEDIUM | CRITICAL | 🔴 | P1 |
| UART physical access | HIGH | HIGH | 🟠 | P1 |
| ASAR tampering | LOW (needs write) | HIGH | 🟡 | P2 |
| Widevine extraction | MEDIUM | LOW | 🟢 | P3 |
| Network MITM | MEDIUM | MEDIUM | 🟡 | P2 |

---

*Attack surface reframed for SD-locked scenario. All offline storage vectors eliminated. Focus shifted to live exploitation.*
