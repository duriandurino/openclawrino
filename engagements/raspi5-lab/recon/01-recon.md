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

### NetBIOS / NMBLOOKUP
```bash
nmblookup -A <subnet_broadcast>
# Windows network name resolution — may reveal hostname
```

---

## 1.2 DNS Enumeration

If the Pi has a hostname or is accessible via DNS:

```bash
# Forward lookup
dig raspberrypi.local
nslookup <hostname>

# Reverse lookup on suspected IPs
dig -x 192.168.1.x

# Check for any .local or .home.arpa records
dig @<dns_server> <domain> ANY
```

---

## 1.3 OSINT (if externally accessible)

**Note:** The Pi 5B is on a local network, so external OSINT is limited unless:
- Port forwarding is configured on the router
- The Pi has a public IP or is exposed via VPN/tunnel
- There's a public-facing service hosted on it

### Shodan (if public IP found)
```bash
# From our Kali box with Shodan CLI
shodan search "raspberrypi <public_ip>"
shodan search "hostname:raspberrypi"
shodan search "product:OpenSSH product:Linux"

# Or via web
# https://www.shodan.io/search?query=raspberrypi
```

### Censys.io
```bash
# Web-based: search for the Pi's public IP or hostname
# https://censys.io/ipv4/<public_ip>
```

---

## 1.4 Passive Traffic Analysis

### tcpdump — Listen Without Interacting
```bash
# Capture traffic to/from suspected Pi IP (no active probing)
sudo tcpdump -i eth0 host 192.168.1.x -w raspi-recon.pcap

# Watch for mDNS announcements
sudo tcpdump -i wlan0 port 5353 -n

# Look for DHCP traffic
sudo tcpdump -i eth0 port 67 or port 68 -n
```

### What to Look For
- **DHCP lease requests** — hostname, MAC vendor (Raspberry Pi Foundation: B8:27:EB, DC:A6:32, E4:5F:01)
- **mDNS announcements** — services, hostname
- **SSH banners** — OpenSSH version reveals OS age
- **NTP traffic** — timing info, NTP server preferences
- **SMB/NetBIOS** — Windows compatibility, workgroup names

---

## 1.5 MAC Address Fingerprinting

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

# Or with nmap
nmap -sn 192.168.1.0/24 --script mac-geolocation
```

---

## 1.6 Passive Port Detection (via mDNS/SSDP)

Without sending packets to the target directly:

```bash
# mDNS service discovery (target announces itself)
avahi-browse -a -r -t | grep -A5 "raspberrypi"

# SSDP discovery (if UPnP enabled)
nmap --script upnp-info -p 1900 239.255.255.250

# Check ARP cache after any mDNS queries
arp -an
```

---

## 1.7 Recon Summary Template

Document findings before moving to active enumeration:

```
TARGET RECON SUMMARY
=====================
IP Address:        ___________
MAC Address:       ___________
MAC Vendor:        ___________ (confirm: Raspberry Pi Foundation)
Hostname:          ___________
OS (guessed):      ___________
mDNS Services:     ___________
  - SSH:           ___________
  - HTTP:          ___________
  - Samba:         ___________
  - VNC:           ___________
  - Other:         ___________
Open Ports (observed): ___________
Default Creds:     ___________
Storage Lock:      CONFIRMED — cannot image SD/NVMe off-device
Physical Access:   YES / NO
```

---

## 1.8 Next Steps

Once passive recon is complete, move to:
- [Phase 2: Active Enumeration](02-enumeration.md) — nmap, service fingerprinting
- [Phase 3: Hardware Attacks](03-hardware-attacks.md) — if physical access confirmed

---

*Don't jump to active scanning until you've exhausted passive vectors. You might learn everything you need without ever touching the target.*
