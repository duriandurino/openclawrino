# NTV Phoenix & Hardware Lock — Operator Cheatsheet

**Quick reference for technicians and operators**  
**Last Updated:** March 2026

---

## Quick Status Check

```bash
# Check if all services are running
sudo systemctl status hardware-check.service vault-mount.service nctv-watchdog.service

# Check PM2 processes
pm2 status

# Check vault mount
ls -la /home/pi/n-compasstv-secure/
df -h | grep n-compasstv-secure

# Check hardware fingerprint
grep Serial /proc/cpuinfo
cat /sys/block/mmcblk0/device/cid
```

---

## Service Commands

### Check Service Status

```bash
# Individual service status
sudo systemctl status hardware-check.service
sudo systemctl status vault-mount.service
sudo systemctl status nctv-watchdog.service

# View logs
sudo journalctl -u hardware-check.service -f
sudo journalctl -u nctv-watchdog.service -f
sudo journalctl -u vault-mount.service -f
```

### Start/Stop/Restart Services

```bash
# Restart hardware check (triggers vault mount)
sudo systemctl restart hardware-check.service

# Restart watchdog
sudo systemctl restart nctv-watchdog.service

# Stop services
sudo systemctl stop hardware-check.service
sudo systemctl stop nctv-watchdog.service
```

### Enable/Disable Services

```bash
# Enable services (start on boot)
sudo systemctl enable hardware-check.service
sudo systemctl enable vault-mount.service
sudo systemctl enable nctv-watchdog.service

# Disable services (don't start on boot)
sudo systemctl disable repairman.service  # Usually disabled on SD
```

---

## Vault Operations

### Manual Vault Unlock (Emergency)

```bash
# Get Pi serial
SERIAL=$(grep Serial /proc/cpuinfo | cut -d: -f2 | tr -d ' ')
echo "Serial: $SERIAL"

# Open vault
echo -n "$SERIAL" | sudo cryptsetup open /home/pi/vault.img nctv_data --key-file -

# Mount vault
sudo mkdir -p /home/pi/n-compasstv-secure
sudo mount /dev/mapper/nctv_data /home/pi/n-compasstv-secure
sudo chown -R pi:pi /home/pi/n-compasstv-secure

# Verify
ls /home/pi/n-compasstv-secure/
```

### Close Vault

```bash
# Unmount
sudo umount /home/pi/n-compasstv-secure

# Close crypt device
sudo cryptsetup close nctv_data

# Verify closed
ls /dev/mapper/nctv_data  # Should not exist
```

### Vault Status

```bash
# Check if vault is mounted
mount | grep n-compasstv-secure

# Check cryptsetup status
sudo cryptsetup status nctv_data

# List mapped devices
ls /dev/mapper/
```

---

## PM2 Commands

### Basic PM2 Operations

```bash
# View process status
pm2 status
pm2 list

# View logs
pm2 logs
pm2 logs player-server
pm2 logs player-chromium

# Restart processes
pm2 restart player-server
pm2 restart player-chromium
pm2 restart all

# Stop processes
pm2 stop player-server
pm2 stop all

# Start ecosystem
pm2 start /home/pi/n-compasstv/ecosystem.config.js
```

### PM2 Startup Registration

```bash
# Register PM2 startup (run once during install)
pm2 startup
sudo env PATH=$PATH:/usr/local/bin /usr/local/lib/node_modules/pm2/bin/pm2 startup systemd -u pi --hp /home/pi

# Save PM2 config (persists across reboots)
pm2 save
```

---

## Recovery Procedures

### Scenario 1: Player Won't Start

```bash
# Check if vault is mounted
mount | grep n-compasstv

# If not mounted, check hardware lock logs
sudo journalctl -u hardware-check.service --no-pager

# Check for serial mismatch
grep Serial /proc/cpuinfo
cat /sys/block/mmcblk0/device/cid

# Verify against authorized values in /usr/local/bin/hardware_lock.py
```

### Scenario 2: Watchdog Triggered Recovery

```bash
# Check if config.txt was renamed
ls -la /boot/firmware/config.txt*

# If config.txt.bak exists, restore it
sudo mv /boot/firmware/config.txt.bak /boot/firmware/config.txt

# Reboot normally
sudo reboot
```

### Scenario 3: SD Card Failure

```bash
# Check if SD is detected
ls -la /dev/mmcblk0

# If not present, use Phoenix USB:
# 1. Insert USB drive with Phoenix image
# 2. Power cycle Pi
# 3. Wait for emergency mode or surgery mode
```

### Scenario 4: Phoenix Surgery Mode (SD Present)

```bash
# Boot from USB, let repairman.sh run automatically
# Check TTY1 for progress:
# - "MODE: SYSTEM SURGEON (SD Detected)"
# - fsck progress
# - rsync progress
# - "REPAIR COMPLETE. REBOOTING..."
```

---

## Hardware Lock Debugging

### Check Hardware Fingerprints

```bash
# Get current Pi serial
grep Serial /proc/cpuinfo
# Output: Serial: xxxxxxxx (e.g., ffb6d42807368154)

# Get SD CID
cat /sys/block/mmcblk0/device/cid
# Output: 32-character hex string

# View authorized values
grep "AUTHORIZED_" /usr/local/bin/hardware_lock.py
```

### Test Lock Mechanism

```bash
# Simulate hardware mismatch (CAUTION: will lock!)
# Edit hardware_lock.py with wrong serial, then:
sudo systemctl restart hardware-check.service

# Unlock after test
# Restore correct serial in hardware_lock.py
sudo systemctl restart hardware-check.service
```

### Force Unlock (Emergency Only)

```bash
# Skip hardware check and manually start vault
sudo python3 /usr/local/bin/unlock_vault.py

# Start PM2 manually
export PM2_HOME=/home/pi/.pm2
pm2 start /home/pi/n-compasstv-secure/ecosystem.config.js
```

---

## Boot Configuration

### Check EEPROM Settings

```bashn# Read current EEPROM config
sudo rpi-eeprom-config

# Look for:
# BOOT_ORDER=0xf461
# WDT_TIMEOUT=15000
# HALT_ON_ERROR=0
```

### Update EEPROM

```bash
# Create config filecat > /tmp/pieeprom.conf << 'EOF'
[all]
BOOT_UART=1
BOOT_ORDER=0xf461
NET_INSTALL_AT_POWER_ON=1
PSU_MAX_CURRENT=5000
HALT_ON_ERROR=0
WDT_TIMEOUT=15000
EOF

# Apply
sudo rpi-eeprom-config --apply /tmp/pieeprom.conf
```

### Boot Partition

```bash
# Mount boot partition
sudo mount /dev/mmcblk0p1 /boot/firmware

# View boot config
cat /boot/firmware/config.txt

# Common settings:
# hdmi_force_hotplug=1
# hdmi_drive=2
# dtparam=watchdog=on
```

---

## Log Locations

### System Logs

```bash
# systemd journal
sudo journalctl -b  # Current boot
sudo journalctl -b -1  # Previous boot

# Specific services
sudo journalctl -u hardware-check.service --no-pager
sudo journalctl -u vault-mount.service --no-pager
sudo journalctl -u nctv-watchdog.service --no-pager
```

### Application Logs

```bash
# PM2 logs
~/.pm2/logs/

# Player server logs (if running)
ls /home/pi/n-compasstv-secure/player-server/src/logs/

# Database location
ls /home/pi/n-compasstv-secure/player-server/src/db/_data.db
```

---

## Network Diagnostics

### Check Connectivity

```bash
# Basic connectivity
ping -c 4 google.com
ping -c 4 nctvapi2.n-compass.online

# Check API
 curl -I https://nctvapi2.n-compass.online

# Check socket connection
 curl -I https://nctvsocket.n-compass.online
```

### Player API

```bash
# Health check
curl http://localhost:3215/ping

# Reset content
curl http://localhost:3215/api/content/reset

# Device info
curl http://localhost:3215/api/device
```

---

## Common Issues & Fixes

| Issue | Symptoms | Fix |
|-------|----------|-----|
| Hardware mismatch | Lockout screen, Chromium kiosk | Check serial/CID match in hardware_lock.py |
| Vault not mounting | PM2 not starting, missing directory | Check unlock_vault.py logs; verify vault.img exists |
| Watchdog reboot loop | Constant reboots | Check /home/pi/n-compasstv exists; restore from backup |
| SD not detected | Emergency USB mode | Replace SD card; run surgery mode |
| PM2 not starting | Black screen | pm2 status; pm2 resurrect; pm2 save |
| Chromium not launching | No display | Check DISPLAY=:0; check .env file |
| Can't enter license | UI not responding | Ctrl+Shift+K; check socket connection |

---

## Keyboard Shortcuts

### Player Shortcuts (Chromium Kiosk)

| Shortcut | Action |
|----------|--------|
| `Ctrl + Shift + P` | Open player settings/status panel |
| `Ctrl + Shift + K` | Enter license key |
| `Ctrl + Shift + R` | Restart/reload player UI |

### System Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Alt + T` | Open terminal |
| `Ctrl + Alt + F1` | Switch to TTY1 (console) |
| `Ctrl + Alt + F7` | Switch to graphical display |
| `Ctrl + C` | Cancel running command |
| `Ctrl + Z` | Suspend process (then `fg` to resume) |

---

## File Locations Quick Reference

| Path | Description |
|------|-------------|
| `/usr/local/bin/hardware_lock.py` | Hardware verification script |
| `/usr/local/bin/unlock_vault.py` | Vault unlock script |
| `/usr/local/bin/nctv-watchdog.sh` | Watchdog script |
| `/usr/local/bin/repairman.sh` | Phoenix recovery script |
| `/etc/systemd/system/hardware-check.service` | Hardware check service |
| `/etc/systemd/system/vault-mount.service` | Vault mount service |
| `/etc/systemd/system/nctv-watchdog.service` | Watchdog service |
| `/etc/systemd/system/repairman.service` | Phoenix service |
| `/home/pi/vault.img` | Encrypted vault container |
| `/home/pi/n-compasstv-secure/` | Decrypted vault mount |
| `/home/pi/lockout.html` | Lockout screen HTML |
| `/boot/firmware/config.txt` | Boot configuration |
| `/boot/firmware/config.txt.bak` | Backup (created by watchdog) |
| `/proc/cpuinfo` | Pi serial number |
| `/sys/block/mmcblk0/device/cid` | SD card CID |

---

## Emergency Contacts / Escalation

| Issue | Contact | Notes |
|-------|---------|-------|
| Hardware failure | Field technician | Replace Pi/SD |
| Software bug | Dev team | Check logs, file issue |
| Security incident | Security team | Lockout, audit |
| Cloud API issues | Platform team | Check dashboard status |

---

## Script Quick Deploy

### Deploy Hardware Lock on New Pi

```bash
#!/bin/bash
# Run as root

# 1. Update authorized values
SERIAL="YOUR_PI_SERIAL"
CID="YOUR_SD_CID"
sed -i "s/AUTHORIZED_PI_SERIAL.*/AUTHORIZED_PI_SERIAL = \"$SERIAL\"/" /usr/local/bin/hardware_lock.py
sed -i "s/AUTHORIZED_SD_CID.*/AUTHORIZED_SD_CID = \"$CID\"/" /usr/local/bin/hardware_lock.py

# 2. Create vault
dd if=/dev/zero of=/home/pi/vault.img bs=1M count=4096
SERIAL=$(grep Serial /proc/cpuinfo | cut -d: -f2 | tr -d ' ')
echo -n "$SERIAL" | cryptsetup luksFormat /home/pi/vault.img --key-file -
echo -n "$SERIAL" | cryptsetup open /home/pi/vault.img nctv_data --key-file -
mkfs.ext4 /dev/mapper/nctv_data

# 3. Enable services
systemctl enable hardware-check.service
systemctl enable vault-mount.service
systemctl enable nctv-watchdog.service

# 4. Copy application to vault
mount /dev/mapper/nctv_data /home/pi/n-compasstv-secure
cp -r /path/to/player/* /home/pi/n-compasstv-secure/
umount /home/pi/n-compasstv-secure
cryptsetup close nctv_data
```

---

**End of Operator Cheatsheet**
