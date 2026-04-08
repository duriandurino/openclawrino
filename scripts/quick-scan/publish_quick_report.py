#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ACCOUNT = "hatlesswhite@gmail.com"
SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}

IGNORE_PATTERNS = [
    re.compile(r"apache\s+2\.4\.(49|50|51)", re.I),
    re.compile(r"cve-2021-41773", re.I),
    re.compile(r"cve-2021-42013", re.I),
]


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


def extract_section_lines(text: str, heading: str) -> list[str]:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return []
    start = text.find("\n", start)
    if start == -1:
        return []
    start += 1
    end = text.find("\n## ", start)
    block = text[start:end if end != -1 else None]
    return [line.strip() for line in block.splitlines() if line.strip()]


def extract_adaptive_context(report_info: dict) -> dict:
    text = report_info.get("text", "")
    return {
        "quick_scan": True,
        "quick_scan_sections": {
            "executive_summary": extract_section_lines(text, "Executive Summary"),
            "target_fingerprint": extract_section_lines(text, "Target Fingerprint"),
            "why_varied": extract_section_lines(text, "Why This Quick Scan Varied"),
            "recommended_next_action": extract_section_lines(text, "Recommended Next Action"),
            "quick_recommendations": extract_section_lines(text, "Recommendations"),
        },
    }


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


def likely_generic_false_positive(row: dict) -> bool:
    finding = row["finding"]
    lower = finding.lower()
    for pattern in IGNORE_PATTERNS:
        if pattern.search(finding):
            return True
    if "apache" in lower and any(token in lower for token in ["microsoft-httpapi", "httpapi", "kestrel"]):
        return True
    return False


def normalize_row(row: dict) -> dict | None:
    if likely_generic_false_positive(row):
        return None
    finding = row["finding"]
    lower = finding.lower()
    severity = row["severity"]
    confidence = row["confidence"]

    if "smb signing" in lower:
        severity = "High"
        confidence = "observed"
    elif "rdp" in lower and "metadata" in lower:
        severity = "Medium"
        confidence = "observed"
    elif "winrm" in lower or "5985" in lower:
        severity = "High"
        confidence = "observed"
    elif "mysql" in lower or "3306" in lower:
        severity = "Medium"
        confidence = "observed"
    elif "kestrel" in lower or "access-control-allow-origin: *" in lower:
        severity = "Medium"
        confidence = "observed"

    return {**row, "severity": severity, "confidence": confidence}


def remediation_for(finding: str, severity: str) -> str:
    lower = finding.lower()
    if "smb" in lower and "signing" in lower:
        return "Enforce SMB signing via Group Policy and restrict SMB exposure to trusted management segments only. Re-test with SMB security-mode checks after policy refresh."
    if "rdp" in lower:
        return "Restrict RDP to approved admin hosts, require MFA/VPN in front of remote access, and verify Network Level Authentication plus account lockout controls are enforced."
    if "winrm" in lower or "5985" in lower:
        return "Restrict WinRM to trusted administration networks, prefer HTTPS/5986 where possible, and verify only intended admin groups can use remote management."
    if "mysql" in lower or "3306" in lower:
        return "Restrict MySQL to approved application hosts only, disable public exposure where unnecessary, and verify account/network ACLs for the service."
    if "kestrel" in lower or "access-control-allow-origin: *" in lower:
        return "Review the exposed web/API service for intended authentication and CORS scope. Restrict allowed origins/methods and validate whether the service should be reachable from the current segment."
    if "missing " in lower:
        return "Apply the missing security control, then verify the header/control is present in a follow-up scan."
    if severity in ("Critical", "High"):
        return "Perform targeted validation immediately, patch or reconfigure the exposed service, and verify the issue is no longer reachable from the current network segment."
    return "Validate the observation manually, document whether it is expected, and harden the service if the exposure is unnecessary."


def hardening_for(finding: str) -> str:
    lower = finding.lower()
    if any(x in lower for x in ["rdp", "winrm", "smb"]):
        return "Segment management services away from user networks, monitor remote administration events centrally, and enforce least-privilege access for all admin paths."
    if "mysql" in lower:
        return "Keep database services on dedicated application/admin networks, monitor for unexpected remote logins, and document the expected client set."
    if any(x in lower for x in ["http", "kestrel", "api", "cors"]):
        return "Maintain a patching cadence for web-facing components, reduce banner leakage, and monitor for unexpected management endpoints on non-standard hosts."
    return "Keep exposed services minimized, monitor access patterns, and document expected network exposure so deviations stand out quickly."


def impact_for(severity: str, finding: str) -> str:
    if severity == "Critical":
        return "If this candidate is confirmed, it could allow severe compromise of the target service or remote code execution."
    if severity == "High":
        return "If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths."
    if severity == "Medium":
        return "This may reveal useful attacker information or weaken defensive posture if left unaddressed."
    return "This is currently a lower-confidence or lower-impact observation, but it may still aid attacker reconnaissance or chaining."


def title_for(finding: str) -> str:
    cleaned = finding.strip()
    if len(cleaned) <= 80:
        return cleaned
    short = cleaned[:80].rsplit(" ", 1)[0]
    return short.strip(" -:;,.	")


def build_findings_json(report_info: dict, rows: list[dict], adaptive_context: dict | None = None) -> dict:
    findings = []
    normalized_rows = [row for row in (normalize_row(r) for r in rows) if row is not None]
    for idx, row in enumerate(normalized_rows, start=1):
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
    payload = {"target": f"{report_info['target']} (Quick Scan)", "findings": findings, "enhancements": enhancements}
    if adaptive_context:
        payload.update(adaptive_context)
    return payload


def build_publish_env() -> dict:
    env = os.environ.copy()
    # Important: do not inject a fallback GOG_KEYRING_PASSWORD here.
    # If gog's file keyring was initialized with a different passphrase,
    # forcing a guessed default creates the repeated AES KeyUnwrap loop.
    return env


def explain_publish_failure(output: str) -> str:
    text = (output or "").strip()
    lower = text.lower()
    if "keyunwrap" in text or "integrity check failed" in lower:
        return (
            "Google publish failed because gog is trying to decrypt the saved Google token with the wrong "
            "file-keyring passphrase. This is why the auth issue keeps looping. Use the same stable "
            "GOG_KEYRING_PASSWORD that was used when gog auth was created, or reset the gog keyring/token "
            "and re-auth once with a known automation passphrase."
        )
    if "no tty available for keyring file backend passphrase prompt" in lower:
        return (
            "Google publish failed because gog uses the file keyring backend and this automation run has no TTY "
            "to enter the keyring passphrase. Set GOG_KEYRING_PASSWORD in the automation environment to the same "
            "passphrase used by gog auth, or re-auth gog with a known automation passphrase."
        )
    return text or "report generator publish failed"


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
    adaptive_context = extract_adaptive_context(report_info)
    findings_payload = build_findings_json(report_info, rows, adaptive_context)
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

    env = build_publish_env()
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise SystemExit(explain_publish_failure(result.stderr.strip() or result.stdout.strip()))

    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
