# Enum Summary

## Goal

- Confirm the actual V2 authorization and unlock flow using live target evidence.

## Hypotheses

- Hardware Lock V2 gates on current Pi serial and SHA256 of current SD CID using values from `hardware-lock.env`.
- Unlock key is derived deterministically from `AUTHORIZED_PI_SERIAL:AUTHORIZED_SD_CID_SHA256` and then used directly as LUKS key bytes.
- Player files remain unavailable because the vault is not opening or the bind-mount source layout is incomplete.

## Actions Taken

- Reviewed live contents of `hardware_lock.py` and `unlock_vault.py`.
- Reviewed live `hardware-lock.env` values after manual edit.
- Verified `vault.img` exists and is a LUKS2 container.
- Checked current mount and mapper state.
- Verified actual live Pi serial, SD CID, and SHA256(CID) against the edited environment file.
- Executed `unlock_vault.py` directly and captured the exact `cryptsetup` failure.
- Reviewed service unit chain, alternatives path, runtime symlink target, file timestamps, and journal logs.
- Reviewed `repairman.sh`, `nctv-watchdog.sh`, and candidate recovery-source locations.

## Observations

- `hardware_lock.py` does not unlock the vault, it only validates serial and SD CID hash and returns success when they match.
- `unlock_vault.py` independently re-validates serial and SD CID hash before deriving the unlock key.
- Derived key material is `sha256(f"<AUTHORIZED_PI_SERIAL>:<AUTHORIZED_SD_CID_SHA256>")` returned as raw digest bytes.
- The edited env values now match the current hardware exactly, so authorization passes.
- Direct vault unlock still fails with `cryptsetup open` returning `No key available with this passphrase` and exit status 2.
- `vault.img` exists at `/var/lib/nctv-phoenix/vault.img` and uses LUKS2 with one keyslot.
- No mapper device for `nctv-phoenix-vault` is currently open and no relevant mounts are active.
- `/usr/bin/nctv-player` is a broken symlink to `/etc/alternatives/nctv-player`, which points to `/opt/nctv-player/nctv-player`.
- The player runtime paths are expected to appear only after vault content is mounted and bind-mounted into place.
- `vault-mount.service` entered a large restart loop repeatedly hammering the same failing unlock path until it was manually stopped.
- `repairman.sh` expects an external `nctv-phoenix` repair payload and confirms hardened fail-closed behavior when the vault cannot be unlocked.
- No external repair source is currently mounted under the locations checked.

## Interesting Leads

- The current `unlock_vault.py` was modified after initial deployment, so its logic may no longer reflect the original provisioning-time unlock routine.
- The actual LUKS key likely corresponds to original provisioning values or an earlier derivation formula no longer present on-box.
- The real player payload likely exists either inside the vault or in an external repair source expected by `repairman.sh`.

## Failed Attempts

- Manual edit of `hardware-lock.env` did not result in unlocked player state.
- Direct execution of the current `unlock_vault.py` failed even after environment values were changed to match current hardware.
- On-box searches did not locate the original installer, provisioning package, or external repair payload.

## Confirmed Findings

- V2 is env-driven for authorization checks, not hardcoded in the current script version.
- The current unlock key derivation formula is known, but it does not unlock the real vault on this device.
- The vault is not currently mounted and the player runtime paths are not yet exposed.
- The current launcher path depends on `/opt/nctv-player/nctv-player`, which remains absent because the vault is still locked.
- The engagement is currently blocked on recovering original vault key material, original provisioning logic, or an external repair payload.

## Evidence References

- EVI-004
- EVI-005
- EVI-006
- EVI-007

## Decision

- Pivot
- Reason: additional live service or env tweaking is unlikely to help; the next meaningful path is recovery of original vault key material, original provisioning artifacts, or a targeted forensic sweep for remnants.
