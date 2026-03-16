# Phase 1: Passive Reconnaissance

> **Agent:** specter-recon  
> **Phase:** Recon  
> **Methodology:** Passive only — no direct interaction with target

---

## 1.1 Network Discovery (LAN)

Since we're on the same network, start with local discovery.

### ARP Scan
```bash
# Find all hosts on the local subnet
sudo arp-scan --localnet

# Or with nmap
nmap -sn 192.168.1.0/24
```

### mDNS / Avahi Enumeration
Raspberry Pi OS ships with Avahi (mDNS). The Pi will likely advertise itself.

```bash
# Discover .local hosts
avahi-browse -a -r -t

# Or using nmap
nmap --script dns-sd-discovery -p 5353 <subnet>

# Direct queries
dig @224.0.0.251 -p 5353 _workstation._tcp.local PTR
```

### Expected mDNS Services
| Service Type | Typical on Pi | What It Reveals |
|-------------|---------------|-----------------|
| `_ssh._tcp` | Yes (if enabled) | SSH availability, port |
| `_http._tcp` | Possible (if web server) | Web interface |
| `_smb._tcp` | Possible (if Samba) | File shares |
| `_VNC._tcp` | Possible (if VNC) | Remote desktop |
| `_workstation._tcp` | Yes | Hostname, basic info |

---

## 1.2 OSINT (if externally accessible)

### Shodan (if public IP found)
```bash
shodan search "raspberrypi <public_ip>"
shodan search "hostname:raspberrypi"
shodan search "product:OpenSSH product:Linux"
```

---

## 1.3 Passive Traffic Analysis

```bash
# Capture traffic to/from suspected Pi IP (no active probing)
sudo tcpdump -i eth0 host 192.168.1.x -w raspi-recon.pcap

# Watch for mDNS announcements
sudo tcpdump -i wlan0 port 5353 -n
```

### What to Look For
- **DHCP lease requests** — hostname, MAC vendor
- **mDNS announcements** — services, hostname
- **SSH banners** — OpenSSH version reveals OS age
- **NTP traffic** — timing info, NTP server preferences

---

## 1.4 MAC Address Fingerprinting

Raspberry Pi Foundation OUIs:

| OUI Prefix | Device |
|------------|--------|
| `B8:27:EB` | Raspberry Pi (older) |
| `DC:A6:32` | Raspberry Pi (newer) |
| `E4:5F:01` | Raspberry Pi (Pi 4/5 era) |
| `28:CD:C1` | Raspberry Pi (Pi 5 specific batches) |

```bash
# Check if a MAC matches Pi
arp-scan --localnet | grep -i "b8:27:eb\|dc:a6:32\|e4:5f:01"
```

---

## 1.5 Recon Summary Template

```
TARGET RECON SUMMARY
=====================
IP Address:        ___________
MAC Address:       ___________
MAC Vendor:        ___________
Hostname:          ___________
OS (guessed):      ___________
mDNS Services:     ___________
  - SSH:           ___________
  - HTTP:          ___________
  - Samba:         ___________
  - VNC:           ___________
Open Ports:        ___________
Storage Lock:      CONFIRMED
Physical Access:   YES / NO
```

---

## 1.6 Next Steps

- [Phase 2: Active Enumeration](../enum/02-enumeration.md)
- [Phase 3: Hardware Attacks](../exploit/03-hardware-attacks.md)

---

*Don't jump to active scanning until you've exhausted passive vectors.*
