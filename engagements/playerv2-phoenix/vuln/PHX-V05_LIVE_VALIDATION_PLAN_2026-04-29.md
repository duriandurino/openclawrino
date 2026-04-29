# PHX-V05 — Controlled Live Validation Plan

Date: 2026-04-29
Target: playerv2-phoenix
Finding candidate: PHX-V05 — Recovery-path abuse potential via `repairman.sh`
Validation goal: Determine whether Phoenix will accept attacker-controlled USB recovery content without a visible authenticity gate, while minimizing operational and evidentiary risk.

## Current evidence baseline

Already supported by recovered Phoenix scripts and setup artifacts:
- `repairman.sh` runs automatically when the system boots from a USB environment whose boot-drive parent resolves to `sdb`
- if `/dev/mmcblk0` exists, the script enters surgery mode and performs `fsck`, mounts the SD root, and `rsync`s `/` from the USB runtime onto the SD
- the script then rebuilds `fstab`, restores firmware config, reapplies `BOOT_ORDER=0xf461`, forces graphical target/lightdm, toggles services, and reboots
- no visible signature check, authenticity check, or operator-authentication gate was observed in the recovered script body before restore actions proceed

This means PHX-V05 is already stronger than a pure hypothesis. The live validation goal is to prove or disprove whether **attacker-controlled repair content is actually accepted in practice**.

## Validation posture

This validation should follow the least-risk proof ladder:
1. **Design review confirmation**
2. **Non-destructive acceptance check**
3. **Sacrificial-media replay if needed**
4. **Production-target destructive replay only if explicitly justified later**

For this phase, stop at Level 2 or Level 3 unless there is a clear reason to escalate.

## Preconditions

Before any live replay:
- confirm the target device and media are in scope for physical recovery-path testing
- preserve current engagement evidence and note the exact starting state
- prepare rollback expectations in writing
- avoid using the primary production SD as the first destructive test surface

## Recommended safest validation path

### Phase A — Non-destructive acceptance indicators

Goal: prove the target will enter Phoenix USB recovery logic and trust the USB environment enough to start the path, without allowing the script to fully overwrite the main SD.

#### Setup idea
Prepare a **controlled Phoenix-style USB recovery medium** that matches the expected boot condition and includes:
- a benign marker file proving operator control of the USB runtime
- logging wrappers or echoed markers around the `repairman.sh` stages if that can be done without changing the meaning of the test
- a deliberate early-stop guard before the `rsync` write stage, if test instrumentation is allowed

#### Success indicators for Phase A
Any of the following would strengthen PHX-V05 materially:
- TTY1 shows `MODE: SYSTEM SURGEON (SD Detected)` from the operator-controlled USB environment
- the target executes attacker-supplied recovery-script logic up to a safe marker point
- logs or console output prove the system accepted the USB runtime as the trusted repair source
- no additional operator-authentication or signature-verification gate appears before trust is granted to the recovery path

#### Stop condition for Phase A
Stop immediately if:
- the test would proceed into real `rsync` overwrite behavior on the primary SD
- unexpected device state appears that is not covered by the current rollback plan
- the target reveals hidden gating logic that changes the test assumptions

### Phase B — Sacrificial-media recovery replay

Only run this if Phase A is insufficient.

Goal: determine whether attacker-controlled content is actually written through the recovery path when the target is paired with a sacrificial SD or non-production clone media.

#### Setup idea
- use sacrificial SD media or an explicitly disposable test image
- prepare a Phoenix-style USB recovery source with a uniquely identifiable benign marker payload
- keep the payload minimal and non-malicious, for example a harmless file, banner string, or non-executable visible marker that would be copied only if `rsync` trust is real

#### What to observe
- whether the system boots the USB recovery path automatically
- whether the surgery mode proceeds without authenticity challenge
- whether the benign marker is copied onto the sacrificial SD image
- whether service toggles and firmware/config changes also occur as scripted

#### Success condition for Phase B
PHX-V05 can move much closer to verified if:
- the target accepts the operator-controlled Phoenix-style USB source
- proceeds through repairman workflow without signature/authentication challenge
- and copies benign attacker-controlled marker content to sacrificial target media

### Phase C — What not to do in first live replay

Do **not** begin by:
- letting a modified repair USB overwrite the primary production SD
- introducing destructive or ambiguous payloads
- using malware-like or persistence-oriented markers
- changing too many variables at once, which would weaken the evidence value

## Evidence checklist

Capture all of the following:
- photos or video of TTY1 recovery messages
- exact USB preparation notes
- exact files or marker content added to the operator-controlled recovery source
- exact moment the system enters repairman path
- whether any signature, prompt, password, or trust gate appears
- whether the marker content is copied to target media
- whether any service-state changes or boot-order resets occur
- cleanup or restoration actions performed afterward

## Decision outcomes

### Outcome 1 — Hidden gate appears
If the target presents a real authenticity or operator-authentication gate before recovery trust is granted:
- keep PHX-V05 below verified
- document the gate precisely
- revise the finding toward weaker or more conditional language

### Outcome 2 — Recovery path is accepted but no write proof yet
If the target clearly accepts the USB runtime as trusted but the test stops before write actions:
- keep PHX-V05 as **Supported, stronger evidence**
- justify that the acceptance path is proven but full exploit effect remains intentionally unexecuted

### Outcome 3 — Benign attacker-controlled content is written to sacrificial media
If the target copies operator-controlled benign content from the USB runtime to sacrificial media without authenticity gating:
- promote PHX-V05 to **Verified**
- draft score-ready finding fields
- treat this as a high-confidence integrity-impact recovery-path weakness

## Recommended next operator task

The cleanest next move is to prepare a **non-destructive Phase A test design** with a marker-based USB recovery source and an explicit early stop before `rsync`, then decide whether the target setup allows that instrumentation safely.
