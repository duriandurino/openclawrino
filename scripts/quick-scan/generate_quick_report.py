#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path
import json

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


def load_fingerprint(base: Path) -> dict:
    path = base / "quick-scan" / "fingerprint.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


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


def classify_target_story(fp: dict) -> tuple[str, list[str], list[str]]:
    frameworks = set(fp.get("frameworks", []))
    deployments = set(fp.get("deployments", []))
    surfaces = set(fp.get("surfaces", []))
    traits = set(fp.get("traits", []))
    titles = fp.get("titles", [])
    title_blob = " ".join(titles).lower()
    target_blob = str(fp.get("target", "")).lower()

    story = "general web application"
    emphasis: list[str] = []
    recommendations: list[str] = []
    qualifiers: list[str] = []

    if "nextjs" in frameworks and "vercel" in deployments:
        story = "Vercel-hosted Next.js application"
        emphasis.append("deployment metadata, response header posture, and frontend routing clues")
        recommendations.append("Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.")
    elif "vercel" in deployments:
        story = "Vercel-hosted web application"
        emphasis.append("deployment-layer clues and externally visible response behavior")
        recommendations.append("Review Vercel edge/header configuration to ensure baseline browser protections are applied consistently.")

    if "auth-facing" in traits:
        story = f"auth-facing {story}"
        emphasis.append("authentication surface and access-control-adjacent behavior")
        recommendations.append("Prioritize login, session, and access-control review if this target is important beyond public brochureware.")
    if "ssr-or-hybrid" in traits:
        emphasis.append("server-rendered route behavior and cache/header consistency across rendered pages")
    if "spa-or-js-heavy" in traits:
        emphasis.append("client-side behavior and browser-facing hardening")
    if "api-docs" in surfaces or "graphql" in surfaces:
        emphasis.append("API exposure clues rather than only page presentation")
    if "redirect-response" in traits:
        emphasis.append("redirect behavior, canonical host handling, and edge routing consistency")
    if "portfolio-like" in traits or any(token in title_blob for token in ["portfolio", "engineer", "developer", "designer", "consultant"]):
        qualifiers.append("public portfolio-style surface")
        recommendations.append("Treat public profile and contact metadata as part of the exposed surface, especially if it influences impersonation, scraping, or social-engineering risk.")
    if "catalog-like" in traits or any(token in title_blob for token in ["book", "library", "catalog", "shop", "store", "market", "fair"]) or any(token in target_blob for token in ["book", "library", "catalog", "shop", "store", "market", "fair"]):
        qualifiers.append("public catalog or content-style surface")
        recommendations.append("Validate whether search, content, and image-delivery routes expose data or caching behavior beyond the intended public catalog experience.")
    if titles:
        recommendations.append(f"Use the discovered title/context ({titles[0]}) to decide whether this is primarily a marketing surface, operational app, or user-facing portal before prioritizing deeper testing.")

    if qualifiers:
        story = f"{story} serving as a {' and '.join(dict.fromkeys(qualifiers))}"

    emphasis = list(dict.fromkeys(emphasis))
    recommendations = list(dict.fromkeys(recommendations))
    return story, emphasis, recommendations


def describe_fingerprint(fp: dict) -> list[str]:
    lines: list[str] = []
    frameworks = fp.get("frameworks", [])
    deployments = fp.get("deployments", [])
    surfaces = fp.get("surfaces", [])
    traits = fp.get("traits", [])
    titles = fp.get("titles", [])
    dedup = fp.get("deduplication", {})
    story, emphasis, _ = classify_target_story(fp)

    lines.append(f"- Target appears to be a {story}.")
    if frameworks:
        lines.append(f"- Observed framework indicators: {', '.join(f'`{x}`' for x in frameworks)}")
    if deployments:
        lines.append(f"- Observed deployment indicators: {', '.join(f'`{x}`' for x in deployments)}")
    if surfaces:
        lines.append(f"- Observed exposed surfaces: {', '.join(f'`{x}`' for x in surfaces)}")
    if traits:
        lines.append(f"- Target traits inferred from artifacts: {', '.join(f'`{x}`' for x in traits)}")
    if titles:
        lines.append(f"- Title hints: {', '.join(f'`{x}`' for x in titles)}")
    if emphasis:
        lines.append(f"- Report emphasis for this target: {', '.join(emphasis)}")

    if dedup.get("overlays_skipped_due_to_dedup"):
        lines.append("- Adaptive overlays: Skipped (target-specific checks already covered by base profile)")
    elif dedup.get("executed_steps_analyzed", 0) > 0:
        lines.append(f"- Adaptive overlays: Analyzed {dedup['executed_steps_analyzed']} executed steps for deduplication")

    return lines


def executive_summary(profile: str, target: str, mode: str, counts: Counter, total: int, fingerprint: dict) -> list[str]:
    lines = ["## Executive Summary", ""]
    story, emphasis, _ = classify_target_story(fingerprint or {})
    if total == 0:
        lines.append(f"- Quick scan profile `{profile}` ran against `{target}` in `{mode}` mode and treated the target as a {story}, but did not capture notable candidate findings from the current artifact set.")
        lines.append("- This suggests either a relatively clean exposed surface or limited visibility from low-impact triage checks.")
    else:
        highest = next((sev for sev in ["Critical", "High", "Medium", "Low", "Info"] if counts.get(sev)), "Info")
        lines.append(f"- Quick scan profile `{profile}` ran against `{target}` in `{mode}` mode and treated the target as a {story}, capturing {total} meaningful candidate observations with highest provisional severity `{highest}`.")
        lines.append("- These results are triage-oriented and should be manually validated before being treated as confirmed vulnerabilities.")
    if fingerprint:
        focus = fingerprint.get("report_focus", [])
        merged_focus = list(dict.fromkeys(emphasis + focus))
        if merged_focus:
            lines.append(f"- This quick scan adapted its framing toward: {', '.join(merged_focus)}.")
    lines.append("")
    return lines


def phase_excerpt(path: Path | None, title: str) -> list[str]:
    if not path or not path.exists():
        return [f"## {title}", "", "- No summary generated for this phase.", ""]
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    excerpt = text[:30]
    return [f"## {title}", "", *excerpt, ""]


def recommended_next_action(counts: Counter, has_recon: bool, has_enum: bool, has_vuln: bool, fingerprint: dict) -> list[str]:
    lines = ["## Recommended Next Action", ""]
    story, _, recs = classify_target_story(fingerprint or {})
    if counts.get("Critical") or counts.get("High"):
        lines.append(f"- Escalate to a full pentest workflow or targeted manual validation immediately for the highest-risk candidates on this {story}.")
    elif counts.get("Medium"):
        lines.append(f"- Perform focused manual validation on the medium-severity candidates and expand service-specific enumeration where relevant for this {story}.")
    elif has_enum or has_vuln:
        lines.append(f"- Preserve artifacts and consider a deeper follow-up scan if this {story} matters operationally.")
    else:
        lines.append(f"- If higher confidence is needed, rerun with a broader profile or move to a full pentest workflow for this {story}.")
    for rec in recs[:2]:
        lines.append(f"- {rec}")
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
    fingerprint = load_fingerprint(base)

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
    ]
    if fingerprint:
        summary_lines.extend(["## Target Fingerprint", ""])
        summary_lines.extend(describe_fingerprint(fingerprint) or ["- No fingerprint details captured."])
        if fingerprint.get("profiles_considered"):
            summary_lines.append(f"- Adaptive overlays considered: {', '.join(fingerprint['profiles_considered'])}")
        summary_lines.append("")
    summary_lines.extend([
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
    ])
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
    report_lines.extend(executive_summary(args.profile, args.target, args.mode, counts, len(candidates), fingerprint))
    if fingerprint:
        report_lines.extend(["## Target Fingerprint", ""])
        report_lines.extend(describe_fingerprint(fingerprint) or ["- No fingerprint details captured."])
        if fingerprint.get("profiles_considered"):
            report_lines.append(f"- Adaptive overlays considered: {', '.join(fingerprint['profiles_considered'])}")
        report_lines.append("")
        if fingerprint.get("report_focus"):
            story, emphasis, recs = classify_target_story(fingerprint)
            report_lines.extend(["## Why This Quick Scan Varied", ""])
            report_lines.append(f"- This target was framed as a {story} based on lightweight fingerprint evidence.")
            report_lines.extend([f"- Focused on {item}" for item in list(dict.fromkeys(emphasis + fingerprint.get("report_focus", [])))])
            if recs:
                report_lines.extend([f"- Reporting bias adjusted toward: {item}" for item in recs[:2]])
            report_lines.append("")
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
    report_lines.extend(recommended_next_action(counts, recon_summary is not None, enum_summary is not None, vuln_summary is not None, fingerprint))
    report_lines.extend(phase_excerpt(recon_summary, "Recon Summary"))
    report_lines.extend(phase_excerpt(enum_summary, "Enumeration Summary"))
    report_lines.extend(phase_excerpt(vuln_summary, "Vulnerability Summary"))
    report_lines.extend([
        "## Recommendations",
        "",
        "- Validate candidate findings manually before escalation or reporting as confirmed issues.",
        "- Escalate to a full pentest workflow if exposed services, weak posture, or high-risk candidates are found.",
        "- Preserve engagement artifacts for follow-up analysis and retesting.",
    ])
    _, _, tailored_recs = classify_target_story(fingerprint or {})
    for rec in tailored_recs[:3]:
        report_lines.append(f"- {rec}")
    report_lines.extend([
        "",
    ])
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(executive_summary_path)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
