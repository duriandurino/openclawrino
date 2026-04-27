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
- **Google / gog automation:** Stable passphrase preference is `hatlesswhite`. Reuse this for `GOG_KEYRING_PASSWORD` and related re-auth/reset flows unless the user changes it.
- **OpenCode preference:** For coding-heavy implementation work, default to OpenCode first unless the user explicitly asks for another harness.
- **OpenCode helpers:** Reusable vibe-coding helpers live at `scripts/opencode/reusable/opencode_vibe_loop.py` and `scripts/opencode/reusable/opencode_vibe_swarm.py` for main-session or sub-agent implementation work.
- **Session reset harness caveat:** `memory/` is gitignored, so `scripts/session_flush_harness.py` can write the daily memory note locally but the durable reset checkpoint for handoff/commit is `state/session-reset-handoff.json`.

## Quick Scan / Reporting Lessons (2026-04-08)

- Adaptive quick scan must affect the **actual findings and recommendation mix**, not just the narrative wrapper.
- Different webapps may share some baseline findings, but the final quick-scan finding set should diverge when target fingerprint/context differs.
- The quick-scan pipeline had two separate flattening issues that were fixed:
  - published final report flow was dropping adaptive context and reverting to a generic template
  - final finding synthesis was converting candidate rows too directly, causing different webapps to inherit nearly identical findings
- Publishing reliability issue was traced to **gog file-keyring passphrase mismatch**, not random Google auth breakage. Avoid forcing guessed fallback passphrases.
- Quick-scan publishing now writes compact `.publish.json` summaries so link retrieval does not depend on scraping long console logs.
- Quick scans are not complete until published outputs are generated, retrieved, and sent back to the user.
- Published quick-scan links must be retrieved with `scripts/quick-scan/get_publish_links.py`, not copied manually from logs or memory.
- PPT generation was improved to scale with findings, so slide decks can expand beyond a near-fixed length when the evidence warrants it.
- On 2026-04-13, non-interactive gog publishing was re-verified with `GOG_KEYRING_PASSWORD=hatlesswhite`, and the final quick-scan publish summary output was cleaned so the links block is emitted once with correct docs/PDF/slides/drive mapping.
- User preference reinforced on 2026-04-14: for report-capable workflows, publishing should be automatic and prioritized by default, without waiting for an extra confirmation, unless the user explicitly says not to publish.

## Workflow / Documentation Rules (2026-04-17)

- For direct requests like `pentest <target>`, always send the short pre-engagement intake first and do not begin active testing until authorization and scope are explicit.
- That intake rule is now pinned in both `AGENTS.md` and `skills/pentest-orchestrator/SKILL.md`.
- Docs report output should include the pre-engagement charter / ROE details from `engagements/<target>/00-charter/engagement-charter.md` and `scope-and-roe.md`.
- This pre-engagement intake section is **Docs-only**. PPT / slide output should stay unchanged unless explicitly requested.
- Do not assume a local CVSS research/reference standard exists yet. The user plans to add it later under `pentest-references/`, and reporting/skills should only wire to it after those files are actually present.

## Migration / Player V2 Packaging Notes (2026-04-16)

- Full `~/.openclaw` backup/restore is the simplest brain-migration path to a new Linux PC. Best practice is fresh install first, stop OpenClaw, restore `~/.openclaw`, then restore extra auth outside it such as `~/.ssh`, git creds, optional `~/.ollama`, and related tool config.
- `memory/` is gitignored, so it must be copied manually during migration even if the repo itself is restored cleanly.
- The reusable Player V2 package was finalized for live Raspi testing. Beginner run order is: setup, shared install if needed, package install if needed, bootstrap/work folder, device baseline, network check, local files, secrets, final bundle.
- `pandoc` remains optional and missing in this environment, so markdown bundle generation works, but HTML/PDF/PPTX export requires pandoc on the target system.

## Context / Reset Workflow Notes (2026-04-20)

- A new soft command, `/remember`, is intended as the reset-safe recall entry point for durable context snapshots.
- When implementing or using reset-safe context capture, keep the saved snapshot concise and centered on the current task, objective, and immediate next action.
- Durable reset handoff state belongs in `state/session-reset-handoff.json`, not in `memory/`, because `memory/` is gitignored.

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

## Vault.img Decryption (2026-03-18)
- **LUKS2 encrypted:** AES-XTS-256, argon2id PBKDF, UUID `9757eca5-e8a1-4f8a-9c20-8c9252d61d09`
- **Location:** `/home/pi/vault.img` (separate from SD card partition)
- **Key slot 0 enabled**, 8 total slots
- **cryptsetup 2.6.0** on Player
- **Passphrase NOT found in nctv-installer/** — scripts are just app installers (NGINX, Node 20, Chromium)
- **Next: search Player Server app `/home/pi/n-compasstv/player-server/` and `/opt/electron-player/` for decryption key**
- Common passwords `raspberry`, `nctv360` failed
- `/etc/crypttab` empty — no auto-unlock configured

### Vault Decryption — SUCCESS (2026-03-18)
- **Passphrase:** `ffb6d42807368154\n` (with trailing newline!)
- **Unlock command:** `echo "ffb6d42807368154" | sudo cryptsetup open /home/pi/vault.img nctv_data -`
- **Key detail:** Use `echo` (with newline), NOT `echo -n --key-file -`
- **Discovery:** From `.bash_history` and `hardware_lock.py` hardcoded serial
- **Vault contents:** player-server/, db_backup_dirty/, logs/, backup/, ecosystem.config.js
- **Vulnerabilities:** V-012 (CRITICAL), V-013 (HIGH), V-014 (MEDIUM)

## PlayerV2 / `setup.enc` Follow-up (2026-04-08)

- Stored encrypted inbound artifact at `engagements/playerv2-artifacts/inbound/setup.enc` and verified OpenSSL salted format before deeper analysis.
- Safe file-level quick scan confirmed the container format, but no inner payload claims were made without decryption.
- Full engagement rounds were completed for `setup.enc`, including an evidence-backed exploit-adjacent validation attempt using the previously confirmed Pi-serial-derived passphrase `ffb6d42807368154` against targeted OpenSSL combinations in an isolated analysis directory.
- Result: **no successful decryption** with that adjacent-key hypothesis. This is a verified blocked path, not a successful crack.
- Strongest next step remains obtaining the true passphrase/key material or the original workflow/script that created `setup.enc`.
