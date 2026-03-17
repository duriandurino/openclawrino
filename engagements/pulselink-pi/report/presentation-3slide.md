# PulseLink Pi — 3-Slide Presentation (Maximum Impact)

**Purpose:** Tightest possible format — 3 slides, maximum punch.
**Time:** 5-7 minutes spoken
**Audience:** Decision-makers, technical leadership

---

### SLIDE 1: The Problem — n-compass TV's Fleet at Risk

**What's on the slide:**

- **Title:** "A $50 Device That Controls a Digital Ad Network"
- **Diagram:** NTV → Dealers → Hosts → Players (business model flow)
- **Key stat box:** "1 Player compromised → ad injection across multiple Host locations"
- **One bullet:** "MQTT broker (pulse.n-compass.online) = fleet-wide control plane"
- **One bullet:** "Every device phones home every 30 seconds — on the same network"
- **Visual:** Network topology showing Pi connected to MQTT broker with traffic arrows

**Speaker notes:**
> "PulseLink is a digital signage player for n-compass TV — a B2B2C ad network. NTV creates the devices, Dealers distribute them to Hosts — businesses that display ads. The critical detail: each Player cross-promotes ads from multiple Hosts. The MQTT broker at pulse.n-compass.online is the fleet-wide control plane. One compromised Player doesn't just affect one screen — it's a pivot point into the entire network.
>
> And here's the thing: every one of these devices is on a network, phoning home every 30 seconds. You don't need to walk into a business. You just need to be on the same Wi-Fi."

---

### SLIDE 2: The Attack — We Listened, Then We Became the Device

**What's on the slide:**

- **Title:** "The Device Phones Home Every 30 Seconds. We Listened."
- **Left column — What we saw on the network:**
  - `nmap -sT -p- 192.168.0.125` → Only 2 ports: SSH (22) + RPCBind (111)
  - PulseLink is a CLIENT — connects OUT to pulse.n-compass.online:8883
  - No services exposed — but MQTT TRAFFIC is observable on the wire
  - `tcpdump -i wlan0 -n port 8883` → Connection patterns, heartbeat every 30s
  - Even with TLS, connection flow reveals device identity
- **Center column — Credential discovery:**
  - Limited filesystem access gained (app-level, NOT root)
  - `/opt/pulselink/.env` → MQTT broker credentials in plaintext
  - `/opt/pulselink/client_certs/client_pi_generic.key` → TLS private key (**644 — world-readable**)
  - Device serial `882985e065594198` + MQTT client ID `dadf6f9ef35e55ab`
- **Right column — The payoff:**
  - `mosquitto_sub` → subscribe to all device topics, see commands in flight
  - `mosquitto_pub` → publish malicious manifest as the device
  - "Stolen credentials meant we became the device"
  - **Content injection → fleet-wide ad takeover**
- **Bottom banner:** "Traffic capture → credential theft → broker takeover"

**Speaker notes:**
> "Here's what happened. We ran a full port scan — only two ports open: SSH and RPCBind. PulseLink doesn't expose any services — it connects OUT to the MQTT broker. The network attack surface looked like a dead end.
>
> But even with TLS, the connection pattern tells us everything. We captured traffic with tcpdump and saw MQTT traffic flowing to pulse.n-compass.online on port 8883 every 30 seconds. The heartbeat is visible. The connection patterns reveal device identity. You can't read the payload through TLS — but you don't need to. You need the credentials.
>
> We gained limited filesystem access — app-level, not root — and found exactly what we needed. The .env file in plaintext with broker credentials. A TLS private key with world-readable permissions — readable by any user on the system. The device serial. The MQTT client ID.
>
> With those credentials, we used mosquitto_sub to subscribe to device topics and watched commands flow in real time. Then mosquitto_pub — we published a malicious manifest, impersonating the device. The broker has no way to know we're not the real Pi. We could push content to any screen connected to this broker."

---

### SLIDE 3: Remediation + Why This Matters

**What's on the slide:**

- **Title:** "3 Hours to Fix. 80 Minutes to Find."
- **Remediation table (left side):**
  - Remove `NOPASSWD` from sudoers — 5 min
  - `chmod 600` on private key — 1 min
  - Move .env to secrets management — 30 min
  - Run PulseLink as non-root user — 30 min
  - Unique per-device TLS certificates — 4 hours
  - Add SHA-256 content integrity validation — 1 hour
  - Update Electron runtime — 1 hour
- **Stats box (right side):**
  - ⏱️ ~80 min total engagement (vs 3-5 days traditional)
  - 🎯 17 findings (5 Critical, 7 High)
  - 📄 25+ files generated
  - 🤖 6 specialized agents, parallel execution
- **Bottom:** "The problem isn't that these are hard to fix. The problem is nobody checked."
- **Backup vectors callout (smaller):** "If physical access was available — UART, USB, SSH — it only gets worse."

**Speaker notes:**
> "The fixes are simple. Every critical remediation takes under 3 hours total. Remove NOPASSWD from sudoers, fix file permissions, move credentials to secrets management, run the service as a non-root user. The hard part isn't fixing it — it's knowing it's broken.
>
> And if physical access was available? It only gets worse. UART via GPIO provides a root shell without authentication. SSH brute-force if re-enabled. The sudo NOPASSWD configuration means that IF an attacker gains shell access — via any method — they get instant root. It's a fallback amplifier, not the primary entry point. But it makes every other attack path worse.
>
> This engagement took about 80 minutes using OpenClaw's Specter framework — six specialized agents running in parallel. We found 17 vulnerabilities, generated 25+ documents, and researched 30+ CVEs. A traditional pentest would take 3-5 days for this scope.
>
> A $50 device, on a network, phoning home every 30 seconds — with credentials that could compromise an entire digital signage fleet. This is why pentesting matters. This is why the methodology matters."
