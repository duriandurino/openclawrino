#!/usr/bin/env python3
"""Run a standardized DNS baseline and save raw/parsed/summary artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.shared.lib.output_helpers import artifact_paths, timestamp_now, write_json, write_text
from scripts.shared.lib.target_helpers import validate_target

RECORD_TYPES = ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]


def run_dig(domain: str, record_type: str) -> list[str]:
    try:
        result = subprocess.run(
            ["dig", "+short", domain, record_type],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except FileNotFoundError:
        raise RuntimeError("missing dependency: dig")
    answers = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return answers


def main() -> int:
    parser = argparse.ArgumentParser(description="Standardized DNS baseline recon")
    parser.add_argument("--domain", required=True, help="Target domain")
    parser.add_argument("--engagement", required=True, help="Engagement folder name")
    parser.add_argument("--base-dir", default=str(ROOT), help="Workspace base directory")
    args = parser.parse_args()

    target, _ = validate_target(args.domain, allowed_kinds=["domain", "host"])
    artifacts = artifact_paths(args.base_dir, args.engagement, "recon", "recon-dns-baseline", target)

    records = {}
    raw_lines = []
    for record_type in RECORD_TYPES:
        answers = run_dig(target, record_type)
        records[record_type] = answers
        raw_lines.append(f"## {record_type}\n" + ("\n".join(answers) if answers else "<no-answer>"))

    findings = []
    for rtype, answers in records.items():
        for answer in answers:
            findings.append({"type": rtype, "value": answer})

    payload = {
        "target": target,
        "phase": "recon",
        "script": "scripts/recon/dns/recon_dns_baseline.py",
        "timestamp": timestamp_now(),
        "status": "success",
        "findings": findings,
        "records": records,
        "artifacts": {
            "raw": str(artifacts["raw"]),
            "parsed": str(artifacts["parsed"]),
            "summary": str(artifacts["summary"]),
        },
    }

    summary = "\n".join([
        f"# DNS Baseline — {target}",
        "",
        f"- Engagement: `{args.engagement}`",
        f"- Target: `{target}`",
        f"- Record types checked: {', '.join(RECORD_TYPES)}",
        f"- Findings captured: {len(findings)}",
        "",
        "## Highlights",
        *[f"- {rtype}: {', '.join(values) if values else 'no answer'}" for rtype, values in records.items()],
    ]) + "\n"

    write_text(artifacts["raw"], "\n\n".join(raw_lines) + "\n")
    write_json(artifacts["parsed"], payload)
    write_text(artifacts["summary"], summary)

    print(json.dumps(payload["artifacts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
