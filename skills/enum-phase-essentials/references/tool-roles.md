# Tool Roles in Enumeration

## Discovery tools
Use for breadth and candidate generation:
- Masscan
- fast Nmap host/port discovery
- Sublist3r / Amass for subdomain seeds
- Gobuster / ffuf / dirb for web content discovery

## Validation tools
Use for confidence and enrichment:
- Nmap `-sV` and targeted NSE scripts
- smbclient
- rpcclient
- protocol-aware HTTP checks
- Burp site map / authenticated mapping

## Rule
Fast tools generate candidates.
Validation tools decide what enters the real inventory.
