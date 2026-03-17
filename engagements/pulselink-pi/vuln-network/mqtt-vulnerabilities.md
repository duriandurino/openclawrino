# MQTT Protocol Vulnerability Analysis — PulseLink Infrastructure

**Engagement:** pulselink-pi  
**Phase:** Network Vulnerability Analysis (MQTT Protocol)  
**Date:** 2026-03-17  
**Analyst:** specter-vuln

---

## 1. MQTT Protocol Overview — PulseLink Context

PulseLink uses MQTT v3.1.1 (Eclipse Paho Go client) communicating with broker `pulse.n-compass.online:8883` (MQTTS). The protocol choice is standard for IoT but introduces several inherent security challenges.

### MQTT v3.1.1 vs 5.0 Security Differences

| Feature | MQTT v3.1.1 | MQTT v5.0 | Relevance to PulseLink |
|---------|-------------|-----------|----------------------|
| **Enhanced Authentication** | None (username/password only) | AUTH packet support for challenge-response | PulseLink relies on TLS client certs only — no app-layer auth |
| **Reason Codes** | Limited error info | Detailed reason codes on all packet types | v3.1.1 makes debugging harder, may mask attacks |
| **Session Expiry** | Clean session flag only | Session Expiry Interval (granular control) | v3.1.1 sessions persist indefinitely if not cleaned |
| **Server Disconnect** | Client-initiated only | Server can send DISCONNECT with reason | Blind to why connections drop |
| **Topic Aliases** | Not supported | Reduces bandwidth, complicates logging | Not applicable, but limits monitoring capability |
| **Flow Control** | None | Receive Maximum, topic alias limits | v3.1.1 is vulnerable to unbounded message queues |

**Finding:** PulseLink uses MQTT v3.1.1, which lacks built-in enhanced authentication (AUTH packets), granular session management, and flow control. These are security-relevant features only available in MQTT 5.0.

**Severity:** Medium  
**Impact:** Limited ability to implement sophisticated authentication flows; harder to detect anomalous sessions

---

## 2. Default/Anonymous MQTT Access Risks

### The Problem
MQTT was designed with minimal built-in security. By default, many broker implementations allow:
- Anonymous connections (no authentication required)
- Unrestricted publish/subscribe to all topics
- No access control enforcement

### PulseLink Specific Risk
The PulseLink broker uses TLS client certificate authentication on port 8883, which prevents completely anonymous access. However:

1. **Certificate-based ≠ Authenticated:** If the broker only validates TLS certificate presence (not identity), any device with a valid cert can connect
2. **`client_pi_generic.crt` naming** strongly suggests shared fleet certificates
3. **No application-layer authentication** — no username/password, no OAuth/JWT

### Attack Scenario
```
1. Attacker extracts client_pi_generic.crt + key from one device
2. Attacker connects to pulse.n-compass.online:8883 with valid cert
3. Broker accepts connection (cert is valid)
4. Attacker has same access as any legitimate device
5. No way to distinguish attacker from real device
```

**Severity:** High  
**Impact:** Single credential compromise = full fleet impersonation

---

## 3. MQTT Topic ACL Bypass Techniques

### How Topic ACLs Work (and Fail)
MQTT brokers implement ACLs to restrict which topics clients can publish/subscribe. Common bypass techniques:

#### 3.1 Wildcard Injection (# and +)
The MQTT wildcard characters allow pattern-based subscriptions:
- `#` — multi-level wildcard (matches everything below)
- `+` — single-level wildcard (matches one level)

**Common bypass patterns:**
```
#                → Subscribe to ALL topics (total access)
pulselink/#       → All PulseLink topics
pulselink/+/cmd   → All device command topics
pulselink/devices/+/+ → All device data and commands
```

#### 3.2 CVE-2024-31409 — Unblocked Wildcards
A real-world vulnerability in CyberPower PowerPanel (CISA ICSA-24-123-01) demonstrated that MQTT wildcards not properly blocked can allow attackers with access to any device to extract data from the entire system.

**Relevance to PulseLink:** If the broker doesn't properly restrict wildcard subscriptions, an attacker with one compromised device certificate could subscribe to `#` and capture all fleet communications.

#### 3.3 Topic Enumeration
Without proper ACLs, attackers can enumerate topics by:
1. Subscribing to progressively specific patterns
2. Monitoring retained messages
3. Using `$SYS` broker topics to discover structure

**Severity:** High  
**Impact:** Wildcard access = total fleet visibility; topic enumeration enables targeted attacks

---

## 4. MQTT Message Replay Attacks

### How Replay Attacks Work
MQTT v3.1.1 has **no built-in anti-replay mechanisms**:
- No message timestamps in the protocol
- No nonces or sequence numbers
- Messages can be captured and re-published

### Attack Scenarios for PulseLink

#### 4.1 Content Replay
```
1. Attacker captures legitimate content update message
   Topic: pulselink/devices/RPI-001/content
   Payload: {"url": "https://legit-cdn.com/ad.mp4"}
2. Replays message weeks later
3. Device loads outdated/malicious content
```

#### 4.2 Command Replay
```
1. Attacker captures device management command
   Topic: pulselink/devices/RPI-001/cmd
   Payload: {"action": "reboot"}
2. Replays at a disruptive time (e.g., during a presentation)
```

#### 4.3 QoS 1/2 Amplification
Replayed QoS 1/2 messages trigger broker delivery guarantees, multiplying resource consumption and potential disruption.

**Severity:** Medium  
**Impact:** Stale or malicious commands replayed; content manipulation

---

## 5. QoS Abuse (Message Flooding)

### QoS Levels and Resource Impact
| QoS | Handshake | Resource Cost | DoS Potential |
|-----|-----------|---------------|--------------|
| 0 | None | Minimal | Low |
| 1 | PUBACK | Medium (message storage) | Medium |
| 2 | PUBREC/PUBREL/PUBCOMP | High (4-step handshake) | High |

### Attack Vectors
1. **QoS 2 Flood:** Publishing large volumes of QoS 2 messages forces the broker to maintain state for each message's 4-step handshake
2. **Persistent Session Exploitation:** QoS 1/2 messages queued for disconnected clients with persistent sessions can overwhelm clients on reconnect
3. **Payload DoS:** Oversized payloads combined with high QoS levels maximize resource exhaustion
4. **SlowITe Attack:** Slow DoS that monopolizes broker connections with minimal resources

### PulseLink Impact
- Digital signage requires timely content updates — DoS disrupts display
- Single broker = single point of failure for entire fleet
- Resource-constrained Raspberry Pi devices are vulnerable to message bursts

**Severity:** Medium  
**Impact:** Display disruption, broker overload, device unresponsiveness

---

## 6. Summary of Protocol Vulnerabilities

| # | Vulnerability | Severity | CVE Reference |
|---|--------------|----------|---------------|
| 1 | MQTT v3.1.1 lacks enhanced auth features | Medium | N/A (protocol limitation) |
| 2 | Shared certificate = no device uniqueness | High | N/A (architecture) |
| 3 | Wildcard subscription ACL bypass | High | CVE-2024-31409 |
| 4 | Message replay (no anti-replay in v3.1.1) | Medium | N/A (protocol limitation) |
| 5 | QoS abuse for DoS | Medium | N/A (protocol limitation) |
| 6 | Topic enumeration | Medium | N/A (misconfiguration) |

---

## Recommendations

1. **Implement application-layer message signing** to prevent replay attacks
2. **Enforce strict ACL policies** — block `#` wildcard subscriptions for devices
3. **Add per-device authentication** (username/password or unique certs) on top of TLS
4. **Implement rate limiting** on the broker to prevent QoS abuse
5. **Consider migrating to MQTT 5.0** for enhanced authentication and flow control
6. **Use message timestamps and nonces** in payloads for replay detection
