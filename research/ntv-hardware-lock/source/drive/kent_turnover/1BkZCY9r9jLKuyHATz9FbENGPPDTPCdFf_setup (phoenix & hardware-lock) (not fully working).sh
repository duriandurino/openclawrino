#!/bin/bash
# NTV360 Pi Scripts and Services Setup
# Run as root directly or with sudo.

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo ./setup.sh)"
  exit 1
fi

echo "Creating services and scripts for NTV360 Pi setup..."

# 1. Create systemd services
cat << 'EOF' > /etc/systemd/system/hardware-check.service
[Unit]
Description=Hardware Lockout Screen
After=graphical.target
StartLimitIntervalSec=0

[Service]
User=pi
Group=pi
Environment=DISPLAY=:0
Environment=WAYLAND_DISPLAY=wayland-0
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=XAUTHORITY=/home/pi/.Xauthority
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/python3 /usr/local/bin/hardware_lock.py
Restart=on-failure
RestartSec=5s
Type=idle
TimeoutStartSec=60
RemainAfterExit=yes

[Install]
WantedBy=graphical.target
EOF

cat << 'EOF' > /etc/systemd/system/nctv-watchdog.service
[Unit]
Description=N-Compass Directory Watchdog
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/nctv-watchdog.sh
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

cat << 'EOF' > /etc/systemd/system/vault-mount.service
[Unit]
Description=Unlock and Mount Project Vault
After=hardware-check.service local-fs.target
Requires=hardware-check.service
Before=pm2-pi.service

[Service]
Type=oneshot
User=root
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/python3 /usr/local/bin/unlock_vault.py
RemainAfterExit=yes
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=graphical.target
EOF

cat << 'EOF' > /etc/systemd/system/repairman.service
[Unit]
Description=N-Compass Phoenix Repair Technician
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/repairman.sh
User=root
Restart=no

[Install]
WantedBy=multi-user.target
EOF

# 2. Create python and bash scripts
cat << 'EOF' > /usr/local/bin/hardware_lock.py
import subprocess
import sys
import os
import time

AUTHORIZED_PI_SERIAL = "10000000d58ec40c"
AUTHORIZED_SD_CID = "1b534d4542315154305bde6365015a00"

def get_pi_serial():
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    return line.split(":")[1].strip()
    except:
        return None
    return None

def get_sd_cid():
    try:
        with open("/sys/block/mmcblk0/device/cid", "r") as f:
            return f.read().strip()
    except:
        return None

if __name__ == "__main__":
    current_serial = get_pi_serial()
    current_cid = get_sd_cid()

    if current_serial == AUTHORIZED_PI_SERIAL and current_cid == AUTHORIZED_SD_CID:
        print("Hardware Verified.")
        subprocess.run(["/usr/bin/python3", "/usr/local/bin/unlock_vault.py"], check=False)

        time.sleep(5)
        print("Vault ready. Starting PM2 services...")

        # Define environment correctly
        pi_env = os.environ.copy()
        pi_env["PM2_HOME"] = "/home/pi/.pm2"
        pi_env["HOME"] = "/home/pi"
        pi_env["PATH"] = "/usr/local/bin:/usr/bin:/bin:" + pi_env.get("PATH", "")

        # 1. Clear existing list instead of killing the whole daemon
        subprocess.run("sudo -u pi /usr/local/bin/pm2 delete all", shell=True, env=pi_env, check=False)
        time.sleep(1)

        # 2. Start the processes from the secure vault
        # Use the full path to PM2 to be safe
        pm2_start_cmd = "sudo -u pi /usr/local/bin/pm2 start /home/pi/n-compasstv-secure/ecosystem.config.js"
        subprocess.run(pm2_start_cmd, shell=True, env=pi_env, check=False)

        # 3. Give it a moment to actually spin up the processes
        time.sleep(10)

        # 4. Save the state so it is persistent
        subprocess.run("sudo -u pi /usr/local/bin/pm2 save --force", shell=True, env=pi_env, check=False)
        print("Processes saved. Boot sequence complete.")
        sys.exit(0)


    else:
        print("Hardware Mismatch! Locking UI...")

        #Lock the data
        mnt = "/home/pi/n-compasstv-secure"
        subprocess.run(f"sudo umount -l {mnt}", shell=True, stderr=subprocess.DEVNULL)
        # Close the encrypted container so the key is wiped from RAM
        subprocess.run("sudo cryptsetup close nctv_data", shell=True, stderr=subprocess.DEVNULL)    
        # ----------------------------------------
        subprocess.run("sudo losetup -D", shell=True, stderr=subprocess.DEVNULL)
        # System-level stops
        subprocess.run(["sudo", "systemctl", "stop", "pm2-pi"], check=False)

        # System-level stops
        subprocess.run(["sudo", "systemctl", "stop", "pm2-pi"], check=False)
        subprocess.run(["sudo", "systemctl", "stop", "watchdog"], check=False)

        # Kill PM2 processes
        for _ in range(3):
            subprocess.run(["pm2", "stop", "all"], env=dict(os.environ, HOME="/home/pi"), check=False)
            time.sleep(1)

        # Environment for Pi 5 / Wayland
        env = os.environ.copy()
        env["DISPLAY"] = ":0"
        env["WAYLAND_DISPLAY"] = "wayland-0"
        env["XDG_RUNTIME_DIR"] = "/run/user/1000"

        cmd = [
            "chromium-browser",
            "--kiosk",
            "--incognito",
            "--no-sandbox",
            "file:///home/pi/lockout.html"
        ]

        # Launch Chromium
        process = subprocess.Popen(cmd, env=env)

        # time.sleep(5)
        if process.poll() is not None:
            print("Chromium failed to stay open. Exiting for restart.")
            sys.exit(1)

        print("Lockscreen active. Standing guard.")
        process.wait()
        sys.exit(1)
EOF

cat << 'EOF' > /usr/local/bin/nctv-watchdog.sh
#!/bin/bash
# N-Compass Dead Man's Switch v3.3 (High-Reliability Edition)

# 1. THE GRACE PERIOD COUNTDOWN
TOTAL_WAIT=60
echo "System just booted. Starting $TOTAL_WAIT second grace period..."

while [ $TOTAL_WAIT -gt 0 ]; do
    if [ $((TOTAL_WAIT % 10)) -eq 0 ]; then
        echo "Grace period: $TOTAL_WAIT seconds remaining before watchdog arming..."
    fi
    sleep 1
    TOTAL_WAIT=$((TOTAL_WAIT - 1))
done

echo "!!! WATCHDOG ARMED AND ACTIVE !!!"

CHECK_DIR="/home/pi/n-compasstv"

while true; do
    if [ ! -d "$CHECK_DIR" ]; then
        echo "!! CRITICAL: $CHECK_DIR is missing!"

        # Countdown to Reboot
        REBOOT_TIMER=5
        while [ $REBOOT_TIMER -gt 0 ]; do
            echo ">> PREPARING NUCLEAR RECOVERY IN $REBOOT_TIMER SECONDS..."
            sleep 1
            REBOOT_TIMER=$((REBOOT_TIMER - 1))
        done

        sudo mount /dev/mmcblk0p1 /boot/firmware
        sudo mv /boot/firmware/config.txt /boot/firmware/config.txt.bak
        sync

        sudo reboot
    else
        echo "Watchdog Heartbeat: Folder exists. All systems nominal."
    fi
    sleep 20
done
EOF

cat << 'EOF' > /usr/local/bin/unlock_vault.py
import subprocess
import os
import sys

def get_pi_serial():
    with open("/proc/cpuinfo", "r") as f:
        for line in f:
            if line.startswith("Serial"):
                return line.split(":")[1].strip()
    return ""

serial = get_pi_serial()
vault = "/home/pi/vault.img"
mnt = "/home/pi/n-compasstv-secure"

# 1. Clean up any stuck mounts from a bad reboot
subprocess.run(f"sudo umount -l {mnt}", shell=True, stderr=subprocess.DEVNULL)
subprocess.run("sudo cryptsetup close nctv_data", shell=True, stderr=subprocess.DEVNULL)

# 2. Open and Mount using the Hardware Serial
cmd = f"echo -n '{serial}' | sudo cryptsetup open {vault} nctv_data --key-file -"
if subprocess.run(cmd, shell=True).returncode == 0:
    os.makedirs(mnt, exist_ok=True)
    subprocess.run(f"sudo mount /dev/mapper/nctv_data {mnt}", shell=True)
    subprocess.run(f"sudo chown -R pi:pi {mnt}", shell=True)
    print("SUCCESS: Vault mounted.")
else:
    print("FAILURE: Could not unlock vault.")
    sys.exit(1)
EOF

cat << 'EOF' > /usr/local/bin/repairman.sh
#!/bin/bash
# N-Compass Phoenix v6.0 - Production Release
sleep 15

# 1. BOOT IDENTIFICATION
BOOT_DRIVE=$(lsblk -no PKNAME $(findmnt -n -o SOURCE /))
if [[ "$BOOT_DRIVE" != "sdb" ]]; then
    exit 0
fi

exec > /dev/tty1 2>&1
chvt 1
clear

echo "==============================================="
echo "   N-COMPASS PHOENIX RECOVERY SYSTEM v6.0      "
echo "==============================================="

# 2. EMERGENCY BACKUP PLAYER (If SD is missing or dead)
if [ ! -b "/dev/mmcblk0" ]; then
    echo "!! WARNING: No SD Card detected."
    echo ">> MODE: EMERGENCY STANDALONE PLAYER"
    echo "-----------------------------------------------"

    echo "[!] Activating Backup Player Services..."
    # Start the specific N-Compass processes
    pm2 start /home/pi/n-compasstv/ecosystem.config.js --only player-server
    sleep 2
    DISPLAY=:0 pm2 start /home/pi/n-compasstv/ecosystem.config.js --only player-chromium

    echo "System is now running in Standalone Mode via USB. :3  *-* hihi "
    sleep 5
    chvt 7 || chvt 2
    exit 0
fi

# 3. SURGERY MODE (SD Card is present)
echo ">> MODE: SYSTEM SURGEON (SD Detected)"
echo "-----------------------------------------------"
MAIN_BOOT="/dev/mmcblk0p1"
MAIN_ROOT="/dev/mmcblk0p2"
MOUNT_POINT="/mnt/main_sd"

echo "[1/4] Scrubbing Main SD Filesystem..."
fsck -y $MAIN_BOOT
fsck -y -f $MAIN_ROOT

mkdir -p $MOUNT_POINT
if mount $MAIN_ROOT $MOUNT_POINT; then

    echo "[2/4] Restoring Master Gold Image to SD..."
    rsync -axHAWXS --numeric-ids --info=progress2 \
    --exclude='/mnt/*' --exclude='/proc/*' --exclude='/sys/*' --exclude='/dev/*' \
    --exclude='/tmp/*' --exclude='/run/*' --exclude='/media/*' \
    / $MOUNT_POINT/

    echo "[3/4] Rebuilding Identity (fstab)..."
    echo "proc            /proc           proc    defaults          0       0" > $MOUNT_POINT/etc/fstab
    echo "PARTUUID=$(lsblk -dno PARTUUID /dev/mmcblk0p1)  /boot/firmware  vfat    defaults          0       2" >> $MOUNT_POINT/etc/fstab
    echo "PARTUUID=$(lsblk -dno PARTUUID /dev/mmcblk0p2)  /               ext4    defaults,noatime  0       1" >> $MOUNT_POINT/etc/fstab

    echo "[4/4] Finalizing Firmware..."
    mount $MAIN_BOOT $MOUNT_POINT/boot/firmware
    [[ -f "$MOUNT_POINT/boot/firmware/config.txt.bak" ]] && mv "$MOUNT_POINT/boot/firmware/config.txt.bak" "$MOUNT_POINT/boot/firmware/config.txt"

    echo "Resetting Boot Order to SD-First (0xf461)..."
    sudo vcgencmd bootloader_config | sed 's/0xf.*/BOOT_ORDER=0xf461/' > /tmp/sd_fix_config.txt
    sudo rpi-eeprom-config --apply /tmp/sd_fix_config.txt

    # --- FORCE GUI RECOVERY ---
    echo "[5/5] Ensuring Graphical Auto-login and X11..."
    SD_ROOT="/mnt/main_sd"

    chroot $SD_ROOT systemctl set-default graphical.target
    ln -sf /lib/systemd/system/lightdm.service $SD_ROOT/etc/systemd/system/display-manager.service
    sed -i 's/^#\?wayland_shell=.*/wayland_shell=/' $SD_ROOT/etc/lightdm/lightdm.conf

    chroot $MOUNT_POINT systemctl enable nctv-watchdog.service
    chroot $MOUNT_POINT systemctl disable repairman.service

    echo "-----------------------------------------------"
    echo "REPAIR COMPLETE. REBOOTING TO MAIN SD CARD..."
    umount -R $MOUNT_POINT
    sleep 5
    reboot
else
    echo "!! CRITICAL: SD Mount Failed. Switching to USB Player."
    pm2 start /home/pi/n-compasstv/ecosystem.config.js
    chvt 7
fi
EOF

# 3. Make scripts executable
sudo chmod +x /usr/local/bin/hardware_lock.py
sudo chmod +x /usr/local/bin/nctv-watchdog.sh
sudo chmod +x /usr/local/bin/unlock_vault.py
sudo chmod +x /usr/local/bin/repairman.sh

# 4. Apply EEPROM boot configuration (Optional/if available)
cat << 'EOF' > /tmp/pieeprom.conf
[all]
BOOT_UART=1
BOOT_ORDER=0xf461
NET_INSTALL_AT_POWER_ON=1
PSU_MAX_CURRENT=5000
HALT_ON_ERROR=0
WDT_TIMEOUT=15000
EOF

if command -v rpi-eeprom-config &> /dev/null; then
    echo "Applying EEPROM configuration..."
    sudo rpi-eeprom-config --apply /tmp/pieeprom.conf
else
    echo "rpi-eeprom-config not available. Skipping EEPROM update."
fi

# 5. Reload systemd and enable services
echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling services..."
sudo systemctl enable hardware-check.service
sudo systemctl enable nctv-watchdog.service
sudo systemctl enable vault-mount.service
sudo systemctl enable repairman.service

echo "NTV360 Pi setup is complete."
