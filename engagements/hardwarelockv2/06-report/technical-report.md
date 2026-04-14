# Hardware Lock V2 Penetration Test Report

**Classification:** Internal / Authorized Assessment  
**Status:** Final  
**Version:** 1.0  
**Engagement:** Unlock Player with Hardware Lock V2  
**Target:** hardwareLockV2  
**Assessment window:** 2026-04-13 to 2026-04-14  
**Primary analyst:** Hatless White / specter-report

## Document History

| Version | Date | Author | Notes |
|---|---|---|---|
| 1.0 | 2026-04-14 | specter-report | Final technical report based on validated engagement evidence |

## Engagement Overview

This gray-box assessment evaluated Hardware Lock V2 on an authorized Raspberry Pi target to determine whether the protected player runtime could be unlocked, inspected, and executed without breaking the system. The engagement focused on application image artifacts, hardware-bound authorization logic, vault behavior, and recovery paths.

The assessment reached a meaningful blocked-state conclusion. Testing verified that the local authorization layer is weak enough to be influenced through editable configuration, but the protected runtime remained unavailable because the independent encrypted vault and missing Phoenix recovery artifacts preserved the effective security boundary.

## Scope and Rules of Engagement

### In Scope
- Application-layer and software-related artifacts
- App image-related files
- Keyboard and mouse port interaction
- Read-first inspection of local scripts, package traces, logs, and recovery paths

### Out of Scope
- Breaking the system
- Destructive recovery attempts
- Unapproved offline cracking or destabilizing experiments

### Constraints and Limitations
- No original passphrase information for the image lock was provided
- No original code or process file-pattern guidance was provided
- The target was already in a modified state when analysis resumed because `hardware-lock.env` had previously been edited on-box
- No external repair source, sibling working device, or preserved original provisioning package beyond `setup.enc` was available during this assessment

## Methodology

The assessment followed a structured phase model:

1. **Reconnaissance** - identify prior artifacts, likely lock design, and runtime layout
2. **Enumeration** - validate live lock logic, vault derivation behavior, service chain, and mount state
3. **Vulnerability analysis** - distinguish weak authorization controls from effective cryptographic protections
4. **Exploit / recovery analysis** - test safe, evidence-based recovery hypotheses and inspect residual provisioning artifacts
5. **Reporting** - consolidate validated findings, blocked paths, residual risk, and recommended next actions

## Executive Technical Conclusion

The strongest validated weakness is that the first-layer hardware authorization check depends on editable local configuration in `hardware-lock.env`. With local file edit access, the authorized hardware tuple can be aligned to the current device, allowing the gate check to pass.

That weakness did **not** produce payload access. Direct validation showed the current `unlock_vault.py` derivation still fails to open `/var/lib/nctv-phoenix/vault.img`, which remains a LUKS2 container rejecting the derived key. The expected runtime tree also did not exist locally in usable form: `/opt/nctv-player`, `/var/lib/nctv-player`, and `/mnt/nctv-phoenix-secure` were present only as empty placeholders in the assessed state.

Further forensic review established that the local `setup.enc` artifact is only a bootstrap stage. It installs `nctv-player`, then downloads and decrypts `phoenix.enc`, extracts `nctv-phoenix`, and runs `phoenix_install.sh --guard`. No local copy of `phoenix.enc`, no extracted Phoenix tree, and no evidence-backed rollback source for the original authorized tuple were recovered. Accordingly, the engagement ended in a verified blocked state for internal-only recovery on the present box.

## Findings Summary

| ID | Title | Status | Risk | Affected Asset | Key Point |
|---|---|---|---|---|---|
| F-001 | Local authorization config can be altered via `hardware-lock.env` | validated | Medium | hardwareLockV2 | The authorization gate is locally mutable with file-write access |
| F-002 | Secure payload remains protected by independent LUKS vault key | validated | Medium | hardwareLockV2 | Matching the gate does not unlock the vault |
| F-003 | Current exploit chain is blocked at the cryptographic boundary despite local gate bypass | validated | Medium | hardwareLockV2 | The validated chain stops before runtime access |
| F-004 | Shell history preserves a likely original provisioning workflow and decryption secret for `setup.enc` delivery | validated | High | hardwareLockV2 | Historical bootstrap path and installer secret were recoverable |
| F-005 | Repair workflow depends on an external `nctv-phoenix` source that is currently absent | validated | Medium | hardwareLockV2 | Recovery code exists but is unusable without the external source |
| F-006 | Local runtime and secure mount targets are present only as empty placeholders in the current state | validated | Medium | hardwareLockV2 | Expected runtime files are not locally available |
| F-007 | Phoenix and player belong to a staged protected runtime chain, with `setup.enc` only bootstrapping the second-stage Phoenix installer | validated | Medium | hardwareLockV2 | Restoring player execution depends on the broader guarded Phoenix chain |
| F-008 | Internal-only local recovery is currently blocked because only `vault.img` remains and no original tuple rollback source was recovered | validated | Medium | hardwareLockV2 | The current image alone is insufficient for full local recovery |

## Attack Path Summary

### Validated Path

**AP-001, Config gate bypass only**
- Local file edit access allowed modification of `hardware-lock.env`
- The authorization check could then be aligned with the current hardware tuple
- The gate passed, but this remained non-terminal because the vault stayed locked
- Evidence: EVI-004, EVI-005

### Blocked / Candidate Paths

**AP-002, Recover original provisioning logic or vault key material**  
Plausible, but blocked without original provisioning artifacts, sibling-device comparison, or reliable historical key provenance.

**AP-003, External `nctv-phoenix` repair payload**  
Code path is real and explicit, but the required external repair tree was not available.

**AP-004, Offline vault recovery against `vault.img`**  
Potential last-resort lane only if explicitly authorized as a separate lab effort.

**AP-005, Historical `setup.enc` provisioning reconstruction**  
Validated as high-value architectural evidence, but it did not by itself restore local recovery because the second-stage Phoenix artifacts were missing.

## Validated Findings

### F-001: Local authorization config can be altered via `hardware-lock.env`

**Affected Asset(s):** hardwareLockV2  
**Severity / Risk:** Medium  
**Technical Basis:** Local integrity weakness in authorization configuration  
**Business Impact:** An attacker with local file-write access can align the first hardware gate to current hardware, reducing trust in the device-binding check and weakening confidence in the control stack.  
**Evidence:** EVI-003, EVI-004, EVI-005  

**Reproduction / Validation Steps:**
1. Review the current `hardware_lock.py` and `hardware-lock.env` logic.
2. Compare live Pi serial and SD CID hash against the env-backed authorized tuple.
3. Observe that modifying the env values to match current hardware causes the gate check to pass.

**Remediation:**
- Make authorization material tamper-evident and integrity-protected
- Restrict write access to authorization configuration to a hardened administrative path only
- Prefer device binding anchored in hardware-backed secrets instead of editable plaintext configuration
- Add integrity monitoring for changes to `/etc/nctv-phoenix/hardware-lock.env`

**Verification / Retest Guidance:**
- Attempt the same local configuration edit after remediation
- A fix is effective if unauthorized local edits are blocked, detected, or rendered insufficient to satisfy the authorization gate

**References:** EVI-003, EVI-004, EVI-005  
**Cleanup / Side-Effect Notes:** No additional edits were introduced by this reporting phase; analysis documents an already-observed local modification state.

### F-002: Secure payload remains protected by independent LUKS vault key

**Affected Asset(s):** `/var/lib/nctv-phoenix/vault.img` and dependent runtime chain  
**Severity / Risk:** Medium  
**Technical Basis:** Independent cryptographic boundary separating gate authorization from vault access  
**Business Impact:** Even after gate manipulation, the protected runtime cannot be recovered from the assessed state without valid vault key material or equivalent provisioning artifacts. This materially reduced attacker progress in the observed scenario.  
**Evidence:** EVI-004, EVI-005, EVI-006  

**Reproduction / Validation Steps:**
1. Confirm `vault.img` is a LUKS2 container.
2. Confirm that the env-backed authorization tuple matches current hardware after the local edit.
3. Execute the current unlock path and observe `cryptsetup` rejecting the derived key.
4. Verify that no mapper device or secure mount becomes available.

**Remediation:**
- Preserve the cryptographic separation between the gate and the vault
- Add provenance checks so vault-unlock logic changes can be detected and audited
- Store vault derivation logic and recovery records in a secure, versioned, recoverable process
- Ensure production unlock logic cannot silently drift from provisioning-time assumptions

**Verification / Retest Guidance:**
- Re-run the unlock workflow after hardening and provenance improvements
- A fix is effective if the design remains resistant to local gate manipulation and authorized recovery can still be audited cleanly

**References:** EVI-004, EVI-005, EVI-006  
**Cleanup / Side-Effect Notes:** Repeated blind unlock attempts should be avoided because prior service behavior showed noisy restart loops.

### F-003: Current exploit chain is blocked at the cryptographic boundary despite local gate bypass

**Affected Asset(s):** hardwareLockV2 runtime recovery chain  
**Severity / Risk:** Medium  
**Technical Basis:** Chained attack path validation  
**Business Impact:** A local attacker may weaken the first gate but still fails to reach runtime execution or secure payload access in the assessed state. This limits impact, but it also exposes operational dependency on artifact provenance and recovery quality.  
**Evidence:** EVI-004, EVI-005, EVI-006, EVI-007  

**Reproduction / Validation Steps:**
1. Validate AP-001 by aligning the gate to current hardware.
2. Attempt to continue through the unlock and service chain.
3. Observe that the vault remains locked and launcher/runtime targets remain unavailable.

**Remediation:**
- Treat configuration integrity, vault provenance, and recovery media control as one security boundary, not separate operational concerns
- Add explicit monitoring and fail-safe behavior around repeated failed unlock loops
- Document trusted recovery paths and remove ambiguity about which artifacts are authoritative

**Verification / Retest Guidance:**
- Retest the full chain from authorization to runtime launch after remediation
- A fix is effective if unauthorized gate manipulation does not progress the chain and recovery behavior is deterministic and observable

**References:** EVI-004, EVI-005, EVI-006, EVI-007  
**Cleanup / Side-Effect Notes:** No exploit path to runtime execution was achieved during this engagement.

### F-004: Shell history preserves a likely original provisioning workflow and decryption secret for `setup.enc` delivery

**Affected Asset(s):** Provisioning workflow, bootstrap secrets, shell history  
**Severity / Risk:** High  
**Technical Basis:** Sensitive bootstrap material exposed through shell history and recoverable command artifacts  
**Business Impact:** Recovery of the provisioning command and decryption secret materially lowers the effort needed to reconstruct protected installer behavior. Similar exposure on deployed devices could aid reverse engineering, recovery bypass planning, or unauthorized cloning of install logic.  
**Evidence:** EVI-008, EVI-010, EVI-012  

**Reproduction / Validation Steps:**
1. Review `/home/pi/.bash_history`.
2. Identify the historical provisioning command downloading `setup.enc` and decrypting it with a hardcoded passphrase.
3. Use the recovered passphrase against a local copy of `setup.enc` to confirm the bootstrap script decrypts successfully.

**Remediation:**
- Remove installer secrets and decrypt recipes from shell history and operational runbooks
- Rotate any still-relevant bootstrap passphrases and delivery secrets
- Replace static shared installer secrets with short-lived, per-device, or hardware-backed provisioning controls
- Harden operator procedures so sensitive bootstrap commands are not retained in plaintext history

**Verification / Retest Guidance:**
- Review shell history, notes, and provisioning logs after remediation
- A fix is effective if installer secrets are absent from recoverable operator artifacts and new provisioning material uses rotated or ephemeral secrets

**References:** EVI-008, EVI-010, EVI-012  
**Cleanup / Side-Effect Notes:** Report content redacts operationally sensitive detail where possible; the underlying exposure remains a deployment/process issue.

### F-005: Repair workflow depends on an external `nctv-phoenix` source that is currently absent

**Affected Asset(s):** Repair workflow, runtime restoration path  
**Severity / Risk:** Medium  
**Technical Basis:** Recovery-chain dependency on external trusted payload source  
**Business Impact:** The current device cannot recover locally when the vault fails to unlock, causing repair loops and preventing restoration of the coupled runtime. Operational recovery is therefore highly dependent on preserving valid external repair media.  
**Evidence:** EVI-009, EVI-010, EVI-011  

**Reproduction / Validation Steps:**
1. Review `repairman.sh` and related service behavior.
2. Confirm the script searches for an external `nctv-phoenix` tree under removable or mounted paths.
3. Confirm service logs repeatedly report missing repair source.

**Remediation:**
- Maintain signed, versioned, and access-controlled external repair payloads
- Document and test recovery-source handling as part of operational readiness
- Add clearer operator-visible failure modes instead of indefinite noisy retry loops
- Validate repair media provenance before use

**Verification / Retest Guidance:**
- Present a trusted repair payload and confirm the workflow behaves deterministically
- A fix is effective if the system either restores from trusted media successfully or fails cleanly with actionable telemetry

**References:** EVI-009, EVI-010, EVI-011  
**Cleanup / Side-Effect Notes:** No external repair media was introduced during this engagement.

### F-006: Local runtime and secure mount targets are present only as empty placeholders in the current state

**Affected Asset(s):** `/opt/nctv-player`, `/var/lib/nctv-player`, `/mnt/nctv-phoenix-secure`  
**Severity / Risk:** Medium  
**Technical Basis:** Missing runtime payload despite installed package traces and expected mount points  
**Business Impact:** The assessed device retains launcher paths and placeholder directories without the expected protected runtime. This increases operational fragility and complicates both incident triage and legitimate recovery.  
**Evidence:** EVI-010, EVI-011  

**Reproduction / Validation Steps:**
1. Review package metadata showing `nctv-player` installation traces.
2. Inspect the local runtime and secure mount directories.
3. Confirm that only empty placeholders remain in the current state.

**Remediation:**
- Add integrity checks that compare package metadata against actual deployed runtime content
- Preserve known-good runtime bundles in an authorized recovery repository
- Alert when expected protected runtime trees are missing or drift from package expectations

**Verification / Retest Guidance:**
- Re-audit runtime paths after remediation or restoration
- A fix is effective if expected runtime trees are either present and validated or the system reports a controlled, diagnosable missing-runtime state

**References:** EVI-010, EVI-011  
**Cleanup / Side-Effect Notes:** Findings reflect passive inspection only.

### F-007: Phoenix and player belong to a staged protected runtime chain, with `setup.enc` only bootstrapping the second-stage Phoenix installer

**Affected Asset(s):** Provisioning and guarded runtime chain  
**Severity / Risk:** Medium  
**Technical Basis:** Multi-stage installer and runtime dependency model  
**Business Impact:** Recovering player execution depends on the broader Phoenix chain, not just the launcher package or auth-gate satisfaction. In operational terms, incomplete artifact preservation can break the whole runtime recovery path.  
**Evidence:** EVI-011, EVI-012  

**Reproduction / Validation Steps:**
1. Decrypt the locally recovered `setup.enc` bootstrap script.
2. Review its logic to confirm it installs `nctv-player`, then retrieves and decrypts `phoenix.enc`.
3. Confirm it extracts `nctv-phoenix` and invokes `phoenix_install.sh --guard`.

**Remediation:**
- Preserve and validate the full coupled runtime bundle, not just the first-stage installer
- Maintain trusted archives for second-stage Phoenix artifacts and guarded install scripts
- Document end-to-end runtime recovery procedures that reflect the real staged design

**Verification / Retest Guidance:**
- Reconstruct the provisioning flow in a controlled authorized lab using preserved trusted artifacts
- A fix is effective if the full Phoenix-plus-player chain can be validated and restored deterministically without relying on guesswork

**References:** EVI-011, EVI-012  
**Cleanup / Side-Effect Notes:** This finding is based on direct artifact analysis, not on execution of the missing second-stage payload.

### F-008: Internal-only local recovery is currently blocked because only `vault.img` remains and no original tuple rollback source was recovered

**Affected Asset(s):** Entire local recovery lane on the current box  
**Severity / Risk:** Medium  
**Technical Basis:** Insufficient local provenance to reconstruct the original guarded runtime state  
**Business Impact:** The current device does not retain enough trustworthy local material to restore the full protected runtime from on-box residue alone. Continued internal-only attempts are likely low-yield and may create operational noise without improving recovery.  
**Evidence:** EVI-011, EVI-012, EVI-013  

**Reproduction / Validation Steps:**
1. Search the target for `phoenix.enc`, `phoenix_install.sh`, extracted Phoenix trees, and trustworthy historical tuple records.
2. Confirm these artifacts are absent locally.
3. Confirm that only `vault.img` and placeholder runtime paths remain.

**Remediation:**
- Preserve original provisioning artifacts and authorized recovery sources in a secure repository
- Maintain secure records of original hardware-binding values or equivalent recovery metadata
- Define a formal recovery playbook for authorized reconstruction when local residue is insufficient

**Verification / Retest Guidance:**
- Attempt recovery again only after introducing an authorized artifact source, such as preserved provisioning materials, a trusted sibling-device comparison set, or approved offline lab workflow
- A fix is effective if authorized recovery can proceed without reliance on stale shell history or incomplete local remnants

**References:** EVI-011, EVI-012, EVI-013  
**Cleanup / Side-Effect Notes:** The conclusion here is a reporting boundary: this engagement did not validate full recovery from local residue alone.

## Counterfactual and Unmodified-State Hypotheses

The following items are intentionally separated from validated findings.

These are **plausible but unvalidated** paths that may have worked in an earlier or unmodified device state:

1. **Original env tuple hypothesis**  
   If the original authorized tuple had been preserved, the current or historical unlock routine might have matched the real vault key more closely.

2. **Original provisioning-logic hypothesis**  
   If the original provisioning-time derivation logic differed from the currently observed `unlock_vault.py`, then preserved historical installer artifacts may have explained why the present derivation no longer unlocks the vault.

3. **Second-stage Phoenix survival hypothesis**  
   If `phoenix.enc`, extracted `nctv-phoenix`, or `phoenix_install.sh` had remained locally available, the guarded runtime path might have been testable or restorable in a controlled way.

These hypotheses should guide future authorized recovery efforts, but they should **not** be reported as achieved exploit outcomes.

## Remediation Roadmap

### Immediate
- Protect `hardware-lock.env` against unauthorized local modification
- Rotate or retire any still-valid bootstrap passphrases and provisioning secrets exposed through shell history
- Stop noisy automated retry behavior that repeatedly hammers failing unlock or repair workflows without improving state

### Short-Term
- Establish signed, versioned, access-controlled storage for provisioning and repair artifacts
- Add integrity and provenance checks for unlock logic, repair scripts, and deployed runtime trees
- Document trusted recovery media requirements and operator-visible failure modes

### Medium-Term
- Move device-binding and unlock dependencies toward hardware-backed or tamper-evident controls
- Create a formal recovery playbook covering vault provenance, second-stage Phoenix artifacts, and authorized restoration workflows
- Add drift detection so package metadata, deployed runtime content, and recovery state remain consistent

## Cleanup / Restoration Status

**Tester-created artifacts introduced:** None during this reporting phase beyond engagement documentation.  
**Tester-created artifacts removed:** None.  
**Tester-created artifacts remaining intentionally:** Engagement notes and report deliverables under `engagements/hardwarelockv2/`.  
**Environment restored to agreed state:** No additional live-state changes were introduced as part of this reporting work. The device remained in its observed blocked state.  
**Residual risk after cleanup:** The authorization layer remains weak if local write access is possible, provisioning secrets were historically exposed, and legitimate recovery remains dependent on missing artifact provenance.  
**Client follow-up required:** Yes. A future authorized recovery effort should obtain trusted provisioning artifacts, secure recovery media, or a sibling-device comparison set before additional recovery attempts.

## Retest Guidance

A meaningful retest should only occur once one of the following is available:
- a trusted original provisioning package chain, including second-stage Phoenix artifacts
- a valid external `nctv-phoenix` repair source
- an authorized sibling-device comparison source
- explicit approval for separate offline vault work in a lab environment

Success criteria for retest:
- unauthorized local config edits no longer advance the authorization gate meaningfully
- trusted recovery sources are identifiable and auditable
- the coupled Phoenix-plus-player chain can either be restored legitimately or shown to fail for a clearly logged reason

## Appendix References

- Engagement charter and ROE: `00-charter/`
- Phase summaries: `01-recon/`, `02-enum/`, `03-vuln/`, `04-exploit/`, `05-post-exploit/`
- Evidence register: `registers/evidence-register.md`
- Findings register: `registers/findings-register.md`
- Attack paths: `04-exploit/attack-paths.md`, `registers/attack-path-register.md`

## Final Conclusion

This engagement should be considered complete and meaningful, even though it did not end in full runtime recovery. The assessment proved a weak first-layer authorization control, then demonstrated that the encrypted vault and missing Phoenix provenance still prevented compromise of the protected runtime from the surviving on-box artifacts alone. That distinction matters: env-based auth is weak, but the vault remained the effective security boundary in the assessed state.
