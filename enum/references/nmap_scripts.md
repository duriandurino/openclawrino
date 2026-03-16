# Nmap Script Reference — Useful NSE Scripts

## Discovery Scripts
| Script | Purpose |
|--------|---------|
| `broadcast-ping` | Discover hosts via broadcast ping |
| `llmnr-resolve` | LLMNR/NBT-NS discovery |
| `dns-brute` | DNS brute-force subdomains |
| `smb-enum-shares` | List SMB shares |
| `smb-enum-users` | Enumerate SMB users |

## Service Scripts
| Script | Purpose |
|--------|---------|
| `http-enum` | Enumerate web directories |
| `http-title` | Get page title from web services |
| `http-headers` | Display HTTP response headers |
| `http-methods` | Check allowed HTTP methods |
| `http-git` | Check for exposed .git directories |
| `ftp-anon` | Check for anonymous FTP login |
| `smb-vuln-ms17-010` | Check for EternalBlue |
| `ssh-auth-methods` | List SSH auth methods |
| `dns-recursion` | Check for open DNS recursion |

## Vulnerability Scripts
| Script | Purpose |
|--------|---------|
| `ssl-heartbleed` | Heartbleed detection |
| `ssl-poodle` | POODLE vulnerability |
| `http-shellshock` | Shellshock detection |
| `smb-vuln-ms17-010` | EternalBlue (MS17-010) |
| `rdp-vuln-ms12-020` | RDP DoS vulnerability |

## Usage Examples

```bash
# Run all default scripts
nmap -sC <TARGET>

# Run specific script category
nmap --script vuln <TARGET>

# Run specific script
nmap --script http-enum <TARGET>

# Run with arguments
nmap --script http-enum --script-args http-enum.basepath=/admin <TARGET>

# Script output to file
nmap -sC -oX scan.xml <TARGET>
```
