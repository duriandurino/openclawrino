# NTV Phoenix & Hardware Lock — Open Questions

**Known gaps, uncertainties, and future improvement areas**  
**Last Updated:** March 2026

---

## 🔴 Critical Uncertainties

### 1. Hardware Serial/CID Management

**Question:** How are authorized serial/CID pairs managed across production?

**Current State:**
- Hardcoded in `/usr/local/bin/hardware_lock.py`
- Two different serial/CID pairs found in documentation:
  - Root doc: `ffb6d42807368154` / `1b534d45423151543089c65df4015a00`
  - Kent turnover: `10000000d58ec40c` / `1b534d4542315154305bde6365015a00`

**Uncertainties:**
- ⚠️ Are these per-device, per-batch, or per-deployment?
- ⚠️ How is the "gold master" image updated with new serials?
- ⚠️ What happens when a Pi needs replacement (different serial)?
- ⚠️ Is there a centralized database of authorized hardware?

**Risks:**
- Locked out devices if serials don't match
- Maintenance overhead for each hardware change
- No clear process for Pi replacement

---

### 2. Vault Distribution

**Question:** How is the encrypted vault.img distributed?

**Current State:**
- Vault is LUKS-encrypted container
- Requires Pi serial to decrypt
- Contains complete application stack

**Uncertainties:**
- ⚠️ How is vault.img initially created and populated?
- ⚠️ How are updates to the application deployed?
- ⚠️ Is vault.img cloned from a master or generated per-device?
- ⚠️ What's the process for updating player-server version?

**Evidence:**
- `installer.sh` downloads player-server-2.6.0.zip and player-ui-2.4.1.zip
- No clear evidence of vault creation in installer
- Phoenix `repairman.sh` rsyncs from USB to SD

---

### 3. Phoenix USB Creation Process

**Question:** What is the canonical process for creating Phoenix USBs?

**Current State:**
- `repairman.sh` script exists with recovery logic
- Expects boot from USB (sdb)
- Contains rsync-based restore logic

**Uncertainties:**
- ⚠️ How is the USB initially prepared/flashed?
- ⚠️ What OS version is on the USB?
- ⚠️ How are USB contents updated with new software versions?
- ⚠️ Is there a build script for creating Phoenix USB images?
- ⚠️ How many USBs should field techs carry?

**Risks:**
- Inconsistent USB preparation
- Outdated recovery software
- Field tech confusion

---

## 🟡 Technical Questions

### 4. EEPROM Boot Order Conflicts

**Question:** What happens if EEPROM boot order changes?

**Current State:**
- `BOOT_ORDER=0xf461` (USB before SD)
- Set via `rpi-eeprom-config`
- Phoenix repairman resets to `0xf461`

**Uncertainties:**
- ⚠️ What if EEPROM update fails?
- ⚠️ What if boot order is accidentally changed?
- ⚠️ Is there a fallback if EEPROM is corrupted?
- ⚠️ How is EEPROM version managed across fleet?

**Evidence:**
- Document shows duplicate: `BOOT_ORDER=BOOT_ORDER=BOOT_ORDER=0xf461`
- Suggests possible EEPROM config issues

---

### 5. Vault Corruption Handling

**Question:** What happens if vault.img is corrupted?

**Current State:**
- Vault is LUKS-encrypted file on SD
- Hardware lock unlocks and mounts it
- Watchdog monitors mounted directory

**Uncertainties:**
- ⚠️ How is vault corruption detected?
- ⚠️ What recovery options exist for corrupted vault?
- ⚠️ Is there vault backup/replication?
- ⚠️ Can Phoenix repairman fix vault corruption?

**Current Gap:**
- `repairman.sh` rsyncs filesystem, but may not handle vault-specific corruption
- No explicit vault repair logic found

---

### 6. Network Recovery Limitations

**Question:** Can any recovery happen without physical access?

**Current State:**
- All recovery requires USB insertion
- No network-based recovery mechanism
- Cloud dashboard provides remote commands but not recovery

**Uncertainties:**
- ⚠️ Is physical access always available?
- ⚠️ What are SLA implications for failed devices?
- ⚠️ Could TFTP/Netboot be used for recovery?

---

### 7. Watchdog False Trigger Risk

**Question:** Can watchdog trigger falsely?

**Current State:**
- Monitors `/home/pi/n-compasstv` every 20s
- 60s grace period at boot
- Renames `config.txt` before reboot

**Uncertainties:**
- ⚠️ What if directory is temporarily unavailable (I/O spike)?
- ⚠️ Is 20s check interval appropriate?
- ⚠️ Could a slow SD card cause false triggers?
- ⚠️ Is there a way to "disarm" watchdog temporarily?

**Evidence:**
- Script uses simple `[ ! -d "$CHECK_DIR" ]` check
- No retry logic or "soft" check

---

## 🟢 Improvement Opportunities

### 8. Configuration Management

**Current:** Hardcoded values in Python scripts
**Proposed:** External configuration file

```python
# Instead of:
AUTHORIZED_PI_SERIAL = "ffb6d42807368154"

# Use:
import json
with open('/etc/nctv/hardware-lock.json') as f:
    config = json.load(f)
AUTHORIZED_PI_SERIAL = config['authorized_serial']
```

**Benefits:**
- Easier per-device customization
- Centralized management
- No code changes for new hardware

---

### 9. Hardware Lock Logging

**Current:** Print statements, systemd journal
**Gap:** No persistent audit log of lock events

**Proposed:** SQLite or file-based audit log

```python
# Log to persistent storage
def log_lock_event(event_type, serial, cid, result):
    with open('/var/log/nctv-hardware-lock.log', 'a') as f:
        f.write(f"{timestamp} {event_type} serial={serial} cid={cid} result={result}\n")
```

---

### 10. Vault Health Monitoring

**Current:** Mount success/failure
**Gap:** No integrity checks on vault contents

**Proposed:** Periodic hash verification

```bash
# Create manifest on vault creation
find /home/pi/n-compasstv-secure -type f -exec sha256sum {} \; > /home/pi/vault-manifest.txt

# Verify periodically
sha256sum -c /home/pi/vault-manifest.txt
```

---

### 11. Multi-Hardware Support

**Current:** Single serial/CID pair
**Proposed:** Allow list approach

```python
# Support multiple authorized devices
AUTHORIZED_DEVICES = [
    {"serial": "ffb6d42807368154", "cid": "1b534d..."},
    {"serial": "10000000d58ec40c", "cid": "1b534d..."},
]
```

---

## 📋 Documentation Gaps

### 12. Missing Documentation

| Topic | Status | Priority |
|-------|--------|----------|
| Phoenix USB creation process | ❌ Not found | 🔴 Critical |
| Vault creation procedure | ❌ Not found | 🔴 Critical |
| Serial/CID management workflow | ❌ Not found | 🔴 Critical |
| Fleet update process | ❌ Not found | 🟡 High |
| Troubleshooting runbook | ❌ Not found | 🟡 High |
| Security incident response | ❌ Not found | 🟡 High |
| Performance tuning guide | ❌ Not found | 🟢 Medium |
| Monitoring/alerting setup | ❌ Not found | 🟢 Medium |

---

## 🔍 Ambiguities Found in Source

### A. Duplicate EEPROM Config

**Location:** Scripts and Services doc  
**Issue:**
```
BOOT_ORDER=BOOT_ORDER=BOOT_ORDER=0xf461
```
**Question:** Is this intentional or a documentation error?

---

### B. Multiple Serial/CID Pairs

**Location:** Different files  
**Finding:**
- Root doc: `ffb6d42807368154`
- Kent turnover: `10000000d58ec40c`

**Question:** Are these different environments or different versions?

---

### C. Service Name Inconsistency

**Location:** systemd service files  
**Finding:**
- `setup.sh` references `pm2-pi` and `watchdog`
- But actual service files have different names

**Question:** Are there legacy service names still in use?

---

## 🚀 Future Considerations

### Remote Management

- Network-based vault unlock (secure key escrow?)
- OTA updates for vault contents
- Remote diagnostics beyond socket commands

### Security Enhancements

- TPM integration for Pi 5
- Signed vault images
- Certificate-based hardware attestation

### Scalability

- Automated vault generation
- CI/CD for USB image creation
- Fleet management dashboard

---

## Action Items

| Priority | Item | Owner | Due |
|----------|------|-------|-----|
| 🔴 P0 | Document serial/CID management process | ? | ASAP |
| 🔴 P0 | Document Phoenix USB creation | ? | ASAP |
| 🔴 P0 | Document vault creation procedure | ? | ASAP |
| 🟡 P1 | Create external config for hardware lock | Dev | ? |
| 🟡 P1 | Add audit logging to hardware lock | Dev | ? |
| 🟡 P1 | Clarify EEPROM boot order handling | Dev | ? |
| 🟢 P2 | Create fleet update runbook | Ops | ? |
| 🟢 P2 | Document troubleshooting procedures | Support | ? |

---

## Open Questions Summary

**Total Open Questions:** 11  
**Critical (🔴):** 3  
**High (🟡):** 4  
**Medium (🟢):** 4

**Key Areas:**
1. Hardware binding management
2. Vault lifecycle
3. Recovery process standardization
4. Configuration externalization
5. Documentation completeness

---

**End of Open Questions**
