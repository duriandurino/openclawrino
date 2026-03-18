# Network Reconnaissance — Initial Findings
**Date:** 2026-03-18 09:27 PST
**Target Range:** 192.168.0.0/24
**Intended Target:** Raspberry Pi 5 Player (was 192.168.0.125)

## Critical Discovery
The Player at 192.168.0.125 is **unreachable** (ARP FAILED). However, during subnet enumeration,
the **N-Compass TV Backend Server** was discovered.

## Primary Target: 192.168.0.103 — "G8" (N-Compass TV Backend)

### Host Profile
| Field | Value |
|-------|-------|
| **IP** | 192.168.0.103 |
| **Hostname** | G8.nctv360.com |
| **Domain** | NCTV360 |
| **OS** | Windows 11 (10.0.26100) |
| **MAC** | 58:02:05:2D:05:CC |
| **Role** | N-Compass TV Backend / Dealer Management Server |

### Open Ports & Services
| Port | Service | Notes |
|------|---------|-------|
| **82** | Kestrel (.NET) | Backend API, **CORS wide open**, OPTIONS 200 |
| **135** | MSRPC | Windows RPC |
| **139/445** | SMB/NetBIOS | Domain: NCTV360, File Server active, anonymous DENIED |
| **3306** | MySQL 8.4.8 | Docker (172.24.0.1), root auth required |
| **3307** | MySQL 8.0.45 | Docker (172.25.0.1), root auth required |
| **3389** | RDP | Windows RDP active |
| **4200** | Node.js Express | N-Compass TV Development (Angular frontend) |
| **42052** | Node.js Express | Backend API (empty responses) |
| **5985** | WinRM | HTTP API |
| **7070** | AnyDesk | Remote access |
| **49153-49671** | MSRPC | Multiple RPC endpoints |

### Vulnerability Indicators
1. **CORS misconfiguration** — Kestrel on port 82 allows all origins
2. **MySQL in Docker** — Two separate MySQL instances in Docker containers
3. **AnyDesk** — Third-party remote access tool (potential credential attack)
4. **WinRM + RDP** — Multiple remote management interfaces exposed
5. **No SMB anonymous auth** — Good security, but NetBIOS name泄露

## Other Notable Hosts
| IP | Ports | Notes |
|----|-------|-------|
| 192.168.0.81 | 80 | HTTP, RPi Foundation MAC |
| 192.168.0.145 | 22,80,5900 | SSH+HTTP+VNC, RPi Foundation MAC |
| 192.168.0.244 | 22 | SSH only |

## Attack Vectors Identified
1. **RDP brute force** — Default/weak credentials on G8
2. **MySQL brute force** — Docker-isolated but reachable
3. **WinRM access** — Windows Remote Management
4. **Kestrel API exploitation** — CORS misconfig, potential injection
5. **AnyDesk credential theft** — Third-party remote access
6. **Fleet compromise** — Backend server controls all Players via MQTT
