# Phase 2: Active Enumeration

> **Agent:** specter-enum  
> **Phase:** Enumeration  
> **Methodology:** Active scanning — direct interaction with target

⚠️ **Confirm authorization before running any active scans.**

---

## 2.1 Port Scanning

### Full Port Scan
```bash
# SYN scan (fast, stealthy-ish)
nmap -sS -T2 --top-ports 1000 -oN raspi-nmap.txt <target_ip>

# Full TCP port scan with service detection
nmap -sV -sC -p- -T3 -oA raspi-full <target_ip>

# Quick check — most common services
nmap -sS -sV -F -T4 <target_ip>
```

### Pi-Specific Ports to Check
| Port | Service | Notes |
|------|---------|-------|
| **22** | SSH | Almost always present if headless |
| **80** | HTTP | Pi-hole, web interface, Node-RED |
| **443** | HTTPS | Web interface with TLS |
| **445** | SMB/Samba | File sharing — common on Pi |
| **139** | NetBIOS/SMB | Legacy SMB |
| **5900** | VNC | Remote desktop |
| **5353** | mDNS | Service discovery |
| **8080** | HTTP-alt | Pi-hole admin, OctoPrint, web apps |
| **8443** | HTTPS-alt | Various web interfaces |
| **1883** | MQTT | IoT — Pi is often an IoT hub |
| **62078** | Sync | iOS sync cache (if iPhone connected) |

### UDP Scan (if needed)
```bash
# UDP scan — slower but catches SNMP, DNS, NTP
nmap -sU --top-ports 100 -T3 -oN raspi-udp.txt <target_ip>
```

---

## 2.2 Service Version Detection

```bash
# Aggressive version detection
nmap -sV --version-intensity 9 -p <open_ports> <target_ip>

# OS detection
nmap -O --osscan-guess <target_ip>

# Combined: version + OS + scripts
nmap -sV -sC -O -A <target_ip>
```

### Expected Fingerprints for Pi 5B

**SSH (port 22):**
```
OpenSSH 8.4p1 Debian-5+deb11u2 (or newer)
Protocol 2.0
```
- Debian version reveals Pi OS version

**HTTP (port 80/8080):**
```
Apache/2.4.54 (Raspbian) or nginx/1.18.0
```
- Look for Pi-hole, webmin, custom apps

**Samba (port 445):**
```
Samba smbd - workgroup: WORKGROUP or MSHOME
```
- Check share names, anonymous access

---

## 2.3 SSH Enumeration

```bash
# Banner grab
nc -vn <target_ip> 22

# Full SSH enumeration script
nmap -p 22 --script ssh2-enum-algos,ssh-hostkey,ssh-auth-methods <target_ip>

# Brute-force (if authorized)
hydra -l pi -P /usr/share/wordlists/rockyou.txt ssh://<target_ip>
hydra -L /usr/share/wordlists/users.txt -P /usr/share/wordlists/rockyou.txt ssh://<target_ip>
```

### Common Pi SSH Configurations
```bash
# Check default config on a Pi
cat /etc/ssh/sshd_config | grep -v "^#"
```

Key things to check:
| Setting | Expected | Risk |
|---------|----------|------|
| `PermitRootLogin` | `prohibit-password` or `yes` | `yes` = high risk |
| `PasswordAuthentication` | `yes` (default on Pi OS) | Brute-forceable |
| `Port` | `22` (default) | Unchanged = easy target |
| `AllowUsers` | Not set (all users) | Any valid user can login |
| `PubkeyAuthentication` | `yes` | Secure if passwords disabled |

---

## 2.4 SMB/Samba Enumeration

```bash
# List shares
smbclient -L //<target_ip> -N

# Connect to a share (anonymous)
smbclient //<target_ip>/pi -N

# Enumerate shares with enum4linux
enum4linux -a <target_ip>

# Map shares with smbmap
smbmap -H <target_ip>

# Check for anonymous access
smbmap -H <target_ip> -R
```

### Samba Config to Analyze (on-device)
```bash
cat /etc/samba/smb.conf
```
Look for:
- `[global]` security level — `user` vs `share`
- `[homes]` — home directory sharing
- `[pi]` or custom shares — what's shared
- `guest ok = yes` — anonymous access
- `writable = yes` — can we write?

---

## 2.5 Web Service Enumeration

If HTTP services are found:

```bash
# Basic recon
curl -I http://<target_ip>
curl -s http://<target_ip> | head -50

# Directory busting
gobuster dir -u http://<target_ip> -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
dirb http://<target_ip> /usr/share/wordlists/dirb/common.txt
feroxbuster -u http://<target_ip> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

# Nikto scan
nikto -h http://<target_ip>

# WhatWeb fingerprint
whatweb http://<target_ip>
```

### Common Pi Web Interfaces
| Application | Port | Path | Notes |
|-------------|------|------|-------|
| Pi-hole | 80/8080 | `/admin` | DNS blocker admin panel |
| OctoPrint | 5000/80 | `/` | 3D printer interface |
| Node-RED | 1880 | `/` | IoT flow editor |
| Home Assistant | 8123 | `/` | Smart home hub |
| Webmin | 10000 | `/` | System admin panel |
| Cockpit | 9090 | `/` | Server monitoring |
| Portainer | 9000 | `/` | Docker management |

---

## 2.6 VNC Enumeration

```bash
# VNC service detection
nmap -p 5900-5920 --script vnc-info <target_ip>

# Attempt VNC connection (default password: raspberry)
vncviewer <target_ip>::5900

# Bruteforce (if authorized)
hydra -P /usr/share/wordlists/rockyou.txt vnc://<target_ip>
```

---

## 2.7 NFS Enumeration

```bash
# Show NFS exports
showmount -e <target_ip>

# If NFS is available
mount -t nfs <target_ip>:/export /mnt/nfs_share
ls -la /mnt/nfs_share
```

---

## 2.8 MQTT Enumeration (IoT)

If port 1883 is open — the Pi is likely acting as an MQTT broker or client:

```bash
# Check if anonymous access is allowed
mosquitto_sub -h <target_ip> -t '#' -v

# List topics
mosquitto_sub -h <target_ip> -t '$SYS/#' -v

# Publish (if authorized)
mosquitto_pub -h <target_ip> -t 'test' -m 'hello'
```

---

## 2.9 DNS Enumeration (if Pi-hole)

If Pi-hole is running (common on Pi):

```bash
# Query the Pi's DNS
dig @<target_ip> any localhost

# Try zone transfer (unlikely to work but check)
dig @<target_ip> axfr local

# Enumerate DNS records
dig @<target_ip> <common_subdomains> 

# DNSRecon
dnsrecon -d local -n <target_ip>
```

---

## 2.10 Bluetooth Enumeration

If physical access and the Pi has Bluetooth enabled:

```bash
# Scan for devices
hcitool scan
bluetoothctl scan on

# Pair if possible
bluetoothctl
> pair <MAC>
> connect <MAC>

# SDP service discovery
sdptool browse <target_ip>
```

---

## 2.11 Enumeration Checklist

- [ ] Full port scan completed
- [ ] Service versions identified
- [ ] SSH configuration analyzed
- [ ] SMB shares enumerated
- [ ] Web services mapped
- [ ] VNC checked
- [ ] NFS exports listed
- [ ] MQTT topics observed
- [ ] DNS (Pi-hole) tested
- [ ] Bluetooth services discovered
- [ ] All findings documented

---

## 2.12 Evidence Collection

Save all scan results:

```bash
mkdir -p /home/dukali/.openclaw/workspace/pentest-raspi5b/evidence

# Save nmap results
cp raspi-full.nmap evidence/
cp raspi-full.xml evidence/

# Save service-specific results
cp smb-enum.txt evidence/
cp web-scan.txt evidence/
```

---

## Next Steps

Once enumeration is complete, move to:
- [Phase 3: Hardware Attacks](03-hardware-attacks.md) — GPIO, UART, USB
- [Phase 5: Vulnerability Analysis](05-vulnerability-analysis.md) — CVE matching

---

*Enumeration is where you find the doors. Don't try to open them yet — just map every entry point first.*
