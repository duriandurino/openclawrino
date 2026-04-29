# PlayerV2 Phoenix — Executive Report Draft

Date: 2026-04-29
Target: playerv2-phoenix
Status: Draft

## Executive summary

The strongest currently verified Phoenix issues are not generic software weaknesses. They are failures in the device’s local trust and enforcement model.

The most important finding is that Phoenix authorization depends on the storage appearing under a specific Linux device path. By presenting the same authorized media through a USB SD reader instead of the native slot, the device’s trust logic breaks. That broken trust path then fails open, preserving local GUI and terminal access instead of safely denying it.

A third verified issue showed that the device retained sensitive provisioning material in shell history, including a setup host, encrypted setup artifact reference, and plaintext provisioning passphrase. In practical terms, this means an attacker who reaches local access may recover useful deployment knowledge and secret material that can support follow-on compromise.

## Key findings

### PHX-V01 — Storage-interface-dependent authorization failure
- Severity: Medium
- CVSS: 6.8 (CVSS-B)
- Summary: The authorization design depends on the protected storage being visible specifically as `mmcblk0`. When the same media is presented through a USB SD reader as `sda`, the authorization logic no longer behaves as intended.
- Business meaning: The product’s local hardware-bound trust claim can be bypassed by altering how the same storage is presented to the system.

### PHX-V02 — Fail-open local access after hardware-check crash
- Severity: High
- CVSS: 7.3 (CVSS-B)
- Summary: When the authorization check fails in the USB-presented path, the enforcement control crashes instead of denying access safely. The result is preserved local GUI and terminal access.
- Business meaning: A security control designed to block local access can fail into the opposite state, exposing the device for interactive access and local reconnaissance.

### PHX-V03 — Sensitive provisioning artifact exposure in shell history
- Severity: High
- CVSS: 7.1 (CVSS-B)
- Summary: Local shell history exposed a provisioning command containing a setup host, decryption workflow, and plaintext passphrase.
- Business meaning: An attacker who gains local access may recover reusable operational knowledge and secret material that lowers the effort needed for follow-on compromise.

## Overall risk interpretation

Even though the leading Phoenix attack paths are physical or local, they should not be treated as low-priority issues in this engagement. Physical access is explicitly in scope and directly relevant to the product’s intended trust model. A hardware-lock design that breaks when storage presentation changes, then preserves local access when checks fail, represents a meaningful security design gap rather than a minor edge case.

## Priority remediation themes

1. **Fix identity binding**
   - Bind authorization to stable media identity rather than a fixed Linux device name.

2. **Fail closed on authorization errors**
   - Any inability to validate trusted hardware identity should force the device into a locked state, not an accessible one.

3. **Remove provisioning secrets from local artifacts**
   - Eliminate secret-bearing commands from shell history and rotate exposed setup material.

4. **Strengthen local hardening validation**
   - Re-test boot behavior, lock-state transitions, and recovery/error paths under real alternate media conditions.

## Recommended next step

Proceed with final report development using PHX-V01 through PHX-V03 as the first-wave verified findings set, while keeping the remaining Phoenix observations in controlled validation until they are either confirmed or downgraded to hardening notes.
