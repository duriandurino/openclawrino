# Phase 3: Hardware Attack Vectors

> **Agent:** specter-enum / specter-exploit  
> **Phase:** Physical / Hardware  
> **Prerequisite:** Physical access to the Raspberry Pi 5B

---

## ⚠️ Pi 5B Hardware Changes from Pi 4

The Pi 5 introduces the **RP1 I/O controller chip** (southbridge), which changes how GPIO and peripherals are handled. Key differences:

- GPIO is now managed through RP1, not directly from BCM2712
- PCIe lanes go through RP1 to the BCM2712
- New debug UART header (5-pin) specifically for console access
- Power management IC (PMIC) is separate — new power analysis surface
- RTC battery connector for real-time clock persistence

---

## 3.1 UART Console Access ⭐ (Primary Hardware Vector)

The Pi 5B has a **dedicated UART debug header** — this is your #1 hardware entry point.

### Pin Layout (5-pin UART Header on Pi 5)

```
Pi 5 UART Header (near power button):
┌─────────────────┐
│ ● ● ● ● ●      │
│ 1 2 3 4 5       │
└─────────────────┘

Pin 1: Ground (GND)
Pin 2: TX (Pi transmits)
Pin 3: RX (Pi receives)  
Pin 4: 3.3V (power)
Pin 5: (NC / not connected)

Note: Labels may vary by board revision. Check silkscreen.
```

### Required Hardware
- **USB-to-UART adapter** (FTDI FT232RL, CP2102, or CH340)
- Jumper wires (female-to-female)
- **3.3V adapter** — do NOT use 5V, you'll fry the UART chip

### Connection Steps

```bash
# 1. Connect GND → GND
# 2. Connect TX (Pi) → RX (adapter)
# 3. Connect RX (Pi) → TX (adapter)
# 4. Do NOT connect 3.3V pin (Pi is already powered)

# On your Kali machine:
screen /dev/ttyUSB0 115200

# Or with minicom:
sudo minicom -D /dev/ttyUSB0 -b 115200

# Or with picocom:
picocom -b 115200 /dev/ttyUSB0
```

### What You Get
- **Full serial console** — login prompt, kernel messages, boot log
- If default credentials work: **immediate shell**
- If not: see [credential attacks](#311-uart-console-credential-attacks)

### UART Security Posture (Default Pi OS)
| Setting | Default | Risk |
|---------|---------|------|
| Console enabled | **Yes** | High — physical access = shell |
| Console requires login | **Yes** | Medium — needs credentials |
| Console baud rate | 115200 | Standard |
| Console on GPIO14/15 | Yes (Pi <5) | Pi 5 uses dedicated header |
| Serial console in /etc/securetty | Yes | Root login possible |

---

## 3.2 GPIO Manipulation

### GPIO Pinout (40-pin Header)

The Pi 5 retains the standard 40-pin header:

```
        3.3V [1]  [2] 5V
   GPIO2/SDA [3]  [4] 5V
   GPIO3/SCL [5]  [6] GND
   GPIO4     [7]  [8] GPIO14/TXD
          GND [9]  [10] GPIO15/RXD
  GPIO17     [11] [12] GPIO18
  GPIO27     [13] [14] GND
  GPIO22     [15] [16] GPIO23
          3.3V[17] [18] GPIO24
  GPIO10/MISO[19] [20] GND
   GPIO9/MOSI[21] [22] GPIO25
   GPIO11/SCK[23] [24] GPIO8/CE0
          GND [25] [26] GPIO7/CE1
  GPIO0/ID_SD[27] [28] GPIO1/ID_SC
  GPIO5      [29] [30] GND
  GPIO6      [31] [32] GPIO12
  GPIO13     [33] [34] GND
  GPIO19     [35] [36] GPIO16
  GPIO26     [37] [38] GPIO20
          GND [39] [40] GPIO21
```

### GPIO Attack Vectors

| Vector | Description | Complexity | Impact |
|--------|-------------|------------|--------|
| **UART tap** | Connect to GPIO14/15 for console (Pi <5) | Low | High |
| **I2C sniffing** | GPIO2/3 — eavesdrop on I2C bus (sensors, HATs) | Medium | Medium |
| **SPI interception** | GPIO7-11 — intercept SPI traffic (displays, ADCs) | Medium | Medium |
| **GPIO brute-force** | Toggle pins to trigger hardware events | Low | Low |
| **Power glitching** | VCC pin manipulation for fault injection | High | High |
| **J2 header** | Not standard on Pi 5 — check for debug headers | High | Critical |

### Tools for GPIO
```bash
# Python GPIO access
pip3 install RPi.GPIO
# or
pip3 install gpiozero

# Command-line GPIO tools
sudo apt install gpio-utils
gpio readall    # Pin state dump
gpio mode 4 out # Set pin mode
gpio write 4 1  # Set pin high
```

---

## 3.3 I2C Bus Enumeration

The I2C bus (GPIO2/3) is used for HAT identification and sensor communication:

```bash
# Install tools
sudo apt install i2c-tools

# Scan I2C bus
sudo i2cdetect -y 1    # Bus 1 (user I2C)
sudo i2cdetect -y 0    # Bus 0 (HAT ID EEPROM)

# Read device registers
sudo i2cget -y 1 0xXX 0xYY

# Dump all registers
sudo i2cdump -y 1 0xXX
```

### Interesting I2C Devices
| Address | Device | Notes |
|---------|--------|-------|
| `0x50` | HAT EEPROM | Stores HAT identity, GPIO config |
| `0x68` | RTC (if present) | Real-time clock — time manipulation |
| Others | Sensors/HATs | Depends on attached hardware |

---

## 3.4 USB Attack Vectors

### Attack FROM the Pi (if we have a shell)
- **USB HID injection** — emulating keyboard/mouse
- **USB storage** — mount, exfiltrate, or drop payloads
- **USB Ethernet** — create a network interface for exfil

### Attack TO the Pi (physical)
- **Rubber Ducky** — USB HID payload into Pi's USB ports
- **BadUSB** — firmware-level USB attack
- **USBJuice** — USB power-based attack
- **Charging cable attacks** — data lines in charging cables

### USB Enumeration on Pi
```bash
# List USB devices
lsusb
lsusb -v

# USB device tree
lsusb -t

# Check for USB gadgets (if Pi is configured as gadget)
ls /sys/kernel/config/usb_gadget/
```

### USB Gadget Mode (Offensive)
The Pi 5 can act as a USB device (gadget mode), useful for:
- **RNDIS** — fake Ethernet adapter to host machine
- **HID** — keyboard/mouse injection to connected host
- **Mass Storage** — appear as a USB drive
- **Serial** — USB serial gadget for comms

```bash
# Enable USB gadget mode (config.txt)
# dtoverlay=dwc2  # (Pi 4 syntax, Pi 5 may differ)
```

---

## 3.5 HDMI / Display Output Analysis

### If the Pi Has a Connected Display
- Intercept login prompts
- Watch for screen output during boot
- Capture credentials if typed on physical keyboard

### HDMI Capture
- **HDMI capture card** (USB, ~$15-30) — record all video output
- Watch for password prompts, error messages, config output

### HDMI-CEC Attack
HDMI-CEC allows control of the TV/monitor from the Pi:
```bash
# Check if CEC is active
cec-client -l

# Send CEC commands
echo "on 0" | cec-client RPI -s -d 1
```

---

## 3.6 Power Analysis (Side-Channel)

The Pi 5 uses a dedicated PMIC (Power Management IC) — this is new vs previous Pis.

### Power Monitoring Hardware
- **ChipWhisperer** — professional power analysis / glitching platform
- **PicoScope** — oscilloscope for power trace capture
- **USB power meter** — cheap ($5-10) but basic

### What Power Analysis Can Reveal
- **Crypto key extraction** — differential power analysis (DPA) on operations
- **Boot sequence timing** — identify when crypto operations happen
- **Activity patterns** — what the Pi is doing without observing output
- **Fault injection** — glitch power during critical operations

### Basic Power Monitoring
```bash
# On-device: check current draw
cat /sys/class/power_supply/usb/voltage_now
cat /sys/class/power_supply/usb/current_now

# Monitor via INA219 sensor (I2C power monitor)
# Connected to GPIO pins
```

---

## 3.7 SD Card Physical Attacks

⚠️ **Storage Lock Active** — but SD card physical access still has value.

### What You CAN Do With Physical SD Access
| Action | Feasible? | Notes |
|--------|-----------|-------|
| Clone SD card | ❌ No | Device-locked — won't boot elsewhere |
| Read filesystem offline | ❌ No | Encrypted/device-bound |
| Modify files offline | ❌ No | Same reason |
| **Read SD card CID** | ✅ Yes | Card identification data |
| **Test SD card speed** | ✅ Yes | Performance analysis |
| **Check card model** | ✅ Yes | Brand, capacity, wear level |
| **Insert malicious SD** | ✅ Yes | If Pi boots from USB/NVMe, this is an auxiliary slot attack |

### SD Card Identification
```bash
# On-device SD card info
cat /sys/block/mmcblk0/device/name    # Card name
cat /sys/block/mmcblk0/device/cid     # Card ID (device-locked)
cat /sys/block/mmcblk0/device/csd     # Card specific data
cat /sys/block/mmcblk0/size           # Card size
smartctl -a /dev/mmcblk0              # If smartmontools installed
```

### SD Card Speed / Wear Analysis
```bash
# Write speed test
dd if=/dev/zero of=/tmp/test bs=1M count=512 conv=fdatasync

# Read speed test
dd if=/tmp/test of=/dev/null bs=1M

# Check wear level (if supported)
cat /sys/block/mmcblk0/device/life_time_est
```

---

## 3.8 NVMe Attack Vectors (via HAT)

Pi 5 supports NVMe via the M.2 HAT — this is a new attack surface.

### NVMe Enumeration
```bash
# Check if NVMe is present
sudo nvme list
lsblk -d -o NAME,SIZE,MODEL,TRAN

# Detailed NVMe info
sudo nvme id-ctrl /dev/nvme0n1
sudo nvme smart-log /dev/nvme0n1
```

### NVMe Security Features
| Feature | Status | Notes |
|---------|--------|-------|
| **OPAL SED** | Unlikely default | Hardware encryption — not enabled on Pi OS by default |
| **ATA password** | N/A for NVMe | NVMe uses different security model |
| **Device lock** | ❌ Not on Pi | No built-in NVMe locking |
| **Firmware update** | ✅ Possible | Could be exploited |

### NVMe Attack Vectors
- **Firmware manipulation** — flash malicious NVMe firmware (requires advanced tools)
- **Namespace manipulation** — NVMe supports multiple namespaces
- **Temperature attack** — overclock Pi to trigger thermal throttling via NVMe stress

---

## 3.9 JTAG / Debug Interfaces

### Pi 5B JTAG Status
The Pi 5 does **NOT** expose JTAG on standard GPIO headers by default. However:

- **BCM2712** has JTAG internally — accessible if pads are exposed
- **RP1 debug interfaces** — the new I/O controller may have its own debug ports
- **Test points** — look for unpopulated headers or test pads on the PCB

### Finding Debug Interfaces
1. **Visual inspection** — look for unpopulated headers, test pads
2. **Multimeter probing** — check for JTAG signal continuity
3. **Logic analyzer** — probe unknown headers for JTAG activity

### JTAG Pins (if accessible on BCM2712)
```
TCK — Test Clock
TMS — Test Mode Select  
TDI — Test Data In
TDO — Test Data Out
TRST — Test Reset (if available)
```

### JTAG Tools
```bash
# OpenOCD — JTAG debugging
sudo apt install openocd

# OpenOCD configuration for ARM
openocd -f interface/ftdi/minimodule.cfg -f target/bcm2712.cfg

# J-Link — commercial debugger
JLinkExe -device BCM2712 -if JTAG -speed 4000
```

### What JTAG Gives You
- **Full memory read/write** — dump RAM, extract secrets
- **Breakpoint debugging** — step through code
- **Flash programming** — modify firmware
- **Bypass authentication** — modify security-critical code paths
- **Bypass storage lock** — read raw storage contents directly

---

## 3.10 Board-Level Attacks

### PCB Inspection
Use a magnifier or microscope to inspect:
- **Unpopulated headers** — could be debug ports
- **Test points** — labeled TP1, TP2, etc.
- **Silkscreen markings** — reveal pin functions
- **Board revision** — affects available interfaces

### Soldering / Probing
- **Logic analyzer** (Saleae Logic, etc.) — capture digital signals
- **Oscilloscope** — analog signal analysis
- **Bus Pirate** — multi-protocol debugging tool

### Glitching Attacks
- **Voltage glitching** — momentary VCC drop to skip instructions
- **Clock glitching** — glitch the clock to corrupt execution
- **Laser fault injection** — professional IC-level attack (very advanced)

---

## 3.11 UART Console Credential Attacks

Once you have UART console access, you need to get a shell:

### Default Credentials (Pi OS)
| Username | Password | Status |
|----------|----------|--------|
| `pi` | `raspberry` | ⚠️ **Removed in newer Pi OS** (bookworm+) |
| `pi` | `(blank)` | ⚠️ Some older images |
| `raspberrypi` | `(set at first boot)` | Newer images require setup |

### If Login Prompt is Available
```bash
# Try default credentials
Username: pi
Password: raspberry

# Try common alternatives
Username: root         # (usually no root account on Pi OS)
Username: admin        # password: admin
Username: pi           # password: pi
Username: raspberry    # password: raspberry

# Brute force if necessary (you have physical access)
# Use hydra or manual attempts
```

### If No Password Set (Unsecured)
On some older images or misconfigured Pi:
- Login without password
- Check: `sudo -l` for full root access
- Modify `/boot/cmdline.txt` to add `init=/bin/bash` for root shell (requires reboot)

### Bypass Password via Boot Parameter (Physical Access)
```bash
# 1. Mount the SD card on your Kali machine (if unlocked) or on Pi via USB boot
# 2. Edit /boot/cmdline.txt or /boot/firmware/cmdline.txt

# Add to end of cmdline.txt:
init=/bin/bash

# 3. Boot — you get a root shell with no password
# 4. Change password:
passwd pi
# 5. Remove init=/bin/bash and reboot
```

⚠️ **With storage lock**, steps 1-2 may not work on external machine. You edit
:
. (.

,:...
:...  ::
 and  
: via =B if::
 to to:
:
...

 ( with:
 = =
:...:,/

 =:
:::


 and
 andB -:
...

...

:

:


 / ...
:::
B < =,...

 
:
:
,: ...

:

:

:
:: ...


:,:

...

:
::


:::
,::
...":
::
      BB /boot/firmware/cmdline.txt and append:
```
init=/bin/bash
```

Once the Raspberry Pi reboots, it should boot directly into a root shell and prompt for a command line to continue. Then you can use the passwd command to change the password and then finish booting normally by rebooting again:
```
passwd pi
sync
exec /sbin/init
```

If you don't see the cmdline.txt file in the /boot directory, it might be located in the /boot/firmware directory instead.

You could also change the default user in cmdline.txt by adding the following to the end of the line:
```
systemd.run=/boot/autologin.sh
```

### Passwordless Sudo
If you have a user shell but not root:
```bash
# Check if current user has passwordless sudo
sudo -l

# If ANY command can run as root without password:
sudo bash
# or
sudo su
# or
sudo cat /etc/shadow  # to extract password hashes
```

---

## 3.12 Hardware Attack Checklist

- [ ] **UART console** — connect, test default creds, check for root shell
- [ ] **GPIO header** — map pin states, check for I2C/SPI devices
- [ ] **USB ports** — enumerate devices, test HID injection
- [ ] **HDMI** — capture output if display connected
- [ ] **SD card** — inspect, identify, check lock status
- [ ] **NVMe** — enumerate, check security features
- [ ] **JTAG/debug** — visual inspection, probe test points
- [ ] **Power analysis** — monitor current draw patterns
- [ ] **Bluetooth** — enumerate, check pairing, test auth bypass
- [ ] **Physical inspection** — PCB examination, silkscreen, test pads

---

## Next Steps

- [Phase 4: Storage Lock Bypass](04-storage-lock-bypass.md) — strategies for the locked storage
- [Phase 5: Vulnerability Analysis](05-vulnerability-analysis.md) — map CVEs
- [Phase 6: Exploitation](06-exploitation.md) — execute attacks

---

*Physical access changes everything. The UART console alone is often enough to own the device. Start there.*
