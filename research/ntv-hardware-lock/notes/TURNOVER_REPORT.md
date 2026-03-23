# NTV Phoenix & Hardware Lock — Turnover Report

## Purpose

This document consolidates the turnover materials for the NTV360 Raspberry Pi player platform, focusing on the **Hardware Lock** system, the **Phoenix recovery workflow**, and the surrounding **player runtime** needed to operate and maintain the deployment.

This is an internal handoff document intended to help a new maintainer understand what exists today, how the parts fit together, and what should be validated next.

---

## Executive Summary

The system appears to be built around three operational layers:

1. **NTV360 Player Runtime**
   - Raspberry Pi 5 signage stack using Node.js, PM2, Chromium kiosk, NGINX, and a web dashboard/cloud backend.
   - Core app directories are under `/home/pi/n-compasstv/` and `/var/www/html/ui`.

2. **Hardware Lock**
   - A boot-time integrity and anti-cloning mechanism.
   - Validates the Raspberry Pi serial and SD card CID.
   - If validation succeeds, the secure runtime is unlocked and PM2 services are started.
   - If validation fails, the secure content is unmounted/locked and a Chromium lock screen is shown.

3. **Phoenix Recovery / Repair Tool**
   - A field-recovery concept intended to revive or repair broken players from a USB-based recovery environment.
   - Designed for two scenarios:
     - temporary standalone operation from USB if SD media is dead
     - automated repair/reimage of a corrupted SD card

Together, these layers aim to make the players:
- resistant to simple SD cloning
- self-healing or repairable in the field
- manageable through a dashboard-driven control plane

---

## Source Materials Reviewed

Primary sources were taken from the shared Google Drive turnover folder and downloaded into:

- `research/ntv-hardware-lock/source/drive/root/`
- `research/ntv-hardware-lock/source/drive/kent_turnover/`

Key files reviewed:

- `NTV-Phoenix & Hardware-Lock .md`
- `player_pi (pi player documentation).md`
- `web_dashboard (dashboard website documentation).md`
- `scripts_and_services (NTV_Phoenix & Hardware-Lock).md`
- `setup (executable sudo).sh`
- `setup (phoenix & hardware-lock) (not fully working).sh`
- `installer.sh`
- `pm2-starter.sh`
- `watchdog-starter.sh`
- `config.json`
- `Installing Player (Read Thoroughly) (old version).txt`
- `improvements.md`

---

## System Overview

### 1. Player Runtime

The NTV360 player turns a Raspberry Pi 5 into a digital signage appliance.

Documented runtime characteristics include:

- **Player Server**: Node.js/Express app
- **UI**: Web UI served locally, then displayed in Chromium kiosk
- **NGINX**: local web serving layer
- **PM2**: process supervisor for multiple player processes
- **Chromium kiosk**: fullscreen player interface
- **SQLite / local data**: used by the player stack
- **AnyDesk**: remote support access
- **HDMI-CEC**: TV power/input control
- **Watchdog + scheduled reboots**: unattended resilience measures

From the ecosystem config, the expected PM2-managed apps include:

- `player-server`
- `player-puppeteer`
- `player-electron`
- `player-chromium`

### 2. Control Plane / Dashboard

The dashboard is the cloud control plane for the players.

Documented functions include:

- player/license assignment
- content and playlist management
- scheduling
- remote device actions
- telemetry and screenshots
- status and reporting

The **license key** appears to be the bridge between the physical player and the cloud platform.

### 3. Security & Resilience Layer

The custom security/resilience layer adds:

- hardware verification at boot
- secure vault unlock flow
- watchdog response if critical directories disappear
- a Phoenix USB recovery model for repair/revival

---

## Hardware Lock — What It Does

The Hardware Lock is the anti-cloning and secure-boot gate for the player runtime.

### Main components

Documented components include:

- `/usr/local/bin/hardware_lock.py`
- `/usr/local/bin/unlock_vault.py`
- `/etc/systemd/system/hardware-check.service`
- `/etc/systemd/system/vault-mount.service`

### Boot-time behavior

At a high level:

1. the graphical target is reached
2. `hardware-check.service` runs `hardware_lock.py`
3. the script reads:
   - Raspberry Pi serial from `/proc/cpuinfo`
   - SD card CID from `/sys/block/mmcblk0/device/cid`
4. values are compared with authorized values
5. if valid:
   - vault unlock flow is triggered
   - secure PM2 stack is started
6. if invalid:
   - PM2/services are stopped
   - secure mount is unmounted/closed
   - Chromium lockout UI is launched

### Security intent

The design goal is to stop someone from cloning the player SD card and running proprietary software on unauthorized hardware.

### Observed implementation details

From the turnover scripts:

- authorized hardware values are hardcoded in script text in at least one version
- one implementation starts secure services from `/home/pi/n-compasstv-secure/`
- failed verification leads to a kiosk lock page (`file:///home/pi/lockout.html`)
- the service environment is tuned for graphical boot on Raspberry Pi (`DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`, `XDG_RUNTIME_DIR=/run/user/1000`)

### Operational meaning

If you are maintaining this system, the hardware lock is not just a UI lock — it directly controls whether the protected runtime is allowed to mount/unlock and start.

---

## Vault / Secure Runtime Flow

The turnover materials indicate a protected runtime or protected data area.

### Documented behavior

- `unlock_vault.py` uses `cryptsetup`
- `vault.img` is mounted to `/home/pi/n-compasstv-secure`
- one turnover note claims the Pi serial is used as the decryption key
- the success path then starts PM2 services from the secure location

### Interpretation

The design appears to be:

- keep sensitive runtime/data in an encrypted container
- only unlock it on authorized hardware
- start protected services after successful verification

### Important note

Some turnover files show different hardcoded identifiers across versions. That means there may be:

- multiple generations of the implementation
- outdated notes mixed with newer scripts
- copied examples that do not exactly match production

This must be validated on a live player before treating any specific key path as authoritative.

---

## Phoenix Recovery System — What It Does

Phoenix is described as a USB-based recovery model for field repair.

### Main components

Documented components include:

- `/usr/local/bin/repairman.sh`
- `/etc/systemd/system/repairman.service`

### Intended scenarios

Phoenix is described as covering at least two major failure modes:

#### 1. Emergency Standalone Mode

If the SD card is completely unreadable or absent:

- boot from USB
- run recovery logic
- detect missing `/dev/mmcblk0`
- start a temporary player directly from the USB environment
- keep the display alive while waiting for replacement media

#### 2. Surgery / Repair Mode

If the SD card exists but the installed system is corrupted:

- boot from USB
- detect the internal SD card
- run filesystem repair and/or reimage logic
- restore a known-good image onto the SD card
- rewrite boot configuration
- reboot back to SD-based normal operation

### Boot assumption behind Phoenix

The turnover material references a Raspberry Pi EEPROM boot order that prefers USB in at least some conditions. The docs mention a boot order string like `0xf461`, which aligns with the idea that the device can boot into a recovery USB environment when needed.

### Why Phoenix matters operationally

Phoenix reduces dependence on a fully manual rebuild. Instead of deep troubleshooting on-site, a minimally trained tech can potentially:

- insert recovery USB
- power-cycle device
- let scripted recovery handle the rest

That is a major operational advantage for distributed field deployments.

---

## Watchdog / Dead Man’s Switch

The turnover docs also describe a watchdog-style recovery trigger.

### Main components

- `/usr/local/bin/nctv-watchdog.sh`
- `/etc/systemd/system/nctv-watchdog.service`
- Raspberry Pi hardware watchdog enablement via `/boot/config.txt`
- Linux watchdog package/service

### Intended logic

The watchdog monitors for catastrophic corruption conditions, especially the loss of `/home/pi/n-compasstv`.

If the expected application directory disappears, the system is intended to avoid running in a broken zombie state. Instead, it escalates into a recoverable failure condition that signals the need for Phoenix repair.

### Additional resilience

The broader player docs also describe:

- PM2 checks every ~7 minutes
- nightly reboot
- uptime-triggered reboot
- hardware watchdog for hangs

These form a layered resilience model:

- process restart
- service restart
- reboot
- recovery mode
- USB repair path

---

## Installation / Deployment Flow

Based on the turnover materials, a typical fresh setup appears to be:

1. flash Raspberry Pi OS onto SD card
2. configure display sleep/screensaver behavior
3. install AnyDesk
4. run installer package/scripts
5. install runtime dependencies:
   - nginx
   - nodejs
   - npm
   - pm2
   - chromium
   - gnome-terminal
   - scrot
   - unclutter
   - cec-utils
6. deploy player server and player UI
7. configure PM2 startup
8. configure watchdog
9. reboot and enter/apply license key
10. connect to dashboard and pull operational content

### Important version drift

The docs include both older and newer installation references:

- older instructions mention Buster and Node 12-era assumptions
- newer scripts mention Pi 5 / newer distro compatibility and Node 20

This strongly suggests historical drift. A maintainer should not assume all install docs refer to the same live baseline.

---

## Key Files / Paths Worth Knowing

### Runtime paths

- `/home/pi/n-compasstv/`
- `/home/pi/n-compasstv/player-server/`
- `/var/www/html/ui`
- `/home/pi/.pm2`
- `/home/pi/.config/lxpanel/LXDE-pi/panels/`

### Security / recovery paths

- `/usr/local/bin/hardware_lock.py`
- `/usr/local/bin/unlock_vault.py`
- `/usr/local/bin/nctv-watchdog.sh`
- `/usr/local/bin/repairman.sh`
- `/etc/systemd/system/hardware-check.service`
- `/etc/systemd/system/vault-mount.service`
- `/etc/systemd/system/nctv-watchdog.service`
- `/etc/systemd/system/repairman.service`
- `file:///home/pi/lockout.html`

### Configuration artifacts seen in docs

- `ecosystem.config.js`
- `config.json`
- `panel`
- potential `.env` files in player runtime directories

---

## Likely Operational Flow

### Normal boot

1. Pi boots
2. graphical environment becomes available
3. hardware verification runs
4. vault/protected runtime unlocks if authorized
5. PM2 starts player services
6. Chromium kiosk displays signage UI
7. player communicates with cloud dashboard

### Unauthorized clone boot

1. Pi boots on wrong hardware
2. serial/CID mismatch occurs
3. secure runtime is not allowed to run
4. existing mounts/services are shut down
5. lockout page is displayed

### Corruption event

1. core player directory disappears or system becomes unstable
2. watchdog/escalation logic triggers
3. device halts or enters recoverable broken state
4. technician uses Phoenix USB workflow

### Phoenix repair

1. recovery USB inserted
2. Pi boots recovery environment
3. script chooses standalone mode or surgery mode
4. system either temporarily runs from USB or repairs SD
5. final reboot returns player to normal state

---

## Risks and Maintenance Concerns

### 1. Hardcoded secrets / identifiers

The turnover docs explicitly show hardcoded serials, CIDs, and config values in scripts. That creates maintainability and security issues.

### 2. Documentation drift

There are multiple generations of setup guidance and scripts. Some files are clearly marked “not fully working,” and some old docs target older OS/package assumptions.

### 3. Single-developer knowledge concentration

A lot of the system logic appears custom and operationally important. If the original developer is gone, loss of tacit knowledge becomes the main risk.

### 4. Recovery path confidence gap

Phoenix is described well conceptually, but its real-world reliability should be verified end-to-end on test hardware.

### 5. Version sprawl

The environment spans:
- Raspberry Pi bootloader settings
- systemd services
- shell scripts
- Python scripts
- Node.js/PM2 app stack
- web dashboard integration

Without a canonical version map, troubleshooting will be harder.

---

## Recommended Next Actions for Handoff

### Priority 1 — Build a validated lab baseline

Set up one known-good Pi and document:

- exact OS version
- Node version
- package versions
- PM2 config
- systemd units
- active scripts
- actual boot order / EEPROM config
- whether secure vault path is active in production

### Priority 2 — Verify boot and failure scenarios live

Test, document, and record outcomes for:

- normal boot
- hardware mismatch boot
- deleted runtime directory
- failed player process
- Phoenix standalone boot
- Phoenix SD repair flow

### Priority 3 — Create a canonical maintainer runbook

Convert the current mixed turnover docs into one maintained operational source of truth.

### Priority 4 — Remove hardcoded hardware identity from code

The turnover `improvements.md` is correct to flag this. Long-term, dynamic provisioning or per-device sealed config is more maintainable than static literals embedded in scripts.

### Priority 5 — Establish asset inventory

Track for each field unit:

- Pi serial
- SD CID
- license key / device mapping
- AnyDesk ID
- software version
- last successful Phoenix test

---

## Conclusion

The turnover docs describe a fairly sophisticated Raspberry Pi signage platform with a layered approach to runtime control, anti-cloning, recovery, and fleet operations.

The most important concepts to retain are:

- **Player runtime** powers signage and cloud connectivity
- **Hardware Lock** gates execution to authorized hardware
- **Vault flow** protects sensitive runtime/data
- **Watchdog** detects catastrophic corruption conditions
- **Phoenix** provides USB-based field recovery and repair

The biggest gap is not absence of ideas — it is the lack of a single validated source of truth. The next step is to convert these turnover notes into tested operational knowledge on a real player.
