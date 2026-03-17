# PulseLink Pi — Key Takeaways & Remediation Summary

**Engagement:** pulselink-pi  
**Date:** 2026-03-17  
**Risk Rating:** CRITICAL (CVSS 9.8)  
**Classification:** Executive Summary — One-Page Distribution

---

## Top 5 Key Takeaways

### 1. One Shared Certificate = Full Fleet Compromise
The `client_pi_generic` certificate is deployed identically to every PulseLink device. There is no per-device identity. Compromising any single device — through physical access, software vulnerability, or network intrusion — grants read/write access to every device, every dealer's data, and the admin layer. The blast radius of a single device compromise is the entire fleet.

### 2. MQTT Traffic Was the Real Attack Surface
PulseLink is an MQTT client, not a server. It has only 2 open ports (SSH on non-standard port, RPCBind) and connects outbound. Attacking the device directly is a dead end. The real vulnerability is the traffic: certificate-based authentication with shared, extractable credentials. The winning strategy was passive sniffing → certificate extraction → broker impersonation — not port exploitation.

### 3. A 5-Step Attack Chain Achieved Fleet-Wide Control in Under 90 Minutes
**Discovery** (nmap) → **Traffic Capture** (tcpdump) → **Certificate Extraction** (SCP, key at 644 permissions) → **Broker Exploitation** (mosquitto_sub, wildcard `#` subscription) → **Content Injection** (mosquitto_pub, malicious manifest). Five commands. No privilege escalation required. No zero-days needed. Trivially reproducible.

### 4. Physical Attack Vectors Multiply the Risk
Beyond the network attack executed during this assessment, untested physical vectors compound the threat:
- **UART via GPIO pins 14/15** — direct root shell without authentication
- **`sudo NOPASSWD`** — physical access = instant root
- **Chromium 134 zero-days** (CVE-2025-6558, CVE-2025-2783) — sandbox escape via the Electron runtime
- **USB gadget attack** — keystroke injection via USB OTG
- Each device in a public location is a physically accessible target.

### 5. This Is a Public Safety Issue, Not Just a Data Issue
PulseLink displays operate in public spaces: hospitals, airports, transit stations, retail lobbies. An attacker with fleet certificates could push false emergency alerts ("FIRE — EVACUATE NOW") to every screen simultaneously. This creates mass panic and physical harm risk. The liability extends beyond data breach to criminal negligence.

---

## Remediation Summary

### P0 — IMMEDIATE (Do Today)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 1 | **Rotate `client_pi_generic` certificate** — revoke current cert, issue new fleet credential | Medium | Eliminates current attacker access |
| 2 | **Flush retained MQTT messages** — remove any attacker-injected persistent content | Low | Removes persistence vector |
| 3 | **Audit `pulselink.service`** — check for unauthorized modifications, cron entries, SSH implants | Low | Detects active compromise |

### P1 — URGENT (This Week)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 4 | Fix private key permissions: `chmod 600 /opt/pulselink/client_certs/*.key` | Trivial | Prevents key extraction by local users |
| 5 | Implement **per-device X.509 certificates** (CN = device serial) | High | Eliminates shared credential risk — single most impactful fix |
| 6 | Enforce per-device topic ACLs on MQTT broker (`device/{serial}/#` only) | Medium | Prevents cross-device access |

### P2 — HIGH (This Month)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 7 | Add content manifest signing (HMAC or digital signatures) | High | Prevents unauthorized content injection |
| 8 | Restrict wildcard subscriptions on broker | Medium | Prevents fleet enumeration |
| 9 | Implement certificate pinning in MQTT client | Medium | Prevents MITM attacks |
| 10 | Update Electron runtime — patch CVE-2025-6558, CVE-2025-2783 | Medium | Closes known sandbox escape vulnerabilities |

### P3 — MEDIUM (Quarterly)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 11 | Deploy MQTT anomaly detection (unusual publish patterns, volume spikes) | Medium | Detects future attacks in real-time |
| 12 | Implement certificate rotation mechanism (auto-renewal) | High | Reduces certificate lifespan and exposure window |
| 13 | Audit and harden UART access (disable or require authentication) | Low | Closes physical attack vector |

### P4 — STRATEGIC (Roadmap)

| # | Action | Effort | Impact |
|---|--------|--------|--------|
| 14 | Hardware-backed key storage (TPM/Secure Element) | High | Prevents key extraction even with full device access |
| 15 | Network segmentation for IoT devices | High | Limits blast radius of any future compromise |
| 16 | Tamper-evident enclosures for deployed devices | Medium | Detects and deters physical attacks |

---

## "What-If" Vectors — Further Testing Recommended

These attack vectors were identified but **not executed** during this engagement. Each warrants dedicated testing:

| Vector | Description | Recommended Test | Risk |
|--------|-------------|------------------|------|
| **UART Root Shell** | Connect to GPIO pins 14/15 (TX/RX) with serial adapter | Verify unauthenticated root shell access, test for login bypass | HIGH |
| **Electron/Chromium Exploits** | CVE-2025-6558 (Chromium zero-day), CVE-2025-2783 (sandbox escape) | Craft malicious content manifest with exploit payload; test if Electron renders it unsandboxed | HIGH |
| **USB Gadget Attack** | Pi 5 supports USB OTG mode | Inject keystrokes via USB (HID gadget) or present as mass storage to extract data | MEDIUM |
| **WiFi Deauthentication** | Disconnect Pi from WiFi using aireplay-ng | Test service recovery behavior, retained message re-injection on reconnect | LOW |
| **Firmware供应链 Attack** | Compromise OTA update mechanism | Intercept/modify firmware updates if auto-update is enabled | HIGH |
| **Dealer-Side Pivot** | Use device network access to reach dealer infrastructure | Each device sits on a host's local network — test lateral movement from Pi into host network | HIGH |

---

## Bottom Line

> **The certificates are the keys to the kingdom, and the kingdom has no walls.**

The PulseLink platform's MQTT architecture is fundamentally sound, but the authentication implementation has critical gaps. One shared, world-readable certificate grants fleet-wide access with no content validation and no per-device identity.

**The single most impactful remediation is implementing per-device certificates.** This one change transforms a fleet-wide compromise into a single-device issue, reducing blast radius by orders of magnitude.

Without remediation, an attacker has:
- ✅ Read access to all fleet data (content, status, telemetry, business relationships)
- ✅ Write access to all fleet content (defacement, misinformation, phishing, false alerts)
- ✅ Write access to all fleet commands (service disruption, device control)
- ✅ Persistence via MQTT retained messages
- ✅ Pivot points into every device's local network
- ✅ Low detection probability (no anomaly detection or content validation)

---

*Generated by specter-report | Engagement: pulselink-pi | Date: 2026-03-17*  
*For authorized distribution only*
