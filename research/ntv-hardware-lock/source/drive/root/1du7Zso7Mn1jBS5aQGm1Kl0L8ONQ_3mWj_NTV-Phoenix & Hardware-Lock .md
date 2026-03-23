# Implementation Guide: NTV360 Scripts & Services

This document details the implementation, deployment, and practical use cases of the custom resilience and security scripts developed for the NCompass TV Raspberry Pi 5 players.

---

## 1. System Components & Deployment

The custom layer interacts with systemd, Python 3, and Bash to manage hardware security, application integrity, and automated disaster recovery.

### 1.1 Hardware Security Layer
**Components:**
*   `/usr/local/bin/hardware_lock.py`
*   `/usr/local/bin/unlock_vault.py`
*   `/etc/systemd/system/hardware-check.service`
*   `/etc/systemd/system/vault-mount.service`

**Implementation:**
These scripts are designed to prevent the unauthorized execution of NCompass proprietary software on non-company hardware. The `.service` files bind to the `graphical.target` ensuring that the UI environment can only spin up once the hardware thumbprints match.
*   The `hardware_lock.py` script validates the Raspberry Pi Serial Number (`ffb6d42807368154`) and the SD Card CID (`1b534d45423151543089c65df4015a00`).
*   The `unlock_vault.py` utilizes LUKS encryption (`cryptsetup`) to mount `vault.img` using the Pi's Serial Number as the decryption key to `/home/pi/n-compasstv-secure`.

### 1.2 Dead Man's Switch (Watchdog)
**Components:**
*   `/usr/local/bin/nctv-watchdog.sh`
*   `/etc/systemd/system/nctv-watchdog.service`

**Implementation:**
Operates as a continuous background daemon via systemd (`multi-user.target`). It probes for the `/home/pi/n-compasstv` directory every 20 seconds after an initial 60-second grace period at boot. If missing, it immediately alters `/boot/firmware/config.txt` and forces a reboot to trigger recovery.

### 1.3 Phoenix Recovery System (USB Medic)
**Components:**
*   `/usr/local/bin/repairman.sh`
*   `/etc/systemd/system/repairman.service`

**Implementation:**
This script resides on a specialized USB drive. When a corrupted Pi is booted with the USB inserted, the Pi defaults to booting the USB partition (due to boot order `0xf461`). `repairman.sh` initiates, mounts the internal corrupted SD, runs filesystem checks (`fsck`), formats data, and re-flashes the application hierarchy.

---

## 2. Use Cases and Execution Scenarios

### Scenario A: Unauthorized SD Card Cloning
**Context:** A malicious user or rogue dealer duplicates an NTV360 player SD card to use it on their own hardware to avoid licensing or steal proprietary configs.
**Flow:**
1.  The cloned SD boots on the new Raspberry Pi.
2.  `hardware-check.service` initiates `hardware_lock.py`.
3.  The script detects a mismatch between the expected Pi Serial / SD CID and the actual hardware.
4.  The script permanently stops PM2 background services and launches a Chromium Kiosk pointed to `file:///home/pi/lockout.html`.
5.  **Result:** The cloned player is paralyzed and useless to the attacker.

### Scenario B: Application Folder Corruption or Deletion
**Context:** The player's core codebase `/home/pi/n-compasstv` is accidentally deleted, or the file system corrupts the directory during an improper shutdown.
**Flow:**
1.  `nctv-watchdog.service` polls and finds the directory missing.
2.  The script initiates the 5-second nuclear countdown.
3.  It mounts `/boot/firmware/` and renames `config.txt` to `.bak`.
4.  The system reboots into a halted/recovery state, signaling to the field that a Phoenix repair is required.
5.  **Result:** Prevents the player from entering an unknown zombie state that cannot be diagnosed.

### Scenario C: Complete SD Card Failure (Standalone Fallback)
**Context:** A venue's player Pi has a completely dead, unreadable SD card (`/dev/mmcblk0` is absent). The screen is totally black.
**Flow:**
1.  A technician or venue manager unplugs power, inserts the Phoenix USB drive, and plugs the Pi back in.
2.  The system boots from the USB. `repairman.sh` runs automatically.
3.  The script detects the absence of the SD block device.
4.  It alerts the TTY display: `>> MODE: EMERGENCY STANDALONE PLAYER`.
5.  It immediately spins up `player-server` and `player-chromium` from the USB drive.
6.  **Result:** The player screen turns back on and operates off the USB temporarily, keeping the venue's digital signage alive while a replacement SD is mailed.

### Scenario D: Automated Field Repair (Surgery Mode)
**Context:** An SD card is physically present but the OS or file structure is irreparably corrupted.
**Flow:**
1.  Phoenix USB is inserted and powered.
2.  `repairman.sh` boots from the USB and detects the presence of the corrupted SD card.
3.  It alerts the TTY display: `>> MODE: SYSTEM SURGEON (SD Detected)`.
4.  The script scrubs the main filesystem via `fsck`.
5.  It executes a heavy `rsync` operation, cloning a fresh "Master Gold Image" from the USB directly into the SD card.
6.  It rewrites `fstab` and resets the Pi EEPROM bootloader to boot from SD primarily.
7.  The script reboots the system. The Pi ignores the USB and boots freshly off the fully repaired SD card.
8.  **Result:** A fully autonomous "factory reset" repair performed in the field by a minimally trained human—just plug in the USB.
