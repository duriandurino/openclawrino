# Recon Summary

## Goal

- Identify existing artifacts for hardwareLockV2, locate the protected image and service files, and understand how the hardware lock is enforced without destabilizing the system.

## Hypotheses

- The lock logic binds execution to Raspberry Pi serial and SD card CID values.
- The protected application payload is stored in `vault.img` and mounted to `/home/pi/n-compasstv-secure`.
- Player services are started via PM2 from `ecosystem.config.js` after the lock check succeeds.

## Actions Taken

- Initialized engagement and documentation structure.
- Searched workspace for hardware lock, player, image, and service artifacts.
- Reviewed implementation notes and copied setup scripts from prior research materials.

## Observations

- Prior artifacts show `hardware_lock.py` comparing current hardware against authorized Pi serial and SD CID values, then launching `unlock_vault.py` and PM2 on success.
- `unlock_vault.py` uses the Pi serial as the LUKS key material for `vault.img` mounted to `/home/pi/n-compasstv-secure`.
- `nctv-watchdog.sh` is destructive-risk adjacent because deleting or hiding `/home/pi/n-compasstv` can trigger boot config tampering and reboot.
- `repairman.sh` is a recovery workflow and not a safe first recon path for this engagement.

## Interesting Leads

- Authorized values appear embedded in prior versions of `hardware_lock.py`.
- Vault mount path and PM2 startup path are known from research artifacts.
- Existing `setup.enc` and player-vault related engagements may contain adjacent evidence for Hardware Lock V2.

## Failed Attempts

- None yet.

## Confirmed Findings

- The hardware lock design is serial-based and tied to both Raspberry Pi and SD identifiers in prior implementation artifacts.
- The vault/image unlock flow likely depends on serial-derived key material.
- Service startup likely depends on `/home/pi/n-compasstv-secure/ecosystem.config.js` after successful unlock.

## Evidence References

- EVI-001
- EVI-002

## Decision

- Continue
- Reason: recon has enough concrete implementation detail to move into targeted enumeration of actual V2 artifacts and compare them against prior known versions.
