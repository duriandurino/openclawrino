# Network Vulnerability Analysis — Executive Summary

**Engagement:** pulselink-pi  
**Phase:** Network Vulnerability Analysis  
**Date:** 2026-03-17  
**Analyst:** specter-vuln  
**Target:** PulseLink MQTT Infrastructure (pulse.n-compass.online:8883)

---

## Executive Overview

The PulseLink digital signage infrastructure relies on MQTT (v3.1.1) over TLS for fleet communication between a central broker and Raspberry Pi 5 devices running an Electron + Go application. This analysis identified **14 vulnerabilities** across 5 categories, with **3 rated Critical**, **6 rated High**, and **5 rated Medium**.

The most significant finding is the use of a **shared "generic" client certificate** (`client_pi_generic.crt`) across the entire device fleet. This single credential creates a catastrophic blast radius — compromise of any single device grants full fleet access.

---

## Risk Heat Map

| Category | Critical | High | Medium | Total |
|----------|----------|------|--------|-------|
| **Fleet/Certificate** | 2 | 3 | 0 | 5 |
| **Protocol** | 0 | 2 | 3 | 5 |
| **Architecture** | 1 | 1 | 0 | 2 |
| **TLS** | 0 | 0 | 1 | 1 |
| **Application (Chromium/Electron)** | 0 | 0 | 1 | 1 |
| **Total** | **3** | **6** | **5** | **14** |

---

## Critical Findings (Immediate Action Required)

### CRIT-01: Shared Fleet Certificate — client_pi_generic.crt
- **Category:** Fleet/Certificate
- **CVSS (Est.):** 9.1
- **Description:** A single X.509 certificate (`client_pi_generic.crt`) is shared across all PulseLink devices. The "generic" naming convention strongly indicates fleet-wide certificate reuse.
- **Impact:** One device compromise = full fleet impersonation. Attacker can publish malicious content, subscribe to all device topics, and control the entire digital signage network.
- **Evidence:** Certificate file found at `/opt/pulselink/client_certs/client_pi_generic.crt`
- **Recommendation:** Issue unique X.509 certificates per device immediately. Implement hardware-backed key storage (TPM).

### CRIT-02: Content Injection via MQTT
- **Category:** Architecture
- **CVSS (Est.):** 9.3
- **Description:** MQTT-based content delivery with no message signing or content validation allows attackers with broker access to inject arbitrary content onto all public displays.
- **Impact:** Display of inappropriate/inflammatory content on public screens, reputational damage, legal liability.
- **Attack Path:** Extract shared cert → publish to content topics → all screens display attacker content
- **Recommendation:** Implement HMAC/JWT message signing on all content messages. Validate content URLs against whitelist. Add content integrity verification.

### CRIT-03: Chromium Zero-Day Vulnerabilities
- **Category:** Application
- **CVSS (Est.):** 8.8
- **Description:** Chromium 134.0.6998.179 (used in PulseLink Electron app) has multiple known CVEs including CVE-2025-2783 (zero-day, actively exploited), CVE-2025-10585 (CISA KEV), and CVE-2025-2136.
- **Impact:** Remote code execution via malicious web content. Attacker gains code execution within the Electron process, enabling full MQTT compromise.
- **Recommendation:** Update Electron to latest stable version with patched Chromium. Monitor for CVE-2026-2441, CVE-2026-3909, CVE-2026-3910.

---

## High Findings (Address Within 30 Days)

### HIGH-01: No Certificate Pinning
- **Description:** MQTT client does not pin the broker's certificate, enabling MITM attacks via DNS hijacking, BGP hijacking, or compromised CAs.
- **Recommendation:** Implement certificate pinning in the Paho MQTT client.

### HIGH-02: Wildcard Topic ACL Bypass (CVE-2024-31409 Pattern)
- **Description:** MQTT wildcard subscriptions (#, +) may not be properly restricted, allowing compromised devices to subscribe to all fleet topics. Mirrors CVE-2024-31409 in CyberPower PowerPanel.
- **Recommendation:** Restrict wildcard subscriptions at broker level. Each device should only access its own topics.

### HIGH-03: Message Replay Attacks
- **Description:** MQTT v3.1.1 has no built-in anti-replay mechanisms. Content updates and device commands can be captured and replayed indefinitely.
- **Recommendation:** Implement application-layer timestamps and message nonces. Consider MQTT 5.0 migration.

### HIGH-04: Retained Message Poisoning
- **Description:** MQTT retained messages persist on the broker. Attacker can poison retained messages to affect new devices connecting to the broker.
- **Recommendation:** Restrict publish access to retained messages. Validate retained message sources.

### HIGH-05: Broker Impersonation (No MitM Protection)
- **Description:** Without certificate pinning, attacker can set up rogue broker with valid certificate and redirect traffic via DNS/BGP hijack.
- **Recommendation:** Certificate pinning + monitoring for DNS changes.

### HIGH-06: Certificate Rotation / Revocation Gap
- **Description:** Shared certificate cannot be revoked without affecting all legitimate devices. No evidence of automated certificate rotation.
- **Recommendation:** Implement per-device certs with CRL/OCSP and automated 90-day rotation.

---

## Medium Findings (Address Within 90 Days)

### MED-01: MQTT v3.1.1 Protocol Limitations
- Missing enhanced authentication (AUTH packets), session expiry control, and flow control available in MQTT 5.0.

### MED-02: QoS Abuse Potential
- Attackers can flood broker with QoS 1/2 messages, exhausting resources and causing DoS to digital signage fleet.

### MED-03: $SYS Topic Enumeration
- Broker may expose version, uptime, client count via $SYS topics without authentication, enabling fingerprinting.

### MED-04: TLS 1.2 Cipher Suite Risks
- Unknown whether broker enforces TLS 1.3 minimum or disables weak TLS 1.2 cipher suites (RC4, 3DES, MD5).

### MED-05: CVE-2025-10543 (paho.mqtt.golang ≤ 1.5.0)
- Integer overflow causes information disclosure. Topic data leaks into message bodies. Fixed in 1.5.1. Must verify current version in PulseLink.

---

## Prioritized Remediation Roadmap

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| **P0 (This Week)** | Issue unique certificates per device | Medium | Eliminates CRIT-01 |
| **P0 (This Week)** | Restrict MQTT topic ACLs (no wildcards) | Low | Mitigates HIGH-02 |
| **P1 (2 Weeks)** | Update Electron/Chromium to patched version | Low | Eliminates CRIT-03 |
| **P1 (2 Weeks)** | Implement message signing for content | Medium | Mitigates CRIT-02 |
| **P1 (2 Weeks)** | Verify/update paho.mqtt.golang ≥ 1.5.1 | Low | Eliminates MED-05 |
| **P2 (1 Month)** | Implement certificate pinning | Medium | Eliminates HIGH-01, HIGH-05 |
| **P2 (1 Month)** | Add anti-replay (timestamps/nonces) | Medium | Mitigates HIGH-03 |
| **P2 (1 Month)** | Implement certificate rotation policy | High | Eliminates HIGH-06 |
| **P3 (Quarter)** | Evaluate MQTT 5.0 migration | High | Addresses MED-01 |
| **P3 (Quarter)** | Deploy broker rate limiting | Medium | Mitigates MED-02 |

---

## Vulnerability Summary Table

| # | ID | Title | Category | Severity | CVSS |
|---|-----|-------|----------|----------|------|
| 1 | CRIT-01 | Shared Fleet Certificate | Fleet | Critical | 9.1 |
| 2 | CRIT-02 | Content Injection via MQTT | Architecture | Critical | 9.3 |
| 3 | CRIT-03 | Chromium Zero-Days | Application | Critical | 8.8 |
| 4 | HIGH-01 | No Certificate Pinning | TLS | High | 7.4 |
| 5 | HIGH-02 | Wildcard ACL Bypass | Protocol | High | 7.8 |
| 6 | HIGH-03 | Message Replay Attacks | Protocol | High | 6.5 |
| 7 | HIGH-04 | Retained Message Poisoning | Protocol | High | 7.2 |
| 8 | HIGH-05 | Broker Impersonation | Architecture | High | 7.4 |
| 9 | HIGH-06 | No Certificate Revocation | Fleet | High | 7.8 |
| 10 | MED-01 | MQTT v3.1.1 Limitations | Protocol | Medium | 5.3 |
| 11 | MED-02 | QoS Abuse (DoS) | Protocol | Medium | 5.9 |
| 12 | MED-03 | $SYS Topic Enumeration | TLS | Medium | 4.3 |
| 13 | MED-04 | TLS 1.2 Cipher Risks | TLS | Medium | 5.9 |
| 14 | MED-05 | CVE-2025-10543 (Paho) | Application | Medium | 6.3 |

---

## Conclusion

The PulseLink infrastructure's most critical weakness is its **shared certificate model**. This single architectural decision amplifies every other vulnerability from device-level to fleet-level impact. Combined with the lack of message signing and content validation, an attacker with access to a single device certificate has effective control over the entire digital signage network.

The Electron/Chromium stack adds a significant attack surface with multiple known zero-days. Regular patching of the Electron framework is essential.

**Overall Security Posture:** **HIGH RISK** — Immediate remediation required for critical certificate and content integrity issues.

---

## Files Produced

| File | Description |
|------|-------------|
| `mqtt-vulnerabilities.md` | MQTT protocol vulnerabilities (v3.1.1 weaknesses, wildcard injection, replay, QoS abuse) |
| `tls-analysis.md` | TLS configuration analysis (shared certs, pinning, TLS 1.2/1.3, certificate lifecycle) |
| `paho-cve-research.md` | Eclipse Paho library CVEs (CVE-2025-10543) and Electron/Chromium vulnerabilities |
| `digital-signage-risks.md` | Architecture-level risks (content injection, topic hijacking, broker impersonation, fleet attacks) |
| `vuln-network-summary.md` | This executive summary with prioritized remediation roadmap |

---

*Generated by specter-vuln | 2026-03-17 | Research-based vulnerability analysis (no active exploitation)*
