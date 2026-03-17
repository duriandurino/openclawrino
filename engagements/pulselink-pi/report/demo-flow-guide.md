# Live Demo Flow Guide — PulseLink Pi Pentest

**Purpose:** Step-by-step walkthrough for the presentation demo  
**Date:** 2026-03-17  
**Presenter:** The Darkhorse  
**Duration:** ~25-30 minutes total  

---

## Pre-Demo Setup (Before Presentation)

### Hardware Checklist
- [ ] Raspberry Pi 5 connected to display (HDMI)
- [ ] Keyboard and mouse connected to Pi
- [ ] Pi powered on and logged in as `pi` user
- [ ] Pi connected to WiFi (192.168.0.125)
- [ ] Pi in original VULNERABLE state (see below)

### Required Vulnerable State
The Pi must be set up with these vulnerable configurations for the demo:

| Setting | Required State | How to Set |
|---------|---------------|------------|
| sudo NOPASSWD | Enabled | Add `pi ALL=(ALL) NOPASSWD: ALL` to sudoers |
| Private key | 644 permissions | `sudo chmod 644 /opt/pulselink/client_certs/client_pi_generic.key` |
| pulselink service | `Restart=always` | Ensure no override in `/etc/systemd/system/pulselink.service.d/` |
| SSH | Enabled | `sudo systemctl enable ssh && sudo systemctl start ssh` |
| wlan0 | Up | `sudo ip link set wlan0 up` |
| Playlist | Original content | Restore `/var/lib/electron-player/playlist/playlist-main/` |

### Terminal Preparation
- [ ] Open terminal on Pi (LXTerminal or via Ctrl+Alt+T)
- [ ] Set font size large enough for projector (18pt+)
- [ ] Clear terminal history: `history -c && cat /dev/null > ~/.bash_history`
- [ ] Close all other windows
- [ ] Test HDMI output works

---

## Demo Flow — Problem → Tool → Demo

### Part 1: THE PROBLEM (5 minutes)

#### Step 1.1: Introduce n-compass TV Business Model (2 min)

**What to say:**
> "PulseLink is part of n-compass TV, a B2B2C digital signage ad network. NTV creates Players — these Raspberry Pi devices — and distributes them through Dealers to Hosts, which are business locations. Each Player displays ads for its Host AND cross-promotes ads from other Hosts. The MQTT broker at pulse.n-compass.online is the fleet-wide control plane. One compromised Player could mean ad injection across multiple business locations."

**What to show:** The n-compass TV diagram from the presentation slides.

#### Step 1.2: The Risk (1 min)

**What to say:**
> "Digital signage devices run 24/7 without supervision, connect to cloud services, run full operating systems, and are rarely patched. This makes them high-value targets."

#### Step 1.3: The Tool — OpenClaw Specter Framework (2 min)

**What to say:**
> "Traditional pentesting takes 3-5 days. We used the OpenClaw Specter Framework — six specialized AI agents running in parallel. Each agent handles one phase: recon, enumeration, vulnerability analysis, exploitation, and reporting. What takes days was done in under 2 hours."

**What to show:** The agent workflow diagram. Mention the 2,900+ lines of documentation generated.

---

### Part 2: THE DEMO (15-20 minutes)

#### Demo 1: Recon & Enumeration (2 min)

**What to type:**
```bash
# On the Pi terminal
uname -a
# Expected: Linux raspberry 6.12.47+rpt-rpi-2712 ...

sudo --version
# Expected: Sudo version 1.9.16p2

cat /etc/os-release
# Expected: Debian GNU/Linux 13 (trixie)
```

**What to say:**
> "Physical access to the Pi gives us a terminal. We're running Debian 13 on kernel 6.12.47 with sudo 1.9.16p2. That sudo version is in the vulnerable range for CVE-2025-32463."

**Terminal output reference:** `pi-terminal-output.txt` — sudo --version, os-release

---

#### Demo 2: Instant Root — The Killer Finding (2 min)

**What to type:**
```bash
sudo su
id
```

**Expected output:**
```
uid=0(root) gid=0(root) groups=0(root)
```

**What to say:**
> "Two commands. Zero exploits. No skill required. The pi user has passwordless sudo — we're root in 2 seconds. This is the most devastating finding. Every other finding flows from this root access."

**Terminal output reference:** `pi-terminal-output.txt` — sudo su, id

---

#### Demo 3: Credential Exposure (2 min)

**What to type:**
```bash
cat /opt/pulselink/.env
```

**Expected output:**
```
PULSELINK_MQTT_BROKER_HOST=pulse.n-compass.online
PULSELINK_MQTT_BROKER_PORT=8883
PULSELINK_HEARTBEAT_INTERVAL_SECONDS=30
...
```

```bash
ls -la /opt/pulselink/client_certs/
```

**Expected output:**
```
-rw------- 1 root root 2025 ca.crt
-rw------- 1 root root 2061 client_pi_generic.crt
-rw-r--r-- 1 root root 3268 client_pi_generic.key  ← world-readable!
```

**What to say:**
> "MQTT broker credentials are in plaintext in a .env file. Worse — the TLS private key used for broker authentication is readable by any user. And that key name — 'generic' — suggests it might be shared across multiple devices."

**Terminal output reference:** `pi-terminal-output-2.txt` — .env, client_certs listing

---

#### Demo 4: Content Injection (2 min)

**What to type:**
```bash
cat /var/lib/electron-player/playlist/playlist-main/manifest.json
```

**Expected output:**
```json
{
  "LlYGLooUQamA3PC1pkLs_test.mp4": {"seq": 1, "duration": 34.133, ...},
  "hZ5MKdK0ThqmeeBIAKVA_jujutsu.mp4": {"seq": 2, "duration": 21.184, ...},
  ...
}
```

```bash
ls -la /var/lib/electron-player/playlist/playlist-main/
```

**What to say:**
> "This directory is writable by the pi user. I can replace any video or image file. There's no integrity checking — no checksums, no signatures. An attacker could replace the test video with offensive content, a phishing page, or a malware download QR code."

**Terminal output reference:** `pi-terminal-output-3.txt` and `pi-terminal-output-4.txt` — manifest.json

---

#### Demo 5: Service Control Demonstration (3 min)

**What to type:**
```bash
# Show the service configuration
sudo cat /etc/systemd/system/pulselink.service
```

**Expected output:**
```
[Service]
Type=simple
User=root
WorkingDirectory=/opt/pulselink
ExecStart=/usr/local/bin/pulselink
Restart=always        ← This is the key line
RestartSec=10
```

```bash
# Try to stop the service (IT WON'T WORK)
sudo systemctl stop pulselink
sleep 3
sudo systemctl status pulselink
# Expected: still active — Restart=always overrides the stop
```

**What to say:**
> "The service runs as root with Restart=always. Watch — I try to stop it, and systemd immediately restarts it. To actually kill the player, you have to edit the systemd override to set Restart=no, THEN hit Ctrl+C. That's two steps just to stop the service. This shows how the service configuration provides defense-in-depth — even if you gain root, killing the player requires understanding systemd overrides."

**For the advanced demo (optional):**
```bash
# Create override to disable restart
sudo mkdir -p /etc/systemd/system/pulselink.service.d/
sudo bash -c 'echo -e "[Service]\nRestart=no" > /etc/systemd/system/pulselink.service.d/override.conf'
sudo systemctl daemon-reload

# NOW stop works
sudo systemctl stop pulselink
sudo systemctl status pulselink
# Expected: inactive (dead)
```

```bash
# Restore for demo reset
sudo rm -f /etc/systemd/system/pulselink.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl start pulselink
```

**Terminal output reference:** `pi-terminal-output-6.txt` — service file, `pi-terminal-output-5.txt` — status

---

#### Demo 6: SSH Lockout (2 min)

**What to type:**
```bash
# Show SSH is currently enabled
sudo systemctl status ssh
# Expected: Active (running)

# Demonstrate disabling SSH
sudo systemctl stop ssh
sudo systemctl status ssh
# Expected: Inactive (dead)

# Show that remote access is now impossible
# (If you have a second terminal trying to SSH in, it will fail)
```

**What to say:**
> "With root access, I just disabled SSH. Anyone trying to manage this device remotely is locked out now. Only someone with physical access — a keyboard and mouse — can get back in. This is a double-edged sword: it's a security feature, but an attacker with brief physical access could disable SSH and lock legitimate admins out of their own device."

```bash
# Restore SSH
sudo systemctl start ssh
sudo systemctl status ssh
```

**Terminal output reference:** Terminal output from SSH lockout demonstration

---

### Part 3: IMPACT & REMEDIATION (5 minutes)

#### Step 3.1: Fleet-Wide Impact (2 min)

**What to say:**
> "This isn't just one Pi. Remember the n-compass TV model: NTV, Dealers, Hosts, Players. With the stolen TLS certificates, I can impersonate this device to the MQTT broker. That broker controls ALL Players in the fleet. One compromised Player becomes fleet-wide ad injection. The MQTT broker is the single point of control for the entire digital signage network."

#### Step 3.2: The Fixes (2 min)

**What to say:**
> "The good news: the fixes are simple and fast."

**Show the remediation table:**

| Issue | Fix | Time |
|-------|-----|------|
| sudo NOPASSWD | Remove from sudoers | 5 min |
| Plaintext .env | Use secrets management | 30 min |
| World-readable key | chmod 600 | 1 min |
| Service as root | Create dedicated user | 30 min |
| Content injection | Add checksums | 1 hour |
| Old Electron | Update runtime | 1 hour |

> "All critical fixes in under 3 hours. This isn't a massive refactor — it's basic security hygiene."

#### Step 3.3: The Methodology (1 min)

**What to say:**
> "The Specter Framework isn't limited to Raspberry Pi. The same agent-based workflow applies to web apps, network infrastructure, cloud environments, and mobile apps. Different targets, same process. We generated 17 findings and 2,900+ lines of documentation in under 2 hours. That's the power of parallel agent execution."

---

## Fallback Points

### If `sudo su` doesn't work
- The NOPASSWD might have been fixed. Say: "It appears the sudoers misconfiguration has been remediated — which is exactly what should happen."
- Move to showing the service file and playlist instead.

### If pulselink service isn't running
- Check: `sudo systemctl start pulselink`
- If it fails, show the service file and logs: `sudo journalctl -u pulselink -n 20`

### If WiFi is down
- Restore: `sudo ip link set wlan0 up`
- If DHCP fails, manually: `sudo dhclient wlan0`

### If SSH is already disabled
- This is actually a GOOD demo point — show that you can only access via physical terminal

### If HDMI output doesn't work
- Check cable connection
- Try: `tvservice -p` to restore HDMI
- Fallback to showing output on Pi's terminal directly

---

## Timing Summary

| Section | Duration | Cumulative |
|---------|----------|------------|
| Problem (n-compass TV + risk) | 5 min | 5 min |
| Demo 1: Recon | 2 min | 7 min |
| Demo 2: Instant Root | 2 min | 9 min |
| Demo 3: Credentials | 2 min | 11 min |
| Demo 4: Content Injection | 2 min | 13 min |
| Demo 5: Service Control | 3 min | 16 min |
| Demo 6: SSH Lockout | 2 min | 18 min |
| Impact & Remediation | 5 min | 23 min |
| Buffer/Q&A | 5 min | 28 min |
| **Total** | **~25-30 min** | |

---

## Post-Demo Checklist

- [ ] Restore SSH: `sudo systemctl start ssh && sudo systemctl enable ssh`
- [ ] Restore service auto-restart: `sudo rm -f /etc/systemd/system/pulselink.service.d/override.conf && sudo systemctl daemon-reload && sudo systemctl start pulselink`
- [ ] Restore wlan0: `sudo ip link set wlan0 up`
- [ ] Clear terminal history: `history -c && cat /dev/null > ~/.bash_history`
- [ ] Leave Pi in vulnerable state if another demo is needed, OR apply fixes for production

---

**Generated:** 2026-03-17  
**Agent:** specter-report  
**Classification:** CONFIDENTIAL
