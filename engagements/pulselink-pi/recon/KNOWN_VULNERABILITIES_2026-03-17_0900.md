# Known Vulnerabilities — PulseLink Pi (Live Research)

## Electron / Chromium CVEs

### Critical — Sandbox Escape & RCE

| CVE | Component | Year | CVSS | Description | Exploitability |
|-----|-----------|------|------|-------------|---------------|
| **CVE-2025-4609** | Chromium IPC (ipcz) | 2025 | 9.8 | Sandbox escape via IPC flaw — compromised renderer gains privileged browser process handles. Leads to RCE. Patched in Chromium 136.0.7103.113. Electron apps remain vulnerable if not updated. | HIGH — exploitable via crafted HTML |
| **CVE-2025-6558** | Chromium ANGLE/GPU | 2025 | 9.6 | Zero-day sandbox escape in ANGLE/GPU component. Confirmed exploited in the wild. Affects all Electron apps embedding vulnerable Chromium. | CRITICAL — active exploitation |
| **CVE-2026-2441** | Chrome CSS parsing | 2026 | 9.1 | Zero-day: CSS `@property` + `paint()` worklet UAF → renderer-to-GPU sandbox escape. Affects Chrome and Electron. | HIGH — zero-day, likely unpatched |
| **CVE-2024-7024** | Chrome V8 | 2024 | 8.8 | Inappropriate V8 implementation → sandbox escape via crafted HTML. Fixed in Chrome 126.0.6478.54. | HIGH — if Electron version old |

### High — Context Isolation & Type Confusion

| CVE | Component | Year | CVSS | Description | Exploitability |
|-----|-----------|------|------|-------------|---------------|
| **CVE-2025-10585** | V8 (Chrome) | 2025 | 8.8 | V8 type confusion — CISA KEV catalog entry. Bypasses Electron context isolation. Can be chained with sandbox escape for full RCE. Fixed in Chrome 140.0.7339.185. | HIGH — actively exploited |
| **CVE-2025-2783** | Mojo (Chromium) | 2025 | 8.1 | Logic error in Mojo → sandbox escape on Windows. Chainable with other vulns for code execution. | MEDIUM — needs chaining |
| **CVE-2025-43529** | WebKit/Playwright | 2025 | 8.0 | Malicious webpage escapes renderer sandbox. Impacts underlying WebKit engine. | MEDIUM |
| **CVE-2023-29198** | Electron contextBridge | 2023 | 8.1 | Context isolation bypass via unserializable return values in contextBridge. Affects Electron 22.x-25.x. | HIGH — if Electron version unpatched |
| **CVE-2024-0222** | ANGLE (Chromium) | 2024 | 8.8 | Use-after-free in ANGLE → heap corruption via crafted HTML. | HIGH |
| **CVE-2024-12694** | Compositing (Chromium) | 2024 | 8.8 | Use-after-free in Compositing process → heap corruption via crafted HTML. | HIGH |

### Medium — ASAR Integrity & Updater

| CVE | Component | Year | CVSS | Description | Exploitability |
|-----|-----------|------|------|-------------|---------------|
| **CVE-2025-55305** | Electron ASAR | 2025 | 7.8 | ASAR integrity bypass via resource modification. Requires write access to filesystem. Affects apps with `embeddedAsarIntegrityValidation` + `onlyLoadAppFromAsar` fuses. | MEDIUM — needs local write |
| **CVE-2024-46992** | Electron (Windows) | 2024 | 7.5 | ASAR integrity bypass by modifying content. Affects Electron 30.0.0 and 31.0.0 beta on Windows. | LOW — Windows only |
| **CVE-2024-39698** | electron-updater | 2024 | 7.8 | Improper certificate validation on Windows. Malicious update executable if attacker has write access to launch directory. | LOW — Windows only |
| **CVE-2023-44402** | Electron (macOS) | 2023 | 7.5 | ASAR integrity bypass via filetype confusion on macOS. | LOW — macOS only |
| **CVE-2024-36287** | Electron (debug mode) | 2024 | 7.5 | Debug mode misconfiguration chainable with other vulns. Client-side injection can invoke OS commands. | MEDIUM |

---

## Linux Kernel CVEs (Raspberry Pi OS / Debian 13)

### Critical Privilege Escalation

| CVE | Component | Year | CVSS | Description | Status |
|-----|-----------|------|------|-------------|--------|
| **CVE-2025-38236** | AF_UNIX socket (Linux kernel) | 2025 | 9.8 | Use-after-free in AF_UNIX socket subsystem. Escalate from Chrome renderer sandbox to kernel-level execution. Linux-specific — affects ARM. | 🔴 Critical |
| **CVE-2024-1086** | Linux kernel (nf_tables) | 2024 | 7.8 | Use-after-free in nf_tables → local privilege escalation. Affects wide range of kernel versions. | 🔴 If unpatched |
| **CVE-2022-0847** | Linux kernel ("Dirty Pipe") | 2022 | 7.8 | Non-root users can write to root-owned files. Confirmed affecting RPi OS kernel 5.10. | 🔴 If unpatched |
| **CVE-2025-37974** | Linux kernel (various) | 2025 | TBD | Multiple kernel security issues in various subsystems. | 🟡 Needs version check |
| **CVE-2025-37750** | Linux kernel (various) | 2025 | TBD | Kernel vulnerability — details pending. | 🟡 Needs version check |
| **CVE-2025-21820** through **CVE-2025-21832** | Linux kernel | 2025 | TBD | Series of kernel vulnerabilities across subsystems. | 🟡 Needs version check |

---

## Sudo / System Privilege Escalation

| CVE | Component | Year | CVSS | Description | Status |
|-----|-----------|------|------|-------------|--------|
| **CVE-2025-32463** | sudo (critical) | 2025 | 9.8 | **Critical** — sudo 1.9.14-1.9.17 root via `--chroot` option. Path resolution in chroot before sudoers evaluation → inject `/etc/nsswitch.conf` → load rogue shared library → root. | 🔴 Critical |
| **CVE-2025-32462** | sudo (host option) | 2025 | 7.8 | Privilege escalation via host restriction misconfiguration in sudo rules. Affects 1.8.8-1.9.17. | 🟡 Config-dependent |
| **CVE-2021-3156** | sudo ("Baron Samedit") | 2021 | 7.8 | Heap-based buffer overflow in sudo (1.8.2-1.9.5p1). Local root. | 🔴 If unpatched |
| **CVE-2021-38759** | Raspberry Pi OS | 2021 | 9.8 | Default password "raspberry" for pi user not forced to change. Affects through OS 5.10. | 🔴 Check first |
| **CVE-2024-41637** | RaspAP | 2024 | 9.9 | www-data → root via restapi.service write access + NOPASSWD sudo. Only if RaspAP installed. | 🔴 If present |
| **CVE-2025-6018** + **CVE-2025-6019** | PAM + libblockdev/udisks | 2025 | 8.8 | Chained: PAM misconfiguration + udisks daemon → root for "allow_active" user. | 🔴 If unpatched |
| **CVE-2025-27591** | below (monitoring tool) | 2025 | 7.8 | Privilege escalation via world-writable directory logging error. Requires sudo access to `below`. | 🟡 If installed |
| **CVE-2025-60892** | Raspberry Pi Imager | 2025 | 5.3 | Re-adds user's `id_rsa.pub` to authorized_keys — unintended attack surface. Medium severity. | 🟡 Windows only |

---

## Widevine L3 (DRM) — Known Attacks

| Attack | Year | Method | Impact |
|--------|------|--------|--------|
| **DFA on white-box AES** | 2019 | Differential Fault Analysis recovers encryption keys from Chrome's Widevine L3 | Content key extraction |
| **Full L3 reverse engineering** | 2020-2021 | Complete reverse of Android Widevine L3 CDM implementation | Full DRM bypass |
| **KeyDive tool** | Ongoing | Python + Frida automated key extraction from L3 devices | Device key + content key theft |
| **Qiling emulation + DFA** | Ongoing | Emulate Android Widevine libs on Linux + fault analysis | Key extraction on Linux hosts |

---

## Vulnerability Prioritization for This Engagement

### P0 — Check Immediately
1. **Default password** (`pi`/`raspberry`) — CVE-2021-38759
2. **Electron/Chromium version** — Check against CVE-2025-4609, CVE-2025-6558, CVE-2025-10585
3. **sudo version** — Check against CVE-2025-32463
4. **Kernel version** — Check against Dirty Pipe, CVE-2024-1086, CVE-2025-38236

### P1 — Exploit if Available
1. Chromium sandbox escapes (CVE-2025-4609, CVE-2026-2441)
2. V8 type confusion for context isolation bypass (CVE-2025-10585)
3. Kernel privilege escalation (CVE-2024-1086, Dirty Pipe)
4. UART/JTAG physical access

### P2 — Secondary
1. ASAR tampering (requires filesystem write access)
2. Widevine L3 key extraction
3. User data directory forensics
4. Network service exploitation

---

*CVE data sourced from NVD, Snyk, GitHub Security Advisories, CISA KEV, and vendor disclosures. Last updated: 2026-03-17.*
