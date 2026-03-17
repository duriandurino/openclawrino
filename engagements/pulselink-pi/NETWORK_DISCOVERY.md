# Network Service Discovery
## PulseLink Pi — Port Scanning & Service Enumeration

**Target:** 192.168.0.125 (Raspberry Pi 5)
**Date:** 2026-03-17

---

## 1. Prerequisites

```bash
# Verify target is reachable
ping -c 3 192.168.0.125

# If ping fails, check if Pi is on network
nmap -sn 192.168.0.0/24 | grep 192.168.0.125
```

## 2. Full Port Scan

### Fast comprehensive scan (all 65535 ports)
```bash
nmap -p- --min-rate 1000 -oN /tmp/pi_allports.txt 192.168.0.125
```

### If you want speed + service detection
```bash
nmap -sC -sV -p- --min-rate 1000 \
  -oN /tmp/pi_full_scan.txt \
  192.168.0.125
```

### Aggressive scan with OS detection
```bash
nmap -sS -sV -O -A --min-rate 1000 \
  -oN /tmp/pi_aggressive.txt \
  192.168.0.125
```

### Target only common IoT ports (faster)
```bash
nmap -sC -sV \
  -p 21,22,23,53,80,443,1883,8080,8443,8883,111,5000,5001,5353,62078 \
  -oN /tmp/pi_common_ports.txt \
  192.168.0.125
```

## 3. Service Version Detection

### Detailed service info on open ports
```bash
nmap -sV -sC -p 22,111 \
  --version-intensity 9 \
  -oN /tmp/pi_services.txt \
  192.168.0.125
```

### Probe specific services
```bash
# HTTP services
nmap -sV -p 80,443,8080,8443,5000,5001 \
  --script=http-enum,http-title,http-server-header \
  192.168.0.125

# SSH
nmap -sV -p 22 \
  --script=ssh2-enum-algos,ssh-hostkey \
  192.168.0.125

# RPC
nmap -sV -p 111 \
  --script=rpcinfo \
  192.168.0.125
```

## 4. mDNS / DNS-SD Discovery

### Browse for mDNS services
```bash
avahi-browse -a -t

# Specific service types
avahi-browse -r _http._tcp
avahi-browse -r _mqtt._tcp
avahi-browse -r _ssh._tcp
avahi-browse -r _rfb._tcp
```

### Using nmap mDNS discovery
```bash
nmap --script mdns-discovery -p 5353 192.168.0.125
```

### Using dns-sd (if available)
```bash
dns-sd -B _services._dns-sd._udp local.
```

## 5. Network-Wide Discovery

### ARP scan (fastest for LAN discovery)
```bash
sudo arp-scan --localnet
# or
sudo arp-scan -l
```

### Ping sweep to find all hosts
```bash
nmap -sn 192.168.0.0/24
```

### Find the Pi by hostname pattern
```bash
nmap -sn 192.168.0.0/24 | grep -iE "raspberry|pi|pulselink|nctv"
```

### Identify Pi by MAC vendor (Raspberry Pi Foundation)
```bash
nmap -sn 192.168.0.0/24 -oG - | grep -iE "Raspberry|B8:27|DC:A6|E4:5F"
# Raspberry Pi MAC prefixes:
#   B8:27:EB
#   DC:A6:32
#   E4:5F:01
```

## 6. RPC Enumeration

### Query RPC services
```bash
rpcinfo -p 192.168.0.125

# Using nmap
nmap -sV -p 111 --script=rpcinfo 192.168.0.125
```

### NFS enumeration (if RPC shows mountd)
```bash
showmount -e 192.168.0.125
```

## 7. SMB Enumeration (if port 445 is open)

```bash
# List shares
smbclient -L //192.168.0.125 -N

# Enum4Linux (comprehensive)
enum4linux -a 192.168.0.125
```

## 8. HTTP Service Enumeration (if web interface exists)

```bash
# Basic web scan
nmap -sV -p 80,443,8080,8443,5000,5001 \
  --script=http-enum,http-title,http-headers \
  192.168.0.125

# Directory brute force (if HTTP found)
gobuster dir -u http://192.168.0.125:8080 \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x php,html,json,js

# nikto scan
nikto -h http://192.168.0.125:8080
```

## 9. VNC / Remote Desktop (common on Pi)

```bash
# Check for VNC (port 5900+)
nmap -sV -p 5900-5910 192.168.0.125

# Try VNC connection
vncviewer 192.168.0.125:5900
```

## 10. Bluetooth / BLE Enumeration (Pi-specific)

```bash
# Scan for Bluetooth devices
sudo hcitool scan

# BLE scan
sudo bluetoothctl
# Then: scan on

# Check if Pi is advertising BLE
sudo hcitool lescan
```

## 11. SSH Service Deep Dive

```bash
# SSH enumeration
nmap -sV -p 22 \
  --script=ssh2-enum-algos,ssh-hostkey,ssh-auth-methods \
  192.168.0.125

# Try default credentials
ssh pi@192.168.0.125   # password: raspberry (default)
ssh pi@192.168.0.125 -o BatchMode=yes -o ConnectTimeout=5

# Check for SSH key auth
ssh -v pi@192.168.0.125 2>&1 | grep -i "authentication"
```

## 12. Results Documentation

After scanning, document:

| Port | Service | Version | Notes |
|------|---------|---------|-------|
| 22 | SSH | OpenSSH X.X | Default creds? Key auth? |
| 111 | RPCBind | rpcbind X.X | What RPC services? |
| XXX | XXX | XXX | XXX |

## 13. Comparison with Previous Scan

If you scanned the Pi before (see `engagements/pulselink-pi/enum/`), compare:

```bash
# Compare current scan with previous
diff /tmp/pi_full_scan.txt engagements/pulselink-pi/enum/previous_scan.txt
```

**Key things to check for changes:**
- New ports opened (new services installed)
- New services on existing ports (updates)
- Different service versions (auto-updates?)
- New hostnames or DNS names
