# Phase Complete: Enumeration

**Engagement:** player-network
**Phase:** 2 - Enumeration
**Agent:** Hatless White (manual)
**Date:** 2026-03-18
**Status:** complete

## Found

### 192.168.0.130 (Real Player — MAC: 2c:cf:67:04:0b:d1)
- Port 111/tcp: rpcbind 2-4 (ONLY open TCP port)
- Port 111/udp: rpcbind
- Port 5353/udp: zeroconf/mDNS
- 65534 ports CLOSED (TCP reset)
- No SSH, HTTP, VNC, API exposed

### 192.168.0.161 (Collateral Player — MAC: 2c:cf:67:0f:2c:88)
- Port 22/tcp: SSH (password auth enabled)
- Port 80/tcp: nginx/1.14.2 (reverse proxy, 403 Forbidden)
- Port 3215/tcp: Node.js Express — UNAUTHENTICATED API
- Port 5900/tcp: VNC (RFB 005.000, rate-limited)
- Port 7070/tcp: AnyDesk (SSL)

### 192.168.0.103 (Backend Server G8 — MAC: 58:02:05:2D:05:CC)
- 17+ open ports including MySQL, RDP, WinRM, AnyDesk, APIs
- Port 42052: OAuth2 auth flow confirmed active
- Port 82: Kestrel .NET with CORS wildcard misconfiguration

## Not Found

- No MQTT broker on local network (cloud-hosted at pulse.n-compass.online)
- No anonymous MySQL access on backend
- No unauthenticated endpoints on backend except port 42052 auth API

## Recommended Next

- **Next Phase:** specter-vuln (on 192.168.0.130 specifically)
- **Vector:** network — rpcbind enumeration, UDP services
- **Reason:** Real Player has minimal attack surface (rpcbind only); need deeper vulnerability analysis

## Key Data

### Port Inventory — 192.168.0.130
| Port | State | Service |
|------|-------|---------|
| 111/tcp | OPEN | rpcbind 2-4 |
| 111/udp | OPEN | rpcbind |
| 5353/udp | OPEN | mDNS/zeroconf |

### Port Inventory — 192.168.0.161
| Port | State | Service | Notes |
|------|-------|---------|-------|
| 22/tcp | OPEN | SSH | Password auth, pi user |
| 80/tcp | OPEN | nginx/1.14.2 | 403 Forbidden |
| 3215/tcp | OPEN | Express API | NO AUTH — full data access |
| 5900/tcp | OPEN | VNC | RFB 005.000, rate-limited |
| 7070/tcp | OPEN | AnyDesk | SSL |

### Tools Used
- nmap (full port scan, service detection, OS detection, UDP scan)
- rpcinfo (RPC enumeration)
- curl (HTTP API probing)
- python3 (API exploitation, VNC protocol probing)
- hydra (credential attacks on MySQL, RDP)
- evil-winrm (WinRM credential attacks)

## Confidence

- **Overall:** high
- **Network findings:** high
- **Service identification:** high
- **Vulnerability assessment:** medium

## Notes

- Player at .130 was significantly locked down compared to .161
- Only RPC service exposed — extremely minimal attack surface
- Collateral findings on .161 and .103 are more exploitable
