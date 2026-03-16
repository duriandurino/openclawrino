# App Access & Cloning via UART

This guide covers the process of identifying, analyzing, and extracting applications from a Raspberry Pi 5 via a UART serial console. This is a critical skill when SSH is disabled or network access is restricted.

---

## 1. Connecting via UART

The Raspberry Pi 5 features a dedicated 3-pin debug connector (JST-SH 1.0mm) between the micro-HDMI ports, but traditionally, UART can also be accessed via the 40-pin GPIO header.

### Physical Connection (40-Pin Header)
- **Pin 6:** GND (Ground)
- **Pin 8:** TXD (Transmit -> Connect to Adapter RX)
- **Pin 10:** RXD (Receive -> Connect to Adapter TX)
- **Logic Level:** 3.3V (Do **NOT** use 5V logic adapters)

### Physical Connection (Pi 5 Debug Port)
The Pi 5 has a specific 3-pin "J6" connector (labeled DEBUG) using a 1.0mm pitch JST-SH connector. 
- **Center Pin:** GND
- **Side Pins:** RX (top/left) and TX (bottom/right) - verify against official pinout diagrams.

### Serial Connection Commands
Use `screen` or `minicom` on your Kali/Linux host:
```bash
# Using screen
sudo screen /dev/ttyUSB0 115200

# Using minicom (setup O for 115200 8N1, Hardware Flow Control: Off)
sudo minicom -D /dev/ttyUSB0 -b 115200
```

---

## 2. Locating Installed Apps

Once logged in via UART, explore common installation paths:

### System Paths
- `/opt/`: Often used for proprietary or self-contained third-party software.
- `/usr/local/`: For apps compiled from source or custom scripts.
- `/home/<user>/`: Check for `bin/`, `projects/`, or hidden directories.

### Containerized Apps (Docker)
```bash
# List running containers
docker ps -a

# Inspect a container for volume mounts and environment variables
docker inspect <container_id>

# Extract files directly from a container
docker cp <container_id>:/app/config.json ./config.json
```

### Services & Automation
```bash
# Find active systemd services
systemctl list-units --type=service --state=running

# Locate the service file (reveals ExecStart path)
systemctl cat <service_name>.service

# Check for scheduled tasks
crontab -l
ls -la /etc/cron.*
systemctl list-timers
```

### Package Managers
- **Python:** `pip list` or `pip3 list`
- **Node.js:** `npm list -g --depth=0`
- **Web Servers:** Check `/etc/apache2/sites-enabled/` or `/etc/nginx/sites-enabled/` for Root paths (usually `/var/www/`).

---

## 3. Identifying App Dependencies

To clone an app, you must know what it needs to run.

### System Dependencies
```bash
# List installed system packages
dpkg -l > system_packages.txt

# Trace shared library dependencies for a binary
ldd /path/to/binary
```

### Language-Specific Dependencies
- **Python:** `pip freeze > requirements.txt`
- **Node.js:** Check `package.json` in the app directory.

### Environment Variables
```bash
# Current session variables
env

# System-wide variables
cat /etc/environment
cat /etc/profile.d/*

# App-specific .env files
find /app/path -name ".env"
```

---

## 4. Cloning App Data

### Extraction Strategy
1. **Compress:** Always tar/zip files to preserve permissions and reduce transfer size.
2. **Databases:**
   - **SQLite:** `sqlite3 database.db ".dump" > dump.sql`
   - **MySQL/MariaDB:** `mysqldump -u [user] -p [database] > dump.sql`
   - **PostgreSQL:** `pg_dump [database] > dump.sql`
3. **Configs:** Search for `.json`, `.yaml`, `.ini`, `.conf`, or Windows-style `.config` files.
4. **Secrets:** Grep for "API_KEY", "PASSWORD", "SECRET_KEY" within the app directory.

---

## 5. Recreating the App Environment

1. **Provision Destination:** Set up a similar OS (Raspberry Pi OS Lite or Debian 12).
2. **Install Runtimes:** Install `python3`, `nodejs`, `docker`, etc.
3. **Replay Dependencies:** 
   - `sudo apt install $(cat system_packages.txt)`
   - `pip install -r requirements.txt`
4. **Restore Files:** Extract the tarball and move configs to original paths.
5. **Test:** Run the app manually and monitor logs for missing dependencies/environment variables.

---

## 6. Practical Examples

### Example: Cloning a Python Flask App
```bash
# 1. On Target (via UART)
cd /home/pi/my_flask_app
pip freeze > requirements.txt
tar -czvf app_clone.tar.gz . 

# 2. Transfer (see section 7)

# 3. On Host
mkdir flask_clone && cd flask_clone
tar -xzvf app_clone.tar.gz
pip install -r requirements.txt
python3 app.py
```

### Example: Cloning a Dockerized App
```bash
# Identify volumes
docker inspect my_container | grep -A 10 "Mounts"

# Backup the volume data
tar -czvf db_data.tar.gz /var/lib/docker/volumes/my_db_data/_data

# Export the image (if custom)
docker save my_custom_image | gzip > my_image.tar.gz
```

---

## 7. UART-Specific Tips

Serial consoles are slow (115,200 baud is ~11.5 KB/s). Transferring large files requires strategy.

### Large File Handling
- **Split files:** `split -b 1M bigfile.tar.gz bigfile.part.`
- **Compression:** Use `xz -9` for maximum compression if CPU allows.

### Transferring over UART (The "Hard Way")
If you cannot use `scp` or `nc`: 
1. **Base64 encode:** `base64 file.tar.gz > file.b64`
2. **Capture Output:** Use your terminal emulator's "Logging" or "Capture to File" feature.
3. **Cat the file:** `cat file.b64`.
4. **On Host:** Clean the log file (remove timestamps/shell prompts) and `base64 -d file.b64 > file.tar.gz`.

### UART vs SSHFS
- **UART:** Use only for small configs, scripts, or when the network is dead.
- **SSHFS/SCP:** Always preferred if the network is available and SSH is open.

---

## 8. Checklist

- [ ] Connected via UART at 115200 baud.
- [ ] Identified app install path (e.g., `/opt/myapp`).
- [ ] Mapped all configuration files and .env files.
- [ ] Verified database type and created a dump.
- [ ] Captured dependency list (`pip freeze`, `dpkg -l`, etc).
- [ ] Archived the app directory with `tar -czv`.
- [ ] Verified systemd service or cron entry for persistence.
- [ ] Extracted archive via serial (Base64) or secondary storage (USB).
