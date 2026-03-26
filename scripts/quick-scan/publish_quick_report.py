#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ACCOUNT = "hatlesswhite@gmail.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}


def latest_file(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def read_report_info(report_path: Path) -> dict:
    text = report_path.read_text(encoding="utf-8", errors="ignore")
    info = {"text": text, "profile": "unknown", "mode": "unknown", "engagement": "unknown", "target": "unknown"}
    title_match = re.search(r"^#\s+Penetration Test Report \(Quick Scan\) — (.+)$", text, re.M)
    if title_match:
        info["target"] = title_match.group(1).strip()
    for key in ["Profile", "Mode", "Engagement"]:
        m = re.search(rf"^- {key}: `([^`]+)`$", text, re.M)
        if m:
            info[key.lower()] = m.group(1)
    return info


def parse_candidate_rows(text: str) -> list[dict]:
    rows = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "| Severity | Source | Confidence | Finding |":
            in_table = True
            continue
        if in_table and stripped.startswith("|---"):
            continue
        if in_table and stripped.startswith("|") and stripped.endswith("|"):
            parts = [p.strip().replace("\\|", "|") for p in stripped.strip("|").split("|")]
            if len(parts) == 4:
                sev, source, confidence, finding = parts
                if finding == "No notable candidate findings captured from current summaries.":
                    continue
                rows.append({"severity": sev, "source": source, "confidence": confidence, "finding": finding})
            continue
        if in_table and not stripped:
            break
    unique = []
    seen = set()
    for row in rows:
        key = (row["severity"], row["source"], row["finding"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    unique.sort(key=lambda x: (SEVERITY_ORDER.get(x["severity"], 99), x["finding"]))
    return unique


def remediation_for(finding: str, severity: str) -> str:
    lower = finding.lower()
    if "smb" in lower and "signing" in lower:
        return "Enforce SMB signing via Group Policy and restrict SMB exposure to trusted management segments only. Re-test with SMB security-mode checks after policy refresh."
    if "rdp" in lower:
        return "Restrict RDP to approved admin hosts, require MFA/VPN in front of remote access, and verify Network Level Authentication plus account lockout controls are enforced."
    if "winrm" in lower or "5985" in lower:
        return "Restrict WinRM to trusted administration networks, prefer HTTPS/5986 where possible, and verify only intended admin groups can use remote management."
    if "http" in lower and "apache" in lower:
        return "Manually validate the underlying product/version before acting on this candidate match. If confirmed, patch the affected service and re-test the specific issue path."
    if "missing " in lower:
        return "Apply the missing security control, then verify the header/control is present in a follow-up scan."
    if severity in ("Critical", "High"):
        return "Perform targeted validation immediately, patch or reconfigure the exposed service, and verify the issue is no longer reachable from the current network segment."
    return "Validate the observation manually, document whether it is expected, and harden the service if the exposure is unnecessary."


def hardening_for(finding: str) -> str:
    lower = finding.lower()
    if any(x in lower for x in ["rdp", "winrm", "smb"]):
        return "Segment management services away from user networks, monitor remote administration events centrally, and enforce least-privilege access for all admin paths."
    if "http" in lower or "apache" in lower:
        return "Maintain a patching cadence for web-facing components, reduce banner leakage, and monitor for unexpected management endpoints on non-standard hosts."
    return "Keep exposed services minimized, monitor access patterns, and document expected network exposure so deviations stand out quickly."


def impact_for(severity: str, finding: str) -> str:
    if severity == "Critical":
        return f"If this candidate is confirmed, it could allow severe compromise of the target service or remote code execution."
    if severity == "High":
        return f"If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative access paths."
    if severity == "Medium":
        return f"This may reveal useful attacker information or weaken defensive posture if left unaddressed."
    return f"This is currently a lower-confidence or lower-impact observation, but it may still aid attacker reconnaissance or chaining."


def title_for(finding: str) -> str:
    cleaned = finding.strip()
    if len(cleaned) <= 80:
        return cleaned
    short = cleaned[:80].rsplit(" ", 1)[0]
    return short.strip(" -:;,.\t")


def build_findings_json(report_info: dict, rows: list[dict]) -> dict:
    findings = []
    for idx, row in enumerate(rows, start=1):
        findings.append({
            "id": f"QS-{idx:03d}",
            "title": title_for(row["finding"]),
            "severity": row["severity"],
            "cvss": "N/A",
            "affected": report_info["target"],
            "description": f"Quick scan candidate from the {row['source']} phase: {row['finding']}",
            "evidence": f"Quick scan candidate finding ({row['confidence']}) from {row['source']}: {row['finding']}",
            "impact": impact_for(row["severity"], row["finding"]),
            "remediation": remediation_for(row["finding"], row["severity"]),
            "hardening": hardening_for(row["finding"]),
            "references": [f"Quick scan profile: {report_info['profile']}", f"Execution mode: {report_info['mode']}"]
        })

    enhancements = [
        {"category": "Exposure Management", "recommendation": "Use quick scan as triage only, then validate high-risk candidates manually before operational changes or client delivery."},
        {"category": "Administrative Surface Reduction", "recommendation": "Restrict exposed management services to trusted administration paths, segment them from user networks, and monitor for unexpected remote-access activity."},
        {"category": "Patch and Validation Workflow", "recommendation": "For candidate version-based matches, verify the real product/version before remediation, then patch and re-scan to confirm closure."},
    ]
    return {"target": f"{report_info['target']} (Quick Scan)", "findings": findings, "enhancements": enhancements}


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish latest quick scan via the main pentest report generator")
    parser.add_argument("--engagement", required=True)
    parser.add_argument("--account", default=DEFAULT_ACCOUNT)
    args = parser.parse_args()

    reporting_dir = ROOT / "engagements" / args.engagement / "quick-scan" / "reporting"
    if not reporting_dir.exists():
        raise SystemExit(f"reporting directory not found: {reporting_dir}")

    quick_report = latest_file(reporting_dir, "REPORT_QUICK_SCAN_*.md")
    if not quick_report:
        raise SystemExit("no quick scan markdown report found")

    report_info = read_report_info(quick_report)
    rows = parse_candidate_rows(report_info["text"])
    findings_payload = build_findings_json(report_info, rows)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    findings_path = reporting_dir / f"findings-quick-scan-{ts}.json"
    final_report_path = reporting_dir / f"REPORT_FINAL_QUICK_SCAN_{ts}.md"
    findings_path.write_text(json.dumps(findings_payload, indent=2) + "\n", encoding="utf-8")

    cmd = [
        "python3",
        str(ROOT / "reporting" / "scripts" / "generate_report.py"),
        "--target", f"{report_info['target']} (Quick Scan)",
        "--findings", str(findings_path),
        "--output", str(final_report_path),
        "--upload-drive",
        "--create-doc",
        "--create-slides",
        "--slides-title", f"Penetration Test Report (Quick Scan) — {report_info['target']}",
        "--gdrive-account", args.account,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip() or "report generator publish failed")

    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
