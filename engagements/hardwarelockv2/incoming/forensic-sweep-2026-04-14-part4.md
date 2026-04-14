User-provided forensic sweep output from Telegram attachment 13---8dd2deab-92fc-4dd8-8ed5-fcf07e499074.md on 2026-04-14.

Key observations copied from operator output:
- `/opt/nctv-player`, `/var/lib/nctv-player`, and `/mnt/nctv-phoenix-secure` currently exist but are effectively empty directories.
- `repairman.sh` confirms the hardened recovery design: if the SD is present but the vault fails to unlock, plaintext runtime restore is disabled on the active system, and a surgical restore from an external `nctv-phoenix` source is required.
- `find_repair_root()` only accepts external trees that contain one of: `var/lib/nctv-player`, `home/pi/.config/nctv-player`, `opt/nctv-player`, or `phoenix_install.sh`.
- Local search found only the current local placeholder/runtime paths: `/etc/nctv-phoenix`, `/var/lib/nctv-phoenix`, `/home/pi/.config/nctv-player`, `/opt/nctv-player`, `/usr/bin/nctv-player`, `/usr/share/doc/nctv-player`, `/var/lib/nctv-player`.
- No external repair-root or local installer artifact was found in this pass.
