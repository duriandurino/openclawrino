#!/usr/bin/env python3
"""Regression check for generated PPTX slide text.

Extracts slide text from a PPTX and fails if known broken truncation
patterns are present.

Usage:
    python3 reporting/scripts/check_pptx_slide_text.py --pptx path/to/report.pptx
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from zipfile import ZipFile

BROKEN_SUFFIXES = (
    " then verify the",
    " whether it is",
)

BROKEN_EXACT = {
    "Fix: Apply the missing security control, then verify the",
    "Fix: Validate the observation manually, document whether it is",
}


def extract_slide_text(pptx_path: Path) -> list[str]:
    texts: list[str] = []
    with ZipFile(pptx_path) as zf:
        for name in sorted(n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")):
            data = zf.read(name).decode("utf-8", "ignore")
            texts.extend(t.strip() for t in re.findall(r"<a:t>(.*?)</a:t>", data) if t.strip())
    return texts


def find_broken_lines(lines: list[str]) -> list[str]:
    broken: list[str] = []
    for line in lines:
        if line in BROKEN_EXACT:
            broken.append(line)
            continue
        if any(line.endswith(suffix) for suffix in BROKEN_SUFFIXES):
            broken.append(line)
    return broken


def main() -> int:
    parser = argparse.ArgumentParser(description="Check generated PPTX slide text for known truncation regressions")
    parser.add_argument("--pptx", required=True, help="Path to the generated PPTX")
    args = parser.parse_args()

    pptx_path = Path(args.pptx)
    if not pptx_path.exists():
        print(f"[FAIL] PPTX not found: {pptx_path}", file=sys.stderr)
        return 1

    try:
        lines = extract_slide_text(pptx_path)
    except Exception as exc:
        print(f"[FAIL] Could not inspect PPTX: {exc}", file=sys.stderr)
        return 1

    broken = find_broken_lines(lines)
    if broken:
        print("[FAIL] Found broken slide text lines:", file=sys.stderr)
        for line in broken:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"[OK] Checked {len(lines)} text fragments in {pptx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
