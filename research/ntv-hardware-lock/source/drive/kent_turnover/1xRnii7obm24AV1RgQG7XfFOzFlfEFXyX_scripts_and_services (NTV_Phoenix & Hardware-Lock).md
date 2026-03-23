













pi@raspberrypi:\~ $ sudo rpi-eeprom-config

\[all]

BOOT\_UART=1

BOOT\_ORDER=BOOT\_ORDER=BOOT\_ORDER=0xf461

NET\_INSTALL\_AT\_POWER\_ON=1

PSU\_MAX\_CURRENT=5000

HALT\_ON\_ERROR=0

WDT\_TIMEOUT=15000





&#x09;

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_







***/etc/systemd/system/hardware-check.service***





\[Unit]

Description=Hardware Lockout Screen

After=graphical.target

StartLimitIntervalSec=0



\[Service]

User=pi

Group=pi

Environment=DISPLAY=:0

Environment=WAYLAND\_DISPLAY=wayland-0

Environment=XDG\_RUNTIME\_DIR=/run/user/1000

Environment=XAUTHORITY=/home/pi/.Xauthority

\# Only one sleep is needed

ExecStartPre=/bin/sleep 10

ExecStart=/usr/bin/python3 /usr/local/bin/hardware\_lock.py

Restart=on-failure

RestartSec=5s

\# idle tells systemd to wait until all other jobs are done

Type=idle

TimeoutStartSec=60

RemainAfterExit=yes



\[Install]

WantedBy=graphical.target



\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_





***/etc/systemd/system/nctv-watchdog.service***





\[Unit]

Description=N-Compass Directory Watchdog

After=network.target



\[Service]

Type=simple

ExecStart=/usr/local/bin/nctv-watchdog.sh

Restart=always

User=root



\[Install]

WantedBy=multi-user.target







\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_





***/etc/systemd/system/vault-mount.service***





\[Unit]

Description=Unlock and Mount Project Vault

After=hardware-check.service local-fs.target

Requires=hardware-check.service

Before=pm2-pi.service



\[Service]

Type=oneshot

User=root

\# Give the kernel 5 seconds to stabilize before trying the mount

ExecStartPre=/bin/sleep 5

ExecStart=/usr/bin/python3 /usr/local/bin/unlock\_vault.py

RemainAfterExit=yes

\# This is the secret sauce: if it fails, try again 3 times

Restart=on-failure

RestartSec=5s



\[Install]

WantedBy=graphical.target







\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_







***/etc/system/system/repairman.service***





\[Unit]

Description=N-Compass Phoenix Repair Technician

After=network.target



\[Service]

Type=simple

ExecStart=/usr/local/bin/repairman.sh

User=root

Restart=no



\[Install]

WantedBy=multi-user.target









\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_







***/usr/local/bin/hardware\_lock.py***



import subprocess

import sys

import os

import time



AUTHORIZED\_PI\_SERIAL = "ffb6d42807368154"

AUTHORIZED\_SD\_CID = "1b534d45423151543089c65df4015a00"



def get\_pi\_serial():

&#x20;   try:

&#x20;       with open("/proc/cpuinfo", "r") as f:

&#x20;           for line in f:

&#x20;               if line.startswith("Serial"):

&#x20;                   return line.split(":")\[1].strip()

&#x20;   except:

&#x20;       return None

&#x20;   return None



def get\_sd\_cid():

&#x20;   try:

&#x20;       with open("/sys/block/mmcblk0/device/cid", "r") as f:

&#x20;           return f.read().strip()

&#x20;   except:

&#x20;       return None



if \_\_name\_\_ == "\_\_main\_\_":

&#x20;   current\_serial = get\_pi\_serial()

&#x20;   current\_cid = get\_sd\_cid()



&#x20;   if current\_serial == AUTHORIZED\_PI\_SERIAL and current\_cid == AUTHORIZED\_SD\_CID:

&#x20;       print("Hardware Verified.")

&#x20;       subprocess.run(\["/usr/bin/python3", "/usr/local/bin/unlock\_vault.py"], check=False)



&#x20;       time.sleep(5)

&#x20;       print("Vault ready. Starting PM2 services...")



&#x20;       # Define environment correctly

&#x20;       pi\_env = os.environ.copy()

&#x20;       pi\_env\["PM2\_HOME"] = "/home/pi/.pm2"

&#x20;       pi\_env\["HOME"] = "/home/pi"

&#x20;       pi\_env\["PATH"] = "/usr/local/bin:/usr/bin:/bin:" + pi\_env.get("PATH", "")



&#x20;       # 1. Clear existing list instead of killing the whole daemon

&#x20;       subprocess.run("sudo -u pi /usr/local/bin/pm2 delete all", shell=True, env=pi\_env, check=False)

&#x20;       time.sleep(1)



&#x20;       # 2. Start the processes from the secure vault

&#x20;       # Use the full path to PM2 to be safe

&#x20;       pm2\_start\_cmd = "sudo -u pi /usr/local/bin/pm2 start /home/pi/n-compasstv-secure/ecosystem.config.js"

&#x20;       subprocess.run(pm2\_start\_cmd, shell=True, env=pi\_env, check=False)



&#x20;       # 3. Give it a moment to actually spin up the processes

&#x20;       time.sleep(10)



&#x20;       # 4. Save the state so it is persistent

&#x20;       subprocess.run("sudo -u pi /usr/local/bin/pm2 save --force", shell=True, env=pi\_env, check=False)

&#x20;       print("Processes saved. Boot sequence complete.")

&#x20;       sys.exit(0)





&#x20;   else:

&#x20;       print("Hardware Mismatch! Locking UI...")



&#x20;       # System-level stops

&#x20;       subprocess.run(\["sudo", "systemctl", "stop", "pm2-pi"], check=False)

&#x20;       subprocess.run(\["sudo", "systemctl", "stop", "watchdog"], check=False)



&#x20;       # Kill PM2 processes

&#x20;       for \_ in range(3):

&#x20;           subprocess.run(\["pm2", "stop", "all"], env=dict(os.environ, HOME="/home/pi"), check=False)

&#x20;           time.sleep(1)



&#x20;       # Environment for Pi 5 / Wayland

&#x20;       env = os.environ.copy()

&#x20;       env\["DISPLAY"] = ":0"

&#x20;       env\["WAYLAND\_DISPLAY"] = "wayland-0"

&#x20;       env\["XDG\_RUNTIME\_DIR"] = "/run/user/1000"



&#x20;       cmd = \[

&#x20;           "chromium-browser",

&#x20;           "--kiosk",

&#x20;           "--incognito",

&#x20;           "--no-sandbox",

&#x20;           "file:///home/pi/lockout.html"

&#x20;       ]



&#x20;       # Launch Chromium

&#x20;       process = subprocess.Popen(cmd, env=env)



&#x20;       # time.sleep(5)

&#x20;       if process.poll() is not None:

&#x20;           print("Chromium failed to stay open. Exiting for restart.")

&#x20;           sys.exit(1)



&#x20;       print("Lockscreen active. Standing guard.")

&#x20;       process.wait()

&#x20;       sys.exit(1)









\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_









***/usr/local/bin/nctv-watchdog.sh***



\#!/bin/bash

\# N-Compass Dead Man's Switch v3.3 (High-Reliability Edition)



\# 1. THE GRACE PERIOD COUNTDOWN

TOTAL\_WAIT=60

echo "System just booted. Starting $TOTAL\_WAIT second grace period..."



while \[ $TOTAL\_WAIT -gt 0 ]; do

&#x20;   if \[ $((TOTAL\_WAIT % 10)) -eq 0 ]; then

&#x20;       echo "Grace period: $TOTAL\_WAIT seconds remaining before watchdog arming..."

&#x20;   fi

&#x20;   sleep 1

&#x20;   TOTAL\_WAIT=$((TOTAL\_WAIT - 1))

done



echo "!!! WATCHDOG ARMED AND ACTIVE !!!"



CHECK\_DIR="/home/pi/n-compasstv"



while true; do

&#x20;   if \[ ! -d "$CHECK\_DIR" ]; then

&#x20;       echo "!! CRITICAL: $CHECK\_DIR is missing!"



&#x20;       # Countdown to Reboot

&#x20;       REBOOT\_TIMER=5

&#x20;       while \[ $REBOOT\_TIMER -gt 0 ]; do

&#x20;           echo ">> PREPARING NUCLEAR RECOVERY IN $REBOOT\_TIMER SECONDS..."

&#x20;           sleep 1

&#x20;           REBOOT\_TIMER=$((REBOOT\_TIMER - 1))

&#x20;       done



&#x20;       sudo mount /dev/mmcblk0p1 /boot/firmware

&#x20;       sudo mv /boot/firmware/config.txt /boot/firmware/config.txt.bak

&#x20;       sync



&#x20;       sudo reboot

&#x20;   else

&#x20;       echo "Watchdog Heartbeat: Folder exists. All systems nominal."

&#x20;   fi

&#x20;   sleep 20

done







\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_











***/usr/local/bin/unlock\_vault.py***



import subprocess

import os

import sys



def get\_pi\_serial():

&#x20;   with open("/proc/cpuinfo", "r") as f:

&#x20;       for line in f:

&#x20;           if line.startswith("Serial"):

&#x20;               return line.split(":")\[1].strip()

&#x20;   return ""



serial = get\_pi\_serial()

vault = "/home/pi/vault.img"

mnt = "/home/pi/n-compasstv-secure"



\# 1. Clean up any stuck mounts from a bad reboot

subprocess.run(f"sudo umount -l {mnt}", shell=True, stderr=subprocess.DEVNULL)

subprocess.run("sudo cryptsetup close nctv\_data", shell=True, stderr=subprocess.DEVNULL)



\# 2. Open and Mount using the Hardware Serial

cmd = f"echo -n '{serial}' | sudo cryptsetup open {vault} nctv\_data --key-file -"

if subprocess.run(cmd, shell=True).returncode == 0:

&#x20;   os.makedirs(mnt, exist\_ok=True)

&#x20;   subprocess.run(f"sudo mount /dev/mapper/nctv\_data {mnt}", shell=True)

&#x20;   subprocess.run(f"sudo chown -R pi:pi {mnt}", shell=True)

&#x20;   print("SUCCESS: Vault mounted.")

else:

&#x20;   print("FAILURE: Could not unlock vault.")

&#x20;   sys.exit(1)













\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_







***/usr/local/bin/repairman.sh***



\#!/bin/bash

\# N-Compass Phoenix v6.0 - Production Release

sleep 15



\# 1. BOOT IDENTIFICATION

BOOT\_DRIVE=$(lsblk -no PKNAME $(findmnt -n -o SOURCE /))

if \[\[ "$BOOT\_DRIVE" != "sdb" ]]; then

&#x20;   exit 0

fi



exec > /dev/tty1 2>\&1

chvt 1

clear



echo "==============================================="

echo "   N-COMPASS PHOENIX RECOVERY SYSTEM v6.0      "

echo "==============================================="



\# 2. EMERGENCY BACKUP PLAYER (If SD is missing or dead)

if \[ ! -b "/dev/mmcblk0" ]; then

&#x20;   echo "!! WARNING: No SD Card detected."

&#x20;   echo ">> MODE: EMERGENCY STANDALONE PLAYER"

&#x20;   echo "-----------------------------------------------"



&#x20;   echo "\[!] Activating Backup Player Services..."

&#x20;   # Start the specific N-Compass processes

&#x20;   pm2 start /home/pi/n-compasstv/ecosystem.config.js --only player-server

&#x20;   sleep 2

&#x20;   DISPLAY=:0 pm2 start /home/pi/n-compasstv/ecosystem.config.js --only player-chromium



&#x20;   echo "System is now running in Standalone Mode via USB. :3  \*-\* hihi "

&#x20;   sleep 5

&#x20;   chvt 7 || chvt 2

&#x20;   exit 0

fi



\# 3. SURGERY MODE (SD Card is present)

echo ">> MODE: SYSTEM SURGEON (SD Detected)"

echo "-----------------------------------------------"

MAIN\_BOOT="/dev/mmcblk0p1"

MAIN\_ROOT="/dev/mmcblk0p2"

MOUNT\_POINT="/mnt/main\_sd"



echo "\[1/4] Scrubbing Main SD Filesystem..."

fsck -y $MAIN\_BOOT

fsck -y -f $MAIN\_ROOT



mkdir -p $MOUNT\_POINT

if mount $MAIN\_ROOT $MOUNT\_POINT; then





&#x20;   echo "\[2/4] Restoring Master Gold Image to SD..."

&#x20;   # This rsync ensures the SD becomes an EXACT mirror of the working USB

&#x20;   rsync -axHAWXS --numeric-ids --info=progress2 \\

&#x20;   --exclude='/mnt/\*' --exclude='/proc/\*' --exclude='/sys/\*' --exclude='/dev/\*' \\

&#x20;   --exclude='/tmp/\*' --exclude='/run/\*' --exclude='/media/\*' \\

&#x20;   / $MOUNT\_POINT/



&#x20;   echo "\[3/4] Rebuilding Identity (fstab)..."

&#x20;   echo "proc            /proc           proc    defaults          0       0" > $MOUNT\_POINT/etc/fstab

&#x20;   echo "PARTUUID=$(lsblk -dno PARTUUID /dev/mmcblk0p1)  /boot/firmware  vfat    defaults          0       2" >> $MOUNT\_POINT/etc/fstab

&#x20;   echo "PARTUUID=$(lsblk -dno PARTUUID /dev/mmcblk0p2)  /               ext4    defaults,noatime  0       1" >> $MOUNT\_POINT/etc/fstab



&#x20;   echo "\[4/4] Finalizing Firmware..."

&#x20;   mount $MAIN\_BOOT $MOUNT\_POINT/boot/firmware

&#x20;   \[\[ -f "$MOUNT\_POINT/boot/firmware/config.txt.bak" ]] \&\& mv "$MOUNT\_POINT/boot/firmware/config.txt.bak" "$MOUNT\_POINT/boot/firmware/config.txt"



&#x20;   # Inside repairman.sh Step 4

&#x20;   echo "Resetting Boot Order to SD-First (0xf461)..."

&#x20;   sudo vcgencmd bootloader\_config | sed 's/0xf.\*/BOOT\_ORDER=0xf461/' > /tmp/sd\_fix\_config.txt

&#x20;   sudo rpi-eeprom-config --apply /tmp/sd\_fix\_config.txt



&#x20;   # --- FORCE GUI RECOVERY ---

&#x20;   echo "\[5/5] Ensuring Graphical Auto-login and X11..."

&#x20;   # Point to the SD's root (which the script usually mounts at /mnt/main\_sd)

&#x20;   SD\_ROOT="/mnt/main\_sd"



&#x20;   # Force Graphical Target

&#x20;   chroot $SD\_ROOT systemctl set-default graphical.target



&#x20;   # Overwrite display-manager link to force LightDM

&#x20;   ln -sf /lib/systemd/system/lightdm.service $SD\_ROOT/etc/systemd/system/display-manager.service



&#x20;   # Force X11 over Wayland for Kiosk stability

&#x20;   sed -i 's/^#\\?wayland\_shell=.\*/wayland\_shell=/' $SD\_ROOT/etc/lightdm/lightdm.conf



&#x20;   chroot $MOUNT\_POINT systemctl enable nctv-watchdog.service

&#x20;   chroot $MOUNT\_POINT systemctl disable repairman.service



&#x20;   echo "-----------------------------------------------"

&#x20;   echo "REPAIR COMPLETE. REBOOTING TO MAIN SD CARD..."

&#x20;   umount -R $MOUNT\_POINT

&#x20;   sleep 5

&#x20;   reboot

else

&#x20;   echo "!! CRITICAL: SD Mount Failed. Switching to USB Player."

&#x20;   pm2 start /home/pi/n-compasstv/ecosystem.config.js

&#x20;   chvt 7

fi

