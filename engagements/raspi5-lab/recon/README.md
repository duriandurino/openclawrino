# Phase 1: Reconnaissance

## What Goes Here
- Passive information gathering results
- OSINT findings (Shodan, Google dorking, social media)
- DNS enumeration results (dig, nslookup, amass)
- WHOIS lookups
- Network topology mapping
- ARP scan results
- Information about the target from public sources

## Common Commands
```bash
# DNS enumeration
dig target.local ANY
nslookup target.local

# Network discovery
arp-scan -l                    # Local network hosts
nmap -sn 192.168.1.0/24       # Ping sweep

# Passive recon
amass enum -passive -d target.local
```

## Checklist
- [ ] Target IP(s) identified
- [ ] Domain/subdomain enumeration
- [ ] DNS records collected
- [ ] Network topology mapped
- [ ] Public information gathered
- [ ] Notes documented
