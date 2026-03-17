# Network Enumeration Summary
## PulseLink Pi — Executive Summary

**Engagement:** pulselink-pi
**Phase:** Network Enumeration (enum-network)
**Target:** 192.168.0.125 (Raspberry Pi 5)
**Broker:** pulse.n-compass.online:8883 (TLS)
**Date:** 2026-03-17

---

## Overview

This phase shifts from physical access attacks to **network-based enumeration** of the PulseLink Pi and its MQTT broker infrastructure. The approach focuses on traffic analysis, protocol enumeration, and TLS inspection to discover attack surface without requiring physical device access.

## Attack Vectors Identified

### 1. MQTT Broker Communication (HIGH priority)
- **Target:** pulse.n-compass.online:8883
- **Protocol:** MQTT over TLS with mutual authentication (mTLS)
- **Key finding:** Client certificates stored on Pi at `/opt/pulselink/client_certs/`
- **Risk:** Certificate name `client_pi_generic.crt` suggests shared certs across devices
- **Attack path:** Extract certs via SSH → impersonate any PulseLink device on broker

### 2. Network Traffic Interception (MEDIUM priority)
- **Method:** Packet capture on LAN (tcpdump/Wireshark)
- **Limitation:** MQTT traffic is TLS-encrypted (port 8883)
- **What's visible:** Connection patterns, timing, packet sizes, DNS queries
- **Useful for:** Identifying communication frequency, content update patterns

### 3. Service Enumeration (MEDIUM priority)
- **Known:** SSH (22), RPCBind (111)
- **Unknown:** Web interfaces, VNC, additional services
- **Action:** Full port scan to map complete attack surface

### 4. Certificate-Based Attacks (HIGH priority)
- If PulseLink uses the same CA and client cert across all devices, one compromised device = full fleet access
- Certificate chain analysis can reveal broker infrastructure details

## Enumeration Deliverables

| File | Contents |
|------|----------|
| `tcpdump-guide.md` | Complete tcpdump commands for MQTT traffic capture and analysis |
| `mqtt-enumeration.md` | MQTT protocol enumeration, topic discovery, authentication testing |
| `tls-analysis.md` | TLS certificate extraction, inspection, and security analysis |
| `network-discovery.md` | nmap scanning, mDNS discovery, RPC enumeration, service fingerprinting |
| `enum-network-summary.md` | This file — executive summary and attack path analysis |

## Recommended Execution Order

### Phase A: Passive Discovery (no packets sent)
1. Run `nmap -sn 192.168.0.0/24` to confirm Pi is online
2. Run `avahi-browse -a -t` for mDNS service discovery
3. Run `arp-scan --localnet` to confirm Pi MAC address

### Phase B: Active Port Scanning
1. Run full port scan: `nmap -p- --min-rate 1000 192.168.0.125`
2. Run service detection on open ports
3. Run NSE scripts on discovered services

### Phase C: Traffic Capture
1. Start tcpdump capture on port 8883
2. Let it run for 5-10 minutes to capture connection patterns
3. Analyze capture for metadata (not decrypted content)

### Phase D: TLS & Certificate Analysis
1. SSH into Pi to extract client certificates
2. Analyze cert chain, validity, key reuse
3. Test broker TLS configuration with `openssl s_client`

### Phase E: MQTT Protocol Testing
1. Attempt connection with extracted certificates
2. Enumerate topics via wildcard subscriptions
3. Test publish permissions (read vs read-write)

## Key Intelligence Questions

| Question | How to Answer |
|----------|---------------|
| What services is the Pi running? | nmap full port scan |
| Is MQTT the only communication channel? | Check for HTTP, raw TCP, other protocols |
| Are client certs shared across devices? | Compare cert serial numbers |
| What topics does the device subscribe to? | MQTT topic enumeration |
| Can we inject commands via MQTT? | Test publish to command topics |
| What data does the Pi send to the broker? | Analyze PUBLISH packet topics and payloads |

## Risk Assessment

| Vector | Risk Level | Effort | Notes |
|--------|-----------|--------|-------|
| Extract certs via SSH | **CRITICAL** | Low | Certs stored in plaintext on filesystem |
| MQTT topic enumeration | **HIGH** | Low | Wildcard subscription may be allowed |
| MQTT command injection | **HIGH** | Medium | If publish permissions granted |
| Traffic interception | **MEDIUM** | Low | TLS limits usefulness |
| Service exploitation | **MEDIUM** | Medium | Depends on open ports found |
| Certificate reuse attack | **CRITICAL** | Medium | If same cert used across fleet |

## Tools Required

```bash
# Install if not present
sudo apt install nmap tcpdump wireshark tshark mosquitto-clients arp-scan avahi-utils -y

# Optional: MQTT security testing
pip install mqtt-pwn
```

## Next Steps After Enumeration

1. **If new ports found** → Pass to `specter-vuln` for vulnerability analysis
2. **If MQTT topics discovered** → Research topic-specific attacks
3. **If cert reuse confirmed** → Investigate fleet-wide compromise potential
4. **If web interface found** → Directory brute-force and web app testing
5. **If credentials found** → Pass to `specter-exploit` for exploitation

---

**Status:** Documentation complete — awaiting user execution of commands
**Prepared by:** specter-enum
**Engagement path:** `engagements/pulselink-pi/enum-network/`
