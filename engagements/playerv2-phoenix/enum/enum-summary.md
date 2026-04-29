# Enum Summary

## Reproducibility Notes

The enum phase should be readable as both a summary and a replay guide.

Where evidence already exists, the commands below reflect the actual tool choices and command patterns used to validate the current network picture. If you rerun them from the same network position, you should expect broadly similar results unless the target state has changed.

### Core device-reachability and service-validation commands

```bash
ping -c 2 192.168.1.70
nmap -Pn -sS -sV --version-light --reason -p 22,111 192.168.1.70
nmap -Pn -sU -sV --version-light --reason -p 111,5353 192.168.1.70
nmap -Pn -p- --min-rate 2000 --reason 192.168.1.70
rpcinfo -p 192.168.1.70
showmount -e 192.168.1.70
ssh -v pi@192.168.1.70
```

### Revalidation commands used after misleading local discovery behavior

```bash
nmap --privileged -Pn -n --disable-arp-ping -sS -sV --version-light --reason -p 22,111 -oA engagements/playerv2-phoenix/enum/live/revalidate-known-noarp-2026-04-28 192.168.1.70
nmap --privileged -Pn -n --disable-arp-ping -sU -sV --version-light --reason -p 111,5353 -oA engagements/playerv2-phoenix/enum/live/revalidate-udp-noarp-2026-04-28 192.168.1.70
nmap --privileged -Pn -n --disable-arp-ping --script ssh2-enum-algos,ssh-hostkey -p 22 -oA engagements/playerv2-phoenix/enum/live/ssh-deep-2026-04-28 192.168.1.70
nmap --privileged -Pn -n --disable-arp-ping --script rpcinfo -p 111 -oA engagements/playerv2-phoenix/enum/live/rpc-script-2026-04-28 192.168.1.70
nmap --privileged -Pn -n --disable-arp-ping -sU --script dns-service-discovery -p 5353 -oA engagements/playerv2-phoenix/enum/live/mdns-discovery-2026-04-28 192.168.1.70
nmap --privileged -Pn -n --disable-arp-ping -sS -sV --version-light --reason -p 22,111 -oA engagements/playerv2-phoenix/enum/live/revalidate-known-noarp-2026-04-29 192.168.1.70
nmap --privileged -Pn -n --disable-arp-ping -sU -sV --version-light --reason -p 111,5353 -oA engagements/playerv2-phoenix/enum/live/revalidate-udp-noarp-2026-04-29 192.168.1.70
ssh-keyscan -T 5 192.168.1.70 > engagements/playerv2-phoenix/enum/live/ssh-keyscan-2026-04-29.txt
timeout 5 bash -lc "printf '' | nc -v -w 3 192.168.1.70 1883" > engagements/playerv2-phoenix/enum/live/mqtt-1883-2026-04-29.txt 2>&1
```

### Core API-side enumeration commands

```bash
curl -I https://dev-api.n-compass.online
curl -sk https://dev-api.n-compass.online/
for path in / /health /healthz /status /graphql /.well-known/security.txt /api /api/health /api/v1; do
  printf "\n=== %s ===\n" "$path"
  curl -sk -D - "https://dev-api.n-compass.online$path" -o /dev/null
  curl -sk "https://dev-api.n-compass.online$path"
  printf "\n"
done
```

- Enumeration is now justified based on completed recon for both the API and local device surfaces
- Confirmed starting points for enum:
  - API target: `https://dev-api.n-compass.online`
  - device hostname: `raspberry`
  - device IPv4: `192.168.1.70`
  - device link-local IPv6: `fe80::2ecf:67ff:fe04:bd1`
  - alternate local consoles: tty2 and tty3 with `raspberry login:` visible, reached via `Alt+Fn` rather than `Ctrl+Alt+Fn`
  - trust-related services exposed by failure state: `hardware-check.service` and `vault-mount.service`
- Current enum objective: validate remote reachability, confirm exposed management/services, and turn the device-side trust-path clues into a concrete service and behavior inventory
- Important network note: operator VM is on Wi-Fi SSID `NTV360_5GHz`, but the player Raspberry Pi's connected Wi-Fi / SSID is still unknown, so same-network assumptions must be validated instead of assumed
- First live enum results confirm that network access is viable:
  - `ping -c 2 192.168.1.70` succeeded from the operator VM
  - `ssh -v pi@192.168.1.70` reached the SSH service and failed only at authentication
  - `192.168.1.70` is reachable from the operator VM
  - `22/tcp` is open and running `OpenSSH 10.0p2 Debian 7+deb13u2`
  - `111/tcp` is also open and identified as `rpcbind` version `2-4` on the Pi
  - UDP validation adds `111/udp` and `5353/udp` as confirmed open services, with `5353/udp` identified as mDNS / Zeroconf
  - targeted follow-up reclassified `137/udp` and `1900/udp` as closed on the Pi, so they should be removed from the active candidate list for this host
  - `123/udp` looked `open|filtered` in a fast pass but validated as closed in the targeted follow-up, so it should not enter the confirmed inventory
  - SSH authentication is enforced and currently denies access without valid credentials
  - full TCP sweep currently shows only `22/tcp` and `111/tcp` open on the Pi, with the remaining tested TCP ports reset/closed
  - the exposed `rpcbind` service is a meaningful new lead because it can indicate additional RPC/NFS-style local service dependencies even when only a small port set is externally visible
  - follow-up RPC validation currently shows only the portmapper itself registered across IPv4 and IPv6, with no NFS exports or additional RPC programs proven from this pass
  - SSH deep fingerprinting confirms a modern OpenSSH configuration offering `publickey,password` authentication and host keys for RSA, ECDSA, and ED25519
- Parallel API-side enum shows `dev-api.n-compass.online` is externally hosted behind AWS infrastructure:
  - HTTP response body: `This is N-Compass TV.`
  - HTTP header exposes `Server: awselb/2.0`
  - DNS currently resolves to AWS public addresses `54.210.39.233` and `54.205.199.192`
  - TLS certificate subject is `CN=n-compass.online`
  - root-like paths such as `/`, `/health`, `/healthz`, `/status`, `/graphql`, and `/.well-known/security.txt` all return the same plain-text body through the ELB
  - `/api`, `/api/health`, and `/api/v1` return `404 Not Found` with `Server: Kestrel`, which is useful evidence that a backend application exists behind the load balancer even though the exposed public surface stays minimal
- Live revalidation on 2026-04-28 confirms the host is still reachable at `192.168.1.70`, but normal same-subnet Nmap discovery was initially misleading until ARP-based host discovery was disabled with `-Pn -n --disable-arp-ping`; this means future scans on this segment should avoid trusting default local discovery behavior without a manual sanity check
  - practical replay note: the strongest reproducer here is the saved no-ARP command pattern, for example `nmap --privileged -Pn -n --disable-arp-ping -sS -sV --version-light --reason -p 22,111 192.168.1.70`
- Fresh TCP/UDP validation reconfirms the externally visible device inventory as:
  - `22/tcp` OpenSSH 10.0p2 Debian 7+deb13u2
  - `111/tcp` rpcbind
  - `111/udp` rpcbind
  - `5353/udp` mDNS / Zeroconf
- Manual socket validation also reconfirmed that `22/tcp` and `111/tcp` are accepting connections even when the first Nmap passes incorrectly said the host was down
- SSH algorithm enumeration shows a modern OpenSSH posture with post-quantum-hybrid and Curve25519 KEX support, RSA/ECDSA/ED25519 host-key algorithms, and no obvious weak legacy crypto exposed in this surface check
- RPC revalidation still shows only the portmapper itself registered over IPv4 and IPv6, with no additional RPC programs proven from this pass
- mDNS service-discovery follow-up returns only a generic `workstation` advertisement mapped to `192.168.1.70` and `fe80::2ecf:67ff:fe04:bd1`, which supports host presence but does not yet expose a richer service profile
- Current interpretation: the Raspberry Pi player and the cloud API are likely related operationally, but direct trust-path linkage is not yet proven only from these enum signals
- Current network picture suggests a deliberately sparse device surface, with SSH, rpcbind, and local-service-discovery signals exposed while the cloud endpoint presents a thin ELB front with a Kestrel-backed application visible only indirectly through selected 404 responses
- Passive local-network correlation is partially blocked from this chat runtime because elevated packet capture is unavailable here, so stronger mDNS or outbound-flow proof will require either a local privileged capture or physical-on-device observation
- Follow-up SSH auth-surface characterization on 2026-04-28 confirmed that the target advertises `publickey,password` for candidate users `pi`, `root`, `admin`, `phoenix`, `player`, and `ncompass`; this is useful for account-surface mapping, but no valid credentials were proven from the network side in this pass
- On 2026-04-29, this engagement also resumed network enum through the reusable scripts/manifests layer rather than only manual commands. The runner used was:
  - `python3 scripts/orchestration/run_enum_profile.py --profile enum-player-core --target 192.168.1.70 --engagement playerv2-phoenix`
  - this resolved into reusable scripts including fast port scan, service scan, SSH probe, FTP probe, safe web basic enum, and safe MQTT probe, all under `scripts/enum/` and `scripts/shared/manifests/`
- The reusable scripts-first rerun produced a weaker default result set than the earlier validated inventory:
  - fast top-1000 scan reported `0 hosts up` / no open ports
  - service scan became a no-op because the fast pass discovered nothing
  - SSH probe saw no host-key material
  - MQTT probe observed `1883/tcp timed out`
- Because earlier enum had already shown that default same-subnet discovery can mislead on this LAN, those weaker results were not accepted as final truth without revalidation
- Manual no-ARP revalidation on 2026-04-29 then showed the host is still up but currently presents a more filtered service picture than the earlier validated baseline:
  - `22/tcp` now `filtered` with `no-response`
  - `111/tcp` now `filtered` with `no-response`
  - `111/udp` now `open|filtered`
  - `5353/udp` now `open|filtered`
  - `ssh-keyscan` returned no host keys at that moment
  - raw TCP connect test to `1883/tcp` timed out
- Current interpretation for this network delta:
  - the earlier validated inventory should still be preserved as real earlier state
  - the newest rerun should be preserved as a separate later state showing a more filtered or less reachable posture
  - a partial restart-window capture was also attempted during operator reboot activity, but only the first cycle was preserved; that captured cycle still matched the newer filtered posture rather than the older open-SSH/open-rpcbind state
  - do not flatten these into a single timeless conclusion, because the target appears to have changed behavior over time or across runtime states
- New physical enum evidence from 2026-04-28 and later photo captures shows that the short-lived `tty1` exposure was previously not only a login banner but could momentarily present an interactive shell prompt as `pi@raspberry` before the lockout path resumed
- Current follow-up behavior has shifted: the operator now reports that the `tty1` shell exposure is no longer appearing, with only the OS GUI showing during that window despite no intentional change to the device
- The same transient shell exposure and startup log window captured service-style runtime text including `Completed socket interaction for boot stage config`, `Completed socket interaction for boot stage final`, and later boot-screen output showing `Complete socket interaction for boot stage local`, which suggests the boot path includes an internal staged socket-driven workflow on the primary console
- Additional startup and shutdown-path photo evidence now shows service-start and service-stop output that is likely relevant to player/Phoenix behavior, including:
  - startup-side ordering-cycle clue: `systemd[1]: graphical.target: Job nctv-phoenix.target/start deleted to break ordering cycle starting with graphical.target/start`
  - prior startup/shutdown-side ordering-cycle clue: `systemd[1]: nctv-phoenix.service: Job hardware-check.service/start deleted to break ordering cycle starting with nctv-phoenix.target/start`
  - startup log visibility during Plymouth via `Esc`, showing systemd units for filesystems, socket activation, `cloud-init`, `NetworkManager`, Raspberry Pi EEPROM checks, and boot-stage socket-interaction lines
  - `Stopped nctv-watchdog.service - NCTV Phoenix Directory Watchdog...`
  - `Stopped nctv-watchdog.service - NCTV Phoenix Directory Watchdog.`
  - `Stopped target rpcbind.target - RPC Port Mapper.`
  - `Stopped NetworkManager.service - Network Manager.`
  - `Closed sshd-unix-local.socket - OpenSSH Server Socket (systemd-ssh-generator, AF_UNIX Local).`
  - `Reached target shutdown.target - System Shutdown.`
  - `Reached target poweroff.target - System Power Off.`
- Operator interaction detail now matters for reproduction:
  - the shutdown trigger was corrected again to `Fn+Esc`
  - near the verge of shutdown, pressing `Shift+Esc` appears to be what exposes the stopped-services log output on screen
  - this suggests the visible log dump may depend on a second key interaction during an in-progress shutdown state rather than appearing automatically every time
- One of the shutdown captures also shows a filesystem-check-related unit still active during poweroff flow, including `systemd-fsck@...service - File System Check on /dev/disk/by-partuuid/...` and a running job associated with `/dev/sda1`; this should be treated as a potentially relevant storage-state clue until reproduced more cleanly
- This strengthens the current model that `tty1` is a contested runtime surface that briefly exposes live host-side output before being reclaimed by the wrong-device / hardware-lock path, and also suggests the Phoenix/hardware-check dependency chain deserves direct service-order analysis
- Old engagement artifacts provide a strong historical hypothesis that serial-derived values matter operationally, especially the confirmed `setup.enc` passphrase `theNTVofthe360isthe360oftheNTV`, but that prior evidence is tied to provisioning / installer recovery work and must not be treated as a proven SSH credential without local validation
- Immediate enum follow-up should now focus on high-fidelity physical timing and classification of the `tty1` race window, while preserving the distinction between observed shell exposure, staged socket messages, and the later wrong-device takeover
- On 2026-04-29, the engagement gained a new local-enumeration branch when the operator deliberately changed only the storage presentation method:
  - the same microSD card that previously produced the wrong-device path in direct-slot boot was inserted into an external USB SD adapter and then connected to the Raspberry Pi
  - the operator reported that the player still displayed the normal NTV logo during startup, but this time it stayed at the OS GUI and did not proceed into the earlier `tty1` wrong-device / hardware-lock presentation
  - because this created sustained local terminal access, the enum phase pivoted from blind physical timing work into structured on-device enumeration with explicit care not to trigger unnecessary writes, repairs, or decryption attempts too early
- The first local enumeration goal was to verify whether the changed behavior came from a real storage topology difference or just from timing luck. The exact command block used was:
  - `whoami`
  - `hostnamectl 2>/dev/null || hostname`
  - `uname -a`
  - `lsblk -o NAME,SIZE,TYPE,FSTYPE,LABEL,UUID,MOUNTPOINTS`
  - `mount | egrep '/ |/boot|/boot/firmware|/media|/mnt'`
  - `cat /proc/cmdline`
  - `sudo cat /etc/fstab`
  - `lsusb`
  - `sudo fdisk -l 2>/dev/null | sed -n '1,220p'`
- Those commands established the exact alternate runtime state:
  - current user was `pi`
  - host remained `raspberry`, Debian GNU/Linux 13 (trixie), kernel `6.12.75+rpt-rpi-2712`
  - booted storage was now seen as `/dev/sda`, not `/dev/mmcblk0`
  - `/dev/sda1` was mounted on `/boot/firmware`
  - `/dev/sda2` was mounted on `/`
  - the attached USB reader enumerated as `Genesys Logic, Inc. SD Card Reader and Writer`
  - the partition table and `PARTUUID` values still matched the player image, confirming the storage contents were the same logical boot source while the kernel-visible device path had changed
- The next local enumeration objective was to map which parts of the Phoenix stack were alive, failed, or dependency-blocked. The exact service and path discovery commands used were:
  - `systemctl list-units --type=service --all | egrep -i 'phoenix|nctv|pulse|vault|hardware|lock|watchdog'`
  - `systemctl --failed`
  - `systemctl list-unit-files | egrep -i 'phoenix|nctv|pulse|vault|hardware|lock|watchdog'`
  - `sudo find /opt -maxdepth 4 \( -iname '*phoenix*' -o -iname '*nctv*' -o -iname '*pulse*' -o -iname '*hardware*' -o -iname '*vault*' \) 2>/dev/null | sort`
  - `find /home -maxdepth 4 \( -iname '*phoenix*' -o -iname '*nctv*' -o -iname '*pulse*' -o -iname '*hardware*' -o -iname '*vault*' \) 2>/dev/null | sort`
  - `sudo find /etc -maxdepth 4 \( -iname '*phoenix*' -o -iname '*nctv*' -o -iname '*pulse*' -o -iname '*hardware*' -o -iname '*vault*' \) 2>/dev/null | sort`
- That pass produced the following service-level inventory:
  - `hardware-check.service` loaded, failed
  - `nctv-player.service` loaded, activating, auto-restart
  - `nctv-watchdog.service` loaded, active, running
  - `vault-mount.service` loaded, inactive, dead
  - `repairman.service` loaded, failed
  - relevant non-vault paths currently visible outside the secure runtime included:
    - `/opt/nctv-player`
    - `/home/pi/.config/nctv-player`
    - `/home/pi/.config/pulse`
    - `/etc/nctv-phoenix/hardware-lock.env`
    - Phoenix systemd unit files under `/etc/systemd/system/`
- The engagement then moved from high-level service names into exact unit and script content, because a report-ready explanation required the actual dependency chain. The operator read:
  - `/etc/systemd/system/hardware-check.service`
  - `/etc/systemd/system/vault-mount.service`
  - `/etc/systemd/system/nctv-player.service`
  - `/etc/systemd/system/nctv-watchdog.service`
  - `/etc/systemd/system/nctv-phoenix.target`
  - `/etc/nctv-phoenix/hardware-lock.env`
  - `/usr/local/bin/hardware_lock.py`
  - `/usr/local/bin/unlock_vault.py`
  - `/usr/local/bin/repairman.sh`
  - `/usr/local/bin/nctv-watchdog.sh`
- The most important exact code and config facts recovered from that pass were:
  - `hardware_lock.py` reads the Pi serial from `/proc/cpuinfo` and the SD CID only from `/sys/block/mmcblk0/device/cid`
  - it compares those values to `AUTHORIZED_PI_SERIAL` and `AUTHORIZED_SD_CID_SHA256` in `/etc/nctv-phoenix/hardware-lock.env`
  - if a mismatch is detected, it stops `nctv-player.service`, `lightdm.service`, and `getty@tty1.service`, writes a wrong-device banner to `/dev/tty1`, switches to `tty1`, and loops to keep that lock visible
  - `unlock_vault.py` uses the same hardcoded `/sys/block/mmcblk0/device/cid` path and verifies the actual serial and CID hash before deriving keys
  - its vault unlock key derivation is exactly `sha256(expected_serial + ':' + expected_cid_hash)` using raw digest bytes piped to `cryptsetup`
  - its database key derivation is exactly `sha256(expected_serial + ':' + expected_cid_hash + ':' + DB_KEY_SALT)` using raw digest bytes written to `/var/lib/nctv-player/.db.key`
  - the script expects the encrypted vault at `/var/lib/nctv-phoenix/vault.img`, mounts it at `/mnt/nctv-phoenix-secure`, and bind-mounts secure content back onto `/opt/nctv-player`, `/var/lib/nctv-player`, `/home/pi/.config/nctv-player`, and optionally `/usr/share/doc/nctv-player`
  - `repairman.sh` contains a real recovery routine for restoring an SD install from an external repair source and also contains a branch for `emergency_standalone_mode` when `/dev/mmcblk0` is absent
  - `nctv-watchdog.sh` continuously checks for missing critical runtime directories and, when they are absent, touches `/run/nctv-phoenix-repair-needed` and starts `repairman.service`
- The decisive live enumeration check was to capture service failures with status and journal output. The exact commands used were:
  - `systemctl status hardware-check.service --no-pager -l`
  - `systemctl status repairman.service --no-pager -l`
  - `systemctl status vault-mount.service --no-pager -l`
  - `journalctl -u hardware-check.service -b --no-pager -n 120`
  - `journalctl -u repairman.service -b --no-pager -n 120`
  - `journalctl -u vault-mount.service -b --no-pager -n 120`
- Those outputs provided the exact failure chain instead of a hypothesis:
  - `hardware-check.service` exited with status `1/FAILURE`
  - its traceback repeatedly ended at `FileNotFoundError: [Errno 2] No such file or directory: '/sys/block/mmcblk0/device/cid'`
  - this proved the service was not rejecting the hardware because of a serial or CID mismatch; it was crashing because the expected SD-CID path did not exist in USB-presented boot mode
  - `vault-mount.service` then failed only as a dependency casualty, repeatedly logging `Dependency failed for vault-mount.service - Unlock and Mount NCTV Phoenix Vault.` and never reaching its own unlock logic
  - `repairman.service` looped every minute with `[repairman] starting nctv-phoenix repair flow` followed by `[repairman] repair source missing`
- The engagement then validated the current storage and vault artifacts themselves without attempting an unlock. The exact commands used were:
  - `sudo find /var/lib -maxdepth 3 \( -iname '*nctv*' -o -iname '*phoenix*' -o -iname '*vault*' \) -exec ls -ld {} \;`
  - `sudo ls -l /var/lib/nctv-phoenix /var/lib/nctv-phoenix/vault.img`
  - `sudo file /var/lib/nctv-phoenix/vault.img`
  - `sudo cryptsetup luksDump /var/lib/nctv-phoenix/vault.img | sed -n '1,160p'`
  - `sudo find /var/lib/nctv-player -maxdepth 3 -exec ls -ld {} \;`
  - `sudo find /usr/share/doc/nctv-player -maxdepth 3 -exec ls -ld {} \;`
- Those commands showed:
  - `/var/lib/nctv-phoenix/vault.img` exists and is a 2 GiB LUKS2 encrypted file
  - LUKS UUID is `58a2a481-a39b-4305-8f15-4f20fa1e7d3f`
  - cipher is AES-XTS-plain64 with one active keyslot using Argon2id
  - `/var/lib/nctv-player` exists but is effectively empty in this failure state
  - `/usr/share/doc/nctv-player` also exists only as the base directory
  - this fits the code path in `unlock_vault.py`, because the secure bind mounts never activated after `hardware-check.service` failed
- Package metadata was also checked to understand what the plain package provides without the vault overlay. The commands used were:
  - `sudo sed -n '1,240p' /var/lib/dpkg/info/nctv-player.list`
  - `sudo sed -n '1,260p' /var/lib/dpkg/info/nctv-player.postinst`
  - `sudo sed -n '1,220p' /var/lib/dpkg/info/nctv-player.postrm`
  - `sudo sed -n '1,260p' /var/lib/dpkg/info/nctv-player.md5sums`
- That package review showed:
  - the Debian package lays down the Electron runtime, launcher, icons, and locale assets under `/opt/nctv-player`
  - the post-install script creates only lightweight writable scaffolding such as `/var/lib/nctv-player` and `/var/lib/nctv-player/playlist`
  - package metadata alone does not provide the rich secure runtime content; that content is expected to be overlaid later through the vault bind-mount process
- A final attempted enumeration of Electron application internals produced a useful negative result that should remain documented because it explains why the visible runtime looked thinner than the package manifest suggested. The exact attempted commands were:
  - `strings /opt/nctv-player/resources/app.asar | egrep -i 'nctv-player|vault|db\.key|sqlite|sqlcipher|playlist|server|repair|hardware|serial|cid|unlock' | sed -n '1,260p'`
  - a small Python header walker against `/opt/nctv-player/resources/app.asar`
  - `grep -RniE 'db\.key|better-sqlite3|cipher|sqlcipher|playlist|vault|hardware|repair|serial|cid' /opt/nctv-player/resources/app.asar.unpacked 2>/dev/null | sed -n '1,240p'`
- Actual result from those commands:
  - `strings` returned `No such file` for `/opt/nctv-player/resources/app.asar`
  - the Python ASAR walker failed with `FileNotFoundError: [Errno 2] No such file or directory: '/opt/nctv-player/resources/app.asar'`
  - the unpacked-path grep returned no hits
- That negative result is still meaningful:
  - in this USB-presented, vault-blocked state, the live visible `/opt/nctv-player` layout is not exposing the richer application resources that the package metadata implies should exist in a fully realized runtime view
  - this strengthens the interpretation that the intended operational content path depends heavily on the vault-backed overlay and related recovery/runtime logic
- Current high-confidence local enumeration conclusion:
  - the same player image can boot successfully through a USB mass-storage presentation path
  - in that mode, the system sees the media as `sda` rather than `mmcblk0`
  - Phoenix enforcement code is brittle because both `hardware_lock.py` and `unlock_vault.py` hardcode `/sys/block/mmcblk0/device/cid`
  - the direct consequence is a reproducible fail-open-like state for local access: `hardware-check.service` crashes, `vault-mount.service` dependency-fails, `repairman.service` loops looking for a repair source, and the operator remains in a usable local GUI/terminal environment instead of being locked back to the wrong-device screen
- This branch should not be flattened into the earlier direct-slot observations. It is a separate, reproducible physical enumeration state with different attack surface, different service behavior, and a stronger evidence trail for a future vulnerability write-up around storage-interface-dependent authorization failure
