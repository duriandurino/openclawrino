#!/usr/bin/env python3
"""
Pentest Report Generator

Reads structured findings (JSON) and generates a formatted markdown report
with all required sections including security enhancement recommendations.

Usage:
    python3 generate_report.py --target <target> --findings <findings.json> --output <report.md>
    python3 generate_report.py --target <target> --findings <findings.json> --output <report.md> --upload-drive --gdrive-account hatlesswhite@gmail.com
    python3 generate_report.py --target <target> --findings <findings.json> --output <report.md> --create-slides --slides-title "Pentest Report"

Findings JSON format:
{
    "target": "192.168.1.105",
    "findings": [...],
    "enhancements": [...]
}
"""

import json
import argparse
import subprocess
from datetime import datetime


SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}


def run_gog(command):
    """Run a gog command and return parsed JSON when possible."""
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gog command failed")

    stdout = result.stdout.strip()
    if not stdout:
        return None

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return stdout


def upload_to_drive(path, account=None, parent=None):
    """Upload a file to Google Drive via gog."""
    cmd = ["gog", "drive", "upload", path, "--json"]
    if account:
        cmd.extend(["-a", account])
    if parent:
        cmd.extend(["--parent", parent])
    return run_gog(cmd)


def create_slides_from_markdown(title, content_file, account=None, parent=None):
    """Create Google Slides deck from markdown via gog."""
    cmd = ["gog", "slides", "create-from-markdown", title, "--content-file", content_file, "--json"]
    if account:
        cmd.extend(["-a", account])
    if parent:
        cmd.extend(["--parent", parent])
    return run_gog(cmd)


def generate_executive_summary(findings, enhancements):
    """Generate plain-language executive summary."""
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
    for f in findings:
        sev = f.get("severity", "Info")
        counts[sev] = counts.get(sev, 0) + 1

    total = len(findings)
    lines = []
    lines.append(f"This assessment identified **{total} findings** across the target:\n")
    lines.append(f"| Severity | Count |")
    lines.append(f"|----------|-------|")
    for sev in ["Critical", "High", "Medium", "Low", "Info"]:
        if counts[sev] > 0:
            lines.append(f"| {sev} | {counts[sev]} |")

    # Top 3 findings
    sorted_findings = sorted(findings, key=lambda x: SEVERITY_ORDER.get(x.get("severity", "Info"), 99))
    if sorted_findings:
        lines.append(f"\n### Priority Actions\n")
        for i, f in enumerate(sorted_findings[:3], 1):
            lines.append(f"{i}. **{f.get('title', 'Untitled')}** ({f.get('severity', 'N/A')}) — {f.get('impact', 'No impact description')[:120]}")

    return "\n".join(lines)


def format_finding(finding, index):
    """Format a single finding section."""
    lines = []
    fid = finding.get("id", f"VULN-{index:03d}")
    title = finding.get("title", "Untitled Finding")
    lines.append(f"### {fid} — {title}\n")
    lines.append(f"- **Severity:** {finding.get('severity', 'N/A')}")
    if finding.get("cvss"):
        lines.append(f"- **CVSS Score:** {finding['cvss']}")
    lines.append(f"- **Affected Target:** {finding.get('affected', 'N/A')}")
    lines.append(f"- **Description:** {finding.get('description', 'No description provided')}")
    lines.append(f"- **Evidence:** ```\n{finding.get('evidence', 'No evidence recorded')}\n```")
    lines.append(f"- **Impact:** {finding.get('impact', 'No impact assessment')}")
    lines.append(f"- **Remediation:** {finding.get('remediation', 'No remediation provided')}")

    if finding.get("hardening"):
        lines.append(f"- **Hardening:** {finding['hardening']}")

    if finding.get("references"):
        refs = finding["references"]
        if isinstance(refs, list):
            refs_str = ", ".join(refs)
        else:
            refs_str = str(refs)
        lines.append(f"- **References:** {refs_str}")

    return "\n".join(lines) + "\n"


def generate_report(data):
    """Generate the full report markdown."""
    target = data.get("target", "Unknown Target")
    findings = data.get("findings", [])
    enhancements = data.get("enhancements", [])
    date = datetime.now().strftime("%Y-%m-%d")

    lines = []

    # Title
    lines.append(f"# Penetration Test Report — {target}")
    lines.append(f"\n**Date:** {date}")
    lines.append(f"**Target:** {target}")
    lines.append(f"**Findings:** {len(findings)}\n")
    lines.append("---\n")

    # Executive Summary
    lines.append("## 1. Executive Summary\n")
    lines.append(generate_executive_summary(findings, enhancements))
    lines.append("\n---\n")

    # Methodology
    lines.append("## 2. Methodology\n")
    lines.append("The assessment followed a structured penetration testing methodology:\n")
    lines.append("1. **Reconnaissance** — Passive information gathering (DNS, WHOIS, OSINT)")
    lines.append("2. **Enumeration** — Active service discovery and fingerprinting")
    lines.append("3. **Vulnerability Analysis** — CVE matching and manual testing")
    lines.append("4. **Exploitation** — Proof-of-concept exploitation of confirmed vulnerabilities")
    lines.append("5. **Post-Exploitation** — Privilege escalation and impact assessment")
    lines.append("6. **Reporting** — Documented findings with remediation guidance\n")
    lines.append("---\n")

    # Findings
    lines.append("## 3. Findings\n")
    sorted_findings = sorted(findings, key=lambda x: SEVERITY_ORDER.get(x.get("severity", "Info"), 99))
    for i, finding in enumerate(sorted_findings, 1):
        lines.append(format_finding(finding, i))

    lines.append("---\n")

    # Security Enhancement Recommendations
    lines.append("## 4. Security Enhancement Recommendations\n")
    if enhancements:
        for enh in enhancements:
            cat = enh.get("category", "General")
            rec = enh.get("recommendation", "No recommendation provided")
            lines.append(f"### {cat}\n")
            lines.append(f"{rec}\n")
    else:
        lines.append("No additional enhancement recommendations identified.\n")
    lines.append("---\n")

    # Risk Summary Matrix
    lines.append("## 5. Risk Summary Matrix\n")
    lines.append("| ID | Finding | Severity | Remediation Priority |")
    lines.append("|----|---------|----------|---------------------|")
    for i, f in enumerate(sorted_findings, 1):
        fid = f.get("id", f"VULN-{i:03d}")
        title = f.get("title", "Untitled")
        sev = f.get("severity", "N/A")
        priority = "Immediate" if sev in ("Critical", "High") else "Scheduled" if sev == "Medium" else "Low Priority"
        lines.append(f"| {fid} | {title} | {sev} | {priority} |")
    lines.append("")

    # Appendices
    lines.append("---\n")
    lines.append("## 6. Appendices\n")
    lines.append("### A. Tools Used\n")
    lines.append("- nmap, masscan (enumeration)")
    lines.append("- Metasploit, custom scripts (exploitation)")
    lines.append("- Shodan, crt.sh (OSINT)")
    lines.append("- Burp Suite, curl (web testing)")
    lines.append("")
    lines.append("### B. Scope Boundaries\n")
    lines.append("All testing was conducted within the authorized scope. No denial-of-service attacks were performed without explicit permission.\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate pentest report from findings JSON")
    parser.add_argument("--target", required=True, help="Target name/IP for report header")
    parser.add_argument("--findings", required=True, help="Path to findings JSON file")
    parser.add_argument("--output", required=True, help="Output report path (markdown)")
    parser.add_argument("--upload-drive", action="store_true", help="Upload generated report to Google Drive via gog")
    parser.add_argument("--gdrive-account", help="Google account email for gog operations")
    parser.add_argument("--gdrive-parent", help="Optional parent Drive folder ID")
    parser.add_argument("--create-slides", action="store_true", help="Create a Google Slides deck from the generated markdown")
    parser.add_argument("--slides-title", help="Slides title (default: Penetration Test Report — <target>)")
    args = parser.parse_args()

    with open(args.findings) as f:
        data = json.load(f)

    report = generate_report(data)

    with open(args.output, "w") as f:
        f.write(report)

    print(f"[OK] Report generated: {args.output}")
    print(f"     Target: {args.target}")
    print(f"     Findings: {len(data.get('findings', []))}")
    print(f"     Enhancements: {len(data.get('enhancements', []))}")

    if args.upload_drive:
        try:
            upload_result = upload_to_drive(args.output, account=args.gdrive_account, parent=args.gdrive_parent)
            file_data = upload_result.get("file", upload_result) if isinstance(upload_result, dict) else upload_result
            if isinstance(file_data, dict):
                print(f"[OK] Drive upload: {file_data.get('name', args.output)}")
                if file_data.get("id"):
                    print(f"     Drive File ID: {file_data['id']}")
                if file_data.get("webViewLink"):
                    print(f"     Drive Link: {file_data['webViewLink']}")
            else:
                print(f"[OK] Drive upload completed: {file_data}")
        except Exception as e:
            print(f"[WARN] Drive upload failed: {e}")

    if args.create_slides:
        slides_title = args.slides_title or f"Penetration Test Report — {args.target}"
        try:
            slides_result = create_slides_from_markdown(slides_title, args.output, account=args.gdrive_account, parent=args.gdrive_parent)
            pres = None
            if isinstance(slides_result, dict):
                pres = slides_result.get("presentation") or slides_result.get("file") or slides_result
            if isinstance(pres, dict):
                print(f"[OK] Slides created: {pres.get('name', slides_title)}")
                if pres.get("presentationId"):
                    print(f"     Slides ID: {pres['presentationId']}")
                elif pres.get("id"):
                    print(f"     Slides ID: {pres['id']}")
                if pres.get("webViewLink"):
                    print(f"     Slides Link: {pres['webViewLink']}")
            else:
                print(f"[OK] Slides created: {slides_result}")
        except Exception as e:
            print(f"[WARN] Slides creation failed: {e}")


if __name__ == "__main__":
    main()
