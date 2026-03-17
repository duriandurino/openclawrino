# Reverse Fix Guide — PulseLink Pi Restoration

**Purpose:** Step-by-step commands to restore the Pi to its ORIGINAL (pre-pentest) state  
**Target:** 192.168.0.125 — Raspberry Pi 5 Model B  
**Date:** 2026-03-17  
**⚠️ FOR DEMONSTRATION/DOCUMENTATION ONLY — DO NOT execute these commands in a real engagement**

---

## Overview

This guide documents the EXACT commands needed to undo every change made during the penetration test. **In a real engagement, these would NOT be run** — the pentester leaves findings in place for the client to remediate. This exists solely for demo preparation and to document what was changed.

---

## 1. Re-enable SSH

**What was done:** SSH was disabled via system settings to demonstrate the SSH lockout finding (V-014).

**To restore:**
```bash
# Method 1: Using raspi-config (if available)
sudo raspi-config
# Navigate to: 3 Interface Options → I2 SSH → Enable

# Method 2: Direct systemd
sudo systemctl enable ssh
sudo systemctl start ssh

# Method 3: Enable the socket directly
sudo systemctl enable ssh.socket
sudo systemctl start ssh.socket

# Verify SSH is listening
sudo ss -tlnp | grep :22
# Expected: LISTEN  0  128  0.0.0.0:22  ...
```

---

## 2. Restore sudo NOPASSWD (⚠️ DOCUMENTATION ONLY — DO NOT DO THIS IN REAL LIFE)

**What was done:** Documented that the `pi` user has `(ALL) NOPASSWD: ALL` in sudoers. This is the PRIMARY finding (V-001).

**⚠️ CRITICAL WARNING:** The entire purpose of this pentest was to FIND this misconfiguration. Restoring it defeats the purpose. **Never re-introduce NOPASSWD sudo in production.**

**For demo purposes only — what the original sudoers line looked like:**
```bash
# Original state (VULNERABLE — do NOT restore in production):
# The pi user had this line in /etc/sudoers:
pi ALL=(ALL:ALL) ALL
pi ALL=(ALL) NOPASSWD: ALL

# To verify the CURRENT (fixed) state after remediation:
sudo cat /etc/sudoers | grep pi
# Should show: pi ALL=(ALL:ALL) ALL  (without NOPASSWD)

# If you somehow need to reproduce the vulnerable state for demo setup:
echo 'pi ALL=(ALL) NOPASSWD: ALL' | sudo EDITOR='tee -a' visudo
# ⚠️ AGAIN: Only do this for demo setup, NEVER in production
```

---

## 3. Restore File Permissions on Private Key (⚠️ DOCUMENTATION ONLY)

**What was done:** Documented that `/opt/pulselink/client_certs/client_pi_generic.key` had 644 permissions (V-004).

**For demo setup only — to reproduce the vulnerable state:**
```bash
# Original (VULNERABLE) permissions:
sudo chmod 644 /opt/pulselink/client_certs/client_pi_generic.key

# Correct (FIXED) permissions:
sudo chmod 600 /opt/pulselink/client_certs/client_pi_generic.key

# Verify
ls -la /opt/pulselink/client_certs/
# Should show: -rw------- 1 root root ... client_pi_generic.key
```

---

## 4. Restore pulselink Service Auto-Restart (⚠️ FOR DEMO ONLY)

**What was done:** Demonstrated that `Restart=always` in the service file prevents `systemctl stop` from working (V-016). The override was edited to set `Restart=no`, then `Ctrl+W` (Ctrl+C equivalent) killed the player permanently.

**To restore the original `Restart=always` behavior:**

```bash
# Check if there's an override
sudo systemctl cat pulselink

# If override exists, remove it
sudo rm -f /etc/systemd/system/pulselink.service.d/override.conf

# Reload systemd
sudo systemctl daemon-reload

# Verify Restart=always is back
sudo cat /etc/systemd/system/pulselink.service | grep Restart
# Should show: Restart=always

# Restart the service
sudo systemctl restart pulselink

# Verify it's running
sudo systemctl status pulselink
```

**To reproduce the original vulnerable state for demo setup:**
```bash
# The original service file has:
# [Service]
# Restart=always
# RestartSec=10

# This means 'systemctl stop pulselink' does NOT stop it —
# systemd immediately restarts it. To actually stop it:
# 1. Create override: sudo systemctl edit pulselink
# 2. Add: [Service]
#          Restart=no
# 3. sudo systemctl daemon-reload
# 4. sudo systemctl stop pulselink
# 5. Now Ctrl+C in the terminal kills it permanently
```

---

## 5. Re-enable pulselink Service

**What was done:** The service was stopped during the service control demonstration.

**To re-enable:**
```bash
# Ensure the service is enabled
sudo systemctl enable pulselink

# Start the service
sudo systemctl start pulselink

# Verify it's running
sudo systemctl status pulselink

# Check logs
sudo journalctl -u pulselink --since "5 minutes ago" --no-pager
```

---

## 6. Restore Network Connectivity

**What was done:** `wlan0` was brought down to demonstrate WiFi deauth risk (V-009, terminal-output-4.txt).

**To restore:**
```bash
# Bring wlan0 back up
sudo ip link set wlan0 up

# Verify
ip addr show wlan0
# Should show: state UP

# Check if WiFi reconnected
ping -c 3 8.8.8.8
```

---

## 7. Remove Any Temporary Files Created During Testing

```bash
# Clean up exploit artifacts (if CVE-2025-32463 was demonstrated)
sudo rm -rf /tmp/exploit_chroot

# Clean up evidence files (if saved locally on Pi)
rm -f /tmp/pulselink_*.txt /tmp/shadow.txt /tmp/passwd.txt
rm -f /tmp/ssh_*.txt /tmp/wifi_passwords.txt
rm -f /tmp/listening_ports.txt /tmp/all_connections.txt
rm -f /tmp/pulse_processes.txt /tmp/mpv_script.txt /tmp/vlc_script.txt
rm -rf /tmp/app_unpacked /tmp/app.asar

# Clear bash history (if desired)
history -c
cat /dev/null > /home/pi/.bash_history
sudo cat /dev/null > /root/.bash_history
```

---

## 8. Full Restoration Checklist

Use this checklist to verify the Pi is back to its original state:

| # | Item | Command to Verify | Expected Result |
|---|------|-------------------|-----------------|
| 1 | SSH enabled | `sudo systemctl status ssh` | Active (running) |
| 2 | sudo NOPASSWD present | `sudo cat /etc/sudoers \| grep pi` | `pi ALL=(ALL) NOPASSWD: ALL` ⚠️ |
| 3 | Private key permissions 644 | `ls -la /opt/pulselink/client_certs/client_pi_generic.key` | `-rw-r--r--` ⚠️ |
| 4 | Service Restart=always | `sudo cat /etc/systemd/system/pulselink.service \| grep Restart` | `Restart=always` |
| 5 | pulselink running | `sudo systemctl status pulselink` | Active (running) |
| 6 | wlan0 up | `ip link show wlan0` | state UP |
| 7 | No temp exploit files | `ls /tmp/exploit_chroot 2>/dev/null` | No such file |
| 8 | .env unchanged | `sudo cat /opt/pulselink/.env` | Plaintext credentials present ⚠️ |

⚠️ Items marked ⚠️ are the VULNERABLE states that were found. In production remediation, these should REMAIN FIXED (not reverted).

---

## Important Notes

1. **This guide is for DEMO PREPARATION ONLY.** The presenter may need to set up the Pi in its vulnerable state to demonstrate findings live.

2. **In a real engagement**, the pentester does NOT restore vulnerable configurations. The client is expected to remediate based on the findings report.

3. **The vulnerable state** (NOPASSWD sudo, world-readable keys, etc.) is intentionally INSECURE. Only reproduce it temporarily for demonstration purposes.

4. **After the demo**, re-apply all fixes:
   - Remove NOPASSWD from sudoers
   - Set private key to 600 permissions
   - Run pulselink as non-root user
   - Update Electron/Chromium
   - Move credentials to secrets management

---

**Generated:** 2026-03-17  
**Agent:** specter-report  
**Classification:** CONFIDENTIAL
