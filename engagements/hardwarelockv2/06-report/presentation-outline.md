# Hardware Lock V2
## Penetration Test Report

**Target:** hardwareLockV2  
**Date:** 2026-04-14  
**Overall Risk:** 🟡 **MEDIUM**  
**Status:** Final

---

# Executive Summary
---
## Executive Summary

- Local env-based authorization can be altered with file-write access
- The LUKS vault still blocked recovery of the protected runtime
- Phoenix recovery depends on a staged artifact chain that was no longer present locally
- **Bottom Line:** The first gate is weak, but the encrypted vault remained the effective security boundary in the assessed state

---

# Scope, ROE & Methodology
---
## Scope, ROE & Methodology

**Target:** Hardware Lock V2 on authorized Raspberry Pi device  
**Access Level:** Local gray-box analysis  
**Authorization:** Confirmed  
**Limitations:** Modified env state, missing Phoenix artifacts, no external repair source

**Phases:**
- ✅ Recon / Discovery - identified hardware lock and vault chain
- ✅ Enumeration - validated auth logic, vault state, and service dependencies
- ✅ Validation / Analysis - separated weak config auth from strong cryptographic boundary
- ✅ Exploit / Recovery Analysis - confirmed blocked state from surviving local artifacts

---

# Attack Path / Engagement Story
---
## Attack Path / Engagement Story

| Step | Action | Result | Evidence |
|------|--------|--------|----------|
| 1 | Review auth logic and env-backed tuple | Gate shown to depend on editable local config | EVI-004, EVI-005 |
| 2 | Align env values to current hardware | Authorization passes | EVI-005 |
| 3 | Run unlock path against `vault.img` | `cryptsetup` rejects derived key | EVI-005, EVI-006 |
| 4 | Inspect provisioning and repair chain | Missing Phoenix artifacts keep recovery blocked | EVI-008 to EVI-013 |

---

# Findings Summary
---
## Findings Summary

| # | Finding | Severity | Status | Asset |
|---|---------|----------|--------|-------|
| F-001 | Local auth config mutable via `hardware-lock.env` | 🟡 MEDIUM | validated | hardwareLockV2 |
| F-004 | Shell history exposed provisioning bootstrap secret and flow | 🟠 HIGH | validated | provisioning workflow |
| F-005 | Repair path depends on missing external `nctv-phoenix` source | 🟡 MEDIUM | validated | recovery workflow |
| F-007 | `setup.enc` only bootstraps second-stage Phoenix installer | 🟡 MEDIUM | validated | staged runtime chain |
| F-008 | Internal-only local recovery remains blocked | 🟡 MEDIUM | validated | current box state |

---

# F-001: Mutable Local Authorization Gate
---
## F-001: Mutable Local Authorization Gate
### 🟡 MEDIUM - validated

**What:** `hardware-lock.env` can be edited locally so the device appears authorized on current hardware.

**Impact:** A local attacker with write access can weaken trust in the first hardware-bound gate.

**Evidence:** EVI-003, EVI-004, EVI-005

**Fix:**
- Protect config integrity
- Restrict local write access
- Use tamper-evident or hardware-backed binding

---

# F-004: Provisioning Secret Exposure
---
## F-004: Provisioning Secret Exposure
### 🟠 HIGH - validated

**What:** Shell history preserved the command and passphrase used to decrypt `setup.enc`.

**Impact:** Historical installer logic and secrets become recoverable, aiding reverse engineering and unauthorized reconstruction.

**Evidence:** EVI-008, EVI-012

**Fix:**
- Rotate exposed bootstrap secrets
- Remove sensitive installer commands from history
- Use short-lived or per-device provisioning secrets

---

# F-005/F-008: Recovery Chain Blocked by Missing Phoenix Artifacts
---
## F-005/F-008: Recovery Chain Blocked by Missing Phoenix Artifacts
### 🟡 MEDIUM - validated

**What:** Repairman expects an external `nctv-phoenix` tree, while local Phoenix installer artifacts no longer survive on-box.

**Impact:** The system cannot recover the coupled Phoenix-plus-player runtime from local residue alone.

**Evidence:** EVI-009 to EVI-013

**Fix:**
- Preserve trusted recovery media
- Archive the full staged runtime chain
- Build a formal, testable recovery playbook

---

# Remediation & Retest Roadmap
---
## Remediation & Retest Roadmap

**🟠 Immediate (0-24 hours):**
- Protect `hardware-lock.env`
- Rotate old provisioning secrets
- Stop uncontrolled unlock/repair retry loops

**🟡 Short-term (1-7 days):**
- Preserve signed provisioning and repair artifacts
- Add integrity checks for unlock logic and runtime trees

**🟡 Medium-term (1-4 weeks):**
- Move toward hardware-backed binding
- Build a formal recovery repository and playbook

**Retest Success Looks Like:**
- Unauthorized config edits no longer advance recovery
- Trusted artifacts allow deterministic, auditable recovery testing

---

# Cleanup, Residual Risk & Next Steps
---
## Cleanup, Residual Risk & Next Steps

**Cleanup Status:** No new live artifacts introduced by reporting  
**Residual Risk:** Weak local auth remains relevant, and recovery remains fragile without trusted artifact provenance

**Next Steps:**
- Obtain trusted provisioning or repair artifacts
- Compare against a known-good sibling device if authorized
- Consider offline vault work only as a separately approved effort

---
