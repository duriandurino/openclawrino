# Enum Skill — Usage Examples (Phase 0)

## Example 1: Quick Port Scan
- **User:** "Scan this host for open ports"
- **Action:** Top-1000 port scan with service detection
- **Resources:** scripts/scan_enum.py --fast

## Example 2: Full Enumeration
- **User:** "Full service enumeration on 192.168.1.105"
- **Action:** All ports → service detection → script scan
- **Resources:** scripts/scan_enum.py --full

## Example 3: Web Directory Busting
- **User:** "Bust directories on this web server"
- **Action:** Gobuster with common wordlist + extensions
- **Resources:** scripts/web_enum.py

## Example 4: Service Fingerprint
- **User:** "What's running on port 8080?"
- **Action:** Detailed service version detection + script scan on specific port
- **Resources:** nmap -sV -sC -p 8080 <TARGET>

## Example 5: Subnet Scan
- **User:** "What hosts are alive in this subnet?"
- **Action:** Ping sweep across subnet
- **Resources:** nmap -sn <SUBNET>

## Example 6: SMB Enumeration
- **User:** "Check for anonymous SMB access on this host"
- **Action:** List shares, check anonymous access, enum4linux
- **Resources:** smbclient, enum4linux

## Example 7: Web Security Check
- **User:** "Check this web app for security headers and misconfig"
- **Action:** Security headers + whatweb fingerprint + robots.txt
- **Resources:** scripts/web_enum.py (skip bust)
