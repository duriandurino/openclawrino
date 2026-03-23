sudo tee /usr/local/bin/hardware_lock.py > /dev/null << 'EOF'
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

        # Lock the data
        mnt = "/home/pi/n-compasstv-secure"
        subprocess.run(f"sudo umount -l {mnt}", shell=True, stderr=subprocess.DEVNULL)
        subprocess.run("sudo cryptsetup close nctv_data", shell=True, stderr=subprocess.DEVNULL)  
        subprocess.run("sudo losetup -D", shell=True, stderr=subprocess.DEVNULL)

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

        if process.poll() is not None:
            print("Chromium failed to stay open. Exiting for restart.")
            sys.exit(1)

        print("Lockscreen active. Standing guard.")
        process.wait()
        sys.exit(1)
EOF


sudo tee /etc/systemd/system/hardware-check.service > /dev/null << 'EOF'
[Unit]
Description=Hardware Lockout Screen
After=graphical.target
StartLimitIntervalSec=0

[Service]
# Changed to root so it can manage mounts/encryption without sudo prompts
User=root
Group=root
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



sudo tee /usr/local/bin/unlock_vault.py > /dev/null << 'EOF'
import subprocess
import os
import sys

def get_pi_serial():
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Serial"):
                    return line.split(":")[1].strip()
    except:
        return ""
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



sudo tee /etc/systemd/system/vault-mount.service > /dev/null << 'EOF'
[Unit]
Description=Unlock and Mount Project Vault
After=hardware-check.service local-fs.target
Requires=hardware-check.service
# This ensures PM2 doesn't start until the vault is ready
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