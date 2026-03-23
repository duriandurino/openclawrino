# NTV Phoenix & Hardware Lock — Architecture Summary

**System:** NCompass TV NTV360 Player Infrastructure  
**Date:** March 2026  
**Scope:** Component architecture, data flow, and security model

---

## 1. System Component Map

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              RASPBERRY PI 5 HARDWARE                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   EEPROM     │  │  SD Card     │  │    USB       │  │   HDMI/TV    │         │
│  │  (Boot ROM)  │  │ (Primary OS) │  │  (Phoenix)   │  │  (Display)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼─────────────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │                 │
          ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           BOOTLOADER / BOOT SEQUENCE                            │
│                                                                                 │
│   ┌──────────────────────────────────────────────────────────────────────┐       │
│   │ BOOT_ORDER=0xf461  (USB → SD fallback)                             │       │
│   │   • Try USB mass storage first                                       │       │
│   │   • Fall back to SD card if USB unavailable                        │       │
│   └──────────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SYSTEMD SERVICE LAYER                                  │
│                                                                                 │
│   ┌────────────────────────┐    ┌────────────────────────┐                       │
│   │  hardware-check.srv  │───→│   vault-mount.srv      │                       │
│   │  ├─ hardware_lock.py │    │   ├─ unlock_vault.py   │                       │
│   │  ├─ Verify Serial    │    │   ├─ cryptsetup LUKS   │                       │
│   │  └─ Verify SD CID    │    │   └─ mount /dev/mapper │                       │
│   └────────────────────────┘    └───────────┬────────────┘                       │
│                                             │                                   │
│   ┌────────────────────────┐    ┌───────────▼────────────┐                       │
│   │  nctv-watchdog.srv   │    │      pm2-pi.srv        │                       │
│   │  ├─ Dead man's switch│    │      ├─ player-server  │                       │
│   │  ├─ Monitor /n-cstv  │    │      └─ player-chromium │                       │
│   │  └─ Nuclear recovery │    └─────────────────────────┘                       │
│   └────────────────────────┘                                                   │
│                                                                             │
│   ┌────────────────────────┐                                                   │
│   │   repairman.srv        │  (USB boot only)                                  │
│   │   ├─ Emergency Player  │                                                   │
│   │   ├─ Surgery Mode      │                                                   │
│   │   └─ rsync restore     │                                                   │
│   └────────────────────────┘                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION LAYER                                    │
│                                                                                 │
│   ┌────────────────────────────────────────────────────────────────────────┐     │
│   │                    LUKS ENCRYPTED VAULT                               │     │
│   │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │     │
│   │  │   vault.img     │───→│  /dev/mapper/   │───→│ n-compasstv-sec │  │     │
│   │  │  (AES-encrypted)│    │  nctv_data      │    │   ure/            │  │     │
│   │  └─────────────────┘    └─────────────────┘    └─────────────────┘  │     │
│   │           ▲                                    ┌───────────────┐      │     │
│   │           │                                    │ player-server │      │     │
│   │           │         Key = Pi Serial Number     │ ├─ Node.js/   │      │     │
│   │           └────────────────────────────────────│ │   Express     │      │     │
│   │                                              │ │ ├─ Socket.IO    │      │     │
│   │                                              │ │ ├─ SQLite DB    │      │     │
│   │                                              │ │ └─ API routes   │      │     │
│   │                                              │ └───────────────┘      │     │
│   │                                              │ ┌───────────────┐       │     │
│   │                                              │ │player-chromium│       │     │
│   │                                              │ │ ├─ Kiosk mode │       │     │
│   │                                              │ │ ├─ Wayland/X11│       │     │
│   │                                              │ │ └─ http://local│       │     │
│   │                                              │ │   host/ui       │       │     │
│   │                                              │ └───────────────┘       │     │
│   └────────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CLOUD CONNECTIVITY                                   │
│                                                                                 │
│   ┌────────────────────────┐    ┌────────────────────────┐                       │
│   │   REST API             │    │   Socket.IO            │                       │
│   │   nctvapi2.n-compass   │◄──→│   nctvsocket.n-compass │                       │
│   │   .online              │    │   .online              │                       │
│   │                        │    │                        │                       │
│   │   ├─ Content sync      │    │   ├─ Screenshot        │                       │
│   │   ├─ Playlists         │    │   ├─ Reboot            │                       │
│   │   ├─ License check     │    │   ├─ Content update    │                       │
│   │   └─ Telemetry         │    │   ├─ CEC control       │                       │
│   └────────────────────────┘    │   └─ Speedtest         │                       │
│                                 └────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Hardware Layer

| Component | Specification | Role |
|-----------|-------------|------|
| Raspberry Pi 5 | 4GB+ RAM, ARM64 | Primary compute |
| EEPROM | 512KB Boot ROM | Boot order configuration |
| SD Card | 16GB+ microSD | Primary storage (encrypted vault) |
| USB Drive | 16GB+ USB 3.0 | Phoenix recovery media |
| HDMI Output | CEC-enabled | TV control and display |

### 2.2 Security Components

| Component | Technology | Input | Output |
|-----------|-----------|-------|--------|
| Hardware Fingerprint | CPU Serial + SD CID | `/proc/cpuinfo`, `/sys/block/mmcblk0/device/cid` | Match/Mismatch decision |
| Vault Encryption | LUKS (dm-crypt) | Pi Serial Number | `/dev/mapper/nctv_data` |
| Lockout UI | Chromium Kiosk | `file:///home/pi/lockout.html` | Visual lockout screen |

### 2.3 Systemd Services

| Service | Type | Trigger | Dependencies |
|---------|------|---------|--------------|
| `hardware-check.service` | Idle | `graphical.target` | — |
| `vault-mount.service` | Oneshot | `hardware-check.service` | `hardware-check.service` |
| `nctv-watchdog.service` | Simple | `multi-user.target` | `network.target` |
| `repairman.service` | Simple | `multi-user.target` (USB only) | `network.target` |

### 2.4 Application Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Runtime | Node.js | v20.x | Player server execution |
| Process Mgr | PM2 | Latest | Service orchestration |
| Database | SQLite3 | 3.x+ | Local data storage |
| Web Server | NGINX | Latest | Static asset serving |
| Browser | Chromium | Latest | Kiosk display |
| TV Control | CEC Utils | Latest | HDMI-CEC commands |

---

## 3. Data Flow Diagrams

### 3.1 Normal Boot Flow

```
┌─────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────┐
│  Power  │───→│  EEPROM Boot │───→│  SD Card     │───→│  systemd     │───→│ Graphical│
│  On     │    │  (0xf461)    │    │  Mounted     │    │  Init        │    │ Target  │
└─────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └────┬────┘
                                                                               │
                                    ┌──────────────────────────────────────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │ hardware-check   │
                           │ .service starts  │
                           └────────┬─────────┘
                                    │
                                    ▼
                           ┌──────────────────┐
                           │ hardware_lock.py │
                           │ ├─ Read Serial   │
                           │ ├─ Read SD CID   │
                           │ └─ Compare       │
                           └────────┬─────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                    Match ▼                Mismatch ▼
                         │                     │
                         ▼                     ▼
                ┌─────────────────┐   ┌─────────────────┐
                │ unlock_vault.py │   │ Lock System     │
                │ ├─ cryptsetup   │   │ ├─ Stop PM2     │
                │ ├─ mount        │   │ ├─ Stop svcs    │
                │ └─ chown        │   │ └─ Kiosk Lock   │
                └────────┬────────┘   └─────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ PM2 Starts       │
                │ ├─ player-server │
                │ └─ player-chrom  │
                │    ium           │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Content Plays  │
                │ on TV          │
                └─────────────────┘
```

### 3.2 Phoenix Recovery Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PHOENIX USB BOOT FLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────────────┐
│ Power On +   │───→│ EEPROM sees  │───→│ repairman.service executes           │
│ USB Inserted │    │ USB (sdb)    │    └──────────────┬───────────────────────┘
└──────────────┘    └──────────────┘                   │
                                                       ▼
                                  ┌──────────────────────────────────────┐
                                  │ Check /dev/mmcblk0                   │
                                  │ (SD card presence)                   │
                                  └──────────────┬───────────────────────┘
                                                 │
                              ┌──────────────────┴──────────────────┐
                              │                                      │
                       Absent ▼                             Present ▼
                              │                                      │
                    ┌─────────┴──────────┐              ┌─────────────┴────────────┐
                    │ EMERGENCY MODE     │              │ SURGERY MODE             │
                    │                    │              │                          │
                    │ TTY Display:     │              │ 1. fsck boot partition   │
                    │ "EMERGENCY         │              │ 2. fsck root partition   │
                    │  STANDALONE        │              │ 3. rsync USB→SD        │
                    │  PLAYER"           │              │ 4. Rebuild fstab        │
                    │                    │              │ 5. Reset boot order     │
                    │ Actions:           │              │ 6. Force GUI target     │
                    │ ├─ pm2 start       │              │ 7. Reboot to SD         │
                    │ ├─ player-server   │              │                          │
                    │ └─ player-chrom    │              └────────────┬─────────────┘
                    │                    │                           │
                    └─────────┬──────────┘                           │
                              │                                      │
                              ▼                                      ▼
                    ┌─────────────────┐                   ┌─────────────────┐
                    │ Player runs from  │                   │ Repaired SD     │
                    │ USB temporarily   │                   │ boots normally  │
                    └─────────────────┘                   └─────────────────┘
```

### 3.3 Hardware Lock Verification Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HARDWARE LOCK STATE MACHINE                           │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────┐
                         │    START    │
                         └──────┬──────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Read /proc/cpuinfo    │
                    │ Extract Serial        │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Read /sys/block/      │
                    │ mmcblk0/device/cid    │
                    │ Extract SD CID        │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Compare against       │
                    │ hardcoded values      │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
        Match ▼                             Mismatch ▼
              │                                   │
    ┌─────────┴──────────┐            ┌──────────┴───────────┐
    │ AUTHORIZED PATH    │            │ LOCKOUT PATH         │
    │                    │            │                      │
    │ ├─ Call unlock_    │            │ ├─ Stop pm2-pi       │
    │ │   vault.py       │            │ ├─ Stop watchdog     │
    │ ├─ Mount vault     │            │ ├─ Stop all PM2      │
    │ └─ Start PM2 svcs  │            │ ├─ Launch Chromium   │
    │                    │            │ └─ Display lockout   │
    └─────────┬──────────┘            │    .html             │
              │                       └──────────────────────┘
              ▼
    ┌─────────────────┐
    │ System Operational
    └─────────────────┘
```

### 3.4 Watchdog Monitoring Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DEAD MAN'S SWITCH LOGIC                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   Boot Start    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ 60s Grace Period │────→│ Countdown to    │
│ (allow boot)    │     │ Arm Watchdog    │
└─────────────────┘     └────────┬────────┘
                                   │
                                   ▼
                         ┌─────────────────┐
                    ┌───→│ Check /home/pi/ │
                    │    │ n-compasstv    │
                    │    │ exists?         │
                    │    └────────┬────────┘
                    │             │
              No ┌──┴──┐ Yes     │
                 │     └──────────┘
                 ▼                 │
        ┌─────────────────┐        │
        │ 5s TTY Warning  │        │
        │ "PREPARING      │        │
        │  NUCLEAR..."    │        │
        └────────┬────────┘        │
                 │                │
                 ▼                │
        ┌─────────────────┐       │
        │ Mount /boot/      │       │
        │ firmware          │       │
        │ Rename config.txt │       │
        │ → config.txt.bak  │       │
        └────────┬────────┘       │
                 │                │
                 ▼                │
        ┌─────────────────┐       │
        │    REBOOT       │       │
        │ (Recovery Mode) │       │
        └─────────────────┘       │
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Sleep 20s      │
                         │ Loop back      │
                         └─────────────────┘
```

---

## 4. Security Model

### 4.1 Threat Model

| Threat | Mitigation | Component |
|--------|-----------|-----------|
| SD cloning to unauthorized Pi | Hardware fingerprint check | `hardware_lock.py` |
| Vault extraction from SD | LUKS encryption with hardware-derived key | `unlock_vault.py` |
| Application tampering | Encrypted vault + integrity checks | Watchdog + vault |
| Filesystem corruption | Dead man's switch recovery | `nctv-watchdog.sh` |
| Complete SD failure | USB emergency fallback | `repairman.sh` |
| Boot-time attack | EEPROM boot order enforcement | EEPROM config |

### 4.2 Encryption Details

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         VAULT ENCRYPTION DETAILS                             │
└─────────────────────────────────────────────────────────────────────────────┘

Vault Container: /home/pi/vault.img
├── Format: LUKS (Linux Unified Key Setup)
├── Cipher: AES-XTS-PLAIN64 (default dm-crypt)
├── Key Size: 256-bit
├── Passphrase: Raspberry Pi Serial Number
│   └── Source: /proc/cpuinfo (hex string)
│   └── Example: "ffb6d42807368154"
│
└── Mount Chain:
    1. cryptsetup open vault.img nctv_data --key-file -
       └─ Creates /dev/mapper/nctv_data
    2. mount /dev/mapper/nctv_data /home/pi/n-compasstv-secure
       └─ Decrypted filesystem available

Security Properties:
├── Vault is bound to specific Pi (serial-derived key)
├── Cloned vault cannot be decrypted on different Pi
├── No stored key material (derived at runtime)
└── cryptsetup close wipes key from kernel on unmount
```

### 4.3 Boot Security

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BOOT SECURITY CHAIN                                │
└─────────────────────────────────────────────────────────────────────────────┘

Boot Order: 0xf461 (hex)
├─ 4 = USB mass storage
├─ 6 = USB device boot (MSD)
├─ 1 = SD card (MMC)
└─ f = Restart (loop)

Priority: USB first, then SD

Use Cases:
├── Normal boot: SD card (fails USB check, falls through)
├── Recovery boot: USB present, boots from USB
└── Forced recovery: watchdog renames config.txt

EEPROM Protection:
├── WDT_TIMEOUT=15000 (15s hardware watchdog)
├── HALT_ON_ERROR=0 (reboot on error)
└── BOOT_ORDER locked until reset
```

---

## 5. Service Dependencies

### 5.1 Startup Dependency Graph

```
graph TD
    A[systemd] --> B[graphical.target]
    A --> C[multi-user.target]
    
    B --> D[hardware-check.service]
    D --> E[vault-mount.service]
    E --> F[pm2-pi.service]
    
    C --> G[nctv-watchdog.service]
    C --> H[repairman.service]
    
    D -.->|Requires| I[Local FS]
    E -.->|Requires| D
    E -.->|Before| F
    
    style D fill:#f9f,stroke:#333
    style E fill:#f9f,stroke:#333
    style G fill:#ff9,stroke:#333
    style H fill:#99f,stroke:#333
```

### 5.2 Conditional Execution

| Service | Condition | Action if Skipped |
|---------|-----------|-------------------|
| `hardware-check.service` | Always | System cannot decrypt vault |
| `vault-mount.service` | Hardware check passes | PM2 starts without vault |
| `nctv-watchdog.service` | Always | No corruption monitoring |
| `repairman.service` | Boot device = USB | N/A (SD boot skip) |

---

## 6. Configuration Reference

### 6.1 Critical Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| EEPROM config | `/usr/bin/rpi-eeprom-config` | Boot order, watchdog timeout |
| Boot config | `/boot/firmware/config.txt` | Display, kernel parameters |
| Service configs | `/etc/systemd/system/*.service` | Startup behavior |
| Hardware lock | `/usr/local/bin/hardware_lock.py` | Authorized serial/CID |
| Vault script | `/usr/local/bin/unlock_vault.py` | Decryption logic |
| PM2 ecosystem | `/home/pi/n-compasstv-secure/ecosystem.config.js` | Process definitions |

### 6.2 Environment Variables

| Variable | Set By | Used By |
|----------|--------|---------|
| `PM2_HOME` | `hardware_lock.py` | PM2 process manager |
| `DISPLAY=:0` | systemd service files | Chromium kiosk |
| `WAYLAND_DISPLAY=wayland-0` | systemd service files | Pi 5 display |
| `XDG_RUNTIME_DIR` | systemd service files | Wayland/X11 |

---

## 7. Monitoring & Telemetry

### 7.1 Health Check Points

| Check | Script | Frequency | Failure Action |
|-------|--------|-----------|--------------|
| Hardware fingerprint | `hardware_lock.py` | Boot only | Lockout kiosk |
| Vault mount | `unlock_vault.py` | Boot only | Exit with error |
| Directory existence | `nctv-watchdog.sh` | Every 20s | Nuclear reboot |
| PM2 process status | `pm2-watchdog.sh` | Every 7 min | Restart processes |
| System uptime | `check-uptime.sh` | Every 8 hours | Force reboot |

### 7.2 Log Aggregation

```
Log Sources:
├── systemd journal: journalctl -u <service>
├── PM2 logs: ~/.pm2/logs/
├── Player logs: /home/pi/n-compasstv-secure/player-server/src/logs/
└── Application DB: /home/pi/n-compasstv-secure/player-server/src/db/_data.db

Key Tables (SQLite):
├── error_logs: Application errors
├── computer_usage: CPU/RAM/uptime telemetry
├── internet_logs: Speed test results
└── content_play_log: Playback history
```

---

**End of Architecture Summary**
