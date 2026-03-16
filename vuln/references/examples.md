# Vuln Skill — Usage Examples (Phase 0)

## Example 1: Check Vulnerabilities on Host
- **User:** "Check for vulnerabilities on 192.168.1.105"
- **Action:** Read enum results, run NSE vuln scripts, research CVEs
- **Resources:** scripts/cve_lookup.py --file, nmap --script vuln

## Example 2: Research Specific Service
- **User:** "What CVEs affect OpenSSH 8.2p1?"
- **Action:** searchsploit + NVD API lookup for that version
- **Resources:** scripts/cve_lookup.py --service openssh --version "8.2p1"

## Example 3: Analyze Scan Results
- **User:** "Analyze these scan results for known weaknesses"
- **Action:** Parse enum JSON output, map each service to known CVEs
- **Resources:** scripts/cve_lookup.py --file loot/enum-<target>-<date>.json

## Example 4: Check Exploitability
- **User:** "Is this service exploitable?"
- **Action:** searchsploit for public exploits, check if target version matches
- **Resources:** searchsploit, scripts/cve_lookup.py

## Example 5: Specific CVE Lookup
- **User:** "Tell me about CVE-2024-6387"
- **Action:** Query NVD for full CVE details, CVSS score, affected versions
- **Resources:** scripts/cve_lookup.py --cve CVE-2024-6387

## Example 6: Risk Assessment
- **User:** "What's the risk of running vsftpd 3.0.3?"
- **Action:** Search for known CVEs, check if any public exploits exist, assess CVSS
- **Resources:** scripts/cve_lookup.py --service vsftpd --version "3.0.3"
