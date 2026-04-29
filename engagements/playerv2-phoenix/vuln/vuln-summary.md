# PlayerV2 Phoenix — Vulnerability Summary

Date: 2026-04-29
Phase: Vulnerability Analysis
Target: playerv2-phoenix
Scoring standard: CVSS v4.0
Scoring label used for populated entries below: CVSS-B

## Analyst decisions locked in for this round

- **PHX-V01** and **PHX-V02 remain separate findings**
- **PHX-V03 is treated as still operationally useful**, not just stale historical exposure
- **PHX-V05 to PHX-V08 remain candidate-stage items** pending stronger validation

## Current finding-state overview

### Report-ready or near-report-ready
1. **PHX-V01 — Storage-interface-dependent authorization failure**
   - Validation status: Verified
   - CVSS status: score-ready
   - Recommended severity direction: High practical priority, Medium technical severity likely

2. **PHX-V02 — Fail-open local access after hardware-check crash**
   - Validation status: Verified
   - CVSS status: score-ready
   - Recommended severity direction: High practical priority, High technical severity within physical/local path constraints

3. **PHX-V03 — Sensitive provisioning artifact exposure in shell history**
   - Validation status: Verified
   - CVSS status: score-ready
   - Recommended severity direction: Medium-to-High depending on final wording around ongoing utility of the exposed passphrase/workflow

### Candidate-stage findings
4. **PHX-V04 — Fragile vault authorization chain and dependency-only gating**
   - Validation status: Supported
   - CVSS status: provisional only
   - Recommendation: likely root-cause/supporting finding unless separate attacker benefit is proven

5. **PHX-V05 — Recovery-path abuse potential via `repairman.sh`**
   - Validation status: Hypothesis
   - CVSS status: not scored yet
   - Recommendation: validate source acceptance and authenticity controls first

6. **PHX-V06 — Pre-lock startup race exposing shell/GUI access**
   - Validation status: Supported / partially observed
   - CVSS status: not scored yet
   - Recommendation: re-check reproducibility before full scoring

7. **PHX-V07 — Exposed physical shutdown / local availability disruption path**
   - Validation status: Supported
   - CVSS status: not scored yet
   - Recommendation: decide later whether this lands as a main finding or hardening observation

8. **PHX-V08 — Sparse network surface with state drift**
   - Validation status: Context only
   - CVSS status: not applicable as a standalone finding right now
   - Recommendation: keep as environment context only unless tied to a concrete weakness

## Score-ready finding blocks

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
- **cvss_rationale:** The attacker needs physical access to present the same protected media through a USB SD path, but no prior privileges or victim interaction are required. The bypass undermines the intended authorization boundary and can expose sensitive local system access conditions on the vulnerable device itself.
- **cvss_assumptions:** Base-only scoring was used. Threat and Environmental metrics were not enriched. This score treats the vulnerability as the authorization-bypass condition itself and keeps the more direct fail-open access consequence in PHX-V02. The vulnerable system is the Phoenix player, and no separate subsequent-system impact is claimed in Base.
- **cve_ids:** []
- **cwe_ids:** ["CWE-306", "CWE-693", "CWE-20"]
- **impact:** The intended hardware-bound authorization check can be bypassed by changing only the storage presentation path, weakening the product's local trust boundary and enabling a more accessible device state than intended.
- **evidence:** Same Phoenix player microSD booted successfully through a USB SD reader; runtime block device changed from `mmcblk0` to `sda`; `hardware_lock.py` and `unlock_vault.py` both depended on `/sys/block/mmcblk0/device/cid`; `hardware-check.service` crashed with `FileNotFoundError` for the missing mmc path.
- **remediation:** Refactor the authorization logic to bind to the actual protected media identity regardless of transport path, not a fixed Linux block-device name. Validate media identity through stable device attributes and explicitly deny access when the trusted identity cannot be confirmed.
- **hardening_recommendations:** Normalize media-identification logic across boot modes, add explicit fail-closed handling for identity-read errors, and add startup tests that simulate alternate storage presentation methods such as USB-attached readers.
- **retest_guidance:** Reboot the same authorized media through both the native slot and an external USB SD reader. Confirm the lock logic still identifies the trusted media correctly and denies or constrains access safely when identity checks fail.

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
- **cvss_rationale:** Physical access is required, but the attacker does not need existing credentials or user participation. Once the enforcement component crashes, the device preserves local shell/GUI access instead of failing safely, resulting in direct confidentiality and integrity exposure on the vulnerable system.
- **cvss_assumptions:** Base-only scoring was used. Threat and Environmental metrics were not enriched. This finding is intentionally kept separate from PHX-V01 and scored as the fail-open consequence after the authorization path crashes. Availability impact is limited rather than high because the device remains partially operational rather than fully destroyed or permanently denied.
- **cve_ids:** []
- **cwe_ids:** ["CWE-754", "CWE-248", "CWE-693"]
- **impact:** A local attacker can preserve interactive access to the underlying OS environment when the lock enforcement component crashes, defeating the intended deny-by-default behavior.
- **evidence:** `hardware-check.service` repeatedly exited with `1/FAILURE`; traceback terminated at missing `/sys/block/mmcblk0/device/cid`; wrong-device lock takeover did not reassert as expected; GUI and terminal access remained available long enough for local recon as user `pi`.
- **remediation:** Implement explicit fail-closed behavior for all authorization-check exceptions. If hardware identity cannot be validated, force the device into a minimal locked state that prevents shell and GUI access until an authenticated recovery procedure is completed.
- **hardening_recommendations:** Add exception-safe guardrails around hardware-check execution, isolate the lock path from nonessential UI startup, and add negative-path integration tests that verify inaccessible or renamed device identities do not expose an interactive session.
- **retest_guidance:** Repeat the USB-presented boot path and verify that an identity-read failure results in an enforced locked state rather than continued GUI or shell access. Confirm journal and service states show safe denial instead of crash-driven exposure.

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
- **cvss_rationale:** The attacker needs local access to the shell history context, which in this engagement was realistically obtainable after the fail-open path. No extra victim interaction is needed, and the recovered provisioning command exposes operationally useful secret material and deployment workflow details that may support further compromise.
- **cvss_assumptions:** Base-only scoring was used. Threat and Environmental metrics were not enriched. This score assumes the exposed provisioning passphrase and command structure remain operationally useful enough to support attack chaining, as judged from current engagement context. No separate subsequent-system impact is claimed until broader infrastructure abuse is directly validated.
- **cve_ids:** []
- **cwe_ids:** ["CWE-532", "CWE-312", "CWE-798"]
- **impact:** An attacker with local shell access can recover plaintext provisioning material, installation workflow details, and a potentially reusable setup passphrase that may support reinstallation, recovery-path abuse, or related environment compromise.
- **evidence:** `/home/pi/.bash_history` contained the full command `curl -fsSL http://3.211.184.159:8080/setup.enc | openssl enc -aes-256-cbc -d -salt -pbkdf2 -k "theNTVofthe360isthe360oftheNTV" | sudo bash` along with other operator commands that confirmed direct local shell history exposure.
- **remediation:** Remove plaintext secret-bearing bootstrap commands from shell history, move provisioning secrets into protected noninteractive channels, and rotate any passphrases, setup artifacts, or related deployment credentials that may still be valid.
- **hardening_recommendations:** Disable or tightly control shell history for privileged provisioning workflows, use one-time tokens or device-bound secrets for setup, and audit historical images or gold masters for embedded operational secrets.
- **retest_guidance:** After remediation, confirm shell history no longer captures secret-bearing provisioning commands, confirm any prior passphrase has been rotated or invalidated, and test that recovered historical setup material cannot be reused successfully.

---

## PHX-V04 — Fragile vault authorization chain and dependency-only gating

- **finding_id:** PHX-V04
- **title:** Fragile vault authorization chain and dependency-only gating
- **severity:** Medium
- **validation_status:** Supported
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** null
- **cvss_vector:** null
- **cvss_severity:** Medium
- **cvss_rationale:** Candidate-stage architectural weakness. The trust chain is brittle and appears to inherit the same device-identity assumption, but a separate attacker benefit beyond PHX-V01 and PHX-V02 has not been bounded cleanly enough for final scoring.
- **cvss_assumptions:** This item remains provisional. It should either be merged into PHX-V01 root cause analysis or scored separately only if distinct attacker leverage is demonstrated.
- **cve_ids:** []
- **cwe_ids:** ["CWE-693", "CWE-670"]
- **impact:** The vault-control path can enter an inconsistent state where a critical security boundary depends on a crash-prone upstream hardware-check assumption.
- **evidence:** `vault-mount.service` required `hardware-check.service`; vault unlock did not run in USB-presented mode because the dependency failed first; `unlock_vault.py` repeated the same `mmcblk0` CID assumption.
- **remediation:** Decouple vault authorization from brittle single-path device naming assumptions and design the chain so that authorization failure resolves into a deterministic secure state.
- **hardening_recommendations:** Reduce duplicated trust assumptions across services, centralize device-identity resolution, and add dependency-failure tests that verify clean secure fallback behavior.
- **retest_guidance:** Re-test alternate storage-presentation scenarios after redesign and confirm vault gating fails safely without exposing inconsistent semi-operational states.

---

## PHX-V05 — Recovery-path abuse potential via `repairman.sh`

- **finding_id:** PHX-V05
- **title:** Recovery-path abuse potential via `repairman.sh`
- **severity:** Medium
- **validation_status:** Hypothesis
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** null
- **cvss_vector:** null
- **cvss_severity:** Medium
- **cvss_rationale:** Candidate only. The recovery path appears trust-sensitive and potentially high impact, but exploitability has not been verified.
- **cvss_assumptions:** No score assigned until source acceptance, authenticity validation behavior, and attacker control feasibility are proven.
- **cve_ids:** []
- **cwe_ids:** ["CWE-494", "CWE-829"]
- **impact:** If exploitable, an attacker-controlled repair source could compromise player integrity or restore attacker-chosen content to the protected media.
- **evidence:** `repairman.sh` searched multiple removable-media paths for `nctv-phoenix`; if found and `/dev/mmcblk0` existed it could perform surgical restore actions; `nctv-watchdog.sh` could trigger `repairman.service` by touching `/run/nctv-phoenix-repair-needed`.
- **remediation:** Require signed and authenticated recovery bundles, verify source integrity before any restore action, and limit repair triggering to authenticated maintenance workflows.
- **hardening_recommendations:** Treat recovery media as hostile by default, add cryptographic verification to restore artifacts, and log any repair-mode entry with tamper-evident records.
- **retest_guidance:** Build a controlled test repair source and verify whether unsigned or attacker-modified content is rejected before any write action occurs.

---

## PHX-V06 — Pre-lock startup race exposing shell/GUI access

- **finding_id:** PHX-V06
- **title:** Pre-lock startup race exposing shell/GUI access
- **severity:** Medium
- **validation_status:** Supported / partially observed
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** null
- **cvss_vector:** null
- **cvss_severity:** Medium
- **cvss_rationale:** Candidate only. A pre-auth startup race may exist, but the reproducibility and achievable attacker actions are not yet bounded tightly enough for final scoring.
- **cvss_assumptions:** No score assigned until the timing window is reproduced consistently and the reachable actions inside that window are documented.
- **cve_ids:** []
- **cwe_ids:** ["CWE-362", "CWE-367"]
- **impact:** If reliably reproducible, a local attacker may interact with shell or GUI state before the intended lock workflow takes control.
- **evidence:** Prior observations showed transient `tty1` shell exposure, temporary GUI visibility before takeover, and systemd ordering-cycle clues involving Phoenix boot targets.
- **remediation:** Re-order startup so the lock state asserts before any interactive session or GUI path becomes visible, and gate boot-time transitions on explicit authorization completion.
- **hardening_recommendations:** Disable unnecessary local consoles during early boot, minimize unauthenticated startup surfaces, and add boot-sequence tests for transient exposure windows.
- **retest_guidance:** Capture repeated boot cycles with exact timing notes and confirm whether an attacker can consistently reach actionable interaction before lock takeover.

---

## PHX-V07 — Exposed physical shutdown / local availability disruption path

- **finding_id:** PHX-V07
- **title:** Exposed physical shutdown / local availability disruption path
- **severity:** Low
- **validation_status:** Supported
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** null
- **cvss_vector:** null
- **cvss_severity:** Low
- **cvss_rationale:** Candidate only. The issue currently reads more like a kiosk-hardening availability concern than a fully developed exploit finding.
- **cvss_assumptions:** No score assigned until the shutdown path is reproduced and its ease, reliability, and controls are documented more clearly.
- **cve_ids:** []
- **cwe_ids:** ["CWE-693"]
- **impact:** A local actor may be able to disrupt player availability through exposed keyboard-triggered shutdown behavior.
- **evidence:** Operator observations and on-screen shutdown target messages appeared during interaction with `Fn+Esc` and related key sequences.
- **remediation:** Restrict or intercept unauthorized local shutdown paths in kiosk mode and require authenticated maintenance procedures for controlled power actions.
- **hardening_recommendations:** Disable high-risk key combinations in the deployed UI path, lock down local console behavior, and add watchdog recovery logic appropriate to business uptime requirements.
- **retest_guidance:** Reproduce the key sequence under controlled conditions and document whether shutdown can be triggered consistently without authorized maintenance access.

---

## PHX-V08 — Sparse network surface with state drift

- **finding_id:** PHX-V08
- **title:** Sparse network surface with state drift
- **severity:** Low
- **validation_status:** Not Applicable
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** null
- **cvss_vector:** null
- **cvss_severity:** Low
- **cvss_rationale:** This is currently environment context, not a standalone vulnerability. It does not warrant final scoring unless tied to a concrete reachable weakness.
- **cvss_assumptions:** Retained only as operating context for later reasoning, not as a report-ready finding.
- **cve_ids:** []
- **cwe_ids:** []
- **impact:** None as a standalone finding at present.
- **evidence:** Observed network state drift between earlier SSH/rpcbind visibility and later filtered results during revalidation.
- **remediation:** Continue monitoring service-state changes and tie any future network concern to a verified reachable weakness before reporting it as a vulnerability.
- **hardening_recommendations:** Maintain minimal exposed services and investigate unexpected service-state drift for operational assurance.
- **retest_guidance:** Repeat network validation if the target runtime changes or a new reachable service appears.

## Recommended next move

- Use PHX-V01 to PHX-V03 directly as the initial reporting-ready Phoenix findings set.
- Treat PHX-V04 as likely supporting/root-cause material unless separate exploit value becomes clearer.
- Keep PHX-V05 to PHX-V07 in candidate validation flow, and keep PHX-V08 as context only.
