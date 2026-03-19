---
name: reporting
description: "Generate penetration testing reports with findings, evidence, and actionable security enhancement recommendations. Use when: creating a pentest report, documenting vulnerabilities, generating findings summary, writing remediation guidance, or producing executive summaries after testing. Every finding MUST include severity, proof, remediation steps, and specific hardening recommendations. NOT for: note-taking during testing (use workspace notes), raw scan output (format in findings), or code review reports."
metadata: { "openclaw": { "emoji": "📋" } }
---

# Reporting Skill

Generate professional pentest reports. Every vulnerability reported must include clear remediation and hardening recommendations — the client should finish reading with an action plan, not just a list of problems.

## When to Use

✅ **USE this skill when:**
- "Generate the report for this pentest"
- "Write up the findings for target X"
- "Create an executive summary"
- "Document this vulnerability"
- "What's the remediation for CVE-2024-XXXX?"
- "Format my notes into a report"

## When NOT to Use

❌ **DON'T use this skill when:**
- Raw data collection → use the phase-specific skill
- During active testing (save notes to workspace instead)
- Code review reports → different format and audience

## Report Structure

Every report follows this structure. No exceptions.

```markdown
# Penetration Test Report — [Target]

## 1. Executive Summary
- Scope, dates, methodology overview
- Risk summary (Critical/High/Medium/Low counts)
- Top 3 findings in plain language

## 2. Methodology
- Phases executed (Recon → Enum → Vuln → Exploit → Post)
- Tools used
- Scope boundaries respected

## 3. Findings
For EACH vulnerability:

### [Finding ID] — [Title]
- **Severity:** Critical / High / Medium / Low / Info
- **CVSS Score:** X.X (if applicable)
- **Affected Target:** IP/hostname/service
- **Description:** What the vulnerability is
- **Evidence:** Screenshot reference, command output, or proof-of-concept
- **Impact:** What an attacker could achieve
- **Remediation:** Specific steps to fix (see "Remediation Standards" below)
- **Hardening:** Additional measures to prevent recurrence (see "Hardening Standards" below)
- **References:** CVE links, advisories, OWASP references

## 4. Security Enhancement Recommendations
Cross-cutting improvements that apply beyond individual findings.
See `references/enhancement_template.md` for categories.

## 5. Risk Summary Matrix
| Finding | Severity | Status | Remediation Priority |
|---------|----------|--------|---------------------|

## 6. Appendices
- Raw scan data (sanitized)
- Tool output summaries
- Network diagrams (if applicable)
```

## Remediation Standards

Every finding MUST have remediation guidance. Not vague — specific and actionable.

**Bad remediation:**
> "Fix this vulnerability"

**Good remediation:**
> "Upgrade OpenSSH from 8.2p1 to 9.5p1: `sudo apt update && sudo apt install openssh-server`. Verify with `ssh -V` after restart."

For each finding, provide:

1. **Immediate fix** — the specific action to close the vulnerability
2. **Verification step** — how to confirm the fix worked
3. **Rollback plan** — if the fix breaks something (when applicable)

## Hardening Standards

Beyond fixing the specific bug, recommend defenses that reduce the overall attack surface:

| Category | Examples |
|----------|---------|
| Access Control | Principle of least privilege, disable unused accounts, enforce MFA |
| Network | Firewall rules, network segmentation, disable unnecessary ports |
| System | Patch automation, kernel hardening, file integrity monitoring |
| Application | Input validation, security headers, CSRF protection |
| Monitoring | Log aggregation, alerting rules, IDS/IPS tuning |
| Backup | Encrypted backups, tested recovery procedures |

Every critical or high finding should include at least one hardening recommendation beyond the direct fix.

## Severity Classification

Use consistent severity ratings:

| Severity | CVSS Range | Criteria |
|----------|-----------|----------|
| Critical | 9.0–10.0 | Remote code exec, full system compromise, no user interaction |
| High | 7.0–8.9 | Privilege escalation, significant data exposure, auth bypass |
| Medium | 4.0–6.9 | Limited data exposure, requires specific conditions |
| Low | 0.1–3.9 | Information disclosure, defense-in-depth gaps |
| Info | 0.0 | Observations, recommendations, no direct vulnerability |

## Report Generation Workflow

### Step 1 — Gather Findings

```bash
# Collect all phase outputs from engagement directory
ls -la engagements/<target>/recon/
ls -la engagements/<target>/enum/
ls -la engagements/<target>/vuln/
ls -la engagements/<target>/exploit/
ls -la engagements/<target>/post-exploit/
cat engagements/<target>/recon/*.md
cat engagements/<target>/exploit/*.md
```

### Step 2 — Generate Report

```bash
python3 scripts/generate_report.py \
  --target <TARGET> \
  --findings engagements/<target>/reporting/findings-<target>.json \
  --output engagements/<target>/reporting/report-<target>-<date>.md
```

### Step 3 — Optional Google Drive / Slides Publish

If `gog` auth is working, the reporting agent may publish deliverables directly:

```bash
# Upload markdown report to Drive
python3 scripts/generate_report.py \
  --target <TARGET> \
  --findings engagements/<target>/reporting/findings-<target>.json \
  --output engagements/<target>/reporting/REPORT_FINAL_<date>.md \
  --upload-drive \
  --gdrive-account hatlesswhite@gmail.com

# Upload report and generate Google Slides in one step
python3 scripts/generate_report.py \
  --target <TARGET> \
  --findings engagements/<target>/reporting/findings-<target>.json \
  --output engagements/<target>/reporting/REPORT_FINAL_<date>.md \
  --upload-drive \
  --create-slides \
  --slides-title "Pentest Report — <TARGET>" \
  --gdrive-account hatlesswhite@gmail.com
```

Expected outputs:
- Drive file ID + web link for uploaded report
- Google Doc link for the published report
- Styled Google Slides link generated from a PPTX deck

### Step 4 — Review Checklist

Before delivering:
- [ ] Every finding has severity, evidence, remediation, and hardening
- [ ] Executive summary is understandable by non-technical readers
- [ ] Remediation steps are copy-pasteable or have exact commands
- [ ] No sensitive credentials or keys in the report
- [ ] Risk matrix covers all findings
- [ ] Security enhancement section addresses systemic issues

## Findings Format (JSON)

Feed structured findings into the report generator:

```json
{
  "target": "192.168.1.105",
  "findings": [
    {
      "id": "VULN-001",
      "title": "Outdated OpenSSH with CVE-2024-XXXX",
      "severity": "Critical",
      "cvss": 9.8,
      "affected": "192.168.1.105:22",
      "description": "OpenSSH 8.2p1 is vulnerable to...",
      "evidence": "ssh -V => OpenSSH_8.2p1...",
      "impact": "Remote code execution as root...",
      "remediation": "Upgrade to OpenSSH 9.5p1...",
      "hardening": "Disable password auth, enforce key-only...",
      "references": ["CVE-2024-XXXX", "https://..."]
    }
  ],
  "enhancements": [
    {
      "category": "Network Security",
      "recommendation": "Implement network segmentation..."
    }
  ]
}
```
