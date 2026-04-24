#!/usr/bin/env python3
"""Recommend a reusable full-pentest target family from free-text hints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.shared.lib.target_family import list_families, recommend_target_family


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend a full-pentest target family")
    parser.add_argument("--hint", help="Free-text description of the target")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--list", action="store_true", help="List available target families")
    args = parser.parse_args()

    if args.list:
        data = {"families": list_families()}
        print(json.dumps(data, indent=2) if args.json else "\n".join(f"- {item['name']}: {item['description']}" for item in data["families"]))
        return 0

    if not args.hint:
        parser.error("--hint is required unless --list is used")

    result = recommend_target_family(args.hint)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"Recommended family: {result['family']}")
    print(f"Reason: {result['reason']}")
    if result.get("matched"):
        print(f"Matched hints: {', '.join(result['matched'])}")
    if result.get("alternatives"):
        print(f"Alternatives: {', '.join(result['alternatives'])}")
    composed = result["composed"]
    print("Default phase entrypoints:")
    for phase, entrypoint in composed.get("default_entrypoints", {}).items():
        print(f"- {phase}: {entrypoint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
