#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def latest_file(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Print latest published quick-scan links for an engagement")
    parser.add_argument("--engagement", required=True)
    parser.add_argument("--format", choices=["json", "text"], default="text")
    args = parser.parse_args()

    reporting_dir = ROOT / "engagements" / args.engagement / "quick-scan" / "reporting"
    if not reporting_dir.exists():
        raise SystemExit(f"reporting directory not found: {reporting_dir}")

    summary_path = latest_file(reporting_dir, "REPORT_FINAL_QUICK_SCAN_*.publish.json")
    if not summary_path:
        raise SystemExit("no quick-scan publish summary found")

    data = json.loads(summary_path.read_text(encoding="utf-8"))
    payload = {
        "engagement": args.engagement,
        "summary_path": str(summary_path),
        "doc_link": data.get("doc_link"),
        "slides_link": data.get("slides_link"),
        "pdf_link": data.get("pdf_link") or data.get("drive_link"),
        "drive_link": data.get("drive_link"),
        "local_file": data.get("local_file"),
    }

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Engagement: {payload['engagement']}")
        for key, label in [
            ("doc_link", "Doc"),
            ("slides_link", "Slides"),
            ("pdf_link", "PDF"),
            ("drive_link", "Drive file"),
            ("local_file", "Local file"),
        ]:
            if payload.get(key):
                print(f"{label}: {payload[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
