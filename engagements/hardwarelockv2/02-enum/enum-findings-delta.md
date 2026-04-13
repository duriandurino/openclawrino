# Enum Findings Delta

- confirmed findings:
  - V2 compares actual Pi serial against `AUTHORIZED_PI_SERIAL`
  - V2 compares `sha256(actual_sd_cid)` against `AUTHORIZED_SD_CID_SHA256`
  - current env values now match current hardware exactly
  - current vault unlock key formula is `sha256(f"AUTHORIZED_PI_SERIAL:AUTHORIZED_SD_CID_SHA256")` as raw bytes
  - the real LUKS vault rejects that derived key with `cryptsetup` exit status 2
  - `/usr/bin/nctv-player` resolves to `/opt/nctv-player/nctv-player`, which is absent until secure content is exposed
  - no external repair payload is currently mounted for `repairman.sh` to use
- suspected leads:
  - the original vault was provisioned with different authorized values or an earlier unlock derivation routine
  - the current `unlock_vault.py` is edited state and may not match the original deployment logic
  - an external repair source or another working player may still contain the original provisioning materials
- unresolved items:
  - original provisioning-time serial/hash tuple or other key material
  - original unmodified `unlock_vault.py` or installer workflow
  - availability of any repair USB, backup, or sibling device containing `nctv-phoenix` payloads
- escalation to next phase is not justified: not yet, because no viable exploit path exists without recovering the vault key material or original provisioning artifacts
