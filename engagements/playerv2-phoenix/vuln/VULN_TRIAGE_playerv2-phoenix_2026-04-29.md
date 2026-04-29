# PlayerV2 Phoenix — Vulnerability Triage (2026-04-29)

## Scope and Intent

This triage sheet is specific to the **playerv2-phoenix** pentest engagement.
It is not a generic Raspberry Pi list, not a cross-engagement merge, and not a final findings report.
Its purpose is to convert the currently verified recon and enumeration evidence for **PlayerV2 Phoenix** into a vulnerability-phase working set that is ready for:
- CVSS v4.0 scoring
- practical prioritization
- downstream finding development for Raph/reporting
- controlled exploit-validation planning

This file deliberately separates:
- **technical severity** from
- **practical pentest priority** from
- **human override judgment**

That matters here because several Phoenix issues are strongly evidenced but physical/local in attack path, while others are architecturally important but still need one more validation step before they become report-ready findings.

## Scoring Model Used Here

Workspace default:
- **CVSS v4.0 Base** is the active default scoring standard for new scoring work in this workspace.

This triage file does **not** assign final numeric scores yet.
Instead, it prepares each Phoenix candidate with:
- validation status
- evidence basis
- likely CVSS v4 input direction
- practical exploitation priority
- recommended human override note

Use this as the bridge between recon/enum and full vulnerability write-up.

## Priority Buckets

### Priority 1
Strongest, best-evidenced, and most likely to become immediate report-ready findings.

### Priority 2
High-value candidates that are likely real or important, but still need one more validation step or clearer finding boundaries.

### Priority 3
Meaningful hypotheses that may become findings, but should not be scored as confirmed yet.

### Priority 4
Contextual/supporting observations, not report-ready vulnerabilities by themselves.

---

## Candidate PHX-V01 — Storage-interface-dependent authorization failure

### Current status
- **Validation status:** Verified
- **Confidence:** High
- **Priority bucket:** Priority 1

### Core claim
PlayerV2 Phoenix authorization logic depends on the protected storage being visible specifically as `mmcblk0`, and fails when the same authorized player image is presented through a USB SD reader as `sda`.

### Evidence basis
Verified during the playerv2-phoenix engagement by:
- booting the same player microSD through an external USB SD adapter
- observing that the device still boots into the NTV startup sequence
- confirming that the runtime storage path becomes `/dev/sda` instead of `/dev/mmcblk0`
- confirming that the lock path does not assert normally in this mode
- confirming through logs and code review that the authorization path reads `/sys/block/mmcblk0/device/cid`

### Exact supporting facts
- `lsblk` and mount output showed:
  - `/dev/sda1` mounted on `/boot/firmware`
  - `/dev/sda2` mounted on `/`
- `lsusb` showed the external SD reader present
- `hardware_lock.py` reads only:
  - `/sys/block/mmcblk0/device/cid`
- `unlock_vault.py` also reads only:
  - `/sys/block/mmcblk0/device/cid`
- `hardware-check.service` crashed with:
  - `FileNotFoundError: [Errno 2] No such file or directory: '/sys/block/mmcblk0/device/cid'`

### Why this matters
The system’s trust model appears to assume a single hardware presentation path rather than robustly binding authorization to the actual protected media in all legitimate presentation modes. That brittle assumption creates a practical bypass condition for the local lock workflow.

### Likely weakness class
- brittle hardware binding
- improper authorization dependency on device-path assumption
- fail-unsafe local enforcement design

### Technical impact
This condition undermines the intended hardware-lock boundary by allowing the same player image to boot into a more accessible local state when the storage is presented differently.

### Likely CVSS v4 direction
Preliminary vector direction, not final:
- attack vector likely **Physical**
- attack complexity likely **Low** or **Low/Moderate boundary**
- privileges required likely **None** pre-attack
- user interaction likely **None** or minimal operator handling only
- confidentiality/integrity/availability impact depends on whether local access is treated separately or merged with PHX-V02

### Practical pentest priority
- **Very high**
- This is the cleanest and strongest Phoenix vulnerability candidate right now.
- It is already strongly evidenced and likely report-ready once the finding boundary is finalized.

### Human override guidance
Even if the final CVSS base score is moderated by the physical attack vector, human priority should remain high because:
- the control is explicitly intended to prevent local access
- the bypass is reproducible
- the issue directly defeats the product’s trust-boundary claim
- the physical access scenario is already in scope for this engagement

### Recommended next vuln-phase action
- Decide whether PHX-V02 is a separate finding or a technical consequence/subsection of this one.
- Then draft the full finding with evidence and remediation.

---

## Candidate PHX-V02 — Fail-open local access after hardware-check crash

### Current status
- **Validation status:** Verified
- **Confidence:** High
- **Priority bucket:** Priority 1 or merged into PHX-V01

### Core claim
When Phoenix authorization fails in USB-presented boot mode, the enforcement control crashes rather than denying access safely, and the operator retains GUI/terminal access.

### Evidence basis
Verified during the playerv2-phoenix engagement by:
- observing GUI persistence instead of wrong-device lock takeover
- obtaining local terminal access as user `pi`
- reviewing `hardware_lock.py`
- collecting repeated `hardware-check.service` crash traces

### Exact supporting facts
- `hardware-check.service` exits with `1/FAILURE`
- traceback ends at missing `/sys/block/mmcblk0/device/cid`
- device remains usable enough for local shell-based recon
- wrong-device takeover does not reassert in the same way it did under direct-slot boot

### Why this matters
A security control should fail closed or at least fail safe. Here, the error path preserves local operator access, which is the opposite of the intended security objective.

### Likely weakness class
- fail-open security control
- improper exception handling in access enforcement
- denial of enforcement through unhandled runtime assumption

### Technical impact
A local attacker who can trigger the storage-presentation mismatch can preserve access to the underlying OS environment instead of being contained by the lock workflow.

### Likely CVSS v4 direction
Preliminary direction, not final:
- same physical path considerations as PHX-V01
- stronger direct integrity/confidentiality relevance than PHX-V01 if reported separately because the effect is explicit access retention

### Practical pentest priority
- **Very high**
- Strong impact and easy to explain.

### Human override guidance
This may be better scored as part of PHX-V01 to avoid splitting trigger and impact too mechanically.
If reported separately, be careful not to double-count the same exploit path.

### Recommended next vuln-phase action
- Decide report structure:
  - merge into PHX-V01 as the demonstrated impact path, or
  - keep separate if the client benefits from explicit fail-open classification

---

## Candidate PHX-V03 — Sensitive provisioning artifact exposure in shell history

### Current status
- **Validation status:** Verified as exposure
- **Confidence:** High for existence, Medium for downstream exploitability
- **Priority bucket:** Priority 1 or Priority 2 depending on live reusability

### Core claim
Local shell history on the Phoenix device preserved a provisioning command containing a setup host, encrypted provisioning artifact reference, and provisioning passphrase.

### Evidence basis
Verified during the playerv2-phoenix engagement by reading `/home/pi/.bash_history` in the USB-presented local shell state.

### Exact supporting facts
Recovered exact command:
```bash
curl -fsSL http://3.211.184.159:8080/setup.enc | openssl enc -aes-256-cbc -d -salt -pbkdf2 -k "theNTVofthe360isthe360oftheNTV" | sudo bash
```

Additional local shell history entries included:
- `pinctrl get 2-27`
- `sudo raspi-config`
- `ip addr`
- `ls`
- `ls -la`

### Why this matters
This reveals operationally sensitive provisioning logic and preserves a passphrase in plaintext historical artifact form. Even if the exact passphrase is no longer valid for the current vault, it still exposes installation workflow details and may support future chaining.

### Likely weakness class
- insecure credential/secret handling
- sensitive operational artifact retention
- unsafe shell-history exposure of deployment material

### Technical impact
An attacker who reaches local shell history may recover sensitive provisioning intelligence and potentially reusable secret material.

### Likely CVSS v4 direction
Preliminary direction, not final:
- attack vector likely **Local** or **Physical-derived Local**
- confidentiality impact likely meaningful
- direct integrity/availability impact depends on whether the recovered passphrase still works against current artifacts

### Practical pentest priority
- **High**
- especially because the evidence is real and local, not hypothetical
- but it should be separated into:
  - confirmed artifact exposure, and
  - unconfirmed live exploitability of the recovered passphrase

### Human override guidance
Do not overclaim this as an active secret compromise until reusability is validated.
Still, even as a historical artifact exposure finding, it is report-worthy in a system that is supposed to enforce strong hardware-tied protection.

### Recommended next vuln-phase action
- Validate whether the provisioning passphrase is still materially useful for this build or related assets.
- If yes, severity likely rises.
- If no, keep as verified exposure with moderated impact.

---

## Candidate PHX-V04 — Fragile vault authorization chain and dependency-only gating

### Current status
- **Validation status:** Supported
- **Confidence:** Medium-high
- **Priority bucket:** Priority 2

### Core claim
Vault access control depends on a brittle upstream hardware-check dependency rather than a more resilient independent authorization workflow.

### Evidence basis
Supported by unit definitions and service behavior:
- `vault-mount.service` requires `hardware-check.service`
- vault unlock never executes in the USB-presented state because dependency fails first
- `unlock_vault.py` itself repeats the same brittle `mmcblk0` CID assumption

### Why this matters
A critical security boundary, the encrypted secure runtime, inherits fragility from an upstream enforcement component that can crash on device-path assumptions.

### Likely weakness class
- weak trust-chain composition
- brittle dependency design
- duplicated unsafe device-identity assumption

### Technical impact
This can create inconsistent security states where the lock boundary fails, the vault stays unavailable, and the system enters an unintended semi-operational local-access state.

### Likely CVSS v4 direction
This may be better treated as a supporting architectural basis rather than a stand-alone scored finding unless a separate attacker benefit is clearly shown.

### Practical pentest priority
- **Medium-high**
- important for explanation and remediation
- may become a supporting section inside PHX-V01 rather than its own top-level finding

### Human override guidance
Prefer clarity over finding count inflation. If PHX-V01 already explains the issue well, PHX-V04 may belong under technical basis / root cause.

### Recommended next vuln-phase action
- Decide whether to keep as standalone architectural weakness or merge into PHX-V01 root cause.

---

## Candidate PHX-V05 — Recovery-path abuse potential via `repairman.sh`

### Current status
- **Validation status:** Hypothesis
- **Confidence:** Medium
- **Priority bucket:** Priority 3

### Core claim
Phoenix recovery logic may trust external repair sources in a way that could permit unauthorized restore or content injection if an attacker can satisfy the expected repair-source structure.

### Evidence basis
Supported by code review of `repairman.sh` and runtime behavior of `repairman.service` and `nctv-watchdog.sh`.

### Exact supporting facts
- `repairman.sh` searches for repair roots such as:
  - `/mnt/repair-drive/nctv-phoenix`
  - `/media/pi/*/nctv-phoenix`
  - `/run/media/pi/*/nctv-phoenix`
  - `/mnt/*/nctv-phoenix`
- if a source is found and `/dev/mmcblk0` exists, it can perform a surgical restore onto the main SD
- `nctv-watchdog.sh` can touch `/run/nctv-phoenix-repair-needed` and start `repairman.service`

### Why this matters
Recovery and maintenance paths are common high-impact trust boundaries. If they accept attacker-controlled content without strong validation, they can become privileged code/content injection paths.

### Likely weakness class
- insecure recovery/update path
- trust of external media/source without demonstrated authenticity control

### Technical impact
Potential integrity compromise of player runtime or storage if a crafted repair source can be accepted and applied.

### Likely CVSS v4 direction
Too early for final direction. Attack path likely physical/local, but impact could be large if the restore path is controllable.

### Practical pentest priority
- **Medium**
- worth validating, but only after stronger verified findings are formalized

### Human override guidance
Do not score this as confirmed until source acceptance and abuse feasibility are actually demonstrated.

### Recommended next vuln-phase action
- Validate expected repair-source structure and whether authenticity or signature checks exist.

---

## Candidate PHX-V06 — Pre-lock startup race exposing shell/GUI access

### Current status
- **Validation status:** Supported / partially observed
- **Confidence:** Medium
- **Priority bucket:** Priority 3

### Core claim
During direct-slot boot, there appears to be a short-lived race or ordering issue in which shell or GUI state becomes visible before the lock workflow fully takes over.

### Evidence basis
Supported by prior observed `tty1` and GUI exposure, boot-time key interactions, and service-order-cycle clues.

### Exact supporting facts
- transient `tty1` shell exposure was previously observed
- GUI exposure during startup was observed before later takeover
- systemd ordering-cycle messages referenced Phoenix target and graphical target interactions

### Why this matters
Even without the USB-presented bypass, the startup chain itself may expose a temporary local attack window before the intended lock boundary asserts.

### Likely weakness class
- startup race condition
- improper service ordering
- pre-auth local exposure window

### Technical impact
A well-timed local attacker may gain interaction before the lock path asserts, depending on reproducibility and what actions fit in the window.

### Likely CVSS v4 direction
Not ready for reliable scoring until reproducibility and practical exploitability are better bounded.

### Practical pentest priority
- **Medium**
- interesting and potentially useful, but lower than the USB-presented branch because the latter is more stable and better evidenced

### Human override guidance
Treat as a meaningful hypothesis, not a polished final finding yet.

### Recommended next vuln-phase action
- If time permits, run a controlled reproducibility check and document exact achievable actions in the pre-lock window.

---

## Candidate PHX-V07 — Exposed physical shutdown / local availability disruption path

### Current status
- **Validation status:** Supported
- **Confidence:** Medium
- **Priority bucket:** Priority 3

### Core claim
The current Phoenix local environment appears to expose a physical key path that can trigger shutdown or poweroff behavior without normal authorization.

### Evidence basis
Supported by operator observations and visible system shutdown target messages during interaction with `Fn+Esc` and related key sequences.

### Why this matters
For a revenue-generating signage player, unauthorized local shutdown is an availability issue even if it does not directly yield code execution.

### Likely weakness class
- kiosk hardening gap
- exposed local administrative availability control

### Technical impact
Potential denial of service with physical access.

### Likely CVSS v4 direction
Availability-focused, likely lower overall than PHX-V01/02/03 unless shutdown is proven extremely easy and reliable.

### Practical pentest priority
- **Medium-low**

### Human override guidance
Useful if the client cares heavily about uptime and anti-tamper posture. Otherwise likely secondary to access-control failures.

### Recommended next vuln-phase action
- Decide whether this belongs in the main findings set or a hardening observations section.

---

## Candidate PHX-V08 — Sparse network surface with state drift

### Current status
- **Validation status:** Context only
- **Confidence:** High as observation, Low as vulnerability
- **Priority bucket:** Priority 4

### Core claim
The external network surface showed a sparse but shifting service profile, including earlier SSH/rpcbind visibility and later filtered states.

### Why this matters
This is important operational context, but it is not a vulnerability finding by itself.

### Practical pentest priority
- **Low** as a vulnerability candidate
- **High** as environment context for later reasoning

### Human override guidance
Do not score this as a vuln unless it is tied to a concrete reachable weakness.

---

## Recommended Human Priority Order

This is the order I recommend for Phoenix vulnerability work, independent of eventual raw CVSS base score ordering.

1. **PHX-V01** — Storage-interface-dependent authorization failure
2. **PHX-V02** — Fail-open local access after hardware-check crash
3. **PHX-V03** — Sensitive provisioning artifact exposure in shell history
4. **PHX-V04** — Fragile vault authorization chain and dependency-only gating
5. **PHX-V05** — Recovery-path abuse potential
6. **PHX-V06** — Pre-lock startup race exposing shell/GUI access
7. **PHX-V07** — Exposed physical shutdown / local availability disruption path
8. **PHX-V08** — Sparse network surface with state drift

## Recommended Technical Severity vs Practical Priority Notes

### Where technical severity may understate real pentest importance
- **PHX-V01 / PHX-V02** may receive moderated base scoring because the attack path is physical.
- In this engagement, that should **not** reduce practical priority much, because physical access is explicitly in scope and central to the threat model.

### Where human judgment should override pure base-score ordering
- **PHX-V03** may score lower than the access-control failures if treated only as local artifact exposure.
- However, if the recovered provisioning passphrase is still operationally useful, human priority should rise sharply.

### Where restraint matters
- **PHX-V05 / PHX-V06 / PHX-V07** should not be inflated into top-tier findings until we convert them from supported hypotheses into verified exploit conditions.

## Recommended Next Validation Order

### First wave
1. Finalize whether **PHX-V01** and **PHX-V02** are merged or separated.
2. Draft their score-ready evidence blocks.
3. Validate whether **PHX-V03** is only historical exposure or still operationally useful.

### Second wave
4. Test **PHX-V05** in the safest possible controlled way.
5. Revisit **PHX-V06** only if more direct-slot timing evidence is still needed.

### Defer unless needed
6. **PHX-V07** and **PHX-V08** remain secondary unless the client strongly prioritizes uptime/disruption risk.

## Final note for downstream reporting

For Raph/report generation, the most important discipline is not to flatten these into one giant story.
The Phoenix evidence naturally separates into:
- primary authorization/control failure
- resulting local-access consequence
- provisioning-artifact exposure
- architectural/recovery-path supporting weaknesses

That separation will make the eventual scoring, remediation, and retest guidance much cleaner.
