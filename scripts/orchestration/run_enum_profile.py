#!/usr/bin/env python3
"""Run an enum manifest profile with simple placeholder substitution."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_manifest(path: Path) -> dict:
    data: dict = {"steps": []}
    current = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and stripped == "steps:":
            data["steps"] = []
            continue
        if not line.startswith(" ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
            continue
        if stripped.startswith("- script:"):
            script = stripped.split(":", 1)[1].strip().strip('"')
            current = {"script": script, "args": []}
            data.setdefault("steps", []).append(current)
            continue
        if stripped.startswith("args:") and current is not None:
            rest = stripped.split(":", 1)[1].strip()
            if rest.startswith("[") and rest.endswith("]"):
                items = [item.strip().strip('"') for item in rest[1:-1].split(",") if item.strip()]
                current["args"] = items
    return data


def substitute(items: list[str], mapping: dict[str, str]) -> list[str]:
    out = []
    for item in items:
        value = item
        for key, mapped in mapping.items():
            value = value.replace(f"{{{{{key}}}}}", mapped)
        out.append(value)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Run enum profile manifest")
    parser.add_argument("--profile", required=True, help="Manifest name or path")
    parser.add_argument("--target", required=True, help="Target host")
    parser.add_argument("--engagement", required=True, help="Engagement folder name")
    parser.add_argument("--input", default="", help="Optional input artifact path")
    args = parser.parse_args()

    manifest_path = Path(args.profile)
    if not manifest_path.exists():
        manifest_path = ROOT / "scripts" / "shared" / "manifests" / f"{args.profile}.yaml"
    if not manifest_path.exists():
        print(f"manifest not found: {args.profile}", file=sys.stderr)
        return 2

    manifest = load_manifest(manifest_path)
    if manifest.get("phase") != "enum":
        print(f"manifest phase is not enum: {manifest.get('phase')}", file=sys.stderr)
        return 2

    mapping = {
        "target": args.target,
        "engagement": args.engagement,
        "input": args.input,
    }

    print(f"[*] Running enum profile: {manifest.get('name', manifest_path.stem)}")
    for idx, step in enumerate(manifest.get("steps", []), start=1):
        script_rel = step["script"]
        script_path = ROOT / "scripts" / script_rel
        if not script_path.exists():
            print(f"[!] Missing script: {script_path}", file=sys.stderr)
            return 1
        argv = [str(script_path)] + substitute(step.get("args", []), mapping)
        print(f"[{idx}/{len(manifest['steps'])}] {' '.join(argv)}")
        result = subprocess.run(argv, cwd=ROOT)
        if result.returncode != 0:
            print(f"[!] Step failed with exit code {result.returncode}: {script_rel}", file=sys.stderr)
            return result.returncode

    print("[✓] Enum profile complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
