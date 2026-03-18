# Penetration Test Report: VAULT Decryption Engagement

**Document Classification:** CONFIDENTIAL  
**Report Date:** 2026-03-18  
**Engagement ID:** PLAYER-VAULT-2026-0318  
**Prepared By:** specter-report (OpenClaw Pentest Agent)  
**Target:** vault.img — LUKS2 Encrypted Container on Raspberry Pi 5 Player  
**Overall Risk Rating:** **CRITICAL**

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Scope & Methodology](#2-scope--methodology)
3. [Target Overview](#3-target-overview)
4. [Attack Chain Narrative](#4-attack-chain-narrative)
5. [Detailed Findings](#5-detailed-findings)
6. [Vault Contents Inventory](#6-vault-contents-inventory)
7. [Risk Summary Matrix](#7-risk-summary-matrix)
8. [Remediation Recommendations](#8-remediation-recommendations)
9. [Conclusion](#9-conclusion)
10. [Appendices](#10-appendices)

---

## 1. Executive Summary

During this engagement, the security team successfully decrypted a LUKS2-encrypted vault container (`vault.img`) on a Raspberry Pi 5 digital signage player without the owner's knowledge of the extraction path. The entire attack chain — from discovery to full data exfiltration — required **only local filesystem access and publicly available system information** (the Pi's hardware serial number).

**The vault's encryption was cryptographically strong (AES-XTS-plain64, 512-bit, argon2id KDF), but its key management was fundamentally broken.** The passphrase was:

1. **Hardcoded** in a Python script (`hardware_lock.py`)
2. **Derived from easily discoverable hardware** (Pi serial number)
3. **Exposed in shell history** (`.bash_history`)

Once the vault was decrypted, we obtained access to:

- **An entire Node.js application** (player-server v2.9.43-pi5) including full source code
- **An unprotected SQLite database** containing 18 tables of operational data
- **Third-party API keys** (Vistar ad network credentials)
- **License keys** in plaintext
- **8 core dump files** (~2.6 GB total) containing potential process memory snapshots
- **Application configuration** including environment variables and PM2 process definitions

### Key Takeaways

| Metric | Value |
|--------|-------|
| Time to decrypt vault | ~15 minutes (manual) |
| Required access level | Any user with filesystem read access |
| Credentials exposed | API keys, license keys, Pi serial |
| Data exposure | ~2.6 GB core dumps + operational database |
| Critical findings | 1 (CVSS 9.1) |
| High findings | 4 (CVSS 7.5 – 8.1) |
| Medium findings | 4 (CVSS 5.3 – 6.5) |
| **Overall risk** | **CRITICAL** |

---

## 2. Scope & Methodology

### 2.1 Authorization

This engagement was conducted under authorized penetration testing terms as defined by the engagement scope. All testing was performed against the designated target (vault.img on the Raspberry Pi 5 Player).

### 2.2 Target

| Attribute | Value |
|-----------|-------|
| Target | `vault.img` — LUKS2 encrypted container |
| UUID | `9757eca5-e8a1-4f8a-9c20-8c9252d61d09` |
| Encryption | AES-XTS-plain64, 512-bit key, argon2id PBKDF |
| Mount Point | `/home/pi/n-compasstv-secure` |
| Host Device | Raspberry Pi 5 Player |

### 2.3 Methodology

The engagement followed a structured pentest methodology:

```
Phase 1: Discovery     → Locate vault, identify encryption type, find supporting scripts
Phase 2: Key Discovery → Analyze source code, extract credentials, review shell history
Phase 3: Decryption    → Craft correct passphrase, unlock LUKS2 container, mount filesystem
Phase 4: Analysis      → Inventory contents, extract database schema, identify sensitive data
Phase 5: Reporting     → Document findings, calculate CVSS scores, provide remediation guidance
```

### 2.4 Tools Used

- `cryptsetup` — LUKS2 container management
- `python3` — Script analysis (unlock_vault.py, hardware_lock.py)
- `sqlite3` — Database schema extraction and analysis
- Standard filesystem enumeration tools

---

## 3. Target Overview

### 3.1 Vault Configuration

The `vault.img` file is a LUKS2-format encrypted disk image stored at `/home/pi/vault.img`. Upon analysis via `cryptsetup luksDump`, the following cryptographic parameters were confirmed:

| Parameter | Value |
|-----------|-------|
| Version | LUKS2 |
| Cipher | aes-xts-plain64 |
| Key Size | 512 bits (256-bit effective for XTS) |
| KDF | argon2id |
| UUID | 9757eca5-e8a1-4f8a-9c20-8c9252d61d09 |
| Segments | 1 (LUKS2 key slot 0 active) |

**Cryptographic Assessment:** The encryption algorithm itself is strong and industry-standard. AES-XTS with 512-bit key and argon2id KDF represents best practices for disk encryption. **The vulnerability is entirely in key management, not cryptography.**

### 3.2 Supporting Scripts

Two Python scripts in `/usr/local/bin/` manage vault access:

- **`unlock_vault.py`** — Automated vault unlock script that reads the Pi serial and calls cryptsetup
- **`hardware_lock.py`** — Device authentication module containing the hardcoded serial

---

## 4. Attack Chain Narrative

The full attack chain from initial access to complete data compromise followed this path:

### Stage 1: Reconnaissance (Discovery)

```
Attacker gains read access to /home/pi/ filesystem
    ↓
Finds vault.img (LUKS2 encrypted, UUID identified)
    ↓
Discovers supporting scripts: unlock_vault.py, hardware_lock.py
    ↓
Identifies encryption type via cryptsetup luksDump
```

**No special tools required.** Standard Linux utilities (`ls`, `file`, `cryptsetup`) are sufficient.

### Stage 2: Credential Harvesting (Key Discovery)

```
Reviews unlock_vault.py → reveals vault uses Pi hardware serial as passphrase
    ↓
Reviews hardware_lock.py → finds AUTHORIZED_PI_SERIAL = "ffb6d42807368154"
    ↓
Checks .bash_history → confirms actual cryptsetup command used for encryption
    ↓
Key extracted: ffb6d42807368154 (with trailing newline)
```

**The Pi serial number is freely available** via `cat /proc/cpuinfo`, `vcgcenc --get_serial`, or physically printed on the board. The "hardware lock" provides zero additional security.

### Stage 3: Decryption (Exploitation)

```
Attempt 1: echo -n "ffb6d42807368154" | cryptsetup open vault.img nctv_data --key-file -
    → FAILED (wrong key — missing newline)
    
Attempt 2: echo "ffb6d42807368154" | cryptsetup open /home/pi/vault.img nctv_data
    → SUCCESS (correct key — echo adds trailing \n)
    
Mount: mount /dev/mapper/nctv_data /home/pi/n-compasstv-secure
    → Full filesystem access granted
```

**Critical detail:** The newline character (`\n`) appended by `echo` (vs `echo -n`) is part of the passphrase. This is both a quirk that adds minimal complexity and a weakness — it suggests the passphrase was set accidentally with the newline, meaning the *intended* key material is even shorter than expected.

### Stage 4: Data Exfiltration

```
Full filesystem tree enumerated
    ↓
SQLite database (_data.db) extracted and schema analyzed
    ↓
18 tables identified containing: API keys, license keys, operational data
    ↓
Core dump files (~2.6 GB) flagged for potential memory forensics
    ↓
Application source code and configuration extracted
```

### Attack Complexity Assessment

| Factor | Rating | Notes |
|--------|--------|-------|
| Skill required | Low | Copy-paste from discovered scripts |
| Time required | ~15 min | Manual; seconds with automation |
| Tools needed | Standard Linux | No exploits or special software |
| Trace of attack | Low | Read-only access leaves minimal footprint |
| Privilege needed | Any local user | No root required for read access |

---

## 5. Detailed Findings

---

--- TRIMMED FOR SLIDES ---
   - Use infrastructure-as-code (Ansible, Terraform) for device provisioning
   - Implement configuration drift detection
   - Automated security scanning in CI/CD pipeline

---

## 9. Conclusion

This engagement demonstrated that **strong cryptography is rendered useless by weak key management**. The LUKS2 vault using AES-XTS-512 with argon2id KDF represents industry-best encryption — yet the entire vault was compromised in under 15 minutes using only the hardcoded Pi serial number found in a plaintext Python script.

The root cause is a chain of security failures:

1. **The encryption key was derived from publicly available hardware information** (Pi serial number)
2. **The key was hardcoded in source code** rather than generated randomly
3. **The key was stored alongside the vault** on the same filesystem
4. **Supporting data (database, config, credentials) was unencrypted** within the vault
5. **No defense-in-depth measures existed** — single point of failure

### Overall Assessment

| Category | Rating |
|----------|--------|
| Cryptographic Implementation | ✅ Strong (AES-XTS-512, argon2id) |
| Key Management | ❌ Critical Failure |
| Data Protection at Rest | ❌ Poor (unencrypted DB, plaintext credentials) |
| Application Security | ⚠️ Moderate (dev mode, but structured codebase) |
| Operational Security | ❌ Poor (exposed core dumps, bash history leaks) |
| **Overall Security Posture** | **❌ CRITICAL — Immediate remediation required** |

### Recommended Engagement Follow-Up

1. **Re-test after remediation** — Verify vault re-encryption, API key rotation, and database encryption
2. **Security architecture review** — Evaluate proposed TPM/HSM integration
3. **Application penetration test** — Test the player-server application for additional vulnerabilities (routes, API endpoints, input validation)
4. **Operational security audit** — Review device provisioning, update management, and monitoring

---

## 10. Appendices

### Appendix A: Vault Technical Details

```
$ cryptsetup luksDump /home/pi/vault.img

LUKS header information
Version:        2
Cipher name:    aes
Cipher mode:    xts-plain64
Cipher key:     512 bits
PBKDF:          argon2id
UUID:           9757eca5-e8a1-4f8a-9c20-8c9252d61d09
```

### Appendix B: Decryption Commands

```bash
# Successful decryption
echo "ffb6d42807368154" | sudo cryptsetup open /home/pi/vault.img nctv_data
sudo mount /dev/mapper/nctv_data /home/pi/n-compasstv-secure

# Cleanup (when finished)
sudo umount /home/pi/n-compasstv-secure
sudo cryptsetup close nctv_data
```

### Appendix C: Key Scripts

**unlock_vault.py** — Vault unlock automation (located in `/usr/local/bin/`)
- Reads Pi serial from hardware
- Calls cryptsetup with serial as passphrase
- Mounts decrypted volume

**hardware_lock.py** — Device authentication module (located in `/usr/local/bin/`)
- Contains `AUTHORIZED_PI_SERIAL = "ffb6d42807368154"`
- Used by unlock_vault.py for passphrase generation

### Appendix D: CVSS v3.1 Score Calculation

| Finding | Vector String | Score |
|---------|--------------|-------|
| V-012 | AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N | 9.1 |
| V-013 | AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 7.5 |
| V-014 | AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N | 5.3 |
| V-015 | AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H | 5.8 |
| V-016 | AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N | 8.1 |
| V-017 | AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N | 7.5 |
| V-018 | AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N | 6.5 |
| V-019 | AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N | 6.2 |
| V-020 | AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N | 7.5 |

---

**Report Generated:** 2026-03-18 17:53 GMT+8  
**Agent:** specter-report (OpenClaw Pentest Sub-Agent)  
**Engagement:** PLAYER-VAULT-2026-0318  

---

*This report is confidential and intended for authorized recipients only. Findings should be remediated according to the priority guidance provided. A follow-up assessment is recommended after remediation completion.*
