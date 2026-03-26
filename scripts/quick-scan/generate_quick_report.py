#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def latest_file(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def phase_excerpt(path: Path | None, title: str) -> list[str]:
    if not path or not path.exists():
        return [f"## {title}", "", "- No summary generated for this phase.", ""]
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    excerpt = text[:40]
    return [f"## {title}", "", *excerpt, ""]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate quick scan report from phase summaries")
    parser.add_argument("--engagement", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    base = ROOT / "engagements" / args.engagement
    reporting_dir = base / "quick-scan" / "reporting"
    reporting_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")

    recon_summary = latest_file(base / "recon", "RECON_SUMMARY_*.md") if (base / "recon").exists() else None
    enum_summary = latest_file(base / "enum", "ENUM_SUMMARY_*.md") if (base / "enum").exists() else None
    vuln_summary = latest_file(base / "vuln", "VULN_SUMMARY_*.md") if (base / "vuln").exists() else None

    quick_summary = reporting_dir / f"QUICK_SCAN_SUMMARY_{ts}.md"
    quick_report = reporting_dir / f"QUICK_SCAN_REPORT_{ts}.md"

    summary_lines = [
        f"# Quick Scan Summary — {args.target}",
        "",
        f"- Profile: `{args.profile}`",
        f"- Engagement: `{args.engagement}`",
        f"- Generated: `{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}`",
        "",
        "## Available Phase Outputs",
        f"- Recon: {'yes' if recon_summary else 'no'}",
        f"- Enum: {'yes' if enum_summary else 'no'}",
        f"- Vuln: {'yes' if vuln_summary else 'no'}",
        "",
        "## Assessment Note",
        "- This is a rapid triage output, not a full penetration test report.",
        "- Review candidate findings manually before treating them as confirmed vulnerabilities.",
        "",
    ]
    quick_summary.write_text("\n".join(summary_lines), encoding="utf-8")

    report_lines = [
        f"# Quick Security Scan Report — {args.target}",
        "",
        f"- Profile: `{args.profile}`",
        f"- Engagement: `{args.engagement}`",
        f"- Generated: `{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}`",
        "",
        "## Scope",
        "- Rapid triage / hygiene / exposure assessment",
        "- Safe or low-impact checks where possible",
        "- Not a substitute for a full pentest",
        "",
    ]
    report_lines.extend(phase_excerpt(recon_summary, "Recon Summary"))
    report_lines.extend(phase_excerpt(enum_summary, "Enumeration Summary"))
    report_lines.extend(phase_excerpt(vuln_summary, "Vulnerability Summary"))
    report_lines.extend([
        "## Recommendations",
        "",
        "- Validate any candidate findings manually.",
        "- Escalate to a full pentest workflow if exposed services, weak posture, or high-risk candidates are found.",
        "- Preserve the engagement artifacts for follow-up analysis.",
        "",
    ])
    quick_report.write_text("\n".join(report_lines), encoding="utf-8")

    print(quick_summary)
    print(quick_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
