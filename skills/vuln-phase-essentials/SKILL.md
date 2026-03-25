---
name: vuln-phase-essentials
description: "Methodology and decision framework for the penetration testing vulnerability phase. Use when: validating scanner output, distinguishing confirmed vulnerabilities from hypotheses, explaining CVE/CWE/CVSS, prioritizing findings with KEV/EPSS/business context, guiding vuln-analysis workflow, or reinforcing evidence-backed reporting during the vulnerability phase. NOT for: initial recon or active enumeration, hands-on exploitation, post-exploitation, or replacing the specialized vuln skill's concrete checks."
---

# Vulnerability Phase Essentials

Use this skill to make vulnerability analysis defensible, evidence-backed, and report-ready. This is a **methodology layer** for the vulnerability phase, not a replacement for phase-specific scanning or exploitation skills.

## When to Use

✅ **USE this skill when:**
- "Analyze these scan results properly"
- "How do I validate this vulnerability?"
- "What's the difference between CVE, CWE, and CVSS?"
- "How should I prioritize these findings?"
- "Do the vuln phase methodically"
- "This scanner flagged something — how do we confirm it?"
- A sub-agent needs stronger vuln-analysis discipline before writing findings

## When NOT to Use

❌ **DON'T use this skill when:**
- Still discovering services or ports → use `enum`
- Running the concrete vulnerability-analysis task itself without methodology framing → use `vuln`
- Moving into exploit execution → use `exploit`
- Doing post-exploitation → use `post`
- Writing the final overall pentest report only → use `reporting`
- Teaching broad pentest fundamentals across all phases → use `pentest-essentials`

## Core Rules

1. **Scan output is hypothesis, not truth**
   - Unvalidated scanner results are not findings.
   - Treat every alert as a candidate until applicability and evidence are confirmed.

2. **Separate identity, weakness, and severity**
   - **CVE** = the specific vulnerability record
   - **CWE** = the underlying weakness category/root cause pattern
   - **CVSS** = technical severity model, not business priority by itself

3. **Validation before prioritization**
   - Do not rank what you have not confirmed.
   - First prove the issue applies to the exact target/version/configuration.

4. **Minimal safe proof**
   - Use the least invasive test that proves the vulnerability condition or impact.
   - If impact is already decisively proven, do not over-exploit just for drama.

5. **Risk is multi-factor**
   - Combine technical severity, exploitability signals, exposure, and business context.
   - CVSS-only prioritization is an anti-pattern.

## Phase Workflow

### Step 1 — Confirm Applicability
Check:
- exact service / component
- version or build
- deployment context
- reachable attack path
- config conditions required by the suspected issue

Output:
- applicable
- not applicable
- unknown, needs more evidence

### Step 2 — Validate the Vulnerable Condition
Use the least invasive method that proves the issue exists.

Examples:
```bash
# service/version correlation
searchsploit <service> <version>

# targeted Nmap checks after enum
nmap -sV --script vuln -p <ports> <target>

# NVD keyword search
curl -s "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=<service>+<version>&resultsPerPage=5"
```

Evidence to capture:
- exact command or request
- timestamp
- output file path
- observed vulnerable behavior
- why it maps to the claimed vulnerability

### Step 3 — Rule Out False Positives
Ask:
- does the affected version actually match?
- is the vulnerable feature/path enabled?
- can I reproduce the vulnerable condition manually?
- does a second method confirm the first signal?

If not, downgrade to:
- false positive
- not applicable
- unverified hypothesis

### Step 4 — Optional Safe PoC
Only do a PoC when necessary and authorized.

Rules:
- keep it non-destructive
- prefer read-only or low-impact validation
- stop once impact is sufficiently demonstrated
- document reversibility and cleanup if anything changed

### Step 5 — Prioritize
Use these factors together:
- validation status
- CVSS severity
- KEV presence
- EPSS probability
- internet/internal exposure
- asset criticality
- blast radius
- compensating controls
- remediation complexity

## CVE / CWE / CVSS Cheat Sheet

| Item | Meaning | Best use |
|------|---------|----------|
| CVE | Specific published vulnerability | Correlate findings, advisories, fixes |
| CWE | Weakness category / root cause | Explain why it exists and how to prevent recurrence |
| CVSS | Technical severity score | Communicate severity, not final business priority |

Use them together, not interchangeably.

## Prioritization Algorithm

Follow this order:
1. Is it validated and reproducible?
2. Is it actually applicable to this asset/version/config?
3. Is the asset exposed or reachable in the threat model?
4. Is there active exploitation evidence (KEV)?
5. What is the exploitation likelihood (EPSS or equivalent)?
6. What is the technical blast radius?
7. What is the business blast radius?
8. What compensating controls exist — and are they verified?
9. What response is appropriate: patch, mitigate, isolate, monitor?
10. What is the retest plan?

## Discovery Inputs to Use

High-signal manual inputs:
- attack-surface reasoning
- trust-boundary analysis
- config review
- targeted manual validation

Automated inputs:
- Nmap / NSE
- web DAST (Burp, ZAP)
- vuln scanners (e.g. OpenVAS/Nessus where available)
- SAST / code-aware analysis
- dependency / SBOM analysis
- container / IaC / repo scanning
- fuzzing in safe lab contexts

## Evidence Standards

A reportable vulnerability finding should include:
```text
Title
Affected Asset
Validation Status
Evidence
Applicable CVE(s)
Relevant CWE(s)
CVSS (if available)
Exploitability Notes
Business Context
Remediation
Hardening / Compensating Controls
Retest Guidance
```

Status vocabulary:
- **Verified** — directly reproduced / confirmed
- **Not Verified** — suspected but not confirmed
- **Not Applicable** — matched by tool, disproven on target
- **Hypothesis** — plausible candidate pending evidence

## Anti-Patterns

Avoid these mistakes:
- reporting scanner output as a finding without validation
- treating CVSS as the final priority order
- claiming a CVE based only on a product family name
- skipping business context in prioritization
- over-exploiting when a minimal PoC already proves impact
- mixing confirmed vulnerabilities and candidate CVEs without labeling

## Sub-Agent Guidance

When a pentest sub-agent uses this skill, it should:
- separate identification from validation
- write findings that a third party can reproduce
- mark CVEs as candidate vs confirmed explicitly
- include KEV/EPSS/business context when prioritizing
- hand off report-ready vulnerability sections, not loose scan dumps

## References

Load on demand:
- `references/examples.md` — concrete trigger phrases
- `references/prioritization-checklist.md` — vulnerability triage checklist
- `references/reporting-fields.md` — minimum fields for a report-ready vuln finding
- `references/cve-cwe-cvss.md` — compact reference and relationship map
