# Recon Skill — Usage Examples (Phase 0)

Concrete examples gathered for skill triggering and validation.

## Example 1: Full IP Recon
- **User:** "Do a recon on 192.168.1.105"
- **Action:** Reverse DNS → WHOIS → Shodan query → report findings
- **Resources:** scripts/whois_lookup.py, scripts/shodan_query.py

## Example 2: Subdomain Enumeration
- **User:** "Find all subdomains for mytarget.local"
- **Action:** DNS brute-force enumeration + CT log lookup
- **Resources:** scripts/dns_enum.py, scripts/ct_lookup.py

## Example 3: DNS Record Check
- **User:** "Check DNS records for this domain"
- **Action:** Query A, AAAA, MX, NS, TXT, SOA, CNAME records
- **Resources:** Core dig commands (no script needed)

## Example 4: Shodan Search
- **User:** "Search Shodan for open ports on 10.0.0.50"
- **Action:** Query Shodan API for host data (ports, services, banners)
- **Resources:** scripts/shodan_query.py

## Example 5: WHOIS Lookup
- **User:** "Who owns this domain?"
- **Action:** WHOIS lookup, extract registrar/dates/nameservers, redact PII
- **Resources:** scripts/whois_lookup.py

## Example 6: Passive OSINT
- **User:** "Gather OSINT on this target"
- **Action:** Multi-source: DNS + WHOIS + Shodan + CT logs
- **Resources:** All recon scripts

## Example 7: Network Range Sweep
- **User:** "What's on this network segment?"
- **Action:** Reverse DNS sweep across IP range (passive only)
- **Resources:** Core dig commands
