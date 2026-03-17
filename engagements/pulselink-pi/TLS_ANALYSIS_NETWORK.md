# TLS Configuration Analysis — PulseLink MQTT Infrastructure

**Engagement:** pulselink-pi  
**Phase:** Network Vulnerability Analysis (TLS/Certificate)  
**Date:** 2026-03-17  
**Analyst:** specter-vuln

---

## 1. Current TLS Configuration

### Target Details
- **Broker:** pulse.n-compass.online:8883
- **Protocol:** MQTTS (MQTT over TLS)
- **Client Certs Location:** /opt/pulselink/client_certs/
- **Client Certificate:** client_pi_generic.crt
- **CA Certificate:** Present in client_certs directory
- **Client Key:** Present in client_certs directory

### TLS Handshake Analysis (Research-Based)

Without active probing, the following analysis is based on common MQTT TLS configurations and best practices:

**Likely Configuration:**
- TLS 1.2 support (broadest IoT compatibility)
- Possible TLS 1.3 support (depends on broker software)
- Client certificate authentication (mTLS)
- CA-signed server certificate

---

## 2. Shared Certificate Risk — "generic" Certificate Analysis

### Critical Finding: client_pi_generic.crt

The certificate filename `client_pi_generic.crt` is a **significant red flag**:

### What "Generic" Implies
1. **Shared Identity:** One certificate used across multiple (possibly all) devices in the fleet
2. **No Device Individuality:** No way to distinguish one device from another at the TLS layer
3. **Blast Radius:** One compromised device = compromised entire fleet

### Risk Assessment

| Risk | Description | Severity |
|------|-------------|----------|
| **Fleet-Wide Compromise** | Extract cert from one device → impersonate any device | **Critical** |
| **No Individual Revocation** | Cannot revoke a single device without affecting all | **High** |
| **No Audit Trail** | Cannot attribute actions to specific devices | **High** |
| **Firmware Extraction** | Cert accessible from any device's filesystem | **High** |
| **Certificate Reuse** | Attacker uses extracted cert on non-PulseLink devices | **Medium** |

### Attack Chain
```
1. Physical or remote access to ANY PulseLink device
2. Extract /opt/pulselink/client_certs/client_pi_generic.crt + .key
3. Install on attacker-controlled device
4. Connect to pulse.n-compass.online:8883
5. Broker cannot distinguish from legitimate device
6. Publish malicious content, subscribe to all topics, control fleet
```

### Industry Best Practice Comparison
| Practice | PulseLink | Recommended |
|----------|-----------|-------------|
| Unique cert per device | ❌ Generic/shared | ✅ Unique X.509 per device |
| Hardware key storage (HSM/TPM) | ❌ Filesystem | ✅ TPM or HSM |
| Certificate rotation | ❓ Unknown | ✅ 1-2 year rotation |
| Certificate revocation (CRL/OCSP) | ❓ Unknown | ✅ CRL + OCSP |
| Device attestation | ❌ None | ✅ Device identity verification |

**Severity:** Critical  
**Recommendation:** Issue unique X.509 certificates per device with hardware-backed key storage

---

## 3. Certificate Expiration and Rotation Risks

### Common Issues
1. **Expired Certificates:** If certs expire, all devices lose connectivity simultaneously
2. **No Rotation Policy:** Long-lived certificates increase exposure window
3. **Manual Rotation:** At fleet scale, manual cert rotation is error-prone and slow
4. **No CRL/OCSP:** Without revocation infrastructure, compromised certs remain valid until expiration

### PulseLink Risks
- Generic certificate means ALL devices share the same expiration date
- Certificate expiration = fleet-wide outage
- If certificate is compromised mid-lifecycle, no way to revoke without affecting legitimate devices

### Detection Without Authentication
During TLS handshake, the server certificate is presented in plaintext:
```bash
# Passive detection — no authentication needed
openssl s_client -connect pulse.n-compass.online:8883 </dev/null 2>/dev/null | openssl x509 -noout -dates -subject -issuer
```

This reveals:
- Certificate validity period (notAfter)
- Issuing CA
- Subject information
- Whether certificate is near expiration

**Severity:** High  
**Recommendation:** Implement automated certificate rotation with unique per-device certs

---

## 4. TLS 1.2 vs 1.3 — Configuration Concerns

### TLS 1.2 Weaknesses in MQTT Context

| Weakness | Description | Impact |
|----------|-------------|--------|
| **Weak Cipher Suites** | Supports RC4, 3DES, MD5, SHA1 | Downgrade attacks, weak encryption |
| **No Mandatory PFS** | Static RSA key exchange possible | Past sessions decryptable if private key compromised |
| **Plaintext Handshake** | Initial handshake exposes negotiation details | Broker fingerprinting |
| **CBC Vulnerabilities** | BEAST, Lucky 13 attacks | Information disclosure |
| **Downgrade Attacks** | Can be forced to SSLv3/TLS 1.0 | Exploitation of old vulnerabilities |

### TLS 1.3 Improvements
| Feature | TLS 1.2 | TLS 1.3 |
|---------|---------|---------|
| Cipher suites | Many (including weak) | 5 strong AEAD ciphers only |
| Forward secrecy | Optional | Mandatory (ECDHE) |
| Handshake encryption | Partial | Most handshake encrypted |
| Downgrade protection | Weak | Strong |
| Vulnerable features | RSA transport, compression | Removed entirely |

### IoT Context Concern
Many IoT devices and MQTT brokers still default to TLS 1.2 due to:
- Hardware limitations (older chipsets)
- Library support (embedded MQTT clients)
- Configuration inertia

**If PulseLink broker uses only TLS 1.2:** Vulnerable to downgrade and cipher suite attacks  
**If PulseLink broker supports both:** Must ensure TLS 1.3 is preferred and weak TLS 1.2 ciphers are disabled

**Severity:** Medium  
**Recommendation:** Enforce TLS 1.3 minimum; disable all weak TLS 1.2 cipher suites

---

## 5. Certificate Pinning Weaknesses

### The Problem
Certificate pinning requires the client to verify the server's certificate against a known good value (pin). Without pinning:

1. **MITM Potential:** If an attacker can position themselves in the network path (DNS hijacking, BGP hijacking, rogue CA), they can present a valid but fraudulent certificate
2. **Trust Chain Attacks:** Compromised or malicious CAs can issue valid certificates for `pulse.n-compass.online`
3. **No Verification Beyond Chain:** Client only verifies the cert chain, not that it's THE expected certificate

### PulseLink Assessment
- **No evidence of certificate pinning** in the Eclipse Paho Go client by default
- The client likely trusts any certificate signed by the configured CA
- If the CA cert in `/opt/pulselink/client_certs/` is the only trust anchor, compromising it = MITM capability

### Without Pinning
```
Attacker with network position:
1. BGP/DNS hijack → pulse.n-compass.online resolves to attacker
2. Present valid cert signed by any trusted CA
3. Client accepts (no pinning)
4. Full MITM on all MQTT traffic
```

### With Pinning
```
1. Client verifies server cert hash against known pin
2. Attacker's cert doesn't match pin
3. Connection refused
4. Attack detected
```

**Severity:** High  
**Recommendation:** Implement certificate pinning in the Paho MQTT client configuration

---

## 6. Detecting Broker TLS Configuration (Unauthenticated)

### Passive Reconnaissance Techniques

#### 6.1 TLS Version and Cipher Detection
```bash
# Check TLS version support
nmap --script ssl-enum-ciphers -p 8883 pulse.n-compass.online

# Test specific TLS versions
openssl s_client -connect pulse.n-compass.online:8883 -tls1_2
openssl s_client -connect pulse.n-compass.online:8883 -tls1_3

# Cipher suite enumeration
testssl --port 8883 pulse.n-compass.online
```

#### 6.2 Certificate Information (No Auth Required)
```bash
# Full certificate chain
openssl s_client -connect pulse.n-compass.online:8883 -showcerts </dev/null

# Key details
openssl s_client -connect pulse.n-compass.online:8883 </dev/null 2>/dev/null | \
  openssl x509 -noout -text | grep -E "Subject:|Issuer:|Not After|Public-Key|Signature Algorithm"
```

#### 6.3 Shodan/Internet-Wide Search
```
# Find exposed MQTT brokers
ssl.cert.subject.CN:"pulse.n-compass.online" port:8883
```

**Severity:** Informational  
**Recommendation:** These techniques should be used during the enumeration phase with proper authorization

---

## 7. Summary of TLS Vulnerabilities

| # | Vulnerability | Severity | CVSS (Est.) |
|---|--------------|----------|-------------|
| 1 | Shared fleet certificate (client_pi_generic.crt) | Critical | 9.1 |
| 2 | No certificate pinning | High | 7.4 |
| 3 | Unknown certificate rotation policy | High | 7.5 |
| 4 | Unknown TLS version enforcement | Medium | 5.9 |
| 5 | Certificate expiration risk (fleet-wide) | High | 7.2 |
| 6 | No per-device certificate revocation | High | 7.8 |

---

## Recommendations (Prioritized)

1. **CRITICAL:** Issue unique X.509 certificates per device with unique private keys
2. **HIGH:** Implement certificate pinning in MQTT client
3. **HIGH:** Establish certificate rotation policy (90-day or 1-year)
4. **HIGH:** Implement CRL or OCSP for certificate revocation
5. **MEDIUM:** Enforce TLS 1.3 minimum; disable weak TLS 1.2 ciphers
6. **MEDIUM:** Store private keys in hardware security (TPM) where possible
7. **LOW:** Implement certificate transparency monitoring
