# PlayerV2 Phoenix — Technical Report

Date: 2026-04-29
Target: playerv2-phoenix
Status: Final draft for current engagement state
Scoring standard: CVSS v4.0

## 1. Executive technical summary

The current Phoenix assessment identified three verified findings that form a coherent local attack chain, plus one supporting architectural weakness and one meaningful but still unverified recovery-path candidate.

Importantly, the engagement did not stop at passive vulnerability observation. The PHX-V01 to PHX-V02 chain was successfully exercised in practice, producing a meaningful local foothold. From that foothold, the assessment entered bounded post-exploitation through local reconnaissance and sensitive artifact recovery.

The verified path is:
1. **PHX-V01** — authorization can be disrupted by changing how the same storage is presented to the device
2. **PHX-V02** — when that trust path fails, enforcement crashes and preserves local access instead of denying it safely
3. **PHX-V03** — once local access is preserved, sensitive provisioning material can be recovered from shell history

A supporting architectural issue, **PHX-V04**, helps explain why the trust failure propagates into a wider inconsistent security state. A separate recovery-path concern, **PHX-V05**, is supported by recovered script evidence but remains unverified because live acceptance testing could not be completed without the required repair image or alternate test image.

## 2. Report scope for this draft

This report reflects the current validated state of the Phoenix engagement.

### Verified findings
- **PHX-V01 — Storage-interface-dependent authorization failure**
- **PHX-V02 — Fail-open local access after hardware-check crash**
- **PHX-V03 — Sensitive provisioning artifact exposure in shell history**

### Supporting architecture
- **PHX-V04 — Fragile vault authorization chain and dependency-only gating**

### Supported but unverified candidate
- **PHX-V05 — Recovery-path abuse potential via `repairman.sh`**

### Secondary or contextual items not promoted as final findings in this draft
- **PHX-V06** — supported / partially observed startup-race candidate, not yet reproducible enough for final scoring
- **PHX-V07** — low-severity local availability candidate or hardening observation, not yet bounded tightly enough for final scoring
- **PHX-V08** — environment context only, not a standalone report finding

## 3. Verified finding chain

The strongest Phoenix story is not a loose collection of unrelated issues. It is a sequence of trust and enforcement failures.

First, the device’s authorization logic depends on the storage appearing as `mmcblk0`, rather than identifying the trusted media in a transport-independent way. That makes the trust decision fragile.

Second, when this trust assumption breaks in the USB-presented path, the enforcement component does not fail closed. It crashes and leaves the operator with local shell or GUI access.

Third, that preserved local access exposes operationally valuable provisioning material in shell history, including a setup host, decryption workflow, and plaintext passphrase.

This sequence matters because it shows cause, consequence, and attacker value in a clean progression. It also means the engagement already crossed from vulnerability validation into actual local exploitation and early post-exploitation, even though deeper privilege escalation, persistence, and broader environment impact were intentionally left bounded by the evidence.

## 4. Supporting root-cause architecture — PHX-V04

**PHX-V04 — Fragile vault authorization chain and dependency-only gating** is not promoted here as a top-tier standalone finding. Its attacker benefit overlaps heavily with PHX-V01 and PHX-V02. However, it materially explains the failure pattern.

The current design chains `vault-mount.service` behind `hardware-check.service`, and the vault-unlock logic repeats the same `mmcblk0`-specific assumption already seen in the main authorization path. This means the device duplicates a brittle trust dependency across linked components, increasing the chance that a single device-path mismatch will produce a wider unsafe state.

This architectural duplication strengthens the remediation case for:
- centralized device-identity resolution
- transport-independent trusted-media validation
- fail-closed behavior when identity checks cannot complete
- dependency design that resolves into a deterministic locked state rather than a semi-operational accessible state

---

## 5. Finding PHX-V01 — Storage-interface-dependent authorization failure

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
- The finding is limited to the authorization failure condition, not the preserved shell or GUI access that followed

### Remediation
Refactor the authorization logic so that it binds to the protected media identity regardless of whether the storage is presented through the native slot or an external reader. Use stable device attributes rather than a fixed Linux block-device name, and deny access safely when trusted identity cannot be confirmed.

### Hardening recommendations
- Centralize device-identity resolution in a single reusable component
- Remove hardcoded assumptions about `mmcblk0`
- Add explicit fail-closed handling when identity attributes are unavailable
- Eliminate duplicated trust assumptions between `hardware-check.service` and vault-unlock workflows
- Add integration tests that simulate alternate storage presentation methods such as USB-attached readers

### Retest guidance
Reboot the same authorized media in both the native slot and a USB SD reader. Confirm that authorization remains correct in both cases, and that any identity-read failure results in a controlled locked state rather than altered accessibility.

---

## 6. Finding PHX-V02 — Fail-open local access after hardware-check crash

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
A local attacker can preserve interactive access to the underlying OS environment when the authorization component crashes. This defeats the intended deny-by-default behavior and exposes confidentiality and integrity on the vulnerable system. In a device intended to enforce local lockout, preserving local shell or GUI access after enforcement failure is a high-value control failure.

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

## 7. Finding PHX-V03 — Sensitive provisioning artifact exposure in shell history

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

---

## 8. Supported candidate — PHX-V05 Recovery-path abuse potential via `repairman.sh`

### Status
Supported, not verified in the current engagement state

### Why it matters
Recovered Phoenix recovery scripts show a real automatic USB-boot recovery path that performs direct SD repair and `rsync` mirroring from the USB runtime onto the mounted SD root. In the reviewed script logic, no visible signature, authenticity, or operator-authentication gate was found before restore actions proceeded.

If that path accepts attacker-controlled content in practice, it could become a meaningful integrity-impact recovery-path weakness.

### Current evidence basis
- recovered `repairman.sh` and setup artifacts show a real Phoenix recovery path
- the path appears to trust the booted USB runtime as the repair source
- the script performs `fsck`, mounts the SD root, mirrors `/` from the USB runtime, rebuilds `fstab`, restores firmware configuration, toggles services, and reboots
- no visible cryptographic validation or trust gate was observed in the reviewed script body

### Why it is not verified yet
The engagement did **not** complete a live acceptance replay using the required repair image or an alternate test image, because that media was not available during the assessment state covered by this report.

This is a coverage limitation, not contradictory evidence. The candidate remains meaningful, but it is not presented here as a finished verified finding.

### Reporting position
- keep PHX-V05 visible in the report as a supported candidate
- do not assign a final score yet
- do not present it as live-confirmed attacker-controlled acceptance
- keep PHX-V06 and PHX-V07 outside the main scored finding set unless later replay tightens reproducibility and impact framing

### Recommended follow-up
When a repair image or alternate test image becomes available, perform a controlled safest-first replay:
1. non-destructive acceptance proof
2. sacrificial-media write proof if needed
3. final finding promotion only if acceptance is confirmed

---

## 9. Final finding set for current report state

### Main verified findings
- PHX-V01
- PHX-V02
- PHX-V03

### Supporting architecture
- PHX-V04

### Supported candidate pending future validation
- PHX-V05

### Secondary or contextual items retained outside the main finding set
- PHX-V06 — supported / partially observed startup-race candidate
- PHX-V07 — low-severity local availability candidate or hardening observation
- PHX-V08 — context only

## 10. Recommended retest priorities

1. Re-test trusted-media identity handling across native-slot and USB-presented paths
2. Re-test fail-closed behavior on hardware-check exceptions
3. Remove and rotate sensitive provisioning residue, then verify the cleanup
4. Perform controlled PHX-V05 recovery-path validation once required media becomes available
5. Revisit PHX-V06 only if repeated boot-cycle evidence can bound the startup exposure window cleanly
6. Revisit PHX-V07 only if the shutdown/disruption path can be reproduced and justified as more than a hardening issue

## 11. Conclusion

The most important Phoenix risks in the current engagement state are not broad network exposure issues. They are local trust, enforcement, and operational-secret handling failures.

The verified findings already show that Phoenix can:
- make the wrong trust decision when storage presentation changes
- fail open when that trust path breaks
- expose operationally useful provisioning material once local access is preserved

That is already a meaningful and defensible finding set. PHX-V05 remains worth keeping in view, but the report should stay disciplined and distinguish clearly between code-backed concern and live-confirmed exploitability.
