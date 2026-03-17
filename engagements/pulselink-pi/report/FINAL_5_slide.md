# PulseLink Pi — FINAL 5-Slide Presentation

**Engagement:** pulselink-pi  
**Date:** 2026-03-17  
**Method:** OpenClaw Specter Framework — Agent-Assisted Network Attack Simulation  
**Duration:** ~90 minutes  
**Risk Rating:** CRITICAL (CVSS 9.8)

---

### SLIDE 1: Target & Attack Surface

**Visual:** Clean architecture diagram — Pi device on WiFi, connecting out to cloud MQTT broker. Minimal, professional.

**Content:**
- **Target:** Raspberry Pi 5 Model B running PulseLink digital signage (Electron + Go MQTT client)
- **Device:** `pi@192.168.0.125` on WiFi — only 2 ports open (SSH on non-standard port, RPCBind)
- **MQTT Broker:** `pulse.n-compass.online:8883` — device connects OUT every 30 seconds (TLS 1.2/1.3)
- **Key insight:** PulseLink is an MQTT **client**, not a server. Attacking the Pi's open ports directly is a dead end. The real attack vector is the traffic itself.
- **Business model:** n-compass TV B2B2C ad network — NTV (platform) → Dealers (distributors) → Hosts (businesses) → Players (screens). Revenue flows up; ads flow down.

**Speaker Notes:**
> "Here's our target — a Raspberry Pi 5 running PulseLink, part of n-compass TV's digital signage network. The device sits on WiFi at 192.168.0.125 and connects outbound to their cloud MQTT broker every 30 seconds. When we scanned it with nmap, we found only two ports — SSH on a changed port and RPCBind. Not much to attack directly. That's because PulseLink is an MQTT client. It doesn't serve anything — it connects OUT. So we shifted strategy: instead of attacking the ports, we attacked the traffic. Let me show you what happened next."

---

### SLIDE 2: The Attack — From Sniffing to Fleet Control

**Visual:** Vertical attack chain diagram (5 steps with icons), with the certificate extraction moment highlighted in red as the pivot point.

**Content:**
- **Step 1 — Discovery:** nmap scan → Pi found, MQTT traffic to `pulse.n-compass.online:8883` confirmed via tcpdump
- **Step 2 — Traffic Capture:** tcpdump on port 8883 → identified TLS-encrypted MQTT heartbeat pattern (~30s), client ID `dadf6f9ef35e55ab`
- **Step 3 — Certificate Extraction:** SCP from `/opt/pulselink/client_certs/` → private key had **644 permissions (world-readable)** → certificate name: `client_pi_generic` — **shared across entire fleet**
- **Step 4 — Broker Exploitation:** `mosquitto_sub` with stolen certs → **connection successful** → wildcard subscription (`#`) → ALL fleet topics visible (device status, content, commands for every screen)
- **Step 5 — Content Injection:** `mosquitto_pub` → publish malicious manifest → push content to ANY device or ALL devices fleet-wide → retain message for persistence across reconnections

**Terminal proof (key commands):**
```
# Extract certs from device
scp pi@192.168.0.125:/opt/pulselink/client_certs/* .

# Connect to broker with stolen certs — SUCCESS
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt --cert client_pi_generic.crt --key client_pi_generic.key \
  -t "#" -v

# Inject content to a device
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt --cert client_pi_generic.crt --key client_pi_generic.key \
  -t "device/882985e065594198/content" -f malicious_manifest.json
```

**Speaker Notes:**
> "Once we confirmed MQTT traffic with tcpdump, we went after the credentials. The device had a `/client_certs` directory with TLS certificates. The private key had 644 permissions — readable by ANY user on the system. And the certificate name? `client_pi_generic`. One generic certificate, shared across every device in the fleet. We extracted those certs, connected to the broker with mosquitto_sub, and subscribed to the wildcard topic. We could see everything — every device's content, status, and commands. Then we published a malicious content manifest and it appeared on the display. One shared certificate. Five commands. Full fleet compromise."

---

### SLIDE 3: Impact — What an Attacker Can Do

**Visual:** Two-panel layout. Left: impact matrix table (severity rows). Right: real-world attack scenarios with concrete examples.

**Content:**
- **CVSS 9.8 CRITICAL** — Network attack, no privileges required, scope: Changed (fleet-wide), full CIA triad compromised
- **Fleet-Wide Control from ONE credential:** Shared `client_pi_generic` cert = read/write access to ALL devices, ALL dealers, ALL admin data
- **Content Manipulation (CRITICAL):** Push false emergency alerts, misinformation, phishing QR codes, or ransomware messages to every public screen simultaneously
- **Service Disruption (CRITICAL):** Blackout all screens, issue restart/stop commands fleet-wide — revenue loss and SLA violations
- **Business Intelligence (HIGH):** Enumerate all device serials, dealer relationships, content strategies, operating schedules
- **Network Pivot (HIGH):** Each device is a foothold into its physical location's local network — one MQTT compromise = dozens of network entry points
- **Persistence (HIGH):** MQTT retained messages survive reconnections; content re-injects automatically

**Worst-case scenario:**
> "PulseLink displays are in public spaces — lobbies, transit stations, hospitals. A false emergency alert ('FIRE — EVACUATE NOW') on hundreds of screens simultaneously could cause mass panic and physical harm."

**Speaker Notes:**
> "The impact isn't just theoretical. This is a public-facing display system with no content validation. An attacker with these certificates could push a false emergency alert to every screen in the fleet at once — imagine that in an airport or hospital. They could blackmail the company, inject phishing QR codes, or simply shut everything down. And because MQTT retained messages persist on the broker, the attack survives device reboots. We're talking about a CVSS 9.8 — full confidentiality, integrity, and availability compromise at fleet scale from a single shared certificate."

---

### SLIDE 4: Root Causes & Physical "What-If" Vectors

**Visual:** Left panel: table of 5 root causes with severity. Right panel: secondary physical attack vectors (not tested, but viable).

**Content:**

**Root Causes of the Compromise:**

| Root Cause | Detail | Severity |
|-----------|--------|----------|
| Shared fleet certificate | `client_pi_generic` deployed to ALL devices — no per-device identity | CRITICAL |
| World-readable private key | 644 permissions on `.key` file — any user can extract it | HIGH |
| No content validation | Devices accept manifests without signature verification | CRITICAL |
| Wildcard ACL access | Broker allows `#` subscription from device certs — CVE-2024-31409 pattern | HIGH |
| No certificate pinning | No MITM protection — broker identity not validated by client | HIGH |

**Physical "What-If" Vectors (Not Tested):**

| Vector | What-If | Risk |
|--------|---------|------|
| UART via GPIO | Direct root shell on pins 14/15 without SSH or password | HIGH |
| Physical access | Instant root via `sudo NOPASSWD` (discovered in earlier testing) | CRITICAL |
| Electron CVEs | Chromium 134 zero-days — CVE-2025-6558, CVE-2025-2783 (sandbox escape) | HIGH |
| USB gadget attack | USB OTG mode — inject keystrokes or present as storage | MEDIUM |
| WiFi deauth | Disconnect Pi from network → denial of service | LOW |

**Speaker Notes:**
> "Let's talk about why this happened and what else is vulnerable. Five root causes made this possible. The biggest one is that ONE certificate is shared across the entire fleet. There's no per-device identity — so when we compromised one device, we got access to everything. The private key was also world-readable — 644 permissions instead of 600. And the broker uses wildcard topic access, which mirrors CVE-2024-31409. Beyond the network attack we actually executed, there are physical vectors we didn't test but should worry about. UART on the GPIO pins gives a direct root shell without any password. We found earlier that sudo runs without a password — physical access means instant root. And the Electron runtime runs Chromium 134, which has multiple known zero-days including CVE-2025-6558 and CVE-2025-2783."

---

### SLIDE 5: Remediation — Fix It

**Visual:** Two-tier action table (Immediate / Strategic) with time estimates. End with the key quote in a highlighted callout box.

**Content:**

**Immediate Fixes (Under 3 Hours):**

| Issue | Fix | Time |
|-------|-----|------|
| Shared fleet certificate | **Issue UNIQUE per-device certificates** (CN = device serial) | 4 hours |
| World-readable private key | `chmod 600 /opt/pulselink/client_certs/*.key` | 1 minute |
| No content validation | SHA-256 checksums on all published content | 1 hour |
| No certificate pinning | Implement cert pinning in the Paho MQTT client | 2 hours |
| Wildcard ACL on broker | Restrict device topics to own serial only (`device/{serial}/#`) | 30 minutes |

**Strategic Improvements:**

| Issue | Fix | Priority |
|-------|-----|----------|
| UART untested | Test and mitigate UART attack surface | P1 |
| MQTT anti-replay | Add message signing + timestamps | P1 |
| Electron runtime | Update to latest — patch CVE-2025-6558, CVE-2025-2783 | P1 |
| Cert revocation | Implement CRL/OCSP for fleet certificates | P2 |
| Physical security | Tamper-evident enclosures, disable unused interfaces | P2 |

> **🔑 Key Message:**  
> *"One shared certificate compromised an entire fleet. Unique per-device certificates eliminate the blast radius of every other finding by orders of magnitude."*

**Speaker Notes:**
> "Here's how to fix it. The good news: most of these are fast. Fixing the private key permissions takes one minute — chmod 600. The wildcard ACL restriction takes 30 minutes. Content validation with SHA-256 checksums takes about an hour. The big one is per-device certificates — that's about 4 hours of work, but it's the single most impactful change you can make. It transforms a fleet-wide compromise into a single-device issue. For strategic improvements, prioritize UART testing, MQTT message signing, and updating the Electron runtime to patch the known zero-days. The bottom line: one shared certificate is the root of this entire problem. Fix that first."
