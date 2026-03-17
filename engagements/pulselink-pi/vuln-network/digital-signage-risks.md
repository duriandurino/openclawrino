# Digital Signage MQTT Architecture Risks — PulseLink

**Engagement:** pulselink-pi  
**Phase:** Network Vulnerability Analysis (Architecture)  
**Date:** 2026-03-17  
**Analyst:** specter-vuln

---

## 1. Architecture Overview

### PulseLink System Components
```
                    ┌─────────────────────┐
                    │  MQTT Broker         │
                    │  pulse.n-compass.online │
                    │  Port 8883 (MQTTS)  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼───────┐ ┌─────▼────────┐ ┌─────▼────────┐
     │ Pi Device #1   │ │ Pi Device #2 │ │ Pi Device #N │
     │ Electron App   │ │ Electron App │ │ Electron App │
     │ Go MQTT Client │ │ Go MQTT Client │ Go MQTT Client │
     │ Chromium 134   │ │ Chromium 134 │ │ Chromium 134 │
     │ Digital Display│ │ Digital Display│ │ Digital Display│
     └────────────────┘ └──────────────┘ └──────────────┘
```

### Key Architectural Observations
1. **Centralized Broker:** Single MQTT broker serves entire fleet
2. **Pub/Sub Model:** Content and commands delivered via MQTT topics
3. **Electron + Go:** Hybrid app with Chromium rendering and Go networking
4. **TLS Termination:** Broker handles TLS on port 8883
5. **Fleet Management:** MQTT topics likely used for device management and content delivery

---

## 2. Content Injection via MQTT

### Attack Scenario: Malicious Content Display

The most impactful attack against a digital signage system is **content injection** — displaying unauthorized content on public screens.

#### Attack Vector
```
1. Attacker obtains valid MQTT credentials (via shared cert extraction)
2. Attacker publishes to content delivery topic:
   
   Topic: pulselink/devices/{device-id}/content/update
   Payload: {
     "type": "video",
     "url": "https://attacker.com/malicious.mp4",
     "duration": 300,
     "priority": "high"
   }

3. Device receives message, downloads and displays malicious content
4. Public display shows attacker's content
```

#### Impact
- **Reputation damage** — inappropriate/inflammatory content on public displays
- **Social engineering** — fake emergency alerts, phishing URLs
- **Financial harm** — advertising competitor content
- **Legal liability** — content displayed on behalf of the venue owner

#### Amplification Factors
- If using `#` wildcard subscription on content topics → attacker can target all devices simultaneously
- If no content validation on device → any URL/executable content accepted
- If no message signing → replay attacks with old malicious content

**Severity:** Critical

---

## 3. MQTT Topic Hijacking in IoT Fleets

### Topic Structure Discovery

Without seeing the actual topic structure, typical PulseLink topics likely include:

```
pulselink/devices/{device-id}/status          # Device heartbeat
pulselink/devices/{device-id}/content         # Content metadata
pulselink/devices/{device-id}/content/data    # Content binary data
pulselink/devices/{device-id}/cmd             # Device commands
pulselink/devices/{device-id}/config          # Device configuration
pulselink/devices/{device-id}/logs            # Log uploads
pulselink/fleet/broadcast                     # Fleet-wide messages
pulselink/fleet/commands                      # Fleet-wide commands
```

### Hijacking Techniques

#### 3.1 Wildcard Topic Subscription
```python
# Subscribe to everything
client.subscribe("pulselink/#")

# Subscribe to all device commands
client.subscribe("pulselink/devices/+/cmd")

# Subscribe to all content
client.subscribe("pulselink/devices/+/content/#")
```

#### 3.2 Retained Message Poisoning
MQTT retained messages persist on the broker and are delivered to new subscribers. An attacker can:
```
1. Publish malicious retained message to pulselink/devices/+/config
2. New devices connecting will receive poisoned configuration
3. Retained message persists until explicitly cleared
```

#### 3.3 Last Will and Testament (LWT) Abuse
If the broker allows arbitrary LWT topics:
```
1. Connect with LWT topic: pulselink/devices/other-device/status
2. LWT payload: {"status": "compromised", "battery": 0}
3. When attacker disconnects, false status sent for another device
```

**Severity:** High

---

## 4. Broker Impersonation Attacks

### Scenario: Rogue MQTT Broker

An attacker can set up a rogue MQTT broker that appears legitimate:

```
1. Register similar domain: pulse-n-compass.online (vs pulse.n-compass.online)
   or: pulsencompass.online
2. Obtain TLS certificate (free via Let's Encrypt)
3. Configure MQTT broker on port 8883
4. Exploit DNS hijacking or BGP hijacking to redirect traffic
5. Devices connect to rogue broker (cert is valid for rogue domain)
6. Full interception and manipulation of all MQTT traffic
```

### Why This Works (Without Certificate Pinning)
1. Client validates that the certificate is for the connected hostname
2. Attacker's certificate IS valid for the rogue hostname
3. Client trusts any certificate signed by a trusted CA
4. No mechanism to verify "this is THE correct server"

### PulseLink-Specific Risk
- DNS hijacking of `pulse.n-compass.online` → all devices connect to rogue broker
- No certificate pinning means the rogue broker's valid cert is accepted
- Attacker can serve fake content, steal device configurations, inject commands

**Severity:** High

---

## 5. Man-in-the-Middle on MQTT with TLS

### TLS Does Not Equal Security

Even with TLS 1.2/1.3, several MITM scenarios exist:

#### 5.1 CA Compromise
```
If attacker compromises the CA that signed the broker's certificate:
1. Issue fraudulent certificate for pulse.n-compass.online
2. Intercept MQTT traffic (BGP/DNS hijack)
3. Present valid fraudulent certificate
4. Client accepts (chain of trust intact)
```

#### 5.2 Device-Level MITM
If attacker has physical access to a Pi:
```
1. Replace CA certificate in /opt/pulselink/client_certs/ with attacker's CA
2. Intercept traffic between device and broker
3. Present attacker-signed certificates that device trusts
```

#### 5.3 Shared Certificate Amplification
Because all devices use the same certificate:
```
1. MITM one device → capture traffic
2. Use captured credentials to impersonate ANY device
3. Lateral movement across entire fleet with single compromise
```

**Severity:** High

---

## 6. MQTT Broker Enumeration and Fingerprinting

### Unauthenticated Broker Identification

#### 6.1 $SYS Topic Enumeration
Many MQTT brokers expose `$SYS` topics that reveal:
```bash
# Using mosquitto_sub (if anonymous access allowed)
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt -t '$SYS/broker/version' -v

mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt -t '$SYS/broker/uptime' -v

mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt -t '$SYS/broker/clients/total' -v
```

Common `$SYS` topics:
- `$SYS/broker/version` → Mosquitto 2.0.15, EMQX 5.3.0, etc.
- `$SYS/broker/uptime` → How long broker has been running
- `$SYS/broker/clients/connected` → Number of active devices
- `$SYS/broker/messages/received` → Total message count
- `$SYS/broker/load/bytes/received` → Traffic statistics

#### 6.2 TLS Fingerprinting
```
# Certificate subject reveals broker software hints
openssl s_client -connect pulse.n-compass.online:8883 </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -issuer

# Cipher suite order identifies TLS implementation
testssl --port 8883 pulse.n-compass.online
```

#### 6.3 Protocol Behavior Fingerprinting
Different brokers handle edge cases differently:
- **Mosquitto:** Default `$SYS` enabled, specific error messages
- **EMQX:** Different `$SYS` structure, WebSocket support patterns
- **HiveMQ:** Enterprise-oriented responses, clustering indicators
- **ActiveMQ:** Different CONNACK patterns, Java stack traces on errors

#### 6.4 Shodan/Censys Discovery
```
# Shodan queries for MQTT brokers
ssl:"pulse.n-compass.online" port:8883
```

If PulseLink broker is internet-facing, it may be indexed by internet-wide scanners.

**Severity:** Medium  
**Recommendation:** Disable `$SYS` topics or require authentication; restrict broker version disclosure

---

## 7. Fleet-Wide Attack Scenarios

### Scenario 1: Mass Content Defacement
```
1. Extract shared certificate from one Pi
2. Connect to broker
3. Subscribe to pulselink/devices/+/content
4. Publish malicious content to ALL devices simultaneously
5. Every screen in the fleet displays attacker content
```

### Scenario 2: Fleet Surveillance
```
1. Subscribe to pulselink/devices/+/status (all device status)
2. Subscribe to pulselink/devices/+/logs (all device logs)
3. Map entire fleet: device IDs, locations, capabilities
4. Use information for targeted physical attacks
```

### Scenario 3: Persistent Access via Retained Messages
```
1. Publish retained configuration change to device config topic
2. Change persists on broker even after attacker disconnects
3. Next device restart loads poisoned configuration
4. Long-term persistence without maintaining connection
```

### Scenario 4: Supply Chain Attack via OTA
```
If MQTT is used for firmware updates:
1. Intercept firmware update topic
2. Publish malicious firmware URL
3. Device downloads and installs backdoored firmware
4. Backdoor persists across reboots
```

---

## 8. Architecture Risk Summary

| Risk | Category | Severity | Attack Complexity |
|------|----------|----------|-------------------|
| Content injection via MQTT | Application | Critical | Low (with cert) |
| Wildcard topic subscription | Protocol | High | Low |
| Retained message poisoning | Protocol | High | Low |
| Broker impersonation (MITM) | TLS | High | Medium |
| $SYS topic enumeration | Broker | Medium | None (if open) |
| Fleet-wide content defacement | Architecture | Critical | Low |
| Persistent access via retained msgs | Protocol | High | Low |
| Device surveillance | Architecture | Medium | Low |
| Supply chain (OTA hijack) | Application | Critical | Medium |

---

## 9. Recommendations

### Immediate
1. **Restrict MQTT topic ACLs** — devices should only access their own topics
2. **Disable wildcard subscriptions** for device-level clients
3. **Implement message signing** — HMAC or JWT signatures on all content messages
4. **Validate content URLs** — reject non-whitelisted domains on device

### Short-Term
5. **Implement certificate pinning** to prevent broker impersonation
6. **Disable `$SYS` topics** or require authentication
7. **Add per-device authentication** layer on top of TLS
8. **Implement message timestamps** to prevent replay

### Long-Term
9. **Unique certificates per device** with hardware-backed storage
10. **Broker clustering/high availability** — eliminate single point of failure
11. **Network segmentation** — isolate MQTT traffic from general network
12. **Content integrity verification** — hash/签名 verification of all content
13. **Consider MQTT 5.0 migration** for enhanced security features
