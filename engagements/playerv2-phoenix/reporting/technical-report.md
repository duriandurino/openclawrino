# PlayerV2 Phoenix — Technical Report Draft

Date: 2026-04-29
Target: playerv2-phoenix
Status: Draft, first-wave findings prepared for reporting

## Reporting scope for this pass

This draft prepares the first three Phoenix findings for report-ready use:
- **PHX-V01 — Storage-interface-dependent authorization failure**
- **PHX-V02 — Fail-open local access after hardware-check crash**
- **PHX-V03 — Sensitive provisioning artifact exposure in shell history**

These are the strongest currently verified Phoenix findings and reflect the latest analyst decisions:
- PHX-V01 and PHX-V02 remain separate
- PHX-V03 is treated as still operationally useful if missed in a real attack

## Finding PHX-V01 — Storage-interface-dependent authorization failure

### Severity
Medium

### CVSS
- Version: 4.0
- Label: CVSS-B
- Score: 6.8
- Vector: `CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N`

### Description
PlayerV2 Phoenix relies on a storage-interface-specific hardware identity assumption during authorization. The current implementation expects the protected media to appear specifically as `mmcblk0`. When the same authorized player microSD is presented through an external USB SD adapter, the runtime device path changes to `sda`, and the trust logic no longer evaluates the media through a stable identity abstraction.

In practice, this means the authorization control can be bypassed by changing the storage presentation path without changing the media itself. The weakness is not that the system cannot read the correct data, but that it binds trust to a Linux device-name assumption instead of a transport-independent identity model.

### Evidence
During the engagement, the same Phoenix player microSD was booted through an external USB SD reader. In that state:
- `lsblk` and mount output showed the boot and root partitions under `/dev/sda1` and `/dev/sda2`
- `lsusb` confirmed the external SD reader presence
- `hardware_lock.py` read only `/sys/block/mmcblk0/device/cid`
- `unlock_vault.py` repeated the same `mmcblk0`-specific assumption
- `hardware-check.service` crashed with `FileNotFoundError` when `/sys/block/mmcblk0/device/cid` was unavailable

### Impact
This flaw weakens the intended hardware-bound authorization boundary. An attacker with physical access can alter how the same authorized storage is presented to the system and cause the device to enter a more accessible state than intended. Even though the attack path is physical, physical access is central to this engagement and to the product’s actual tamper-resistance claims.

### CVSS rationale
This was scored as **CVSS-B 6.8 / Medium** because the attack requires physical handling of the device media path, but does not require prior privileges, credentials, or victim interaction. The finding is scoped to the authorization-bypass condition itself. The more direct fail-open local-access consequence is intentionally handled separately in PHX-V02.

### Assumptions
- Base-only scoring was used for this pass
- Threat and Environmental metrics were not enriched
- No subsequent-system impact is claimed in this finding
- The finding is limited to the authorization failure condition, not the preserved shell/GUI access that followed

### Remediation
Refactor the authorization logic so that it binds to the protected media identity regardless of whether the storage is presented through the native slot or an external reader. Use stable device attributes rather than a fixed Linux block-device name, and deny access safely when trusted identity cannot be confirmed.

### Hardening recommendations
- Centralize device-identity resolution in a single reusable component
- Remove hardcoded assumptions about `mmcblk0`
- Add explicit fail-closed handling when identity attributes are unavailable
- Add integration tests that simulate alternate storage presentation methods such as USB-attached readers

### Retest guidance
Reboot the same authorized media in both the native slot and a USB SD reader. Confirm that authorization remains correct in both cases, and that any identity-read failure results in a controlled locked state rather than altered accessibility.

---

## Finding PHX-V02 — Fail-open local access after hardware-check crash

### Severity
High

### CVSS
- Version: 4.0
- Label: CVSS-B
- Score: 7.3
- Vector: `CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N`

### Description
When Phoenix authorization failed in the USB-presented boot state, the enforcement path did not deny access safely. Instead, the hardware-check component crashed, and the device retained local GUI and terminal access long enough for meaningful local reconnaissance. This is a classic fail-open outcome in a security-sensitive control path.

The issue is distinct from the authorization-bypass condition in PHX-V01. PHX-V01 explains how the trust decision is broken. PHX-V02 captures what happens when that broken trust path fails unsafely, namely, the operator keeps access instead of being confined by the lock workflow.

### Evidence
During the USB-presented boot path:
- `hardware-check.service` repeatedly exited with `1/FAILURE`
- the traceback terminated at missing `/sys/block/mmcblk0/device/cid`
- the expected wrong-device takeover did not reassert in the same way it had during direct-slot behavior
- GUI and terminal access remained available long enough to perform local shell-based reconnaissance as user `pi`

### Impact
A local attacker can preserve interactive access to the underlying OS environment when the authorization component crashes. This defeats the intended deny-by-default behavior and exposes confidentiality and integrity on the vulnerable system. In a device intended to enforce local lockout, preserving local shell/GUI access after enforcement failure is a high-value control failure.

### CVSS rationale
This was scored as **CVSS-B 7.3 / High** because the path still requires physical access, but it does not require prior credentials or user interaction, and it yields direct access to local system state. Confidentiality and integrity impacts are both high because the exposed session can reveal system information and permit local actions. Availability impact is limited rather than high because the device remains partially operational rather than fully destroyed or permanently denied.

### Assumptions
- Base-only scoring was used for this pass
- Threat and Environmental metrics were not enriched
- The finding is intentionally kept separate from PHX-V01
- No broader subsequent-system impact is claimed without separate validation

### Remediation
Implement explicit fail-closed behavior across all authorization-check error paths. If hardware identity cannot be validated, the device should enter a minimal locked state that blocks shell and GUI access until an authenticated recovery workflow is completed.

### Hardening recommendations
- Add exception-safe guardrails around hardware-check execution
- Ensure lock-state enforcement occurs independently of nonessential UI startup
- Add negative-path integration tests for missing or renamed device identities
- Verify service-ordering so that lock behavior asserts before any interactive local interface is available

### Retest guidance
Repeat the USB-presented boot path after remediation and confirm that any identity-read failure produces a locked state rather than continued local GUI or shell access. Review logs and service status to verify safe denial rather than crash-driven exposure.

---

## Finding PHX-V03 — Sensitive provisioning artifact exposure in shell history

### Severity
High

### CVSS
- Version: 4.0
- Label: CVSS-B
- Score: 7.1
- Vector: `CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N`

### Description
The Phoenix device preserved operationally sensitive provisioning material in local shell history. The recovered command exposed the provisioning host, encrypted setup artifact path, decryption workflow, and a plaintext passphrase. Even where a historical secret may not remain universally valid forever, retaining this material in shell history provides attackers with both sensitive knowledge and a potentially reusable attack component.

In this engagement, the exposure is not treated as harmless residue. It is treated as meaningful attacker material that could realistically support follow-on compromise if defenders miss it, especially when combined with the fail-open local-access path.

### Evidence
`/home/pi/.bash_history` contained the exact command:

```bash
curl -fsSL http://3.211.184.159:8080/setup.enc | openssl enc -aes-256-cbc -d -salt -pbkdf2 -k "theNTVofthe360isthe360oftheNTV" | sudo bash
```

Additional shell-history entries confirmed direct local operator use of the environment, including:
- `pinctrl get 2-27`
- `sudo raspi-config`
- `ip addr`
- `ls`
- `ls -la`

### Impact
An attacker who reaches local shell access can recover plaintext provisioning material and deployment workflow details that may support reinstall paths, recovery-path abuse, or related environment compromise. Even when a specific secret later changes, historical provisioning logic and passphrase exposure still reduce attacker effort and may expose durable deployment patterns across similar systems.

### CVSS rationale
This was scored as **CVSS-B 7.1 / High** because local access to the shell history is required, but in the current Phoenix context that local access was realistically obtainable through the verified fail-open path. No additional user interaction is needed. Confidentiality and integrity were both scored high because the exposed provisioning material may assist further compromise or unauthorized setup actions. Availability was kept limited because direct service denial was not the primary effect.

### Assumptions
- Base-only scoring was used for this pass
- Threat and Environmental metrics were not enriched
- The score assumes the exposed provisioning command and passphrase remain operationally useful enough to support attacker chaining
- No broader subsequent-system or fleet-wide impact is claimed unless separately validated

### Remediation
Remove secret-bearing provisioning commands from shell history, move setup secrets into protected noninteractive mechanisms, and rotate any passphrases, bootstrap artifacts, or related deployment credentials that may still be valid.

### Hardening recommendations
- Disable or tightly restrict shell history for privileged provisioning workflows
- Use one-time, device-bound, or centrally rotated provisioning tokens instead of reusable plaintext passphrases
- Audit historical images, gold masters, and bootstrap scripts for embedded operational secrets
- Minimize local persistence of setup workflows that expose decryption or installation logic

### Retest guidance
After remediation, confirm that shell history no longer stores secret-bearing provisioning commands, verify that any exposed passphrase has been rotated or invalidated, and test that recovered historical setup material cannot be reused successfully.

## Recommended next reporting move

Use PHX-V01 through PHX-V03 as the first-wave Phoenix findings set in the final report. Keep PHX-V04 as likely supporting root-cause material, and keep PHX-V05 through PHX-V07 in validation flow until they are either proven or downgraded to contextual hardening observations.
