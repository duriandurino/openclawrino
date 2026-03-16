# Phase 2: Active Enumeration

> **Agent:** specter-enum  
> **Phase:** Enumeration  
> **Methodology:** Active scanning — direct interaction with target

⚠️ **Confirm authorization before running any active scans.**

---

## 2.1 Port Scanning

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
| **5900** | VNC | Remote desktop |
| **8080** | HTTP-alt | Pi-hole admin, OctoPrint |
| **1883** | MQTT | IoT — Pi is often an IoT hub |

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
- **SSH:** `OpenSSH 8.4p1 Debian-5+deb11u2 (or newer)`
- **HTTP:** `Apache/2.4.54 (Raspbian)` or `nginx/1.18.0`
- **Samba:** `Samba smbd - workgroup: WORKGROUP`

---

## 2.3 SSH Enumeration

```bash
# Banner grab
nc -vn <target_ip> 22

# SSH enumeration script
nmap -p 22 --script ssh2-enum-algos,ssh-hostkey,ssh-auth-methods <target_ip>

# Brute-force (if authorized)
hydra -l pi -P /usr/share/wordlists/rockyou.txt ssh://<target_ip>
```

### Key SSH Config Checks
| Setting | Expected | Risk |
|---------|----------|------|
| `PermitRootLogin` | `prohibit-password` or `yes` | `yes` = high risk |
| `PasswordAuthentication` | `yes` (default on Pi OS) | Brute-forceable |
| `AllowUsers` | Not set (all users) | Any valid user can login |

---

## 2.4 SMB/Samba Enumeration

```bash
# List shares
smbclient -L //<target_ip> -N

# Enumerate shares with enum4linux
enum4linux -a <target_ip>

# Check for anonymous access
smbmap -H <target_ip> -R
```

---

## 2.5 Web Service Enumeration

```bash
# Basic recon
curl -I http://<target_ip>

# Directory busting
gobuster dir -u http://<target_ip> -w /usr/share/wordlists/dirb/common.txt

# Nikto scan
nikto -h http://<target_ip>

# WhatWeb fingerprint
whatweb http://<target_ip>
```

### Common Pi Web Interfaces
| Application | Port | Path |
|-------------|------|------|
| Pi-hole | 80/8080 | `/admin` |
| OctoPrint | 5000/80 | `/` |
| Node-RED | 1880 | `/` |
| Home Assistant | 8123 | `/` |
| Webmin | 10000 | `/` |

---

## 2.6 Evidence Collection

```bash
mkdir -p /home/dukali/.openclaw/workspace/engagements/raspi5-lab/evidence

# Save scan results
cp raspi-full.nmap evidence/
cp raspi-full.xml evidence/
```

---

## Next Steps

- [Phase 3: Hardware Attacks](../exploit/03-hardware-attacks.md)
- [Phase 5: Vulnerability Analysis](../vuln/05-vulnerability-analysis.md)
