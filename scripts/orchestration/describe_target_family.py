#!/usr/bin/env python3
"""Describe a composed full-pentest target family."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.shared.lib.target_family import compose_family


def main() -> int:
    parser = argparse.ArgumentParser(description="Describe a composed full-pentest target family")
    parser.add_argument("--family", required=True, help="Target family name")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    family = compose_family(args.family)
    if args.json:
        print(json.dumps(family, indent=2))
        return 0

    print(f"Family: {family['name']}")
    print(f"Description: {family.get('description', '')}")
    if family.get("lineage"):
        print(f"Lineage: {' -> '.join(family['lineage'])}")
    if family.get("tags"):
        print(f"Tags: {', '.join(family['tags'])}")
    if family.get("target_kinds"):
        print(f"Allowed target kinds: {', '.join(family['target_kinds'])}")
    print("Default phase entrypoints:")
    for phase, entrypoint in family.get("default_entrypoints", {}).items():
        print(f"- {phase}: {entrypoint}")
    print("Phase guidance:")
    for phase, block in family.get("phases", {}).items():
        print(f"- {phase}")
        for key in ("recommended_profiles", "manifests", "capabilities", "notes"):
            values = block.get(key)
            if values:
                joined = "; ".join(values)
                print(f"  - {key}: {joined}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
