# Recon Reference — DNS Record Types & Sources

## DNS Record Types Quick Reference

| Record | Purpose | Example |
|--------|---------|---------|
| A | IPv4 address | `example.com -> 93.184.216.34` |
| AAAA | IPv6 address | `example.com -> 2606:2800:220:1:...` |
| MX | Mail servers (with priority) | `10 mail.example.com` |
| NS | Authoritative name servers | `ns1.example.com` |
| TXT | SPF, DKIM, DMARC, verification | `v=spf1 include:_spf.google.com ~all` |
| SOA | Zone authority (serial, refresh) | Start of Authority data |
| CNAME | Canonical name (alias) | `www.example.com -> example.com` |
| PTR | Reverse DNS (IP -> hostname) | `34.216.184.93.in-addr.arpa -> example.com` |

## OSINT Sources

### Free (No Auth)

| Source | What it provides | URL |
|--------|-----------------|-----|
| crt.sh | Certificate transparency logs | `https://crt.sh/?q=%.<domain>` |
| ViewDNS | Reverse IP, DNS records | `https://api.viewdns.info/` |
| DNSDumpster | DNS recon and research | `https://dnsdumpster.com/` |
| SecurityTrails | Historical DNS (limited free) | `https://securitytrails.com/` |
| WhoisXML API | WHOIS (limited free tier) | `https://whoisxmlapi.com/` |

### Requires API Key

| Source | Free Tier | What it provides |
|--------|-----------|-----------------|
| Shodan | Limited queries | Open ports, services, banners |
| Censys | Limited queries | Certificates, services, hosts |
| VirusTotal | 4 requests/min | Domain reputation, passive DNS |
| BinaryEdge | Limited | Internet scan data |

## Private Network Ranges

Private IPs won't have public DNS records. For internal recon:

| Range | CIDR |
|-------|------|
| 10.0.0.0 | 10.0.0.0/8 |
| 172.16.0.0 | 172.16.0.0/12 |
| 192.168.0.0 | 192.168.0.0/16 |
| 169.254.0.0 | 169.254.0.0/16 (link-local) |

Reverse DNS on private IPs often returns empty — use ARP scanning (enum skill) instead.
