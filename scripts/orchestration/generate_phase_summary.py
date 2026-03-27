#!/usr/bin/env python3
"""Generate standardized phase handoff summaries from phase artifacts.

Initial support: recon, enum, vuln, exploit, post-exploit.
Designed to be reusable later for quick-scan reporting flows.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.shared.lib.output_helpers import write_text

PHASE_META = {
    "recon": {"title": "Reconnaissance", "agent": "specter-recon", "next": "specter-enum", "vector": "network"},
    "enum": {"title": "Enumeration", "agent": "specter-enum", "next": "specter-vuln", "vector": "network"},
    "vuln": {"title": "Vulnerability Analysis", "agent": "specter-vuln", "next": "specter-exploit", "vector": "network"},
    "exploit": {"title": "Exploitation", "agent": "specter-exploit", "next": "specter-post", "vector": "network"},
    "post-exploit": {"title": "Post-Exploitation", "agent": "specter-post", "next": "specter-report", "vector": "impact"},
}


def latest_files(directory: Path, pattern: str) -> list[Path]:
    return sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)


def load_json_files(paths: list[Path]) -> list[dict[str, Any]]:
    out = []
    for path in paths:
        try:
            out.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out


def extract_open_ports(json_payloads: list[dict[str, Any]]) -> list[str]:
    ports = []
    for payload in json_payloads:
        for item in payload.get("open_ports", []):
            ports.append(f"{item.get('port')}/{item.get('protocol', 'tcp')} — {item.get('service', 'unknown')}")
        for item in payload.get("findings", []):
            if isinstance(item, dict) and item.get("type") in {"rdp", "winrm", "share", "path", "enum"}:
                value = item.get("value") or item.get("url") or json.dumps(item)
                ports.append(str(value))
    seen = []
    for item in ports:
        if item not in seen:
            seen.append(item)
    return seen


def extract_recon_findings(json_payloads: list[dict[str, Any]]) -> list[str]:
    findings = []
    for payload in json_payloads:
        records = payload.get("records")
        if isinstance(records, dict):
            for rtype, values in records.items():
                if values:
                    findings.append(f"{rtype}: {', '.join(values[:5])}")
        for item in payload.get("findings", []):
            if isinstance(item, dict):
                if item.get("type") == "subdomain":
                    findings.append(f"Subdomain: {item.get('value')}")
                elif item.get("type") in {"whois", "header", "title", "whatweb"}:
                    value = item.get("value")
                    if value:
                        findings.append(f"{item.get('type').title()}: {value}")
    deduped = []
    for item in findings:
        if item not in deduped:
            deduped.append(item)
    return deduped


def extract_vuln_findings(json_payloads: list[dict[str, Any]]) -> list[str]:
    findings = []
    for payload in json_payloads:
        for item in payload.get("findings", []):
            if not isinstance(item, dict):
                continue
            if "candidate" in item:
                label = item.get("service_context") or item.get("query") or item.get("type") or "candidate"
                findings.append(f"{label}: {item.get('candidate')}")
            elif "title" in item:
                findings.append(f"{item.get('query', 'searchsploit')}: {item.get('title')} (EDB {item.get('edb_id', '?')})")
            elif "value" in item:
                findings.append(str(item.get("value")))
    deduped = []
    for item in findings:
        if item not in deduped:
            deduped.append(item)
    return deduped


def summarize_not_found(phase: str, json_payloads: list[dict[str, Any]]) -> list[str]:
    negatives = []
    if phase == "enum":
        ports = []
        for payload in json_payloads:
            ports.extend(payload.get("open_ports", []))
        if not ports:
            negatives.append("Checked: fast/service scan → Result: no open ports confirmed in collected artifacts")
    if phase == "vuln":
        findings = extract_vuln_findings(json_payloads)
        if not findings:
            negatives.append("Checked: automated CVE/searchsploit/web baseline triage → Result: no candidate vulnerabilities captured")
    if phase == "recon":
        findings = extract_recon_findings(json_payloads)
        if not findings:
            negatives.append("Checked: DNS/WHOIS/HTTP passive recon → Result: limited or no structured findings captured")
    if phase == "exploit":
        findings = extract_action_findings(json_payloads)
        if not findings:
            negatives.append("Checked: exploit planning/attempt artifacts → Result: no exploit attempts or access results captured")
    if phase == "post-exploit":
        findings = extract_action_findings(json_payloads)
        if not findings:
            negatives.append("Checked: post-exploit evidence artifacts → Result: no session facts or loot references captured")
    return negatives or ["Checked: current automated artifacts → Result: no additional negative results explicitly captured"]


def confidence_for_phase(phase: str, json_payloads: list[dict[str, Any]]) -> dict[str, str]:
    status_counter = Counter(payload.get("status", "unknown") for payload in json_payloads)
    if status_counter.get("success") and len(status_counter) == 1:
        overall = "high"
    elif status_counter.get("success"):
        overall = "medium"
    else:
        overall = "low"
    if phase == "recon":
        return {"Overall": overall, "Network findings": "medium", "Service identification": "n/a", "Vulnerability assessment": "n/a"}
    if phase == "enum":
        return {"Overall": overall, "Network findings": overall, "Service identification": overall, "Vulnerability assessment": "n/a"}
    if phase == "vuln":
        return {"Overall": overall, "Network findings": "n/a", "Service identification": "medium", "Vulnerability assessment": overall}
    if phase == "exploit":
        return {"Overall": overall, "Exploit execution": overall, "Access achieved": "medium" if status_counter.get("success") else "low", "Evidence quality": overall}
    return {"Overall": overall, "Session facts": overall, "Loot indexing": overall, "Impact assessment": "medium" if status_counter.get("success") else "low"}


def extract_action_findings(json_payloads: list[dict[str, Any]]) -> list[str]:
    findings = []
    for payload in json_payloads:
        for item in payload.get("findings", []):
            if not isinstance(item, dict):
                continue
            item_type = item.get("type", "finding")
            value = item.get("value") or item.get("candidate") or item.get("title")
            if not value:
                continue
            if item_type == "attempt":
                findings.append(f"Attempt: {value} ({item.get('result', payload.get('status', 'unknown'))})")
            elif item_type == "access":
                findings.append(f"Access: {value}")
            elif item_type == "credential":
                findings.append(f"Credential reference: {value}")
            elif item_type == "evidence":
                findings.append(f"Evidence: {value}")
            else:
                if item_type == "fact" and item.get("key"):
                    findings.append(f"Fact: {item['key']}={value}")
                else:
                    findings.append(f"{item_type.replace('-', ' ').title()}: {value}")
    deduped = []
    for item in findings:
        if item not in deduped:
            deduped.append(item)
    return deduped


def phase_findings(phase: str, json_payloads: list[dict[str, Any]]) -> list[str]:
    if phase == "recon":
        return extract_recon_findings(json_payloads)
    if phase == "enum":
        return extract_open_ports(json_payloads)
    if phase == "vuln":
        return extract_vuln_findings(json_payloads)
    if phase in {"exploit", "post-exploit"}:
        return extract_action_findings(json_payloads)
    return []


def build_key_data(phase: str, engagement: str, json_payloads: list[dict[str, Any]], phase_dir: Path) -> str:
    target = next((p.get("target") for p in json_payloads if p.get("target")), engagement)
    lines = ["### Network", f"- Target: {target}"]
    if phase in {"enum", "vuln"}:
        ports = extract_open_ports(json_payloads)
        lines.append(f"- Open ports / services: {', '.join(ports[:12]) if ports else 'none captured'}")
    elif phase == "recon":
        rec = extract_recon_findings(json_payloads)
        lines.append(f"- Attack surface clues: {', '.join(rec[:8]) if rec else 'none captured'}")
    else:
        actions = extract_action_findings(json_payloads)
        lines.append(f"- Action artifacts: {', '.join(actions[:8]) if actions else 'none captured'}")
    lines.extend(["", "### Credentials", "- None captured by automation", "", "### CVEs / Vulnerabilities"])
    if phase == "vuln":
        vulns = extract_vuln_findings(json_payloads)
        lines.extend([f"- {item}" for item in vulns[:15]] or ["- No candidate vulnerabilities captured"])
    else:
        lines.append("- N/A in this phase")
    lines.extend(["", "### File Paths"])
    for sub in ("raw", "parsed", "summaries"):
        subdir = phase_dir / sub
        if subdir.exists():
            files = sorted(p.name for p in subdir.iterdir() if p.is_file())
            if files:
                lines.append(f"- {sub}: {', '.join(files[:10])}")
    lines.extend(["", "### Access", "- Access level achieved: none", "- Method of access: N/A", "- Credentials obtained: none"])
    return "\n".join(lines)


def recommend_next(phase: str, findings: list[str]) -> tuple[str, str, str]:
    meta = PHASE_META[phase]
    if phase == "recon" and not findings:
        return ("specter-enum", "network", "Passive recon produced limited findings; proceed with cautious live enumeration if authorized.")
    if phase == "enum" and not findings:
        return ("specter-vuln", "network", "Enumeration captured little attack surface; analyze collected evidence before deciding to pivot or stop.")
    if phase == "vuln" and not findings:
        return ("specter-report", "network", "No clear exploit candidates were captured; summarize defensive posture and report remaining unknowns.")
    if phase == "exploit" and not findings:
        return ("specter-post", "impact", "No exploit attempt results were captured; confirm whether execution was skipped, blocked, or still pending.")
    if phase == "post-exploit" and not findings:
        return ("specter-report", "impact", "No post-exploit evidence was captured; summarize current access and residual uncertainty before reporting.")
    return (meta["next"], meta["vector"], f"Automated {phase} artifacts produced reusable evidence for the next phase.")


def render_summary(engagement: str, phase: str, json_payloads: list[dict[str, Any]], phase_dir: Path, status: str) -> str:
    meta = PHASE_META[phase]
    findings = phase_findings(phase, json_payloads)
    not_found = summarize_not_found(phase, json_payloads)
    next_phase, vector, reason = recommend_next(phase, findings)
    confidence = confidence_for_phase(phase, json_payloads)
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    key_data = build_key_data(phase, engagement, json_payloads, phase_dir)

    lines = [
        f"# Phase Complete: {meta['title']}",
        "",
        f"**Engagement:** {engagement}",
        f"**Phase:** {phase}",
        f"**Agent:** {meta['agent']}",
        f"**Date:** {timestamp}",
        f"**Status:** {status}",
        "",
        "## Found",
        "",
    ]
    lines.extend([f"- {item}" for item in findings[:30]] or ["- No significant structured findings captured by automation."])
    lines.extend(["", "## Not Found", ""])
    lines.extend([f"- {item}" for item in not_found])
    lines.extend([
        "",
        "## Recommended Next",
        "",
        f"- **Next Phase:** {next_phase}",
        f"- **Vector:** {vector}",
        f"- **Reason:** {reason}",
        "",
        "## Key Data",
        "",
        key_data,
        "",
        "## Confidence",
        "",
    ])
    for key, value in confidence.items():
        lines.append(f"- **{key}:** {value}")
    lines.extend([
        "",
        "## Notes",
        "",
        "- Generated from standardized phase artifacts under raw/parsed/summaries.",
        "- Review and refine before treating as final handoff for a real engagement.",
        "",
        "## Adaptation",
        "",
        "- **Pivoted from:** N/A",
        "- **Pivoted to:** N/A",
        "- **Reason:** N/A",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate standardized phase summary from artifacts")
    parser.add_argument("--engagement", required=True, help="Engagement name under engagements/")
    parser.add_argument("--phase", required=True, choices=sorted(PHASE_META.keys()))
    parser.add_argument("--status", default="complete")
    parser.add_argument("--output", default="", help="Optional explicit output path")
    args = parser.parse_args()

    phase_dir = ROOT / "engagements" / args.engagement / args.phase
    if not phase_dir.exists():
        print(f"phase directory not found: {phase_dir}", file=sys.stderr)
        return 2

    parsed_files = latest_files(phase_dir / "parsed", "*.json") if (phase_dir / "parsed").exists() else []
    json_payloads = load_json_files(parsed_files)
    if not json_payloads:
        print(f"no parsed JSON artifacts found under {phase_dir / 'parsed'}", file=sys.stderr)
        return 2

    now = datetime.now().strftime("%Y-%m-%d_%H%M")
    prefix = {"recon": "RECON_SUMMARY", "enum": "ENUM_SUMMARY", "vuln": "VULN_SUMMARY", "exploit": "EXPLOIT_SUMMARY", "post-exploit": "POST_EXPLOIT_SUMMARY"}[args.phase]
    output_path = Path(args.output) if args.output else phase_dir / f"{prefix}_{now}.md"
    content = render_summary(args.engagement, args.phase, json_payloads, phase_dir, args.status)
    write_text(output_path, content + "\n")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
