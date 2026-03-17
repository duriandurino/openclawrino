# Eclipse Paho MQTT Library CVE Research

**Engagement:** pulselink-pi  
**Phase:** Network Vulnerability Analysis (Library CVEs)  
**Date:** 2026-03-17  
**Analyst:** specter-vuln

---

## 1. Eclipse Paho MQTT Go Client Library

### Library Details
- **Repository:** https://github.com/eclipse-paho/paho.mqtt.golang (now under eclipse-paho org)
- **Protocol:** MQTT v3.1/3.1.1 (v5 client separate: eclipse/paho.golang)
- **Dependencies:** gorilla/websocket, golang.org/x/net/proxy
- **Use in PulseLink:** Go MQTT client for Raspberry Pi fleet communication

---

## 2. Known CVEs in Eclipse Paho MQTT Go Client

### CVE-2025-10543 — Integer Overflow / Information Disclosure

| Field | Detail |
|-------|--------|
| **CVE ID** | CVE-2025-10543 |
| **CVSS 4.0** | 6.3 (Medium) |
| **CWE** | CWE-197 (Integer Overflow) |
| **Affected Versions** | paho.mqtt.golang ≤ 1.5.0 |
| **Fixed In** | Version 1.5.1 |
| **Authentication Required** | No |

**Description:**  
When UTF-8 encoded strings exceeding 65,535 bytes are passed into the library, an unsafe integer conversion causes the length field to be truncated while the full data is still written. This results in:

1. **Information Disclosure:** MQTT topic data may leak into PUBLISH packet message body content
2. **Malformed Packets:** Incorrect encoding causes unexpected behavior in brokers and other clients
3. **Data Integrity Issues:** Message content becomes intermixed with topic data
4. **No Authentication Required:** Any client sending oversized strings triggers the vulnerability

**Impact on PulseLink:**
- If PulseLink uses paho.mqtt.golang ≤ 1.5.0, content displayed on digital signage could be corrupted
- Topic data leakage could expose internal device addressing scheme
- Malformed packets could cause broker-side issues affecting entire fleet

**Mitigation:**
- Upgrade to paho.mqtt.golang 1.5.1 or later
- Implement input validation rejecting UTF-8 strings > 65,535 bytes
- Monitor MQTT traffic for signs of packet corruption

### GitHub Security Advisories
The Eclipse Paho Go client GitHub repository (https://github.com/eclipse-paho/paho.mqtt.golang/security/advisories) should be monitored for additional advisories. The repository uses GitHub's security advisory system.

---

## 3. Eclipse Paho MQTT C/C++ Libraries

### CVE-2025-66168 — Apache ActiveMQ MQTT Buffer Overflow

| Field | Detail |
|-------|--------|
| **CVE ID** | CVE-2025-66168 |
| **Severity** | Medium |
| **Affected** | Apache ActiveMQ MQTT transport connectors |
| **CWE** | Integer Overflow (remaining length field) |

**Description:**  
Integer overflow due to improper validation of the remaining length field when decoding MQTT packets. Can cause:
- Protocol desynchronization
- Denial of service
- Unexpected broker behavior

**Relevance:** If PulseLink's broker uses Apache ActiveMQ (unlikely for IoT), this applies. More relevant for understanding general MQTT broker vulnerabilities.

### CVE-2024-31041 — Null Pointer Dereference DoS

| Field | Detail |
|-------|--------|
| **CVE ID** | CVE-2024-31041 |
| **Affected** | CyberPower PowerPanel |
| **CWE** | Null pointer dereference in topic filtering |
| **Impact** | Denial of Service |

**Description:**  
A null pointer dereference during MQTT topic filtering can be exploited to crash the MQTT service. This is a broker-side vulnerability but illustrates the risks of MQTT implementations.

---

## 4. Related MQTT Protocol CVEs (2024-2025)

### CVE-2024-6786 — MQTT Path Traversal (Moxa MXview One)

| Field | Detail |
|-------|--------|
| **CVE ID** | CVE-2024-6786 |
| **CVSS 4.0** | High (AV:N/AC:L/AT:P/PR:L/UI:N/VC:H) |
| **CWE** | CWE-22 / CWE-24 (Path Traversal) |
| **Advisory** | CISA ICSA-24-268-05 |
| **Affected** | Moxa MXview One series |

**Description:**  
Attacker crafts MQTT messages with relative path traversal sequences, enabling arbitrary file read on the system. Can expose:
- Configuration files
- JWT signing secrets
- System credentials

**Relevance to PulseLink:** If PulseLink's broker or any MQTT-handling component processes file paths from MQTT payloads without sanitization, similar attacks could extract sensitive configuration from the Pi.

### CVE-2024-31409 — Unblocked MQTT Wildcards (CyberPower)

| Field | Detail |
|-------|--------|
| **CVE ID** | CVE-2024-31409 |
| **CWE** | CWE-863 (Incorrect Authorization) |
| **Advisory** | CISA ICSA-24-123-01 |

**Description:**  
MQTT wildcards not properly blocked in PowerPanel system. After gaining access to any device, attacker can subscribe to all topics using `#` wildcard, extracting data from the entire system.

**Relevance to PulseLink:** Directly applicable — if PulseLink broker doesn't restrict wildcard subscriptions, compromised device = fleet-wide data exposure.

### CVE-2025-29756 — Insufficient Topic Restrictions (Sungrow iSolarCloud)

| Field | Detail |
|-------|--------|
| **CVE ID** | CVE-2025-29756 |
| **Affected** | Sungrow iSolarCloud |
| **Impact** | Extract MQTT credentials and decryption keys from browser |

**Description:**  
Insufficient restrictions on MQTT topics a user can subscribe to. Attacker with account can extract MQTT credentials and decryption key, then subscribe to all messages from all connected devices.

### CVE-2024-31486 — Insecure Password Storage (OPUPI0)

| Field | Detail |
|-------|--------|
| **CVE ID** | CVE-2024-31486 |
| **Affected** | OPUPI0 AMQP/MQTT devices (pre-V5.30) |
| **Impact** | Credential theft via remote shell or physical access |

**Description:**  
MQTT client passwords stored without sufficient protection. Attackers with shell or physical access can retrieve credentials.

---

## 5. Electron + MQTT Integration Vulnerabilities

### Electron-Specific CVEs (Chromium Dependency)

PulseLink runs as an Electron application on Chromium 134.0.6998.179. The following CVEs affect this Chromium version:

#### Critical/High Severity CVEs

| CVE | Severity | Component | Description |
|-----|----------|-----------|-------------|
| **CVE-2025-2783** | High (Zero-day) | Mojo (Windows) | Incorrect handle in Mojo; actively exploited. Fixed in 134.0.6998.177/.178 |
| **CVE-2025-2136** | High | Inspector | Use-after-free; remote heap corruption via crafted HTML |
| **CVE-2025-1914** | High | V8 Engine | Out-of-bounds memory access in JavaScript engine |
| **CVE-2025-10585** | High (KEV) | V8 Engine | Type confusion bug; actively exploited; added to CISA KEV catalog |
| **CVE-2025-1915** | Medium | DevTools | Pathname traversal in DevTools |
| **CVE-2025-1916** | Medium | Profiles | Use-after-free in Chrome profiles |
| **CVE-2025-1917** | Medium | UI | Inappropriate implementation in browser UI |

#### Electron-Specific CVEs

| CVE | Severity | Description |
|-----|----------|-------------|
| **CVE-2025-55305** | High | Arbitrary code injection via resources folder modification; affects Electron < 35.7.5 |
| **CVE-2024-27303** | High | electron-builder vulnerability allowing malicious cmd.exe execution on Windows (pre-24.13.2) |

#### 2026 Zero-Days (If Not Updated)

| CVE | Severity | Component | Fixed In |
|-----|----------|-----------|----------|
| **CVE-2026-2441** | High (Zero-day) | CSS (CSSFontFeatureValuesMap) | Chrome 146+ |
| **CVE-2026-3909** | High (Zero-day) | Skia (OOB write) | Chrome 146.0.7680.75 |
| **CVE-2026-3910** | High (Zero-day) | V8/WASM | Chrome 146.0.7680.75 |

### Impact on MQTT Communication
If the Electron app is compromised via a Chromium vulnerability:
1. Attacker gains code execution within the Electron process
2. The Go MQTT client runs in the same process (or spawned by Electron)
3. Attacker can intercept, modify, or inject MQTT messages
4. Attacker can read/write to the broker using the app's credentials
5. Full compromise of the digital signage content pipeline

**Severity:** Critical  
**Recommendation:** Ensure PulseLink Electron app uses patched Chromium; update Electron to latest stable

---

## 6. Paho Library Security Posture Summary

| Risk | Description | Severity |
|------|-------------|----------|
| **CVE-2025-10543** | Integer overflow info disclosure in paho.mqtt.golang ≤ 1.5.0 | Medium |
| **No MQTT 5.0 support** | Paho Go v3.1.1 lacks modern security features | Medium |
| **WebSocket support** | Paho supports ws:// and wss:// — additional attack surface | Low |
| **Dependency risks** | gorilla/websocket may have its own vulnerabilities | Low |
| **Library staleness** | If PulseLink pins old version, known CVEs remain unpatched | High |

---

## 7. Recommendations

1. **Verify paho.mqtt.golang version** — ensure ≥ 1.5.1 (patches CVE-2025-10543)
2. **Update Electron** to latest stable — Chromium 134 has multiple known zero-days
3. **Monitor** eclipse-paho GitHub security advisories
4. **Pin library versions** with regular update schedule
5. **Implement MQTT message validation** at application layer regardless of library
6. **Consider migrating to paho.golang** (MQTT 5.0 client) for enhanced security features
