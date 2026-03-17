# MEMORY.md — Long-Term Memory

## Pentest Target: Raspberry Pi 5B

- **Target type:** Raspberry Pi 5 Model B
- **Network:** Mixed environment — Windows 11 PCs on same network, Raspi as primary target
- **Physical access:** YES — physical penetration testing is in scope (USB attacks, HDMI, GPIO, SD card, power analysis, JTAG/debug interfaces)
- **Storage lock:** The Raspi's storage device (SD card / NVMe) is locked to the device ID — cannot be cloned or imaged on another machine. All storage-level attacks must happen on the device itself.
- **Attack surface includes:** Network (SSH, services, misconfig) + Physical (USB, GPIO, serial, display output, power side-channels)

## Agent Architecture (Active)

| Agent | Model | Role |
|-------|-------|------|
| specter-recon | xploiter/pentester | Passive recon, OSINT, DNS, Shodan |
| specter-enum | xploiter/pentester | Active scanning, nmap, dirbust |
| specter-vuln | xploiter/the-xploiter | Vulnerability analysis, CVE matching |
| specter-exploit | xploiter/the-xploiter | Exploitation, Metasploit |
| specter-post | xploiter/the-xploiter | PrivEsc, lateral movement, persistence |
| specter-report | xploiter/pentester | Report generation |
| specter-skillcrafter | xploiter/pentester | Creates OpenClaw agent skills |

## Reporting Agent Requirements

- Pentest reports MUST include **security enhancement recommendations** for every vulnerability found
- Each finding should have:
  - Vulnerability description
  - Severity (CVSS or Critical/High/Medium/Low)
  - Proof of concept / evidence
  - **Remediation steps with specific actions**
  - **Hardening recommendations** (not just "fix it" — concrete steps)
- Goal: client should finish reading with an action plan, not just a list of problems

## Tools & Environment

- **OS:** Kali Linux
- **AI models:** ollama/xploiter/pentester (1.6GB), ollama/xploiter/the-xploiter (9.2GB)
- **OpenClaw:** Configured with maxSpawnDepth: 2, maxChildrenPerAgent: 5
- **Skillcrafter:** Custom skill authoring tool created (strict validation, example-driven)
- **Presentation Skill:** New skill created at `skills/presentation/` — generates slide decks from pentest reports. User specifies slide count, skill generates structured slides with speaker notes.
- **GitHub repo:** https://github.com/duriandurino/openclawrino.git
- **Telegram group name:** Changed from "WhiteClaw" to "Penetrator" (2026-03-17)
- **Web search:** Gemini provider configured and working (Google AI Studio API key)

## Presentation Context (2026-03-17)
- **Audience:** Professional presentation
- **Purpose:** Demonstrate value of the Pentester role
- **Scope:** Raspberry Pi as example, but generalizable to all pentesting
- **Deliverable:** Report + Demo
- **Structure needed:** Problem → Tool → Demo (Why, How, When)
- **Key narrative:** Why OpenClaw over other tools, vulnerability and process explanation
- **Goal:** Show OpenClaw can be implemented for general penetration testing, not just RPi

## Additional Observations (2026-03-17)
- **Kill switch:** Easy with physical access. Newer versions have watchdog mitigation. Older deployments still vulnerable.
- **SSH disabled:** Production config — forces physical approach, limits network attacks
- **UART via GPIO:** Untested attack vector — high-priority unaddressed gap
- **App-layer only:** Without physical access, Electron is the only viable attack vector
- **Network surface:** PulseLink is client-only, no inbound services exposed — intentionally minimal

## Raspberry Pi 5 — Confirmed Versions (2026-03-17 via Physical Terminal)
- **Kernel:** 6.12.47-rpt-rpi-2712 (Debian 1:6.12.47-1+rpt1, 2025-09-16, aarch64)
- **Sudo:** 1.9.16p2 — VULNERABLE to CVE-2025-32463 (range: 1.9.14-1.9.17)
- **Node.js:** v22.22.0
- **Electron:** 35.4.0 (Chromium 134.0.6998.179)
- **PulseLink:** 2.0.0 (portable=false, running=true, config at /home/pi/.config/pulselink)
- **pi user:** UID/GID 1000, in sudo group, **NOPASSWD: ALL** (instant root!)
- **Hardware access:** gpio, i2c, spi, video, audio, input, render groups

## Raspberry Pi 5 — Network Profile (2026-03-17)
- **Target IP:** 192.168.0.125/24 (wlan0)
- **Gateway (likely):** 192.168.0.1
- **eth0:** DOWN (no cable, MAC: 2c:cf:67:04:0b:d0)
- **wlan0:** UP (MAC: 2c:cf:67:04:0b:d1)
- **Network reachability:** Live on WiFi, accessible from local network
- **Physical access:** Keyboard + mouse confirmed (direct terminal access — BYPASSES SSH!)
- **SSH default password:** CHANGED (pi/raspberry rejected)

## PulseLink Keyboard Shortcuts (Discovered 2026-03-17)
- **Ctrl+Q** — Quits player briefly; auto-restarts after short delay
- **Ctrl+W** — Same as Ctrl+Q (quit + auto-restart)
- **Ctrl+R** — Restarts player by **synchronizing content to cloud** (triggers network activity — MITM opportunity)

## Raspberry Pi 5 — New Directory Discovery (2026-03-17)
- **`/opt/electron-player/resources/scripts/`** — SUBDIRECTORY FOUND inside accessible electron-player dir
- This was navigated out of (`cd ..` twice), suggesting user explored it
- HIGH PRIORITY for Enum — scripts could contain configs, launch logic, credentials

## n-compass TV Business Model (Discovered 2026-03-17)
**Architecture:** B2B2C digital signage ad network

| Role | Description |
|------|-------------|
| **NTV (n-compass TV)** | Company that creates Players (device + app). Owns the platform and MQTT broker |
| **Dealers** | Middlemen who recruit Hosts and distribute Players from NTV |
| **Hosts** | Businesses/locations where Players are physically placed. Play their own ads + other Hosts' ads |
| **Players** | Raspberry Pi devices running PulseLink. Generate revenue by displaying ads |

**Payment Flow:** Hosts pay Dealers → Dealers pay NTV (Players are the revenue engine)

**Ad Network Model:** Each Player displays:
- The Host's own ads
- Ads from OTHER Hosts in the network (cross-promotion)

**Security Implications:**
- Compromised Player = ad injection across multiple Hosts (supply chain attack)
- MQTT broker (`pulse.n-compass.online`) = central control plane for entire fleet
- Device downtime = direct revenue loss (incentive for always-on)
- Dealer as intermediary = supply chain trust boundary
- Fleet-wide compromise possible via MQTT broker

## SSH Lockout Discovery (2026-03-17)
- SSH can be **disabled via system settings** (not just stopped)
- When SSH is off, **host is unreachable remotely** — only physical access works
- This is a **security feature** but also means remote pentest is impossible without SSH
- Confirms physical access is the primary attack vector for this engagement
- **IMPORTANT:** Network attack chain (tcpdump, mosquitto_sub, MQTT exploitation) was NEVER executed — only theoretical documentation. All network-phase files removed from workspace.
