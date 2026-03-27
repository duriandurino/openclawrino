#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

IGNORED_PREFIXES = (
    "engagement:",
    "target:",
    "status:",
    "generated:",
    "profile:",
    "mode:",
    "steps executed:",
    "open ports / services:",
    "none captured by automation",
    "n/a in this phase",
    "access level achieved:",
    "method of access:",
    "credentials obtained:",
    "raw:",
    "parsed:",
    "summaries:",
)

IGNORED_CONTAINS = (
    "generated from standardized phase artifacts",
    "review and refine before treating as final handoff",
    "pivoted from:",
    "pivoted to:",
    "reason: n/a",
    "**overall:**",
    "**network findings:**",
    "**service identification:**",
    "**vulnerability assessment:**",
    "no significant structured findings captured by automation",
    "none captured",
)

POSITIVE_SIGNALS = (
    "cve-",
    "missing ",
    "exposed",
    "subdomain:",
    "title:",
    "whatweb:",
    "server banner",
    "banner:",
    "unauthenticated",
    "auth bypass",
    "weak credential",
    "open ",
)

BARE_PORT_SERVICE_PATTERNS = (
    "open rdp", "open smb", "open winrm", "open mysql", "open http",
    "open https", "open ssh", "open ftp", "open telnet",
    "rdp/", "smb/", "winrm/", "mysql/", "http/", "https/",
    "ssh ", "ftp ", "telnet ", "rdp ", "smb ", "winrm ",
    "port ", "open port", "service: ", "version: ",
    "3306", "3389", "5985", "5986", "445", "22",
)

MANAGEMENT_EXPOSURES = (
    ("3389/tcp", "RDP exposed", "High", "observed"),
    ("445/tcp", "SMB exposed", "High", "observed"),
    ("5985/tcp", "WinRM/HTTP management surface exposed", "High", "observed"),
    ("3306/tcp", "MySQL service exposed", "Medium", "observed"),
)


def latest_file(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def severity_for_line(line: str) -> str:
    text = line.lower()
    if any(token in text for token in ["rce", "critical", "exploit available", "unauthenticated"]):
        return "Critical"
    if any(token in text for token in ["cve-", "missing hsts", "missing csp"]):
        return "High"
    if any(token in text for token in ["smb", "rdp", "winrm"]):
        sev = "High"
    elif any(token in text for token in ["banner exposed", "server banner", "title:", "whatweb", "subdomain"]):
        return "Medium"
    elif any(token in text for token in ["info", "observed", "header", "robots"]):
        return "Low"
    else:
        return "Info"
    return sev


def is_candidate_line(content: str) -> bool:
    text = content.strip().lower()
    if not text:
        return False
    if text.startswith("**next phase:**") or text.startswith("**vector:**") or text.startswith("**reason:**"):
        return False
    if text.startswith(IGNORED_PREFIXES):
        return False
    if any(fragment in text for fragment in IGNORED_CONTAINS):
        return False
    if any(pat in text for pat in BARE_PORT_SERVICE_PATTERNS):
        return False
    if text.startswith("checked:"):
        return any(signal in text for signal in ("not vulnerable", "patched", "missing", "exposed", "access denied", "anonymous", "null session"))
    return any(signal in text for signal in POSITIVE_SIGNALS)


def extract_candidate_lines(path: Path | None) -> list[dict]:
    if not path or not path.exists():
        return []
    candidates = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line.startswith("-"):
            continue
        content = line.lstrip("- ").strip()
        if not is_candidate_line(content):
            continue
        severity = severity_for_line(content)
        confidence = "candidate"
        lowered = content.lower()
        if "not vulnerable" in lowered or "patched" in lowered:
            confidence = "observed-defensive"
        elif any(token in lowered for token in ["missing", "exposed", "cve-", "weak credential", "unauthenticated"]):
            confidence = "candidate"
        elif any(token in lowered for token in ["title:", "whatweb:", "subdomain:"]):
            confidence = "observed"
        candidates.append({"finding": content, "severity": severity, "confidence": confidence})
    return candidates


def extract_management_exposures(path: Path | None) -> list[dict]:
    if not path or not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    findings = []
    for indicator, finding, severity, confidence in MANAGEMENT_EXPOSURES:
        if indicator.lower() in text.lower():
            findings.append({"finding": finding, "severity": severity, "confidence": confidence})
    return findings


def executive_summary(profile: str, target: str, mode: str, counts: Counter, total: int) -> list[str]:
    lines = ["## Executive Summary", ""]
    if total == 0:
        lines.append(f"- Quick scan profile `{profile}` ran against `{target}` in `{mode}` mode and did not capture notable candidate findings from the current artifact set.")
        lines.append("- This suggests either a relatively clean exposed surface or limited visibility from low-impact triage checks.")
    else:
        highest = next((sev for sev in ["Critical", "High", "Medium", "Low", "Info"] if counts.get(sev)), "Info")
        lines.append(f"- Quick scan profile `{profile}` ran against `{target}` in `{mode}` mode and captured {total} meaningful candidate observations, with highest provisional severity `{highest}`.")
        lines.append("- These results are triage-oriented and should be manually validated before being treated as confirmed vulnerabilities.")
    lines.append("")
    return lines


def phase_excerpt(path: Path | None, title: str) -> list[str]:
    if not path or not path.exists():
        return [f"## {title}", "", "- No summary generated for this phase.", ""]
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    excerpt = text[:30]
    return [f"## {title}", "", *excerpt, ""]


def recommended_next_action(counts: Counter, has_recon: bool, has_enum: bool, has_vuln: bool) -> list[str]:
    lines = ["## Recommended Next Action", ""]
    if counts.get("Critical") or counts.get("High"):
        lines.append("- Escalate to a full pentest workflow or targeted manual validation immediately for the highest-risk candidates.")
    elif counts.get("Medium"):
        lines.append("- Perform focused manual validation on the medium-severity candidates and expand service-specific enumeration where relevant.")
    elif has_enum or has_vuln:
        lines.append("- Preserve artifacts and consider a deeper follow-up scan if this target matters operationally.")
    else:
        lines.append("- If higher confidence is needed, rerun with a broader profile or move to a full pentest workflow.")
    lines.append("")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate quick scan report from phase summaries")
    parser.add_argument("--engagement", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--mode", default="safe")
    parser.add_argument("--steps", default="0")
    args = parser.parse_args()

    base = ROOT / "engagements" / args.engagement
    reporting_dir = base / "quick-scan" / "reporting"
    reporting_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")

    recon_summary = latest_file(base / "recon", "RECON_SUMMARY_*.md") if (base / "recon").exists() else None
    enum_summary = latest_file(base / "enum", "ENUM_SUMMARY_*.md") if (base / "enum").exists() else None
    vuln_summary = latest_file(base / "vuln", "VULN_SUMMARY_*.md") if (base / "vuln").exists() else None

    candidates = []
    for source_name, summary in [("recon", recon_summary), ("enum", enum_summary), ("vuln", vuln_summary)]:
        for item in extract_candidate_lines(summary):
            item["source"] = source_name
            candidates.append(item)

    for item in extract_management_exposures(enum_summary):
        item["source"] = "enum"
        candidates.append(item)

    unique = []
    seen = set()
    for item in candidates:
        key = (item["finding"], item["source"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    candidates = unique
    counts = Counter(item["severity"] for item in candidates)

    executive_summary_path = reporting_dir / f"EXECUTIVE_SUMMARY_QUICK_SCAN_{ts}.md"
    report_path = reporting_dir / f"REPORT_QUICK_SCAN_{ts}.md"

    summary_lines = [
        f"# Executive Summary (Quick Scan) — {args.target}",
        "",
        f"- Profile: `{args.profile}`",
        f"- Mode: `{args.mode}`",
        f"- Engagement: `{args.engagement}`",
        f"- Steps executed: `{args.steps}`",
        f"- Generated: `{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}`",
        "",
        "## Severity Snapshot",
        f"- Critical: {counts.get('Critical', 0)}",
        f"- High: {counts.get('High', 0)}",
        f"- Medium: {counts.get('Medium', 0)}",
        f"- Low: {counts.get('Low', 0)}",
        f"- Info: {counts.get('Info', 0)}",
        "",
        "## Assessment Note",
        "- This is a rapid triage output presented in pentest-report style.",
        "- Review candidate findings manually before treating them as confirmed vulnerabilities.",
        "",
    ]
    executive_summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    report_lines = [
        f"# Penetration Test Report (Quick Scan) — {args.target}",
        "",
        f"- Profile: `{args.profile}`",
        f"- Mode: `{args.mode}`",
        f"- Engagement: `{args.engagement}`",
        f"- Steps executed: `{args.steps}`",
        f"- Generated: `{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}`",
        "",
        "## Scope",
        "- Rapid triage / hygiene / exposure assessment",
        "- Safe or low-impact checks where possible unless a profile explicitly broadens coverage",
        "- This is not a substitute for a full pentest",
        "",
    ]
    report_lines.extend(executive_summary(args.profile, args.target, args.mode, counts, len(candidates)))
    report_lines.extend([
        "## Severity Buckets",
        "",
        f"- Critical: {counts.get('Critical', 0)}",
        f"- High: {counts.get('High', 0)}",
        f"- Medium: {counts.get('Medium', 0)}",
        f"- Low: {counts.get('Low', 0)}",
        f"- Info: {counts.get('Info', 0)}",
        "",
        "## Candidate Findings",
        "",
        "| Severity | Source | Confidence | Finding |",
        "|---|---|---|---|",
    ])
    if candidates:
        for item in candidates[:30]:
            safe_finding = item['finding'].replace('|', '\\|')
            report_lines.append(f"| {item['severity']} | {item['source']} | {item['confidence']} | {safe_finding} |")
    else:
        report_lines.append("| Info | none | none | No notable candidate findings captured from current summaries. |")
    report_lines.extend(["", "## What Needs Manual Validation", ""])
    if candidates:
        report_lines.extend([f"- Validate: {item['finding']}" for item in candidates[:12]])
    else:
        report_lines.append("- Validate whether the limited findings are due to clean posture, low-impact mode, or missing service visibility.")
    report_lines.append("")
    report_lines.extend(recommended_next_action(counts, recon_summary is not None, enum_summary is not None, vuln_summary is not None))
    report_lines.extend(phase_excerpt(recon_summary, "Recon Summary"))
    report_lines.extend(phase_excerpt(enum_summary, "Enumeration Summary"))
    report_lines.extend(phase_excerpt(vuln_summary, "Vulnerability Summary"))
    report_lines.extend([
        "## Recommendations",
        "",
        "- Validate candidate findings manually before escalation or reporting as confirmed issues.",
        "- Escalate to a full pentest workflow if exposed services, weak posture, or high-risk candidates are found.",
        "- Preserve engagement artifacts for follow-up analysis and retesting.",
        "",
    ])
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(executive_summary_path)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
