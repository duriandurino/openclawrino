---
name: recon
description: "Passive reconnaissance, OSINT gathering, and DNS analysis for penetration testing. Use when: user asks to recon a target, enumerate subdomains, look up DNS records, search Shodan for a host, gather OSINT, check WHOIS ownership, or fingerprint services passively. NOT for: active scanning or port scanning (use enum skill), vulnerability analysis (use vuln skill), or exploitation (use exploit skill)."
metadata: { "openclaw": { "emoji": "🔍", "requires": { "bins": ["dig", "whois", "curl"] } } }
---

# Recon Skill

Passive reconnaissance and OSINT gathering. No active probing — this phase is about collecting information without touching the target.

## When to Use

✅ **USE this skill when:**
- "Recon this IP/domain" — full passive recon workflow
- "Find subdomains for target.local" — DNS enumeration
- "Check DNS records for this domain" — A, AAAA, MX, TXT, NS lookups
- "Search Shodan for 192.168.1.1" — Internet-connected device search
- "Who owns this domain?" — WHOIS registration data
- "Gather OSINT on this target" — multi-source intel gathering
- "What services can we find on this host?" — passive service discovery

## When NOT to Use

❌ **DON'T use this skill when:**
- Active port scanning or service probing → use enum skill
- Vulnerability assessment → use vuln skill
- Exploitation or payload delivery → use exploit skill
- Physical access testing → document and escalate to main session

## Target Types

### IP Address (e.g., 192.168.1.105)

Run all passive checks — reverse DNS, WHOIS, Shodan, PTR records.

### Domain (e.g., example.com)

Run DNS enumeration, subdomain discovery, WHOIS, MX/TXT record analysis.

### Hostname (e.g., mytarget.local)

Resolve first, then run IP-based checks on resolved addresses.

## Automation-First Workflows

Prefer the standardized wrappers under `scripts/` before falling back to legacy scripts or ad-hoc commands.

### Recommended Default Profile

For common external web/domain recon:

```bash
python3 scripts/orchestration/run_recon_profile.py \
  --profile recon-external-web \
  --target <DOMAIN> \
  --engagement <target-name>
```

### Quick Recon (Single Target)

For a fast overview of one target:

```bash
# DNS baseline
python3 scripts/recon/dns/recon_dns_baseline.py --domain <DOMAIN> --engagement <target-name>

# WHOIS summary
scripts/recon/whois/recon_whois_summary.sh --domain <DOMAIN> --engagement <target-name>

# HTTP fingerprint
scripts/recon/web/recon_http_fingerprint.sh --target <DOMAIN> --engagement <target-name>
```

### Full Recon (Domain Target)

For a more complete passive domain workflow:

```bash
# Run the standard profile
python3 scripts/orchestration/run_recon_profile.py \
  --profile recon-external-web \
  --target <DOMAIN> \
  --engagement <target-name>

# Optional expanded subdomain collection
scripts/recon/subdomains/subdomain_collect.sh --domain <DOMAIN> --engagement <target-name>
```

### Legacy / Fallback Helpers

Use these when you need a more manual or specialized path:

```bash
python3 recon/scripts/dns_enum.py <DOMAIN>
python3 recon/scripts/whois_lookup.py <DOMAIN>
python3 recon/scripts/ct_lookup.py <DOMAIN>
python3 recon/scripts/shodan_query.py <TARGET>
```

### Network Range Recon

For scanning an IP range (passive only):

```bash
# Reverse DNS sweep
for ip in $(seq 1 254); do
  result=$(dig -x 192.168.1.$ip +short 2>/dev/null)
  [ -n "$result" ] && echo "192.168.1.$ip -> $result"
done
```

## Passive Service Discovery

Use public sources only — no direct connection to target:

```bash
# Shodan (requires SHODAN_API_KEY env var)
python3 scripts/shodan_query.py <TARGET>

# ViewDNS.info reverse IP (web-based, no direct contact)
curl -s "https://api.viewdns.info/reverseip/?host=<TARGET>&output=json"

# Nmap passive only (listens, doesn't probe)
# nmap --script broadcast-ping -sn <NETWORK>
```

## Output Format

Record all findings in a structured format for the reporting phase:

```
TARGET: <ip/domain>
DATE: <timestamp>
DNS RECORDS: <list>
SUBDOMAINS: <list>
WHOIS: <registrar, registrant, dates>
SHODAN: <open ports, services, banners>
OSINT NOTES: <any additional intel>
```

Store outputs in `engagements/<target>/recon/` following the workspace engagement structure. The orchestrator will specify the target name (e.g., `raspi5-lab`). Save findings as `<target>-recon-<date>.md` within that directory. NEVER create ad-hoc directories — always use the engagement structure.

## Notes

- All checks are passive — no packets sent to target unless explicitly authorized for active recon
- Shodan requires `SHODAN_API_KEY` environment variable
- CT log lookups (crt.sh) are free and don't require auth
- Reverse DNS on private IPs (192.168.x.x, 10.x.x.x) may return empty — that's normal
- WHOIS output may vary by TLD and registrar — parse case-by-case
