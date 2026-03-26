# Vault Decryption: NTV Phoenix

---

# Vault Decryption: NTV Phoenix
## Penetration Test Report

**Date:** March 18, 2026  
**Target:** vault.img on Raspberry Pi 5  
**Risk Rating:** CRITICAL 🔴

---

# Executive Summary

**We decrypted a LUKS2 vault in ~15 minutes using only the Pi's serial number.**

**The Attack:**
- Found hardcoded passphrase in Python script
- Passphrase derived from public hardware info
- Zero technical skill required

**Result:** Full access to 2.6GB of sensitive data

---

# The Problem: Strong Crypto, Weak Keys

**Encryption:** AES-XTS-512 with argon2id
- ✅ Industry standard
- ✅ Cryptographically strong

**Key Management:**
- ❌ Hardcoded in source code
- ❌ Derived from serial number
- ❌ Stored next to the vault
- ❌ Exposed in shell history

**Bottom line:** Best encryption, worst key handling

---

# Attack Chain

**Stage 1:** Discover vault.img and supporting scripts

**Stage 2:** Extract passphrase from hardware_lock.py
- AUTHORIZED_PI_SERIAL = "ffb6d42807368154"

**Stage 3:** Decrypt with standard Linux tools
- `echo "ffb6d42807368154" | cryptsetup open vault.img nctv_data`

**Stage 4:** Access all vault contents

---

# What We Found

**Application Data:**
- Complete Node.js source code (player-server v2.9.43)
- Unprotected SQLite database (18 tables)
- API keys for Vistar ad network
- License keys in plaintext

**System Data:**
- 8 core dump files (~2.6 GB)
- PM2 process configurations
- Environment variables

---

# Key Findings

**🔴 CRITICAL — Hardcoded Vault Passphrase (CVSS 9.1)**
- Anyone with filesystem read can decrypt
- Passphrase is public information (Pi serial)

**🟠 HIGH — Unencrypted Database**
- API keys, operational data exposed
- No access controls within vault

**🟠 HIGH — Core Dumps Contain Secrets**
- Memory snapshots may contain credentials
- 2.6 GB of potential sensitive data

---

# Immediate Fixes Required

**🔴 This Week:**
- Re-encrypt vault with random passphrase
- Remove hardcoded keys from scripts
- Rotate all exposed API keys

**🟠 Next 30 Days:**
- Implement TPM/HSM for key storage
- Encrypt database at rest
- Disable core dumps in production

---

# Lessons Learned

**Security is a chain:**
- Strong encryption ≠ secure system
- Key management matters more than algorithms
- Defense in depth prevents single points of failure

**The vault was only as strong as its weakest secret.**
