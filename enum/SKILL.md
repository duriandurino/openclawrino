---
name: enum
description: "Active service enumeration, port scanning, and directory busting for penetration testing. Use when: user asks to scan ports, enumerate services, bust directories on web servers, fingerprint services, find open ports, probe a target for running services, scan a subnet, or enumerate SMB/FTP/HTTP services. NOT for: passive recon (use recon skill), vulnerability analysis (use vuln skill), or exploitation (use exploit skill). This is the active scanning phase — packets WILL be sent to target."
metadata: { "openclaw": { "emoji": "📡", "requires": { "bins": ["nmap", "curl"] } } }
---

# Enumeration Skill

Active scanning and service enumeration. This is the phase where you touch the target — expect IDS/alerts.

## When to Use

✅ **USE this skill when:**
- "Scan this host for open ports"
- "Full service enumeration on 192.168.1.105"
- "Bust directories on this web server"
- "What services are running on port X?"
- "Fingerprint this web app"
- "Enumerate shares on this host"
- "Scan this subnet"
- "Check for anonymous FTP/SMB access"

## When NOT to Use

❌ **DON'T use this skill when:**
- Passive DNS/OSINT work → use recon skill
- Vulnerability analysis of discovered services → use vuln skill
- Exploiting known vulnerabilities → use exploit skill
- Only need DNS records → use recon skill

## ⚠️ Authorization Reminder

Active scanning generates network traffic and may trigger IDS/IPS alerts. **Confirm scope authorization before running any scan.**

## Automation-First Scanning Strategy

Always prefer the standardized wrappers under `scripts/` before building custom scans.

### Recommended Default Profile

For a likely Windows host or generic internal workstation/server:

```bash
python3 scripts/orchestration/run_enum_profile.py \
  --profile enum-windows-host \
  --target <TARGET> \
  --engagement <target-name>
```

### Step 1 — Quick Port Scan (Top 1000)

```bash
scripts/enum/ports/scan_ports_fast.sh --target <TARGET> --engagement <target-name>
```

### Step 2 — Follow-up Service Scan

```bash
scripts/enum/ports/scan_ports_service.sh --target <TARGET> --engagement <target-name>
```

### Step 3 — Service-Specific Baselines

```bash
scripts/enum/web/enum_web_basic.sh --target <TARGET> --engagement <target-name> --safe
scripts/enum/smb/enum_smb_basic.sh --target <TARGET> --engagement <target-name> --safe
scripts/enum/rdp/rdp_probe.sh --target <TARGET> --engagement <target-name>
scripts/enum/winrm/winrm_probe.sh --target <TARGET> --engagement <target-name>
```

### Legacy / Manual Escalation

Use manual commands when the wrappers do not fit the service mix or you need deeper coverage:

```bash
# ARP scan / discovery
sudo nmap -sn 192.168.1.0/24

# Full manual service scan
nmap -sV -sC -p- <TARGET>

# Aggressive focused follow-up
nmap -sV -sC -A -p <OPEN_PORTS> <TARGET>
```

## Nmap Command Reference

### Port Scanning

```bash
# Top ports (fast)
nmap --top-ports 100 -sV <TARGET>

# All ports (thorough)
nmap -p- -sV <TARGET>

# Specific ports
nmap -p 21,22,80,443,8080 -sV <TARGET>

# UDP scan (slow, use carefully)
nmap -sU --top-ports 20 <TARGET>
```

### Service Detection

```bash
# Version detection
nmap -sV --version-intensity 5 <TARGET>

# Default scripts
nmap -sC <TARGET>

# Aggressive (OS detect + scripts + traceroute)
nmap -A <TARGET>
```

### Stealth Options

```bash
# Slow scan (avoid detection)
nmap -sS -T2 --max-rate 10 <TARGET>

# Fragmented packets
nmap -f -sV <TARGET>

# Decoy scan
nmap -D RND:5 -sV <TARGET>
```

### Output Formats

```bash
# All formats
nmap -oA scan_results <TARGET>

# Grepable (for parsing)
nmap -oG scan_results.gnmap <TARGET>

# XML (for tooling)
nmap -oX scan_results.xml <TARGET>
```

## Web Directory Busting

```bash
# gobuster (common wordlist)
gobuster dir -u http://<TARGET>/ -w /usr/share/wordlists/dirb/common.txt

# gobuster with extensions
gobuster dir -u http://<TARGET>/ -w /usr/share/wordlists/dirb/common.txt -x php,html,txt

# feroxbuster (recursive)
feroxbuster -u http://<TARGET>/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

# ffuf (virtual host fuzzing)
ffuf -u http://<FUZZ>.target.local/ -H "Host: FUZZ.target.local" -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt
```

## Service-Specific Enumeration

### HTTP/HTTPS

```bash
# Basic recon
nmap -sV -p 80,443 --script http-enum,http-title,http-headers <TARGET>

# Technology fingerprint
whatweb http://<TARGET>

# Nikto scan
nikto -h http://<TARGET>
```

### SMB

```bash
# List shares
smbclient -L //<TARGET> -N

# Enumerate with enum4linux
enum4linux -a <TARGET>

# Check anonymous access
smbclient //<TARGET>/anonymous -N
```

### FTP

```bash
# Check anonymous login
ftp <TARGET>
# Try: anonymous / anonymous

# Nmap FTP scripts
nmap -p 21 --script ftp-anon,ftp-bounce,ftp-syst <TARGET>
```

### SSH

```bash
# Banner grab
nc <TARGET> 22

# Nmap SSH scripts
nmap -p 22 --script ssh-auth-methods,ssh-hostkey <TARGET>
```

## Output

Save all scan results for the vuln analysis phase:

```bash
mkdir -p engagements/<target>/enum/
nmap -oA engagements/<target>/enum/enum-<target>-$(date +%Y%m%d) <TARGET>
```

Document findings in `engagements/<target>/enum/` following the workspace engagement structure. The orchestrator will specify the target name. Preserve original filenames. NEVER create ad-hoc directories.
- Open ports with service/version info
- Discovered directories/endpoints
- Anonymous access findings
- Interesting banner grabs
