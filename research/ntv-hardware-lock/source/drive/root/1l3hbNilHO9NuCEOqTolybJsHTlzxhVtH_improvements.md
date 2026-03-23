# System Improvements: NTV360 Resilience Scripts

While the architecture currently implements highly capable cryptographic locks and self-healing mechanisms via Phoenix, transitioning these systems toward true Enterprise scalability requires additional architectural refinements.

The following list details specific, actionable improvements for `hardware_lock.py`, `nctv-watchdog.sh`, and `repairman.sh`.

---

## 1. Implement Dynamic Provisioning (Over-The-Air Keystores)
**Current Issue:**
The variables `AUTHORIZED_PI_SERIAL` and `AUTHORIZED_SD_CID` are hardcoded directly into the raw text of `/usr/local/bin/hardware_lock.py`. This severely bottlenecks mass deployment. You cannot push a blanket update across the fleet because each player needs a different script containing its own unique serial.

**Improvement Action:**
*   When a technician first provisions a player via entering the license key in the dashboard UI (`Ctrl + Shift + K`), the system should record the underlying Pi's hardware serial and generate a salted hash. 
*   This hash should be securely sent via the API to the cloud and stored locally in a sealed `.env` keystore. 
*   `hardware_lock.py` should read securely from this provisioned keystore rather than static codebase text. 

## 2. Introduce Telemetry Alerting via Dashboard Socket
**Current Issue:**
The actions of `repairman.sh` and `nctv-watchdog.sh` are isolated to the physical unit (outputting only to `tty1`). The N-Compass Web Dashboard does not visually track when an endpoint suffers fatal corruption or requires Phoenix surgery, forcing dealers to rely entirely on the system's "Offline" UI dot status.

**Improvement Action:**
*   Integrate a `curl` payload into the end of the `repairman.sh` "Surgery" loop.
*   The payload should send a webhook directly to `nctvapi2.n-compass.online/api/device/alert`.
*   The web dashboard could display a specific `Repair Started` or `Surgery Successful` tag in the Single License page, drastically reducing diagnosis ambiguity for the remote technical support team.

## 3. Transition to OverlayFS (Read-Only Root Filesystem)
**Current Issue:**
Both the Dead Man's Switch and Phoenix tools operate Reactively—they fix the filesystem once it breaks. SD Cards inherently break due to continual R/W cycles caused by system logs and constant `player-server` `.db` caching.

**Improvement Action:**
*   Configure Raspberry Pi OS to use OverlayFS natively via `raspi-config`.
*   This forces the root OS partition to remain fundamentally Read-Only. Modifications are pushed to a RAM disk (Tmpfs) and dropped periodically upon reboot. 
*   A dedicated secondary partition (`/data`) should be created exclusively for downloaded N-Compass API assets, SQLite logs, and the AnyDesk configs.
*   **Result:** A Read-Only root practically eliminates filesystem corruption, drastically reducing how often Phoenix `repairman.sh` would need to be deployed.

## 4. Utilize A/B Partition Fallback (`tryboot`)
**Current Issue:**
If the Dead Man's Switch initiates, it halts the player by renaming `config.txt` to `.bak`. This is "Nuclear," as it guarantees the screen goes blank until a technician fixes it. 

**Improvement Action:**
*   Leverage the proprietary Raspberry Pi `tryboot` mechanism.
*   Structure the SD card with two identical OS partitions (Partition A and Partition B).
*   If `nctv-watchdog.sh` detects fatal error in Partition A, it issues `reboot 'tryboot' B`.
*   The system silently reboots into the backup Partition B, letting the screen continue showing the player software smoothly. In the background, Partition B formats and rebuilds Partition A over the internet, restoring the fallback.
