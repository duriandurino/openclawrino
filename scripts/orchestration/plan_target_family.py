#!/usr/bin/env python3
"""Expand a full-pentest target family into a concrete per-phase execution plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.orchestration.run_enum_profile import load_manifest
from scripts.shared.lib.target_family import compose_family, load_target_families, recommend_target_family

PHASE_ORDER = ["recon", "enum", "vuln", "exploit", "post-exploit"]
MANIFESTS_DIR = ROOT / "scripts" / "shared" / "manifests"


def resolve_manifest_name(name: str) -> Path:
    candidate = Path(name)
    if candidate.exists():
        return candidate
    manifest_path = MANIFESTS_DIR / f"{name}.yaml"
    if manifest_path.exists():
        return manifest_path
    raise FileNotFoundError(f"manifest not found: {name}")


def manifest_summary(name: str) -> dict:
    path = resolve_manifest_name(name)
    manifest = load_manifest(path)
    return {
        "name": manifest.get("name", path.stem),
        "path": str(path.relative_to(ROOT)),
        "phase": manifest.get("phase", ""),
        "description": manifest.get("description", ""),
        "steps": manifest.get("steps", []),
    }


def _manifest_names_for_entrypoint(entrypoint: str, data: dict) -> list[str]:
    manifest_sets = data.get("manifest_sets", {})
    block = manifest_sets.get(entrypoint, {})
    manifests = block.get("manifests", []) if isinstance(block, dict) else []
    return [item for item in manifests if item]


def build_plan(family_name: str, target: str, engagement: str, data: dict | None = None) -> dict:
    data = data or load_target_families()
    family = compose_family(family_name, data=data)
    plan = {
        "family": family_name,
        "target": target,
        "engagement": engagement,
        "lineage": family.get("lineage", []),
        "tags": family.get("tags", []),
        "phases": [],
    }

    for phase in PHASE_ORDER:
        block = family.get("phases", {}).get(phase, {})
        entrypoint = family.get("default_entrypoints", {}).get(phase, "")
        manifest_names = []
        for item in _manifest_names_for_entrypoint(entrypoint, data):
            if item not in manifest_names:
                manifest_names.append(item)
        for item in block.get("manifests", []):
            if item not in manifest_names:
                manifest_names.append(item)

        phase_plan = {
            "phase": phase,
            "entrypoint": entrypoint,
            "recommended_profiles": block.get("recommended_profiles", []),
            "capabilities": block.get("capabilities", []),
            "notes": block.get("notes", []),
            "manifests": [manifest_summary(name) for name in manifest_names],
        }
        plan["phases"].append(phase_plan)

    return plan


def render_text(plan: dict) -> str:
    lines = []
    lines.append(f"Family plan: {plan['family']}")
    lines.append(f"Target: {plan['target']}")
    lines.append(f"Engagement: {plan['engagement']}")
    if plan.get("lineage"):
        lines.append(f"Lineage: {' -> '.join(plan['lineage'])}")
    if plan.get("tags"):
        lines.append(f"Tags: {', '.join(plan['tags'])}")
    lines.append("Per-phase execution plan:")
    for phase_block in plan.get("phases", []):
        lines.append(f"- {phase_block['phase']}")
        if phase_block.get("entrypoint"):
            lines.append(f"  - entrypoint: {phase_block['entrypoint']}")
        if phase_block.get("capabilities"):
            lines.append(f"  - capabilities: {', '.join(phase_block['capabilities'])}")
        if phase_block.get("recommended_profiles"):
            lines.append(f"  - recommended_profiles: {', '.join(phase_block['recommended_profiles'])}")
        if phase_block.get("manifests"):
            lines.append("  - manifests:")
            for manifest in phase_block["manifests"]:
                lines.append(f"    - {manifest['name']} ({manifest['path']})")
                if manifest.get("description"):
                    lines.append(f"      description: {manifest['description']}")
                for idx, step in enumerate(manifest.get("steps", []), start=1):
                    args = " ".join(step.get("args", []))
                    lines.append(f"      step {idx}: {step.get('script', '')} {args}".rstrip())
        if phase_block.get("notes"):
            lines.append("  - notes:")
            for note in phase_block["notes"]:
                lines.append(f"    - {note}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan full-pentest execution from a target family")
    parser.add_argument("--family", help="Target family name")
    parser.add_argument("--hint", help="Free-text hint used to recommend a family when --family is omitted")
    parser.add_argument("--target", required=True, help="Concrete target host, domain, or URL")
    parser.add_argument("--engagement", required=True, help="Engagement folder name")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    if not args.family and not args.hint:
        parser.error("either --family or --hint is required")

    data = load_target_families()
    family_name = args.family
    recommendation = None
    if not family_name:
        recommendation = recommend_target_family(args.hint or "", data=data)
        family_name = recommendation["family"]

    plan = build_plan(family_name, target=args.target, engagement=args.engagement, data=data)
    if recommendation is not None:
        plan["recommendation"] = {
            "family": recommendation["family"],
            "reason": recommendation.get("reason", ""),
            "matched": recommendation.get("matched", []),
            "alternatives": recommendation.get("alternatives", []),
        }

    if args.json:
        print(json.dumps(plan, indent=2))
    else:
        if recommendation is not None:
            print(f"Recommended from hint: {recommendation['family']}")
            print(f"Reason: {recommendation.get('reason', '')}")
            if recommendation.get("matched"):
                print(f"Matched hints: {', '.join(recommendation['matched'])}")
            if recommendation.get("alternatives"):
                print(f"Alternatives: {', '.join(recommendation['alternatives'])}")
            print()
        print(render_text(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
