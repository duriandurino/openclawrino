# Phase 2: Enumeration

## What Goes Here
- Port scan results (nmap)
- Service version detection
- OS fingerprinting
- Web directory brute-forcing
- SMB/NetBIOS enumeration
- SNMP enumeration
- Banner grabbing results

## Common Commands
```bash
# Full port scan
nmap -sC -sV -oA enum/full-scan <target>

# Aggressive scan (noisier)
nmap -A -T4 -p- <target>

# UDP top ports
nmap -sU --top-ports 100 <target>

# Web directory busting
gobuster dir -u http://<target> -w /usr/share/wordlists/dirb/common.txt

# SMB enumeration
enum4linux -a <target>
smbclient -L //<target> -N
```

## Checklist
- [ ] All TCP ports scanned
- [ ] Service versions identified
- [ ] OS detected
- [ ] Web directories enumerated
- [ ] Shares enumerated (if Windows/SMB)
- [ ] Results saved to files
