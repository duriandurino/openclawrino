# Target Profile — PulseLink Pi (Enhanced)

## Device Summary

| Attribute | Value |
|-----------|-------|
| **Device** | Raspberry Pi 5 Model B, 4GB RAM |
| **SoC** | Broadcom BCM2712 (4 × Cortex-A76 @ 2.4GHz) |
| **User** | `pi@raspberry` (default credentials) |
| **OS** | Debian GNU/Linux 13 (trixie) / Raspberry Pi OS |
| **Kernel** | Linux 6.x (Raspberry Pi OS custom kernel) |
| **Security posture** | App-level only, NOT kernel/OS hardened |

## Physical Access Status

| Capability | Status |
|------------|--------|
| **Physical access** | ✅ YES |
| **SD card removable** | ❌ LOCKED to device ID |
| **SD card imaging (off-device)** | ❌ BLOCKED |
| **USB access** | ✅ Available (4× USB 3.0, 2× USB 2.0) |
| **GPIO header** | ✅ Available (40-pin) |
| **UART/Serial** | ✅ Available via GPIO pins |
| **JTAG** | ⚠️ Potentially available via GPIO (BCM2712) |
| **HDMI output** | ✅ 2× micro-HDMI |
| **Ethernet** | ✅ Gigabit Ethernet |
| **Wi-Fi** | ✅ 802.11ac dual-band |
| **Bluetooth** | ✅ BLE 5.0 |

## Critical Constraint: SD Card Lock

The SD card is cryptographically locked to this specific device ID. This means:

- **Cannot remove** the SD card and mount it on another machine
- **Cannot image** the SD card for offline analysis
- **Cannot modify** the filesystem from outside the device
- **All storage-level attacks must occur ON the device itself**
- The lock is enforced at the firmware/bootloader level

### Implications for Pentesting

1. **Offline attacks eliminated:** No filesystem extraction, no offline password cracking from shadow files, no binary analysis from mounted volumes
2. **Live-only engagement:** All exploitation must happen while the device is running
3. **Physical interfaces become critical:** GPIO, UART, JTAG, USB become primary attack vectors since storage is off-limits externally
4. **Need persistence on device:** Any tools/payloads must be deployed through the running OS, not written to SD directly

## Installed Applications

| Application | Path | Type | Access |
|-------------|------|------|--------|
| **PulseLink** | `/usr/local/bin/pulselink` | Electron desktop app | Binary in PATH |
| **PulseLink app data** | `/opt/pulselink` | App resources | ❌ Permission denied |
| **Electron Player** | `/opt/electron-player` | Electron/Chromium runtime | ✅ Accessible |
| **Electron Player scripts** | `/opt/electron-player/resources/scripts/` | **Discovered subdirectory** | ✅ Accessible |
| **WidevineCdm** | `/opt/WidevineCdm` | DRM module (L3) | ✅ Accessible |
| **Electron config** | `/home/pi/.config/electron-player` | User data dir | ✅ Likely accessible |
| **Chromium crash reports** | `/home/pi/.config/chromium/Crash Reports` | Crash dumps | ✅ Likely accessible |

## Running Processes (Known)

| Process | Notes |
|---------|-------|
| `pulselink` | Main Electron app process |
| `electron-player` | Electron runtime (utility, gpu, audio, renderer, zygote, ui) |

## User Account Analysis

### `pi@raspberry`
- **Default Raspberry Pi OS account** — high likelihood default password still set
- **Historical CVE:** CVE-2021-38759 — default `raspberry` password not forced change (affects through OS 5.10)
- **Privileges:** Standard user with possible sudo access (default RPi config)
- **Home directory:** `/home/pi/` — standard layout
- **Shell:** Likely `/bin/bash`

## Network Interfaces (CONFIRMED)

| Interface | Status | IP | MAC |
|-----------|--------|----|----|
| `lo` | UP | 127.0.0.1/8 | — |
| `eth0` | **DOWN** (no cable) | None | `2c:cf:67:04:0b:d0` |
| `wlan0` | **UP** (connected) | **192.168.0.125/24** | `2c:cf:67:04:0b:d1` |

- **Network-reachable:** YES — live on WiFi at 192.168.0.125
- **Likely gateway:** 192.168.0.1
- **Subnet:** 192.168.0.0/24
- **Ethernet:** Available but not connected

## Filesystem Notes

- **Root filesystem:** ext4 on SD card (locked)
- **Boot partition:** FAT32 (locked)
- **No LUKS encryption** expected on default RPi OS install
- **Writable locations for pi user:** `/home/pi/`, `/tmp/`, `/var/tmp/`, potentially `/dev/shm/`
- **Writable locations with sudo:** Everywhere

---

*Profile enhanced with SD lock constraint analysis. All vectors reframed for live-device-only engagement.*
