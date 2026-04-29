# Remediation Guide — Player v2 Phoenix

**Classification:** Confidential
**Target:** playerv2-phoenix
**Date:** 2026-04-29 21:05 GMT+8

## Priority 1 — Fix authorization and fail-closed behavior

### Problem
Phoenix trust logic depends on `/sys/block/mmcblk0/device/cid` and does not handle missing-path conditions safely. In the verified exploit path, changing the same trusted media from native SD presentation to USB presentation caused `hardware-check.service` to crash and preserved local GUI and shell access.

### Required fixes
- Replace fixed block-device assumptions with transport-independent media identification.
- Resolve trusted-media identity through stable attributes rather than device-path naming.
- Treat any failure to resolve media identity as an explicit locked state.
- Ensure authorization exceptions cannot leave local GUI, terminal, or interactive sessions exposed.

### Engineering guidance
- Centralize device-identity resolution in one hardened component instead of duplicating logic in `hardware_lock.py` and `unlock_vault.py`.
- Wrap identity-read logic in exception-safe handling with deterministic locked-state output.
- Prevent GUI startup and local shell availability until authorization completes successfully.
- Add unit and integration tests for:
  - native SD boot
  - USB SD adapter presentation
  - missing identity path
  - malformed identity data
  - service dependency failure

### Retest criteria
- The same microSD booted through a USB SD adapter must not produce interactive access.
- Missing or unreadable media identity must produce a locked state, not a crash.
- System logs should show clean denial behavior rather than uncaught exceptions.

## Priority 2 — Remove and rotate exposed provisioning material

### Problem
Shell history retained a plaintext provisioning command including a remote setup host and passphrase.

### Required fixes
- Rotate any provisioning passphrases, setup secrets, and related bootstrap artifacts that may still be valid.
- Remove plaintext secret-bearing setup commands from historical images and active devices where possible.
- Move bootstrap secrets into noninteractive, protected delivery paths.

### Engineering guidance
- Replace static setup passphrases with one-time or device-bound tokens.
- Disable or tightly restrict shell history for privileged provisioning actions.
- Audit build, setup, and field-service workflows for similar retained secrets.
- Review golden images, staging images, and field devices for secret-bearing history files.

### Retest criteria
- `.bash_history` and similar artifacts no longer contain plaintext secret-bearing provisioning commands.
- Rotated provisioning material cannot be reused successfully.
- Setup workflows function without storing reusable plaintext secrets in operator history.

## Priority 3 — Rework vault and key protection

### Problem
After local compromise, the engagement recovered enough trust inputs and derivation logic to open the protected vault read-only and recover secret-bearing runtime material.

### Required fixes
- Reassess whether vault unlock material can be derived too easily from recoverable local values.
- Reduce co-location of trust inputs, derivation logic, database keys, and private keys.
- Remove or isolate private keys from locations reachable through local OS compromise.

### Engineering guidance
- Review whether the vault key derivation should depend on stronger nonrecoverable trust anchors.
- Avoid storing both derivation code and derivation inputs in places reachable from a local foothold.
- Reevaluate storage of `.db.key`, `private_key.pem`, and similar runtime secrets inside the same recoverable protection boundary.
- Introduce explicit tamper and recovery controls for sensitive vault content.

### Retest criteria
- A local foothold should not be sufficient to reproduce vault access using product-resident derivation logic alone.
- Private-key and database-key material should no longer be recoverable from the same post-compromise path.

## Priority 4 — Harden recovery and maintenance workflows

### Problem
Recovered recovery scripts suggest a powerful restore path that may lack visible authenticity validation, although live acceptance testing was blocked during this assessment.

### Required fixes
- Require signed and authenticated recovery sources.
- Block repair or restore execution when authenticity checks fail.
- Log maintenance and repair actions in a tamper-evident way.

### Engineering guidance
- Treat recovery media as hostile until verified.
- Add explicit signature verification before any restore, sync, or reimage action.
- Separate maintenance authorization from ordinary runtime behavior.
- Document safe technician workflows for legitimate field recovery.

### Retest criteria
- Unsigned or altered recovery content must be rejected before any write occurs.
- Repair mode entry and restore activity must be visible in audit records.

## Priority 5 — Reduce local exposure windows and kiosk escape paths

### Problem
Supporting observations showed alternate TTY exposure, early-boot GUI or shell visibility, and likely keyboard-driven shutdown behavior.

### Recommended fixes
- Disable unnecessary alternate TTY access in deployed kiosk state.
- Ensure lock state asserts before any interactive GUI or shell becomes visible.
- Restrict local shutdown shortcuts or require authenticated maintenance flow.
- Review systemd ordering so Phoenix trust enforcement happens before user-facing sessions.

### Retest criteria
- Alternate TTY switching should not reveal login consoles during unauthorized states.
- Boot timing should not expose transient actionable shell or GUI access.
- Keyboard-only shutdown or disruption paths should be controlled.

## Recommended remediation order

1. Fix authorization and fail-closed handling.
2. Rotate and remove exposed provisioning secrets.
3. Rework vault and key protection architecture.
4. Authenticate recovery workflows.
5. Harden kiosk exposure windows and physical disruption paths.

## Validation checklist for engineering and retest

- [ ] USB-presented trusted media no longer bypasses authorization
- [ ] Missing identity path fails closed
- [ ] GUI and shell do not remain available after authorization failure
- [ ] Provisioning passphrase and setup command are rotated and no longer reusable
- [ ] Secret-bearing shell history is eliminated from active and newly provisioned devices
- [ ] Vault access is not reproducible from product-resident trust inputs and scripts alone
- [ ] Private-key and DB-key material are protected behind stronger boundaries
- [ ] Recovery sources require authenticity validation before restore actions
- [ ] Alternate TTY and pre-lock exposure paths are closed or intentionally controlled
