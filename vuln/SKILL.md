---
name: vuln
description: "Vulnerability analysis and CVE matching for penetration testing. Use when: user asks to check for vulnerabilities, match CVEs against service versions, analyze scan results for weaknesses, research exploitability, assess risk of discovered services, or identify known vulnerabilities. This is the analysis phase — no exploitation yet. NOT for: active scanning (use enum skill), exploitation (use exploit skill), or post-exploitation (use post skill)."
metadata: { "openclaw": { "emoji": "🎯", "requires": { "bins": ["nmap"] } } }
---

# Vulnerability Analysis Skill

Analyze discovered services and versions against known CVEs. Identify what's exploitable before attempting exploitation.

## When to Use

✅ **USE this skill when:**
- "Check for vulnerabilities on this host"
- "What CVEs affect OpenSSH 8.2p1?"
- "Analyze these scan results for known weaknesses"
- "Is this service exploitable?"
- "Run vulnerability scripts against this target"
- "Research exploitability of what we found"
- "What's the risk of running this version?"

## When NOT to Use

❌ **DON'T use this skill when:**
- Still gathering service info → use enum skill
- Ready to exploit → use exploit skill
- Post-compromise work → use post skill
- Passive recon → use recon skill

## Workflow

### Step 1 — Review Enum Results

Start from what enumeration found:

```bash
# Read enum results
cat loot/enum-<target>-*.json
cat loot/enum-<target>-detail-*.nmap
```

Extract the service/version pairs for analysis.

### Step 2 — Nmap Vulnerability Scripts

Run targeted nmap NSE vulnerability scripts:

```bash
# All vuln scripts against discovered ports
nmap -sV --script vuln -p <PORTS> <TARGET>

# Specific vulnerability checks
nmap -sV --script ssl-heartbleed,ssl-poodle,http-shellshock,smb-vuln-ms17-010 -p <PORTS> <TARGET>

# HTTP vulnerability scripts
nmap -sV --script http-vuln*,http-sql-injection,http-xss* -p 80,443,8080 <TARGET>
```

### Step 3 — Searchsploit / CVE Research

```bash
# Search for exploits by service/version
searchsploit openssh 8.2
searchsploit vsftpd 3.0.3

# Get exploit details
searchsploit -x 49757

# Mirror exploit to loot for review
searchsploit -m 49757 --loot
```

### Step 4 — Online CVE Databases

```bash
# NVD API (no key needed for basic queries)
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=openssh+8.2&resultsPerPage=5"

# Vulners API (free, good for quick lookups)
curl -s "https://vulners.com/api/v3/search/id/?id=CVE-2024-6387"
```

### Step 5 — Risk Assessment

For each identified vulnerability, assess:

| Factor | Question |
|--------|----------|
| **Exploitability** | Is there a public exploit? How complex? |
| **Access level** | What access is needed? (local, remote, unauthenticated) |
| **Impact** | What's the worst-case outcome? (RCE, DoS, info leak) |
| **Affected version** | Is the target version confirmed vulnerable? |
| **Mitigations** | Are there any mitigating controls in place? |

## CVE Matching from Versions

When a service version is identified, cross-reference with known CVEs:

```bash
# Automated version-to-CVE mapping
python3 scripts/cve_lookup.py --service openssh --version "8.2p1"
python3 scripts/cve_lookup.py --service vsftpd --version "3.0.3"
python3 scripts/cve_lookup.py --file loot/enum-<target>-*.json
```

## Vulnerability Classification

| Category | Examples |
|----------|---------|
| Remote Code Execution | CVE-2024-6387 (regreSSHion), Shellshock |
| Authentication Bypass | Default creds, auth bypass in web apps |
| Privilege Escalation | Local privesc via SUID, kernel exploits |
| Information Disclosure | Directory traversal, info leak in headers |
| Denial of Service | Network-level DoS, resource exhaustion |
| Injection | SQLi, command injection, XSS |

## NSE Script Categories

| Category | What it checks |
|----------|---------------|
| `vuln` | Known CVEs with PoC |
| `auth` | Authentication issues |
| `default` | Default settings/credentials |
| `intrusive` | May disrupt service |
| `safe` | Non-intrusive checks |

## Output Format

Document findings in `loot/vuln-<target>-<date>.md`:

```markdown
# Vulnerability Analysis — <target>

## Services Analyzed
| Port | Service | Version | Status |
|------|---------|---------|--------|
| 22 | ssh | OpenSSH 8.2p1 | VULNERABLE — CVE-2024-6387 |
| 80 | http | Apache 2.4.41 | OK (but missing headers) |

## Findings
### CVE-2024-6387 — regreSSHion
- **CVSS:** 9.8 (Critical)
- **Affected:** OpenSSH 8.2p1-9.6p1
- **Exploit:** Public, reliable RCE as root
- **Exploitable:** YES
- **Notes:** Signal handler race condition, unauthenticated RCE
```

## Decision Tree

```
Service + Version identified
    │
    ├── searchsploit returns results?
    │     ├── YES → Document CVE, check exploit availability
    │     └── NO → Check NSE vuln scripts
    │
    ├── NSE vuln scripts flag it?
    │     ├── YES → Confirm with CVE database
    │     └── NO → Check version against NVD
    │
    └── Any confirmed vulns?
          ├── YES → Prioritize for exploitation (next phase)
          └── NO → Document as "no known CVEs" — note for manual testing
```
