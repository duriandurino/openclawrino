# Phase Complete: Reconnaissance

**Engagement:** player-network
**Phase:** 1 - Reconnaissance
**Agent:** Hatless White (manual, no specter-recon sub-agent)
**Date:** 2026-03-18
**Status:** complete

## Found

- Target identified: 192.168.0.130 (Raspberry Pi 4 Model B, MAC: 2c:cf:67:04:0b:d1)
- Backend server discovered: 192.168.0.103 (G8.nctv360.com, Windows 11)
- Cloud infrastructure mapped: pulse.n-compass.online (MQTT), dev-dashboard.n-compass.online (AWS), d193aoclwas08l.cloudfront.net (CDN)
- Subnet scanned: 192.168.0.0/24 (64 hosts up, 7+ Raspberry Pi devices)
- Collateral Player found: 192.168.0.161 (MAC: 2c:cf:67:0f:2c:88) with unauthenticated API on port 3215

## Not Found

- Original target at 192.168.0.125 → ARP FAILED (IP changed)
- No MQTT broker on local network (cloud-hosted at pulse.n-compass.online)
- No anonymous access on backend MySQL (3306, 3307)

## Recommended Next

- **Next Phase:** specter-enum
- **Vector:** network (target 192.168.0.130 confirmed as real Player)
- **Reason:** Target IP confirmed, need comprehensive port scan and service enumeration on actual Player device

## Key Data

### Network
- Target IP: 192.168.0.130
- Target MAC: 2c:cf:67:04:0b:d1 (Raspberry Pi Trading)
- Gateway: 192.168.0.1 (TP-Link)
- Attacker IP: 192.168.0.129

### Backend Server
- IP: 192.168.0.103
- Hostname: G8.nctv360.com
- Domain: NCTV360
- OS: Windows 11 (10.0.26100)
- Open ports: 82, 135, 139, 445, 3306, 3307, 3389, 4200, 42052, 5985, 7070, 49153-49671

### Cloud
- MQTT Broker: pulse.n-compass.online (3.239.213.203)
- CDN: d193aoclwas08l.cloudfront.net (public access, no auth)
- Dev Dashboard: dev-dashboard.n-compass.online (AWS CloudFront)

### File Paths
- Engagement data: engagements/player-network/
- Nmap scans: engagements/player-network/recon/nmap-*.txt

## Confidence

- **Overall:** high
- **Network findings:** high
- **Service identification:** high
- **Vulnerability assessment:** medium (not all services deeply enumerated)

## Notes

- Player was locked down on 192.168.0.130 (only port 111 open initially)
- Collateral Player at 192.168.0.161 had full API exposure — documented in engagement-report.md
- VNC on collateral Player was rate-limited after 2 attempts
- Report agent generated final-report.md from engagement data

## Adaptation

- **Pivoted from:** 192.168.0.125 (original IP, unreachable)
- **Pivoted to:** 192.168.0.161 (discovered Player on network)
- **Pivoted to:** 192.168.0.130 (confirmed real Player IP from operator)
- **Reason:** Original target IP was stale; scanned subnet to find actual Player devices
