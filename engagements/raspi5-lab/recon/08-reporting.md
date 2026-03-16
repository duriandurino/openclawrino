# Phase 8: Reporting

> **Agent:** specter-report  
> **Phase:** Reporting  
> **Purpose:** Deliver findings to client/owner

---

## 8.1 Report Structure

```
RASPBERRY PI 5B PENETRATION TEST REPORT
========================================

1. Executive Summary
2. Scope & Methodology
3. Findings Summary Table
4. Detailed Findings
   - Finding 1: [Critical/High/Medium/Low]
   - Finding 2: [...]
   - ...
5. Security Enhancement Recommendations
6. Remediation Roadmap
7. Appendices
   - A. Tools Used
   - B. Raw Scan Data
   - C. Evidence / Screenshots
```

---

## 8.2 Executive Summary Template

```markdown
## Executive Summary

This report documents the results of a penetration test conducted against
the Raspberry Pi 5B located at [NETWORK LOCATION] on [DATE].

### Key Findings
- **[X]** Critical findings
- **[X]** High findings
- **[X]** Medium findings
- **[X]** Low findings

### Overall Risk Rating: [CRITICAL / HIGH / MEDIUM / LOW]

### Top 3 Immediate Actions
1. [Most critical fix]
2. [Second most critical]
3. [Third most critical]

### Summary
The Raspberry Pi 5B was [successfully/unsuccessfully] compromised through
[PRIMARY ATTACK VECTOR]. The storage device was confirmed to be locked
to the device ID, preventing offline analysis. All testing was conducted
through [NETWORK/HARDWARE/LIVE SYSTEM] vectors.

The device is running [OS VERSION] with [LIST OF SERVICES]. The most
critical finding was [BRIEF DESCRIPTION].
```

---

## 8.3 Findings Template

Each finding should follow this structure:

```markdown
### Finding [#]: [Finding Title]

**Severity:** [CRITICAL / HIGH / MEDIUM / LOW]  
**CVSS Score:** [X.X] (if applicable)  
**Category:** [Misconfiguration / Vulnerability / Missing Hardening / etc.]  
**Access Required:** [Network / Physical / Shell]  
**Affected Component:** [Service / Software / Hardware]

#### Description
[Detailed description of the vulnerability or misconfiguration]

#### Proof of Concept
[Step-by-step reproduction of the finding]

```
# Command 1
output

# Command 2
output
```

#### Impact
[What an attacker can achieve by exploiting this finding]

#### Remediation
[Specific steps to fix the issue]

#### Security Enhancement Recommendations
[Additional hardening beyond the basic fix]

#### References
- [CVE links, advisory links, documentation]
```

---

## 8.4 Common Findings for Pi 5B

### Finding: Default or Weak Credentials

```markdown
### Finding 1: Default SSH Credentials

**Severity:** CRITICAL  
**CVSS Score:** 9.8  
**Category:** Default Credentials  
**Access Required:** Network (SSH)  
**Affected Component:** SSH Service (port 22)

#### Description
The Raspberry Pi 5B allows SSH login using the default credentials
`pi` / `raspberry`. This is the factory default for pre-Bookworm Pi OS
images and remains the most common attack vector for Raspberry Pi devices.

#### Proof of Concept
```bash
$ ssh pi@192.168.1.100
pi@192.168.1.100's password: raspberry
Linux raspberrypi 6.1.0-rpi7-v8+ #1 SMP PREEMPT ...
pi@raspberrypi:~$ whoami
pi
```

#### Impact
An attacker with network access to the Pi can:
- Gain full user-level access
- Read all user-accessible files
- Attempt privilege escalation to root
- Use the Pi as a pivot point to other network hosts

#### Remediation
1. Change the default password: `passwd`
2. Or better: disable password authentication entirely

```bash
# /etc/ssh/sshd_config
PasswordAuthentication no
PermitEmptyPasswords no
```

#### Security Enhancement Recommendations
1. **Enforce SSH key-only authentication**
   - Generate keypair: `ssh-keygen -t ed25519`
   - Add public key to `~/.ssh/authorized_keys`
   - Set `PasswordAuthentication no` in sshd_config
   
2. **Disable the `pi` user account**
   ```bash
   sudo passwd -l pi  # Lock the account
   # Create a new user with a non-obvious username
   sudo adduser secureadmin
   sudo usermod -aG sudo secureadmin
   ```

3. **Implement fail2ban**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

4. **Change default SSH port**
   ```bash
   # /etc/ssh/sshd_config
   Port 2222
   ```

5. **Restrict SSH access by IP**
   ```bash
   # /etc/ssh/sshd_config
   AllowUsers secureadmin@192.168.1.0/24
   ```
```

---

### Finding: No Firewall Rules

```markdown
### Finding 2: No Firewall Configuration

**Severity:** HIGH  
**CVSS Score:** 7.5  
**Category:** Missing Hardening  
**Access Required:** Network  
**Affected Component:** All network services

#### Description
The Raspberry Pi 5B has no active firewall rules. Both `iptables` and
`nftables` show empty rule sets, leaving all services exposed to any
network that can reach the device.

#### Proof of Concept
```bash
$ ssh pi@192.168.1.100
$ sudo iptables -L -n
Chain INPUT (policy ACCEPT)
target  prot opt source    destination

Chain FORWARD (policy ACCEPT)
target  prot opt source    destination

Chain OUTPUT (policy ACCEPT)
target  prot opt source    destination
```

#### Impact
All listening services are accessible from any network source without
filtering. An attacker on the same network can:
- Port scan and fingerprint the device
- Attempt brute force on any service
- Exploit any running service without network-level blocking

#### Remediation
Configure iptables or ufw with a default-deny policy:

```bash
# Using ufw (simple)
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
# Add rules for any other required services
sudo ufw enable
```

#### Security Enhancement Recommendations
1. **Implement ufw with rate limiting**
   ```bash
   sudo ufw limit 22/tcp  # Rate limit SSH
   ```

2. **Restrict SSH to management subnet only**
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 22
   ```

3. **Enable logging**
   ```bash
   sudo ufw logging on
   # Logs to /var/log/ufw.log
   ```

4. **Consider nftables for complex rules**
   ```bash
   # More flexible than iptables
   sudo apt install nftables
   ```

5. **Review and close unnecessary services**
   ```bash
   sudo ss -tlnp  # See what's listening
   # Disable services not needed
   sudo systemctl disable <service>
   ```
```

---

### Finding: UART Console Unauthenticated

```markdown
### Finding 3: UART Debug Console Accessible Without Authentication

**Severity:** CRITICAL  
**CVSS Score:** 9.1  
**Category:** Hardware Misconfiguration  
**Access Required:** Physical  
**Affected Component:** UART Debug Header

#### Description
The Raspberry Pi 5B's UART debug header provides serial console access
that authenticates using the system password database. If default or
weak credentials are set (Finding 1), physical access to the UART
header grants full shell access without any additional authentication
barrier.

#### Proof of Concept
```bash
# On Kali with USB-to-UART adapter connected:
$ screen /dev/ttyUSB0 115200

raspberrypi login: pi
Password: raspberry

Linux raspberrypi 6.1.0-rpi7-v8+ ...
pi@raspberrypi:~$
```

#### Impact
Anyone with physical access to the device can:
- Gain shell access in seconds
- Bypass any network-level security controls
- Access the storage device while it's unlocked (bypassing storage lock)
- Modify the running system

#### Remediation
1. Ensure the `pi` user password has been changed (see Finding 1)
2. Disable serial console if not needed:
   ```bash
   sudo raspi-config
   # Interface Options → Serial Port
   # Disable serial login shell
   # Enable serial hardware
   ```

#### Security Enhancement Recommendations
1. **Disable serial console entirely**
   ```bash
   # /boot/cmdline.txt — remove console=serial0,115200
   # /etc/securetty — remove ttyAMA0
   ```

2. **Remove the UART header** (if hardware modification is acceptable)
   - Desolder the 5-pin header to prevent easy connection

3. **Implement physical security controls**
   - Lock the Pi in an enclosure
   - Tamper-evident seals on USB and UART ports

4. **Enable secure boot** to prevent boot-level bypass
   ```bash
   sudo rpi-eeprom-update -a
   # Enable secure boot via OTP (one-time programmable)
   ```
```

---

## 8.5 Security Enhancement Recommendations (Summary)

### Critical Priority
| # | Recommendation | Effort | Impact |
|---|----------------|--------|--------|
| 1 | Change all default credentials | Low | 🔴 Critical |
| 2 | Disable SSH password auth (key-only) | Low | 🔴 Critical |
| 3 | Enable secure boot | Medium | 🔴 Critical |
| 4 | Disable UART console or secure it | Low | 🔴 Critical |

### High Priority
| # | Recommendation | Effort | Impact |
|---|----------------|--------|--------|
| 5 | Configure firewall (ufw/nftables) | Low | 🟡 High |
| 6 | Install fail2ban | Low | 🟡 High |
| 7 | Disable unused services | Low | 🟡 High |
| 8 | Enable automatic security updates | Low | 🟡 High |
| 9 | Remove `pi` user account | Low | 🟡 High |

### Medium Priority
| # | Recommendation | Effort | Impact |
|---|----------------|--------|--------|
| 10 | Enable full-disk encryption | High | 🟢 Medium |
| 11 | Implement USB device whitelist | Medium | 🟢 Medium |
| 12 | Set up log monitoring/alerting | Medium | 🟢 Medium |
| 13 | Network segmentation | Medium | 🟢 Medium |
| 14 | Regular firmware updates | Low | 🟢 Medium |

### Low Priority
| # | Recommendation | Effort | Impact |
|---|----------------|--------|--------|
| 15 | Physical security enclosure | Medium | 🟢 Low |
| 16 | Remove unused headers (UART) | Low | 🟢 Low |
| 17 | Implement Bluetooth security | Low | 🟢 Low |
| 18 | GPIO access controls | Medium | 🟢 Low |

---

## 8.6 Remediation Roadmap

```
Week 1 (Immediate):
├── Change all default passwords
├── Disable SSH password auth
├── Enable firewall
└── Disable UART console

Week 2-3:
├── Remove pi user account
├── Install fail2ban
├── Disable unused services
├── Set up automatic updates
└── Review and update SSH config

Month 1:
├── Enable secure boot (if not already)
├── Implement network segmentation
├── Set up log monitoring
└── Review Samba/web service configs

Quarter 1:
├── Evaluate full-disk encryption
├── Physical security controls
├── USB device restrictions
└── Bluetooth security audit
```

---

## 8.7 Evidence Appendix

Store all evidence with integrity:

```
evidence/
├── nmap-full.xml
├── nmap-full.nmap
├── recon-summary.txt
├── ssh-banners.txt
├── smb-enum.txt
├── config-exfil.tar.gz
├── memory-dump.lime
├── screenshots/
│   ├── uart-console.png
│   ├── default-login.png
│   └── root-shell.png
├── hashes.txt          # SHA-256 of all evidence files
└── tools-used.txt      # Tool versions and commands
```

### Evidence Integrity
```bash
# Hash all evidence
sha256sum evidence/* > evidence/hashes.txt

# Verify later
sha256sum -c evidence/hashes.txt
```

---

## 8.8 Report Delivery

- Generate PDF from Markdown (using pandoc or similar)
- Encrypt the report with client's public key
- Deliver via secure channel
- Request acknowledgment of receipt
- Set retention policy for evidence and report

```bash
# Generate PDF from markdown
pandoc 08-reporting.md -o pentest-report-raspi5b.pdf

# Encrypt
gpg --encrypt --recipient client@example.com pentest-report-raspi5b.pdf
```

---

*The report is the deliverable. Everything before this was just groundwork. A pentest without a clear, actionable report is just expensive hacking. Make it count.*
