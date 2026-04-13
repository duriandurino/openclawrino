# Enum Evidence Index

- EVI-004 - live target outputs for `hardware_lock.py`, `unlock_vault.py`, `hardware-lock.env`, `vault.img`, `cryptsetup luksDump`, `mount`, and `/dev/mapper`
- EVI-005 - live verification that current Pi serial and SHA256 of SD CID match the edited env, followed by direct `unlock_vault.py` failure at `cryptsetup open`
- EVI-006 - service unit bodies, broken `/usr/bin/nctv-player` symlink chain, file timestamps, and journal evidence of repeated `vault-mount.service` failures
- EVI-007 - `repairman.sh`, `nctv-watchdog.sh`, and filesystem inspection showing no mounted external repair source and a fail-closed recovery design
