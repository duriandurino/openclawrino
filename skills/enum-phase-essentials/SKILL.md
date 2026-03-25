---
name: enum-phase-essentials
description: "Methodology and decision framework for the penetration testing enumeration phase. Use when: optimizing enumeration for speed with high confidence, structuring host/service/web/AD enumeration workflows, reducing false positives, deciding between Masscan and Nmap roles, tuning scan rates/retries/version detection, or reinforcing evidence-backed service inventory creation. NOT for: passive recon only, vulnerability analysis, exploitation, or replacing the specialized enum skill's concrete probing tasks."
---

# Enumeration Phase Essentials

Use this skill to make enumeration fast, evidence-backed, and operationally disciplined. This is a **methodology layer** for the enumeration phase, not a replacement for concrete enumeration tools.

## When to Use

✅ **USE this skill when:**
- "How do I enumerate faster without losing confidence?"
- "How should I structure enumeration?"
- "When should I use Masscan vs Nmap?"
- "How do I reduce enumeration false positives?"
- "How should I enumerate SMB/RPC/LDAP/HTTP correctly?"
- "How do I tune scan speed safely?"
- A sub-agent needs stronger enum-phase discipline before producing service inventory

## When NOT to Use

❌ **DON'T use this skill when:**
- Still doing passive recon / OSINT only → use `recon`
- Running the actual active enumeration task without methodology framing → use `enum`
- Moving into vulnerability analysis → use `vuln`
- Executing exploitation → use `exploit`
- Teaching broad whole-pentest fundamentals → use `pentest-essentials`
- Writing final reporting only → use `reporting`

## Core Rules

1. **Breadth first, depth second**
   - Use a two-stage pipeline: fast discovery, then targeted validation/enrichment.
   - Do not do deep fingerprinting on everything.

2. **Candidate ≠ confirmed service**
   - High-speed discovery only produces candidates.
   - A primary inventory entry should be validated by version detection, protocol handshake, or another higher-layer signal.

3. **Tuning is part of methodology**
   - Rate, retries, version intensity, and concurrency are not cosmetic.
   - Aggressive settings can save time or destroy accuracy; track the tradeoff intentionally.

4. **Measure accuracy, not just speed**
   - False positives, rescans, and rework are real costs.
   - Enumeration quality should be visible in the evidence and the handoff.

5. **Protocol-specific depth only after trigger**
   - SMB/RPC/LDAP/HTTP deep dives happen after ports/services justify them.
   - Avoid wasting traffic on blind, all-purpose deep probing.

## Overall Workflow

Follow this funnel:
1. scope + rules of engagement
2. target list hygiene
3. passive / low-noise seeding where helpful
4. fast host and port discovery
5. targeted validation and service enrichment
6. protocol-specific deep dives
7. correlation, dedupe, confidence scoring
8. selective rescan on uncertain items
9. prioritized service inventory for the next phase

## Two-Stage Pipeline

### Stage 1 — Fast Discovery
Use fast tools and reduced scope to generate candidates.

Examples:
```bash
# List sanity before touching targets
nmap -sL -iL targets.txt

# Host discovery
nmap -sn -iL targets.txt -oA out/pingsweep

# Fast candidate generation with Masscan
masscan -iL targets.txt -p 22,80,443,445,3389,5985,5986 -oJ out/masscan.json --rate 5000
```

Output:
- candidate live hosts
- candidate open ports
- target sets worth deeper work

### Stage 2 — Targeted Validation
Validate only what discovery justified.

Examples:
```bash
nmap -sS -sV -T4 --open -iL live_hosts.txt -p 22,80,443,445,3389,5985,5986 -oA out/nmap_validate
nmap -sS -sV --version-light -T4 --open -iL live_hosts.txt -p 80,443,445 -oA out/nmap_vlight
```

Output:
- validated service inventory
- version/behavior evidence
- deep-dive trigger list

## Network and Host Enumeration

### Target Hygiene
Validate your target assumptions first.

Examples:
```bash
nmap -sL -iL targets.txt
```

Why it matters:
- catches scope mistakes early
- prevents scanning the wrong assets
- keeps exclusions explicit

### Host Discovery
Match the method to the environment.

Examples:
```bash
nmap -sn -iL targets.txt -oA out/pingsweep
nmap -Pn -iL targets.txt -p 80,443,445 -oA out/no_ping_top_ports
```

Rule of thumb:
- local Ethernet often favors ARP/neighbor-based discovery
- routed or filtered networks may need TCP-based assumptions and later validation

### Host Characterization
Do OS work selectively.

Examples:
```bash
nmap -O --osscan-limit -iL priority_hosts.txt -oA out/os_detect
```

Rule:
- only do host/OS fingerprinting where it is likely to matter and likely to succeed

## Service Enumeration

Treat service enumeration as evidence collection, not decoration.

### Version Detection Strategy
Examples:
```bash
# Triage
nmap -sS -sV --version-light -T4 --open -iL live_hosts.txt -oA out/nmap_vlight

# Deeper validation on important assets
nmap -sS -sV --version-all -T3 --open -iL priority_hosts.txt -oA out/nmap_vall
```

Rule:
- light/moderate first
- heavy only for critical services, ambiguous signatures, or exploit planning

## Protocol Deep Dives

### SMB / RPC / Windows
Use service-triggered enrichment only after SMB/RPC evidence exists.

Examples:
```bash
nmap -p 445,139 --script smb-os-discovery,smb-enum-shares,smb-enum-users -iL smb_hosts.txt -oA out/nmap_smb_scripts
enum4linux -a <IP>
smbclient -L //<IP>/ -N
rpcclient -U "" -N <IP> -c "lsaquery; enumdomusers; enumdomgroups"
```

### LDAP / AD
Trigger only when directory-service ports or context justify it.

Examples:
```text
use auxiliary/gather/ldap_query
run rhost=<DC_IP> username=<USER@DOMAIN> password=<PASS> action=ENUM_ACCOUNTS
```

## Web Enumeration

Web enum needs mapping first, then content discovery, then filtering.

### CLI Content Discovery
Examples:
```bash
gobuster dir -u https://<HOST>/ -w <WORDLIST> -x php,html,js,txt -s 200,204,301,302,307,401,403
dirb https://<HOST>/ /usr/share/wordlists/dirb/common.txt
ffuf -u https://<HOST>/FUZZ -w <WORDLIST> -t 40 -rate 200 -mc all -fc 404 -fs 0
```

### Server Checks
Examples:
```bash
nikto -h https://<HOST>
nikto -h https://<HOST> -Tuning b3
```

Rules:
- map before brute-forcing when possible
- filter soft-404 and uniform redirects aggressively
- validate discovered endpoints with spot checks

## Accuracy Gates

A finding enters the enum inventory only if one of these is true:
- Nmap version detection provides a strong service match
- a protocol-specific client confirms the behavior
- a web endpoint survives anti-noise filtering and spot-check validation
- repeated scans converge on the same answer

If not, label it as:
- candidate
- uncertain
- needs recheck

## Tuning Guidance

Track these knobs intentionally:
- discovery rate
- retries
- timing template
- version intensity
- host grouping / concurrency
- request rate and filters for web fuzzing

Rules:
- faster is useful only if you can still trust the results
- record tuning changes in the evidence notes
- if you crank rate or reduce retries, plan validation or selective rescans

## False-Positive Reduction

Use these methods:
- correlate two different signals
- validate with a protocol client when possible
- use `--reason` or targeted traces on ambiguous Nmap results
- filter web responses by status, size, words, lines, or timing
- rescan uncertain items rather than pretending certainty

## Enumeration KPIs

Track at least:
- time-to-first-validated-inventory
- coverage of scope / port set
- false-positive rate
- rework ratio
- percent of candidate ports later validated

## Report-Ready Enum Output

Your enum handoff should include:
```text
Target(s)
Discovery method used
Validation method used
Confirmed hosts
Confirmed services and ports
Versions / banners / protocol notes
Uncertain items needing recheck
Evidence file paths
Next-phase hypotheses
```

## Anti-Patterns

Avoid:
- deep scanning everything equally
- treating Masscan output as final truth
- using aggressive Nmap timing without measuring accuracy impact
- reporting web paths without anti-soft-404 filtering
- skipping protocol-level validation for SMB/RPC/LDAP conclusions
- creating giant unstructured scan dumps without a validated inventory

## Sub-Agent Guidance

When a pentest sub-agent uses this skill, it should:
- separate discovery from validation
- use fast-then-accurate funnels
- justify protocol-specific deep dives from service evidence
- write enum handoffs that are clean enough for vuln analysis to consume directly
- label uncertain results clearly instead of forcing confidence

## References

Load on demand:
- `references/examples.md` — trigger phrases and expected use
- `references/tool-roles.md` — Masscan/Nmap/web/SMB tool role guidance
- `references/accuracy-gates.md` — validation rules before inventory inclusion
- `references/kpis.md` — measurable enumeration KPIs
