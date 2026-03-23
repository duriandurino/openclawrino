# NCompass TV Player (NTV360)

Digital signage media player for **Raspberry Pi 5**, built with Node.js, Express, and Chromium kiosk mode. Manages content playlists, scheduled playback, HDMI-CEC TV control, remote monitoring, and programmatic ads -- all driven from the NCompass TV cloud platform.

> **Player Server** `v2.9.43-pi5` &nbsp;|&nbsp; **Player UI** `v2.4.1` &nbsp;|&nbsp; **Node.js 20**

---

## What the System Does

The NTV360 Player turns a Raspberry Pi 5 into a fully managed, always-on digital signage endpoint. Once deployed and licensed, the player operates autonomously -- pulling content from the cloud, displaying it on a connected TV, and reporting back health and playback data -- with zero manual intervention required day-to-day.

### Content Playback

The player receives **playlists** from the NCompass TV cloud platform. Each playlist contains a sequence of media items -- images, videos, and web-based content -- organized into **templates** with configurable **zones** (multi-zone layouts). The player downloads all media assets locally so playback continues uninterrupted even during temporary network outages. Content schedules support date ranges, specific days of the week, time windows, and alternating-week patterns.

### Cloud Connectivity

A persistent **Socket.IO** connection to the NCompass TV cloud enables real-time remote control. Administrators can trigger content updates, capture screenshots, reboot the device, run speed tests, and manage HDMI-CEC TV power -- all from the web portal without physical access to the Pi.

### License Management

Each player is bound to a **license key** that associates it with a specific host (venue/location) in the NCompass TV platform. The license determines which playlists, business hours, timezone, and display settings apply. The player reports connection timestamps so the platform can track uptime and availability.

### Self-Healing and Reliability

The system is built for unattended 24/7 operation:

- **Hardware watchdog** -- if the Pi hangs or becomes unresponsive, the hardware timer triggers an automatic reboot
- **PM2 watchdog** -- a crontab job checks every 7 minutes that the `player-server` process is running and restarts it if needed
- **Nightly reboot** -- a scheduled midnight reboot keeps the system fresh
- **Uptime monitor** -- forces a reboot if the system has been running continuously for more than ~25 hours
- **Auto-restart on crash** -- PM2 automatically restarts any process that exits or exceeds its memory limit

### TV Control via HDMI-CEC

The player controls the connected TV through **HDMI-CEC** (Consumer Electronics Control). It can power the TV on/off, set the Pi as the active input source, and respect configured business hours -- automatically turning the display off outside operating hours and back on when business hours resume.

### Programmatic Advertising

The player supports **programmatic ad insertion** through integrations with Vistar Media and Fast Edge (DCP/PI agent). When enabled, the player fetches and plays programmatic ad creatives alongside regular content, tracking impressions for proof-of-play reporting.

### Monitoring and Telemetry

The player continuously collects and reports:

- **Play logs** -- which content played, when, and for how long
- **Resource usage** -- CPU, RAM, and uptime metrics
- **Screenshots** -- on-demand screen captures sent to the cloud
- **Speed tests** -- network bandwidth measurements
- **Error logs** -- application errors and connectivity issues

### Remote Access

**AnyDesk** is installed on every player for remote desktop access. Administrators can connect to any player for troubleshooting, configuration, or manual intervention. AnyDesk IDs can be reset remotely through the socket control interface.

---

## Table of Contents

- [What the System Does](#what-the-system-does)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Fresh Installation (Pi 5)](#fresh-installation-pi-5)
  - [Step 1 -- Flash Raspberry Pi OS](#step-1--flash-raspberry-pi-os)
  - [Step 2 -- Disable Screen Saver](#step-2--disable-screen-saver)
  - [Step 3 -- Install AnyDesk (Remote Access)](#step-3--install-anydesk-remote-access)
  - [Step 4 -- Run the Installer Script](#step-4--run-the-installer-script)
  - [Step 5 -- Start PM2 and Register Startup](#step-5--start-pm2-and-register-startup)
  - [Step 6 -- Setup Watchdog](#step-6--setup-watchdog)
  - [Step 7 -- Verify Installation](#step-7--verify-installation)
- [How It Works](#how-it-works)
- [Environment Configuration](#environment-configuration)
- [PM2 Process Management](#pm2-process-management)
- [Scheduled Tasks (Crontab)](#scheduled-tasks-crontab)
- [Boot Configuration](#boot-configuration)
- [API Routes](#api-routes)
- [Database](#database)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Socket Controls](#socket-controls)
- [Cloning a Player Image](#cloning-a-player-image)
- [Troubleshooting](#troubleshooting)
- [Authors & Maintainers](#authors--maintainers)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                   Raspberry Pi 5                     │
│                                                      │
│  ┌──────────────┐    ┌────────────────────────────┐  │
│  │  player-server│    │        NGINX               │  │
│  │  (Express)    │◄──►│  serves Player UI           │  │
│  │  port 3215    │    │  /var/www/html/ui           │  │
│  └──────┬───────┘    └──────────┬─────────────────┘  │
│         │                       │                    │
│         │              ┌────────▼────────┐           │
│         │              │ Chromium Kiosk   │           │
│         │              │ http://localhost │           │
│         │              │ /ui (fullscreen) │           │
│         │              └─────────────────┘           │
│         │                                            │
│  ┌──────▼────────────────────────────────────┐       │
│  │               PM2 (Process Manager)       │       │
│  │  player-server | player-chromium          │       │
│  └───────────────────────────────────────────┘       │
│         │                                            │
│  ┌──────▼──────┐  ┌──────────┐  ┌──────────────┐    │
│  │  SQLite DB  │  │  CEC     │  │  AnyDesk     │    │
│  │  (_data.db) │  │  (HDMI)  │  │  (Remote)    │    │
│  └─────────────┘  └──────────┘  └──────────────┘    │
└──────────────────────────────────────────────────────┘
          │
          ▼
   NCompass TV Cloud
   (API + Socket.IO)
```

| Component | Technology |
|---|---|
| Backend server | Node.js 20, Express |
| Process manager | PM2 |
| Database | SQLite3 |
| Display engine | Chromium (kiosk mode) |
| Static file server | NGINX |
| TV control | HDMI-CEC (`cec-utils`) |
| Remote access | AnyDesk |
| Realtime comms | Socket.IO |

---

## Project Structure

```
ntv360_player/
├── README.md
│
├── nctv-installer/                           # Installation & setup scripts
│   ├── installer.sh                          # Main installer
│   ├── pm2-starter.sh                        # PM2 startup registration
│   ├── watchdog-starter.sh                   # Hardware watchdog setup
│   ├── panel                                 # LXDE panel config
│   ├── nginx.conf                            # NGINX config (place here before install)
│   └── rpiBG.png                             # Desktop wallpaper
│
└── n-compasstv/                              # Application root
    ├── ecosystem.config.js                   # PM2 process definitions
    └── player-server/                        # Node.js backend
        ├── package.json
        ├── .env                              # Environment variables
        ├── nct-vistar-1.0.1.tgz              # Programmatic ads SDK
        └── src/
            ├── app.js                        # Application entry point
            ├── bin/                           # Shell scripts (20 scripts)
            │   ├── chromium-browser-kiosk-mode.sh
            │   ├── start-chromium-kiosk.sh
            │   ├── pm2-add-chromium-kiosk.sh
            │   ├── pm2-watchdog.sh
            │   ├── crontab-reboot-pi.sh
            │   ├── check-uptime.sh
            │   ├── time-sync.sh
            │   ├── apply-updates.sh
            │   ├── reboot-pi.sh
            │   ├── reboot-player.sh
            │   ├── screenshot.sh
            │   ├── anydesk.sh
            │   ├── reset-anydesk-id.sh
            │   └── ...
            ├── config/                       # Axios and HTTP config
            ├── constants/                    # Boot config, crontab, env profiles
            ├── db/                           # SQLite setup and migrations
            ├── environment/                  # Environment resolver
            ├── middlewares/                   # Express error handling
            ├── models/                       # Data models
            ├── public/                       # Static files, player-data.json
            ├── routes/                       # Express API routes
            └── services/                     # Business logic (socket, cron, etc.)
```

---

## Prerequisites

| Requirement | Details |
|---|---|
| Hardware | Raspberry Pi 5 (4 GB+ RAM recommended) |
| OS | Raspberry Pi OS (Debian Bookworm-based, **64-bit**) |
| Display | HDMI-connected TV or monitor (1080p) |
| Network | Ethernet or Wi-Fi with internet access |
| Storage | 16 GB+ microSD card |

---

## Fresh Installation (Pi 5)

### Step 1 -- Flash Raspberry Pi OS

1. Download the latest **Raspberry Pi OS with Desktop** (Bookworm or later) from [raspberrypi.com](https://www.raspberrypi.com/software/).
2. Flash it to a microSD card using **Raspberry Pi Imager**.
3. On first boot, complete the setup wizard (locale, Wi-Fi, password).
4. Confirm the default user is `pi` with home at `/home/pi`.

### Step 2 -- Disable Screen Saver

Install `xscreensaver` to prevent the Pi from going to sleep:

```bash
sudo apt install xscreensaver -y
```

After install, open **Start > Preferences > Screensaver**, set Mode to **Disable Screen Saver**, then close the app. Takes effect on next reboot.

### Step 3 -- Install AnyDesk (Remote Access)

AnyDesk provides remote desktop access for management and troubleshooting. Install the version compatible with Pi 5:

```bash
sudo apt install libminizip1 -y
wget https://download.anydesk.com/rpi/anydesk_6.1.1-1_armhf.deb
sudo dpkg -i anydesk_6.1.1-1_armhf.deb
```

> Confirm the AnyDesk version with your admin -- newer versions may be available for Pi 5 / `arm64`.

### Step 4 -- Run the Installer Script

Download and extract the installer package:

```bash
curl -O https://ncompasstv-prod-player-apps.s3.amazonaws.com/nctv-installer/<version>/nctv-installer.zip
unzip nctv-installer.zip
```

> Replace `<version>` with the current release tag. Confirm the URL with your admin.

Before running the installer, make sure these files are present inside the `nctv-installer/` folder:

- `nginx.conf` -- NGINX configuration
- `rpiBG.png` -- Desktop wallpaper
- `panel` -- LXDE panel config
- `ecosystem.config.js` -- PM2 process definitions

Run the installer:

```bash
sh nctv-installer/installer.sh
```

**The installer will:**

1. Update and upgrade system packages
2. Install NGINX, Node.js 20, PM2, Chromium, gnome-terminal, scrot, unclutter, cec-utils
3. Create required directories (`/home/pi/n-compasstv`, `/var/www/html/ui`, `/var/www/html/assets`)
4. Download and extract **player-server** (`v2.6.0`) and **player-ui** (`v2.4.1`) from S3
5. Run `npm install` for the player-server (with `node-gyp` fix for Pi 5 compatibility)
6. Copy config files (NGINX, PM2 ecosystem, LXDE panel, wallpaper)
7. Reboot the Pi

### Step 5 -- Start PM2 and Register Startup

After the reboot, open a terminal and run:

```bash
sh nctv-installer/pm2-starter.sh
```

This script:

1. Starts the `player-server` process via PM2
2. Registers PM2 as a systemd startup service so the player launches on boot
3. Saves the PM2 process list

Reboot to verify auto-start:

```bash
sudo reboot
```

The player should launch automatically after reboot and prompt for a license key.

### Step 6 -- Setup Watchdog

The hardware watchdog automatically reboots the Pi if it becomes unresponsive:

```bash
sudo sh nctv-installer/watchdog-starter.sh
```

This script:

1. Enables the hardware watchdog timer in `/boot/config.txt`
2. Installs the `watchdog` package
3. Configures `/etc/watchdog.conf` (device `/dev/watchdog`, timeout 15s, max-load 24)
4. Enables and starts the watchdog systemd service

**Test the watchdog** with the crash simulator (the Pi should hang then reboot):

```bash
sudo bash -c ':(){ :|:& };:'
```

After reboot, if the player starts normally, the watchdog is configured correctly.

### Step 7 -- Verify Installation

Run through this checklist to confirm everything is working:

| Check | Command / Action |
|---|---|
| NGINX | `nginx -v` |
| Node.js | `node -v` (should show v20.x) |
| NPM | `npm -v` |
| PM2 | `pm2 status` (should list `player-server` and `player-chromium`) |
| Chromium | `chromium --version` |
| SCROT | `scrot --version` |
| Unclutter | Mouse pointer hides after ~10 seconds of inactivity |
| CEC Utils | `echo 'scan' \| cec-client -s -d 1` |
| Player server files | `ls /home/pi/n-compasstv/player-server/` (should contain `src/`, `node_modules/`, `package.json`, `.env`) |
| Player UI files | `ls /var/www/html/ui/` |
| Player auto-starts | Player launches on boot |
| Screensaver disabled | Screen stays on indefinitely |
| License key entry | Player prompts for license key (Ctrl+Shift+K) |

---

## How It Works

### Startup Sequence

1. **System boot** -- PM2 starts via systemd, launching `player-server`
2. **Boot config check** -- `player-server` validates `/boot/config.txt` (HDMI, resolution, watchdog); reboots if changes are needed
3. **Express server** -- Starts on port `3215`, registers middleware and API routes
4. **Socket.IO** -- Connects to the NCompass TV cloud socket server for real-time commands
5. **Cron jobs** -- Registers scheduled tasks (play log sender, resource monitor, business hours, cache cleaner, etc.)
6. **Crontab** -- Writes system-level cron entries (midnight reboot, PM2 watchdog, uptime check, time sync)
7. **CEC activation** -- Powers on the TV and sets the Pi as the active HDMI source
8. **Chromium kiosk** -- Launches Chromium in fullscreen kiosk mode pointing to `http://localhost/ui`
9. **License sign-in** -- Reports a "lastConnect" timestamp to the cloud

### Content Flow

1. A license key binds the player to a host in the NCompass TV platform
2. The cloud API delivers playlists, content metadata, and templates
3. `player-server` downloads media assets to `/var/www/html/assets/`
4. NGINX serves the assets and the Player UI
5. Chromium renders the UI, which cycles through content according to playlists and schedules
6. Play logs are stored in SQLite and periodically sent to the cloud

---

## Environment Configuration

### `.env` File (`/home/pi/n-compasstv/player-server/.env`)

```
PORT=3215
DISPLAY=:0
NODE_ENV=development
```

| Variable | Description |
|---|---|
| `PORT` | Express server port (default `3215`) |
| `DISPLAY` | X11 display for GUI apps like Chromium |
| `NODE_ENV` | Environment profile selector |

### Environment Profiles

Set `NODE_ENV` in `.env` to switch between profiles:

| Profile | API Base URL | Socket URL |
|---|---|---|
| `development` | `dev-api.n-compass.online` | `dev-socket.n-compass.online` |
| `staging` | `stg-api.n-compass.online` | `stg-socket.n-compass.online` |
| `production` | `nctvapi2.n-compass.online` | `nctvsocket.n-compass.online` |
| `sandbox` | `sandbox-api.n-compass.online` | `sandbox-socket.n-compass.online` |

---

## PM2 Process Management

Defined in `/home/pi/n-compasstv/ecosystem.config.js`:

| Process | Script | Memory Limit | Purpose |
|---|---|---|---|
| `player-server` | `./src/app.js` | 500 MB | Express API server, cron jobs, socket client |
| `player-chromium` | `chromium-browser-kiosk-mode.sh` | 300 MB | Chromium in fullscreen kiosk |
| `player-puppeteer` | `./app.js` | 300 MB | Puppeteer-based renderer (alternative) |
| `player-electron` | `npm start` | 300 MB | Electron-based renderer (alternative) |

Common PM2 commands:

```bash
pm2 status                          # View all processes
pm2 logs player-server              # Tail server logs
pm2 restart player-server           # Restart the server
pm2 stop player-chromium            # Stop the browser
pm2 start ecosystem.config.js       # Start all defined processes
```

---

## Scheduled Tasks (Crontab)

The player server writes these entries to the system crontab on startup:

| Schedule | Script | Purpose |
|---|---|---|
| `0 0 * * *` | `crontab-reboot-pi.sh` | Nightly reboot at midnight |
| `7-59/7 0 * * *` | `pm2-watchdog.sh` | PM2 health check (midnight hour, every 7 min) |
| `*/7 1-23 * * *` | `pm2-watchdog.sh` | PM2 health check (rest of day, every 7 min) |
| `15 */8 * * *` | `check-uptime.sh` | Force reboot if uptime exceeds ~25 hours |
| `*/5 * * * *` | `time-sync.sh` | NTP time sync via `htpdate` |

---

## Boot Configuration

The player server auto-manages `/boot/config.txt` with these settings. If any are missing or incorrect, the server writes them and triggers a reboot.

| Parameter | Value | Purpose |
|---|---|---|
| `hdmi_drive` | `2` | Force HDMI output (not DVI) |
| `hdmi_group` | `1` | CEA mode (TVs) |
| `hdmi_mode` | `31` | 1080p @ 50Hz, 16:9 |
| `hdmi_force_hotplug` | `1` | Force HDMI even if no display detected |
| `dtoverlay` | `vc4-fkms-v3d` | FKMS display driver |
| `disable_overscan` | `1` | No overscan borders |
| `max_framebuffers` | `2` | Dual framebuffer support |
| `boot_delay` | `0` | No boot delay |
| `avoid_warnings` | `1` | Hide low-voltage/temp warning icons |
| `dtparam=audio` | `off` | Audio output disabled |
| `dtparam=watchdog` | `on` | Hardware watchdog enabled |

---

## API Routes

The player server exposes a local REST API at `http://localhost:3215/api/`:

| Route | Purpose |
|---|---|
| `/api/checkup` | Health check and diagnostics |
| `/api/content` | Content management (download, reset, list) |
| `/api/device` | Device info (MAC, hostname, system stats) |
| `/api/download` | Asset download management |
| `/api/filler` | Filler content logic |
| `/api/license` | License key registration and validation |
| `/api/player` | Player state and control |
| `/api/playlist` | Playlist content and ordering |
| `/api/programmatic` | Programmatic ad integration (Vistar / Fast Edge) |
| `/api/template` | Template zone layout management |
| `/api/update` | Player server and UI update mechanism |

Useful endpoints:

```bash
curl http://localhost:3215/ping               # Health check
curl http://localhost:3215/api/content/reset   # Reset player database
```

---

## Database

The player uses **SQLite3** with the database file stored at:

```
/home/pi/n-compasstv/player-server/src/db/_data.db
```

Key tables:

| Table | Purpose |
|---|---|
| `license` | License key, type, display settings |
| `contents` | Downloaded content metadata |
| `playlist_contents` | Content-to-playlist mapping with scheduling |
| `content_play_log` | Per-content play counts and timestamps |
| `template_zones` | Multi-zone template layout definitions |
| `host_info` | Business name, timezone, venue ID |
| `computer_usage` | CPU/RAM/uptime telemetry |
| `error_logs` | Error tracking |
| `internet_logs` | Speed test results |
| `global_settings` | Programmatic ad API keys |
| `vistar_content` | Vistar programmatic ad assets |
| `programmatic_ads` | Programmatic ad play records |

Database backups are stored in:
- `/home/pi/n-compasstv/db_backup_clean/` -- clean backups
- `/home/pi/n-compasstv/db_backup_dirty/` -- pre-reset backups

---

## Keyboard Shortcuts

These shortcuts work when the player is running in Chromium kiosk mode:

| Shortcut | Action |
|---|---|
| `Ctrl + Shift + P` | Open player settings / status panel |
| `Ctrl + Shift + K` | Enter license key |
| `Ctrl + Shift + R` | Restart / reload the player UI |

---

## Socket Controls

When a player is registered with a license key, the following remote commands are available from the NCompass TV portal (Single License Page):

- **Screenshot** -- capture and upload a screenshot of the current display
- **Reboot Player** -- restart the player-server and Chromium processes
- **Reboot Pi** -- full system reboot
- **Content Update** -- trigger an immediate content sync
- **Restart AnyDesk** -- restart the AnyDesk service
- **Reset AnyDesk ID** -- delete the AnyDesk config to generate a new ID
- **Speedtest** -- run a network speed test
- **CEC Controls** -- power on/off the TV via HDMI-CEC

---

## Cloning a Player Image

To create a reusable SD card image from a fully configured player:

```bash
# 1. Stop the browser to prevent content display during clone
pm2 stop player-chromium

# 2. Reset the player database (removes license binding)
curl http://localhost:3215/api/content/reset

# 3. Stop AnyDesk
sudo systemctl stop anydesk

# 4. Reset the AnyDesk ID (new ID will generate on next boot)
sudo rm /etc/anydesk/service.conf

# 5. Shut down the Pi
sudo shutdown now
```

Remove the SD card and create a clone using your preferred imaging tool (e.g., Raspberry Pi Imager, Win32DiskImager, `dd`).

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Player doesn't start on boot | Run `pm2 startup` and `pm2 save` to re-register the systemd service |
| Chromium doesn't launch | Check `DISPLAY=:0` in `.env`; verify X11 session is running |
| Black screen / no HDMI | Check `/boot/config.txt` for correct HDMI settings; try `hdmi_force_hotplug=1` |
| Player stuck / frozen | The watchdog should auto-reboot; if not, run `sudo reboot` |
| `node-gyp` errors on install | Run `npm install node-gyp@latest` before `npm install` |
| SQLite errors | Check permissions on the `db/` folder: `chmod -R 777 /home/pi/n-compasstv/player-server/src/db/` |
| PM2 processes missing | Run `pm2 start /home/pi/n-compasstv/ecosystem.config.js` then `pm2 save` |
| AnyDesk not connecting | Restart: `sudo systemctl restart anydesk` |
| CEC not controlling TV | Verify with `echo 'scan' \| cec-client -s -d 1`; some TVs have limited CEC support |
| Content not updating | Check internet, then `curl http://localhost:3215/api/content/reset` and reboot |

---

## Authors & Maintainers

- **Earl Vhin Gabuat** -- Original author
- **NCompass TV Team** -- [github.com/NCompass-TV](https://github.com/NCompass-TV)

---

*Last updated: March 2026*
