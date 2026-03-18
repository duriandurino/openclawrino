# N-Compass TV Digital Signage — Penetration Test Presentation

**Target:** PulseLink Player (Raspberry Pi 5B) + N-Compass TV Infrastructure
**Engagements:** Hardware Pentest (2026-03-17) + Network Pentest (2026-03-18)
**Presented by:** Hatless White — OpenClaw Pentest Agent
**Classification:** CONFIDENTIAL

---

### SLIDE 1: Title Slide

**Visual:** Company logo + target device image + engagement dates

**Content:**
- **N-Compass TV Digital Signage Network**
- Penetration Test Results — Combined Report
- Hardware Assessment (Mar 17) + Network Assessment (Mar 18)
- Target: PulseLink Raspberry Pi Player Fleet
- Presenter: Hatless White (OpenClaw Agent)
- Classification: Confidential

**Speaker Notes:**
"Today I'm presenting the combined findings from a two-day penetration test of N-Compass TV's digital signage infrastructure. Day one focused on hardware-level physical access testing against a Raspberry Pi 5B Player running PulseLink. Day two expanded to network-based testing across the local subnet, covering multiple Player devices and backend infrastructure. Together, these engagements uncovered 23 vulnerabilities — 6 critical and 7 high severity — spanning physical access controls, application security, API design, and network architecture."

**Transition:** Let's start with why this matters.

---

### SLIDE 2: Problem Statement

**Visual:** Risk matrix showing business impact categories with current risk levels (color-coded)

**Content:**
- **What is n-compass TV?** — B2B2C digital signage ad network
  - NTV provides Players → Dealers distribute → Hosts display → Revenue flows
- **Why test?** — Compromised Player = ad injection across fleet
- **Attack model:** Device compromise → MQTT control plane → fleet-wide impact
- **Key risk:** MQTT broker (`pulse.n-compass.online`) is the single control plane for ALL Players

**Architecture Diagram:**
```
NTV (Platform) → Players (RPi devices) → Hosts (display locations)
      ↓                                       ↑
 MQTT Broker ← Controls ALL Players ←────────┘      ↑
 (Single Point of Control)                           │
      ↓                                              │
 Dealers (distribute & recruit) ─────────────────────┘
```

**Speaker Notes:**
"N-Compass TV operates a B2B2C digital signage ad network. The company creates Player devices — Raspberry Pi units running PulseLink software — which Dealers distribute to Hosts, which are businesses that display ads. The critical security concern is the MQTT broker at pulse.n-compass.online, which serves as the single control plane for the entire Player fleet. One compromised Player could potentially lead to device impersonation, credential theft, and ad injection across multiple Host locations. The cross-promotion model means each Player displays ads from other Hosts in the network — compromising one device has cascading effects."

**Transition:** Here's what we tested and how.

---

### SLIDE 3: Target Overview & Methodology

**Visual:** Split screen — left side: target inventory table; right side: phased methodology diagram

**Content:**
- **Targets Tested:**
  - Raspberry Pi 5B Player (192.168.0.125) — Physical access
  - Raspberry Pi 4 Player (192.168.0.161) — Network access (collateral)
  - Windows Backend Server (192.168.0.103) — Network (collateral)
  - Cloud Infrastructure — CDN, MQTT broker, dashboards

- **Methodology (PTES-aligned):**
  - Phase 1: Reconnaissance & Discovery
  - Phase 2: Service & Enumeration
  - Phase 3: Vulnerability Analysis
  - Phase 4: Exploitation (proof of concept)
  - Phase 5: Reporting

- **Tools:** Nmap, cURL, Hydra, Netdiscover, FreeRDP, tshark, ollama (xploiter models)

**Speaker Notes:**
"We tested four primary targets. The main engagement was the Pi 5B Player with full physical access — we had a keyboard and mouse directly connected, bypassing SSH entirely. We also tested a collateral Pi 4 Player and a Windows backend server from the network, plus cloud infrastructure including a CloudFront CDN and the MQTT broker. We followed PTES methodology across all phases. A key differentiator: this assessment was powered by OpenClaw's agent-orchestrated workflow — specialized AI agents handled each phase in parallel while a human operator directed strategy and validated findings."

**Transition:** Let's start with the hardware assessment findings from Day 1.

---

### SLIDE 4: Hardware Pentest Findings (Day 1 — Physical Access)

**Visual:** Severity badges + attack chain flow diagram + key finding callouts

**Content:**

| # | Finding | Severity | CVSS |
|---|---------|----------|------|
| V-001 | sudo NOPASSWD → instant root | 🔴 CRITICAL | 10.0 |
| V-002 | sudo 1.9.16p2 — CVE-2025-32463 | 🔴 CRITICAL | 9.8 |
| V-003 | MQTT credentials in plaintext (.env) | 🔴 CRITICAL | 9.0 |
| V-004 | TLS private key world-readable (644) | 🔴 CRITICAL | 8.8 |
| V-015 | Fleet-wide compromise via MQTT broker | 🔴 CRITICAL | 9.5 |
| V-011 | Playlist content injectable via filesystem | 🟠 HIGH | 7.5 |
| V-017 | Shared TLS certs across fleet | 🟠 HIGH | 8.0 |

**Attack Chain (2 commands, 0 exploits):**
```
Physical access → sudo su (no password) → uid=0(root) →
Extract MQTT creds → Extract TLS keys → Device impersonation →
Fleet-wide ad injection via MQTT broker
```

**Key Takeaway:** Root access in **2 commands**. No exploits needed.

**Speaker Notes:**
"Day one was the physical access assessment. The result was devastating — we achieved root access in exactly two commands. `sudo su` with no password prompt, giving us uid=0 root. From there, we extracted MQTT broker credentials stored in plaintext in /opt/pulselink/.env, grabbed the TLS private key with world-readable permissions, and gained full device control. The fleet-wide risk is the critical finding: the MQTT broker controls every Player in the n-compass network. A compromised device can impersonate any other device, inject malicious ad content, and propagate across Host locations. We also discovered shared TLS certificates across the fleet — the filename 'client_pi_generic' strongly suggests the same cert is deployed to multiple devices."

**Transition:** Day 2 shifted to network-only access — no physical touch. Here's what changed.

---

### SLIDE 5: Network Pentest Findings (Day 2 — Remote Only)

**Visual:** Network topology diagram + findings table with severity badges

**Content:**

| # | Finding | Target | Severity | CVSS |
|---|---------|--------|----------|------|
| V-001 | Unauthenticated Player API (:3215) | 192.168.0.161 | 🔴 CRITICAL | 9.8 |
| V-002 | Public CloudFront CDN (content theft) | AWS CloudFront | 🟠 HIGH | 7.5 |
| V-003 | Backend server — 17+ open services | 192.168.0.103 | 🟠 HIGH | 8.1 |
| V-004 | OAuth2 flow weakness (no PKCE) | Backend API | 🟠 HIGH | 7.2 |
| V-005 | CORS misconfiguration (`*` + credentials) | Kestrel :82 | 🟡 MEDIUM | 5.3 |
| V-006 | VNC service exposed | 192.168.0.161 | 🟡 MEDIUM | 5.9 |

**Player v2 (Hardened Device — 192.168.0.130):**
- ✅ 65,534 ports scanned — only 1 open (rpcbind)
- ✅ iptables DROP policy on all non-essential ports
- ✅ SSH rejects connections (not just password rejection)
- ✅ No exploitable network attack surface
- **Conclusion:** Physical access is the only viable vector for properly hardened Players

**Key Takeaway:** The unauthenticated API on port 3215 is exploitable in **< 5 minutes** by anyone on the network.

**Speaker Notes:**
"Day 2 removed physical access entirely. We scanned 65,534 ports across multiple devices. The critical finding was an unauthenticated Express API running on port 3215 of the Pi 4 Player — it exposes device fingerprints, ad playlists with CDN URLs, and content status without any authentication. We extracted a full 7-item playlist with CloudFront URLs in under 5 minutes. The backend Windows server had 17+ open services including MySQL databases, RDP, WinRM, and AnyDesk. However, a positive finding: the newer Pi 5B Player (192.168.0.130) was properly hardened — only rpcbind exposed, everything else dropped. This proves the security architecture works when implemented correctly."

**Transition:** Here's what needs to happen next.

---

### SLIDE 6: Remediation Roadmap

**Visual:** Three-phase timeline with priority flags (P0/P1/P2) + effort indicators

**Content:**

**Phase 1 — Emergency (0–48 Hours) 🔴**
- Remove `NOPASSWD: ALL` from all Player sudoers
- Bind Player API to localhost (127.0.0.1) — OTA update fleet-wide
- Restrict private key permissions (`chmod 600` on all TLS keys)
- Move MQTT credentials to secrets management (systemd LoadCredential)
- Fix CORS: remove `Access-Control-Allow-Origin: *` + credentials combo

**Phase 2 — Urgent (1–2 Weeks) 🟠**
- Rotate shared TLS certificates → unique per-device certs
- Implement CloudFront Signed URLs for ad content
- Run PulseLink as non-root service user
- Update Electron/Chromium runtime (CVE-2025-6558, CVE-2026-2441)
- Implement PKCE in OAuth2 flow + rate limiting on login endpoint
- Network segmentation: VLAN for Players, separate from backend servers

**Phase 3 — Strategic (1–3 Months) 🟢**
- Device attestation for MQTT (unique per-device credentials + broker ACLs)
- Bastion host with MFA for all admin access (RDP, WinRM, SSH)
- Signed firmware update pipeline + secure boot
- Quarterly penetration testing program
- Deploy EDR on backend servers

**Bottom Line:** P0 items can be fixed in 48 hours via OTA update. The fleet-wide risk drops dramatically once the API is bound to localhost and NOPASSWD is removed.

**Speaker Notes:**
"The remediation roadmap has three phases. Phase 1 is emergency — these are 48-hour fixes that can be deployed via OTA update. Binding the API to localhost alone eliminates the most exploitable network vulnerability. Removing NOPASSWD from sudoers eliminates the instant-root path. Phase 2 addresses certificate rotation, content signing, and network segmentation over 1-2 weeks. Phase 3 is strategic: device attestation, secure boot, and a quarterly pentest program. The key message: P0 items are cheap and fast to fix, but they require immediate action. Every day these remain unpatched, the fleet is exposed."

**Transition:** So why did we do it this way?

---

### SLIDE 7: Why OpenClaw + Q&A

**Visual:** Comparison table (Traditional vs Agent-Assisted) + contact/info box

**Content:**

**How OpenClaw Changed the Game:**
- **6 specialized AI agents** (recon, enum, vuln, exploit, post, report) operated in parallel
- **50-70% time reduction** — 2-day engagement that would take 4-5 days traditionally
- **2,900+ lines of structured documentation** generated during the engagement (not after)
- **Live CVE research** — real-time lookups against NVD, MITRE, CISA KEV
- **Scalable** — same methodology works for web apps, networks, cloud, mobile

**This Engagement by the Numbers:**
| Metric | Value |
|--------|-------|
| Total vulnerabilities found | 23 |
| Critical severity | 6 |
| High severity | 7 |
| Attack chains demonstrated | 3 |
| Time to root (hardware) | 2 commands |
| Time to fleet data (network) | < 5 minutes |
| Documentation generated | 2,900+ lines |
| Engagement duration | 2 days |

**Agent Team:**
| Agent | Role |
|-------|------|
| specter-recon | OSINT, attack surface mapping |
| specter-enum | Port scanning, service fingerprinting |
| specter-vuln | CVE verification, risk ranking |
| specter-exploit | Exploitation, privilege escalation |
| specter-post | Persistence, lateral movement |
| specter-report | Report generation |

**Questions?**

**Speaker Notes:**
"Before I open for questions, I want to highlight the methodology. This assessment was conducted using OpenClaw's agent-orchestrated framework. Six specialized AI agents — each focused on a specific phase of the pentest — operated in parallel while a human operator directed strategy. The result was a 2-day engagement that would traditionally take 4-5 days, with 2,900 lines of structured documentation generated in real-time rather than assembled days after the fact. The agents found 23 vulnerabilities across hardware and network vectors, demonstrated 3 complete attack chains, and delivered everything in a consistent, reproducible format. This approach is target-agnostic — the same framework works for web applications, network infrastructure, cloud environments, and mobile apps. Thank you. I'm happy to take questions."

---

*Presentation generated by specter-report (OpenClaw Pentest Agent)*
*Hardware Engagement: pulselink-pi (2026-03-17)*
*Network Engagement: player-network + player-v2 (2026-03-18)*
*Classification: CONFIDENTIAL*
