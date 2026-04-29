# PlayerV2 Phoenix — PHX-V01 to PHX-V03 Finding Blocks

Date: 2026-04-29
Target: playerv2-phoenix
Scoring standard: CVSS v4.0
Published stage: CVSS-B

## Scope note

These are the first fully score-ready Phoenix vulnerability findings.
They are kept separate on purpose:
- **PHX-V01** is the authorization-bypass condition
- **PHX-V02** is the fail-open exposure consequence
- **PHX-V03** is the sensitive artifact exposure that becomes reachable and operationally useful in that exposed state

---

## PHX-V01 — Storage-interface-dependent authorization failure

- **finding_id:** PHX-V01
- **title:** Storage-interface-dependent authorization failure
- **severity:** Medium
- **validation_status:** Verified
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** 6.8
- **cvss_vector:** CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N
- **cvss_severity:** Medium
- **cvss_rationale:** The attack requires physical access because the same trusted media must be presented through an alternate transport path, but no prior credentials or user interaction are required. The vulnerability breaks the intended media-bound authorization logic and materially weakens the local trust boundary of the Phoenix player.
- **cvss_assumptions:** Base-only scoring was used. Threat and Environmental metrics were not enriched. This finding is scored as the authorization-bypass condition itself, not the full fail-open access consequence, which is intentionally separated into PHX-V02.
- **cve_ids:** []
- **cwe_ids:** ["CWE-306", "CWE-693", "CWE-20"]
- **evidence:** The same Phoenix player microSD booted successfully through a USB SD reader. The runtime block device shifted from `mmcblk0` to `sda`. Both `hardware_lock.py` and `unlock_vault.py` depended on `/sys/block/mmcblk0/device/cid`, and `hardware-check.service` failed with `FileNotFoundError` because the expected path did not exist in the alternate presentation mode.
- **impact:** The intended hardware authorization boundary can be bypassed by changing only how the trusted media is presented to the OS. This weakens local device trust decisions and enables a more exposed operating state than the design intended.
- **remediation:** Bind authorization checks to stable media identity rather than a fixed Linux device name. Resolve trusted-media identity through attributes that remain valid across supported transport paths, and explicitly deny access when the device identity cannot be confirmed.
- **hardening_recommendations:** Centralize media-identity resolution, make alternate storage-presentation tests part of pre-release validation, and ensure all identity-read failures resolve into deterministic fail-closed behavior.
- **retest_guidance:** Reboot the same authorized media through both the internal slot and an external USB SD reader. Confirm the device still recognizes the trusted media correctly or denies access safely when identity resolution fails.

---

## PHX-V02 — Fail-open local access after hardware-check crash

- **finding_id:** PHX-V02
- **title:** Fail-open local access after hardware-check crash
- **severity:** High
- **validation_status:** Verified
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** 7.3
- **cvss_vector:** CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N
- **cvss_severity:** High
- **cvss_rationale:** Physical access is required, but the attacker does not need existing credentials or victim interaction. When the enforcement component crashes, Phoenix preserves interactive shell and GUI access instead of failing into a safe locked state, creating direct confidentiality and integrity exposure on the vulnerable device.
- **cvss_assumptions:** Base-only scoring was used. Threat and Environmental metrics were not enriched. This finding is intentionally scored as the fail-open consequence after enforcement failure, separate from the authorization-bypass mechanics in PHX-V01. Availability impact is limited because the device remains partially functional rather than completely denied.
- **cve_ids:** []
- **cwe_ids:** ["CWE-754", "CWE-248", "CWE-693"]
- **evidence:** `hardware-check.service` repeatedly exited with `1/FAILURE`, with traceback ending at the missing `/sys/block/mmcblk0/device/cid` path. The expected lock takeover did not reassert, and GUI plus terminal access remained available long enough for local reconnaissance as user `pi`.
- **impact:** A local attacker can preserve interactive access to the underlying OS environment when the lock-enforcement component fails, defeating intended deny-by-default local protection.
- **remediation:** Make all authorization-check exceptions fail closed. If hardware identity validation fails, force the device into a minimal locked state that blocks shell and GUI access until an authenticated recovery workflow completes.
- **hardening_recommendations:** Add exception-safe control flow around lock enforcement, isolate lock-state assertion from nonessential UI startup, and add negative-path tests that verify renamed, missing, or inaccessible device identities cannot expose an interactive session.
- **retest_guidance:** Repeat the USB-presented boot path and verify that identity-read failure results in enforced lock state rather than continued GUI or shell exposure. Confirm logs show safe denial, not crash-driven access.

---

## PHX-V03 — Sensitive provisioning artifact exposure in shell history

- **finding_id:** PHX-V03
- **title:** Sensitive provisioning artifact exposure in shell history
- **severity:** High
- **validation_status:** Verified
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** 7.1
- **cvss_vector:** CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N
- **cvss_severity:** High
- **cvss_rationale:** The attacker needs local shell access to view the history context, which was realistically reachable through the observed fail-open path. No user interaction is needed, and the exposed provisioning command reveals plaintext secret material plus workflow details that may be operationally useful for further compromise.
- **cvss_assumptions:** Base-only scoring was used. Threat and Environmental metrics were not enriched. This score assumes the exposed setup passphrase and command structure remain materially useful in the current deployment context. No separate subsequent-system impact is claimed until broader infrastructure misuse is directly validated.
- **cve_ids:** []
- **cwe_ids:** ["CWE-532", "CWE-312", "CWE-798"]
- **evidence:** `/home/pi/.bash_history` contained the full command `curl -fsSL http://3.211.184.159:8080/setup.enc | openssl enc -aes-256-cbc -d -salt -pbkdf2 -k "theNTVofthe360isthe360oftheNTV" | sudo bash` together with related operator commands, confirming direct local exposure of provisioning material and workflow.
- **impact:** An attacker with local shell access can recover plaintext provisioning material, installation workflow details, and a potentially reusable setup secret that may support recovery-path abuse, reinstall abuse, or related operational compromise.
- **remediation:** Remove secret-bearing bootstrap commands from shell history, rotate any exposed passphrases or related deployment material, and move provisioning secrets into protected noninteractive delivery paths.
- **hardening_recommendations:** Disable or tightly restrict shell history for privileged provisioning operations, use one-time or device-bound provisioning secrets, and audit historic images or gold masters for embedded operational credentials.
- **retest_guidance:** After remediation, confirm shell history no longer captures secret-bearing provisioning commands, confirm prior passphrases are invalidated or rotated, and verify recovered historical setup material cannot be reused successfully.
