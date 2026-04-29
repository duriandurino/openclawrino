# PHX-V05 Operator Runbook — Safest-First Live Validation

Date: 2026-04-29
Target: playerv2-phoenix
Purpose: Give the operator a concrete, low-risk procedure for validating whether Phoenix accepts attacker-controlled USB recovery content.

## Mission

Prove or disprove this claim with minimal risk first:

> A Phoenix-style USB recovery source can be accepted as trusted repair input without a visible authenticity gate.

This runbook is designed to stop before destructive overwrite on the primary SD unless you intentionally move into a later sacrificial-media phase.

## Validation levels in this runbook

- **Level A:** Non-destructive acceptance proof
- **Level B:** Sacrificial-media write proof

Do **Level A first**.
Do **not** jump to Level B on the primary production SD.

## Required materials

### For Level A
- the Phoenix target device
- physical access to keyboard/display
- the suspected Phoenix recovery USB or a controlled Phoenix-style USB test medium
- a camera or phone for TTY1 photos/video
- a notepad for exact timestamps and observed strings

### For Level B
- all of the above, plus:
- sacrificial SD media or an explicitly disposable test image
- a uniquely identifiable benign marker payload prepared on the USB runtime

## Pre-run checklist

Before powering on:
- confirm the target is in scope for physical recovery-path testing
- confirm you are **not** about to overwrite the primary SD during Level A
- note the current media arrangement and what is inserted where
- note whether the current target SD must be preserved untouched
- prepare to stop immediately if the flow reaches real `rsync` on the primary SD

Record:
- date and time
- target label
- USB medium label or identifier
- SD medium label or identifier
- whether this is Level A or Level B

## Level A — Non-destructive acceptance proof

### Goal
Show that the target enters Phoenix recovery mode and begins trusting the USB recovery environment, without permitting a full restore onto the primary SD.

### Safest execution idea
Use a Phoenix-style USB test medium that includes:
- a visible operator marker, for example a file named `PHX-V05-MARKER.txt`
- if safely possible, a modified `repairman.sh` that emits a unique marker string and exits **before** the real `rsync` write stage

### Example safe marker string
Use something obvious and unique, for example:
- `PHX-V05 SAFE MARKER: operator-controlled recovery path reached`

### Level A procedure
1. Power off the target.
2. Insert the controlled USB recovery medium.
3. Keep the primary SD arrangement documented exactly as found.
4. Power on the device.
5. Watch TTY1 closely.
6. Capture photos or video of the following if they appear:
   - `N-COMPASS PHOENIX RECOVERY SYSTEM v6.0`
   - `MODE: SYSTEM SURGEON (SD Detected)`
   - any operator marker string you added
   - any prompt, password request, signature check, or trust gate
7. If the path reaches the point just before real `rsync` on the primary SD, stop the test rather than letting the overwrite continue.

### Level A success conditions
Any of these count as useful success:
- the device executes the operator-controlled recovery script path
- TTY1 shows Phoenix surgery mode from the operator-controlled USB environment
- your unique safe marker appears on screen or in logs
- no visible authenticity gate appears before the recovery path is trusted

### Level A failure or block conditions
Document and stop if:
- the device refuses to use the USB recovery path
- the USB does not meet the expected boot condition
- a signature/authentication gate appears
- the test would continue into real write actions on the primary SD

## Level B — Sacrificial-media write proof

### Goal
Show that operator-controlled benign content can actually be written through the recovery path when using sacrificial media.

### Benign marker guidance
Use a non-malicious marker that proves copy behavior, such as:
- `/opt/phx-v05-marker.txt`
- `/home/pi/PHX-V05_MARKER.txt`
- a harmless banner line inside a non-critical text file

Avoid:
- persistence mechanisms
- executable payloads
- ambiguous changes that could be confused with normal Phoenix content

### Level B procedure
1. Replace the primary target SD with sacrificial media, or use a clearly disposable test image.
2. Prepare the operator-controlled Phoenix-style USB source with the benign marker present in the runtime filesystem.
3. Boot the device from the USB medium.
4. Let surgery mode proceed only if the sacrificial-media condition is confirmed.
5. Capture TTY1 progress, especially:
   - surgery-mode banner
   - `fsck` output
   - `rsync` stage
   - reboot messaging
6. After reboot or controlled shutdown, inspect the sacrificial media for the benign marker.
7. Record whether service toggles, boot-order resets, and related scripted changes also occurred.

### Level B success conditions
PHX-V05 moves close to verified if:
- the target accepted the USB recovery source without authenticity challenge
- the operator-controlled marker was copied to sacrificial media
- the behavior matches the reviewed `repairman.sh` flow

## Evidence form to fill during the run

### Session header
- Date/time:
- Operator:
- Target:
- Validation level:
- USB identifier:
- SD identifier:

### Observed boot behavior
- Did USB boot path trigger? yes/no
- Did `N-COMPASS PHOENIX RECOVERY SYSTEM v6.0` appear? yes/no
- Did `MODE: SYSTEM SURGEON (SD Detected)` appear? yes/no
- Did any unique marker appear? yes/no
- Did any prompt/auth gate appear? yes/no
- Did real `rsync` begin? yes/no

### Outcome classification
- Outcome 1: hidden gate found
- Outcome 2: trust path accepted, no write proof yet
- Outcome 3: benign marker copied to sacrificial media

### Notes
- exact observed strings:
- exact timestamps:
- photos/video filenames:
- stop point used:
- cleanup performed:

## Interpretation guide

### If Level A succeeds
You can say:
- the target accepted operator-controlled recovery-path logic far enough to strengthen PHX-V05 materially
- no visible authenticity gate appeared before trust was granted to the recovery path

### If Level B succeeds
You can say:
- Phoenix accepted operator-controlled recovery content and wrote benign operator-controlled material to sacrificial media without visible authenticity gating
- PHX-V05 should be upgraded toward verified status

### If a hidden gate appears
You should immediately narrow the finding and document the gate precisely.

## Safety rules

- never let the first replay overwrite the primary SD just to get stronger proof faster
- one variable at a time
- benign markers only
- preserve exact evidence
- stop once the claim is proven enough for the current phase
