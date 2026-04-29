# PlayerV2 Phoenix — Vulnerability Evidence Index

Date: 2026-04-29

## Purpose

This file captures the concrete source material used to support Phoenix vulnerability-phase judgments, especially where the current engagement is combining live validation with code-review-backed reasoning from recovered Phoenix scripts and turnover artifacts.

## PHX-V04 / PHX-V05 supporting sources used in this pass

### Source 1
- Path: `research/ntv-hardware-lock/source/drive/kent_turnover/1xRnii7obm24AV1RgQG7XfFOzFlfEFXyX_scripts_and_services (NTV_Phoenix & Hardware-Lock).md`
- Relevant sections:
  - `***/usr/local/bin/nctv-watchdog.sh***`
  - `***/usr/local/bin/repairman.sh***`
- Key observations:
  - `nctv-watchdog.sh` watches for `/home/pi/n-compasstv` disappearance after a 60-second grace period
  - on trigger, it mounts `/dev/mmcblk0p1`, renames `/boot/firmware/config.txt` to `config.txt.bak`, syncs, and reboots
  - `repairman.sh` exits unless the root boot drive parent is `sdb`
  - if `/dev/mmcblk0` exists, `repairman.sh` performs `fsck`, mounts `/dev/mmcblk0p2`, and `rsync`s `/` from the USB runtime onto the mounted SD root
  - the script rebuilds `/etc/fstab`, restores firmware config, applies `BOOT_ORDER=0xf461`, forces graphical target/lightdm, enables `nctv-watchdog.service`, disables `repairman.service`, then reboots
  - no cryptographic verification, signature validation, content authenticity gate, or operator authentication check was observed in the quoted script body before the restore path proceeds

### Source 2
- Path: `research/ntv-hardware-lock/source/drive/kent_turnover/1BkZCY9r9jLKuyHATz9FbENGPPDTPCdFf_setup (phoenix & hardware-lock) (not fully working).sh`
- Relevant sections:
  - generated `repairman.sh`
  - generated service enablement block
- Key observations:
  - the setup script confirms the same `repairman.sh` recovery logic and shows `repairman.service` being enabled in the generated deployment flow
  - the logic again shows direct restore actions and service toggling without visible authenticity checks on the restore source

## PHX-V05 validation conclusion for this pass

### What was verified
- The Phoenix recovery path is **real and code-backed**, not just a conceptual note.
- The recovery logic is designed to run automatically when booted from a USB environment matching the script's expected boot-device condition.
- In surgery mode, the script performs direct filesystem operations and a full `rsync` mirror from the live USB runtime to the mounted SD root.
- The reviewed recovery path, as captured in the recovered scripts, showed **no visible signature check, authenticity check, or operator-authentication gate** before restore actions proceed.

### What was not yet verified live
- A full safe live replay showing that an attacker-controlled USB repair source is accepted on the target device without additional hidden controls.
- Whether external constraints not visible in the recovered script, such as a protected physical repair medium, immutable trusted USB image, or additional deployment-side assumptions, reduce exploitability in practice.

### Current analyst judgment
- PHX-V05 should be upgraded from a loose hypothesis to a **stronger supported candidate**, but it is still not treated as fully verified exploitation.
- The evidence now supports saying the restore path appears to trust the booted USB environment as the gold image source and does not visibly verify authenticity before performing recovery actions.
- Final promotion to a scored verified finding should wait for a controlled live validation or equivalent stronger proof that attacker-controlled content would actually be accepted in the target workflow.
