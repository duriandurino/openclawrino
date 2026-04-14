User-provided forensic sweep output from Telegram attachment 12---aa826fbb-030d-4fd9-a966-3f668b5d2336.md on 2026-04-14.

Key observations copied from operator output:
- dpkg logs show nctv-player 1.1.3 was installed via apt.
- /var/lib/dpkg/info/nctv-player.list and md5sums enumerate the packaged runtime, including /opt/nctv-player/resources/app.asar and /opt/nctv-player/nctv-player.
- /var/tmp/dispsetup.sh exists as a leftover script worth inspection.
- Follow-up inspection showed `/var/tmp/dispsetup.sh` is only a display-setup helper using `xrandr` and optional `/usr/share/ovscsetup.sh`; it is not a provisioning or unlock script.
- `dpkg -s nctv-player` confirms package version 1.1.3 and maintainer metadata only.
- `nctv-player.postinst` only sets the `/usr/bin/nctv-player` alternative and SUID bit on `chrome-sandbox`; no setup, unlock, repair, or provisioning logic was found.
- `strings` and `grep` against `app.asar` and unpacked runtime bits returned no obvious setup/unlock/repair indicators in this pass.
- repairman.sh explicitly searches these external repair roots:
  /mnt/repair-drive/nctv-phoenix
  /media/pi/*/nctv-phoenix
  /run/media/pi/*/nctv-phoenix
  /mnt/*/nctv-phoenix
- unlock_vault.py confirms bind-mount logic against /mnt/nctv-phoenix-secure.
