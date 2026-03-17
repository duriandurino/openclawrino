# Application Research — PulseLink Pi (Enhanced)

## 1. PulseLink Identification

### Primary Candidate: pulselink.app — Universal Content Sharing Platform

Based on web research, the most likely match for the PulseLink running on this Raspberry Pi is **PulseLink (pulselink.app)** — a universal content sharing platform designed for seamless cross-platform sharing across operating systems and devices.

**Key Characteristics:**
- **Purpose:** Instant sharing of text, links, and files between devices
- **Platforms:** Android, iOS, Windows, Mac, Linux, and web browsers
- **Features:**
  - Instant sharing with a few clicks
  - Cross-ecosystem bridging (e.g., start email on phone, continue on laptop)
  - Real-time content transfer
  - No third-party service dependency (direct device-to-device)
- **Architecture:** Electron-based desktop app (confirmed by process structure on target)
- **Website:** https://pulselink.app

**Why this is likely the target:**
- Runs on Linux via Electron (matches `/usr/local/bin/pulselink` + `/opt/electron-player`)
- Cross-platform sharing app would need persistent network connectivity
- Electron Player runtime at `/opt/electron-player` is separate from the app binary

### Alternative Candidates (Less Likely)

| Candidate | Notes | Likelihood |
|-----------|-------|------------|
| Encom Wireless PulseLink | Radio config/diagnostics, AES-128 encryption | Low — niche industrial tool |
| PulseLink Beacon | SMS handler, Android-only | Very Low — no Android on RPi |
| Custom/internal PulseLink | Could be a bespoke internal app | Possible — needs binary analysis |

### Attack Surface (PulseLink-specific)

As a cross-platform content sharing app:
- **Network services:** Likely listens on local ports for device discovery/sharing
- **WebSocket communication:** Real-time sync between devices
- **File handling:** Accepts file transfers — potential for malicious file injection
- **URL handling:** Processes shared links — potential for URL scheme exploits
- **API integrations:** May have OAuth tokens, API keys stored locally
- **Electron-based:** Subject to all Electron/Chromium vulnerabilities

---

## 2. Electron Player Analysis

### Runtime Details

**Location:** `/opt/electron-player`
**Type:** Standard Electron/Chromium runtime (separate from app binary)

### Process Architecture (Observed)

| Process | Function | Security Relevance |
|---------|----------|-------------------|
| **utility** | Storage + network sandbox | Handles persistent storage, network I/O |
| **gpu** | Hardware acceleration | GPU sandbox escape vector (CVE-2025-6558) |
| **audio** | Audio processing | Limited attack surface |
| **renderer** | UI rendering (Chromium) | PRIMARY ATTACK TARGET — XSS, sandbox escape |
| **zygote** | Process spawning | Sandbox foundation |
| **ui** | Main UI process | Privileged, has Node.js access |

### Security Configuration (Unknowns)

| Setting | Status | Impact |
|---------|--------|--------|
| `nodeIntegration` | Unknown | If `true` in renderer → RCE via XSS |
| `contextIsolation` | Unknown | If `false` → renderer can access Electron APIs |
| `sandbox` | Unknown | If `false` → renderer has OS-level access |
| `webSecurity` | Unknown | If `false` → CORS bypass, mixed content |
| `allowRunningInsecureContent` | Unknown | If `true` → MITM opportunities |
| `experimentalFeatures` | Unknown | Additional attack surface |

### User Data Directory

**Path:** `/home/pi/.config/electron-player`

**Contents (typical Electron/Chromium structure):**

| Path | Contents | Forensic Value |
|------|----------|---------------|
| `Local Storage/leveldb/` | LevelDB databases with app state | HIGH — app data, user preferences, potentially auth tokens |
| `Session Storage/leveldb/` | Session-scoped storage | MEDIUM — active session data |
| `Cookies` | Encrypted cookie database | HIGH — session tokens, auth credentials (encrypted, needs key) |
| `Cache/` | HTTP cache, shader cache | LOW — temporary data |
| `GPUCache/` | GPU shader cache | LOW |
| `Code Cache/` | Compiled JS/CSS cache | LOW |
| `Crashpad/` | Crash dump data | MEDIUM — may contain memory snapshots |
| `DawnCache/` | WebGPU cache | LOW |
| `Network/` | Network state, HSTS pins | MEDIUM — network behavior history |
| `blob_storage/` | Blob URL data | LOW |
| `FileSystem/` | HTML5 filesystem API data | MEDIUM — may contain app files |
| `shared_proto_db/` | Shared protocol buffers | LOW |
| `optimization_guide_*` | Chrome optimization data | LOW |

### Key Forensic Targets in User Data

1. **Local Storage LevelDB** — Read with Python `plyvel` or Go LevelDB tools
   - Contains key-value pairs with app state
   - May include auth tokens, user preferences, cached data
   - Files: `CURRENT`, `LOCK`, `LOG`, `MANIFEST-*`, `*.log`, `*.ldb`

2. **Cookies (encrypted)** — Chromium encrypts cookies with OS keyring
   - On Linux: uses `libsecret`/`gnome-keyring` or DPAPI-like mechanism
   - Encryption key stored in `Local State` (JSON, contains `os_crypt.encrypted_key`)
   - Decryption requires access to the running session's keyring

3. **Crash Reports** — `/home/pi/.config/chromium/Crash Reports`
   - Minidumps may contain memory contents
   - Could reveal decrypted data, keys, or sensitive state

---

## 3. WidevineCdm Analysis

### Overview

**Location:** `/opt/WidevineCdm`
**Type:** Widevine Content Decryption Module — L3 (software-only)

### Security Level

| Level | Hardware | Security | Status on RPi |
|-------|----------|----------|---------------|
| L1 | Trusted Execution Environment (TEE) | Hardware-protected keys | ❌ Not available |
| L2 | Hardware video decoding | Software keys, HW decode | ❌ Not available |
| **L3** | **Software-only** | **No hardware protection** | ✅ **ACTIVE** |

### Known Widevine L3 Vulnerabilities

Widevine L3 has been **repeatedly compromised** due to its software-only implementation:

1. **DFA Attack (2019):** Differential Fault Analysis against white-box AES in Chrome's Widevine, recovering original encryption keys
2. **Full Reverse Engineering (2020-2021):** Android L3 CDM fully reverse-engineered
3. **Key Extraction Tools Available:**
   - **KeyDive** (Python) — Automated L3 key extraction via Frida hooks
   - **Qiling Framework** — Emulate Android libs + DFA attacks
   - **widevine-l3-decryptor** (GitHub) — Direct L3 content decryption

### Attack Vectors via Widevine

| Vector | Description | Difficulty |
|--------|-------------|------------|
| **CDM binary analysis** | Reverse engineer `/opt/WidevineCdm` for key material | Medium |
| **Frida injection** | Hook Widevine functions to extract keys from running process | Medium |
| **Content key extraction** | Extract content keys from decrypted streams | Medium |
| **Private key extraction** | Recover device private key from L3 implementation | Hard |
| **Client ID extraction** | Extract device/client identification data | Easy-Medium |

### Forensic Value

Widevine L3 extraction could reveal:
- Device-specific encryption keys
- Content decryption keys (for any DRM-protected media)
- Client identification data
- Private key material

**Note:** This is primarily valuable if PulseLink uses Widevine for DRM-protected content delivery.

---

## 4. Integrated Attack Chain (Application-Level)

### Chain 1: Electron Renderer → Full System

```
Renderer Process (Chromium sandbox)
    ↓ [XSS in PulseLink UI or CVE-2025-4609 IPC exploit]
Escape Chromium Sandbox
    ↓ [Context isolation bypass or Node.js integration]
Access Node.js APIs via preload/main
    ↓ [child_process.exec, fs module]
Execute OS commands as pi user
    ↓ [sudo misconfiguration or kernel exploit]
Escalate to root
```

### Chain 2: ASAR Tampering (Requires Write Access)

```
Write access to /opt/pulselink/resources/app.asar
    ↓ [npx asar extract]
Unpack application source
    ↓ [Inject malicious JavaScript]
Modify app behavior (backdoor, keylogger, data exfil)
    ↓ [npx asar repack]
Repackage and replace ASAR
    ↓ [Restart PulseLink]
Malicious code executes with app privileges
```

### Chain 3: User Data Forensics → Credential Harvest

```
Access /home/pi/.config/electron-player/
    ↓ [Read LevelDB files]
Extract Local Storage data (auth tokens, API keys)
    ↓ [Extract encrypted cookies]
Decrypt cookies using OS keyring access
    ↓ [Combine with app tokens]
Full session hijacking or API access
```

---

*Research enhanced with live web search results. All CVEs verified against current databases.*
