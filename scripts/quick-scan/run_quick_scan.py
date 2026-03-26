#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.orchestration.run_enum_profile import substitute


MODE_DEFAULTS = {
    "safe": {
        "safe_flag": "--safe",
        "fast_flag": "",
        "skip_optional_recon": "false",
        "skip_optional_vuln": "false",
    },
    "fast": {
        "safe_flag": "--safe",
        "fast_flag": "--fast",
        "skip_optional_recon": "true",
        "skip_optional_vuln": "false",
    },
}

PREFERRED_ENUM_JSON_PATTERNS = [
    "nmap-service-*.json",
    "nmap-fast-*.json",
    "web-basic-*.json",
    "smb-basic-*.json",
    "rdp-probe-*.json",
    "winrm-probe-*.json",
    "*.json",
]


def load_recommender():
    module_path = ROOT / "scripts" / "quick-scan" / "recommend_profile.py"
    spec = importlib.util.spec_from_file_location("quickscan_recommend_profile", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load recommender from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_quick_manifest(path: Path) -> dict:
    data: dict = {"steps": []}
    current: dict | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and stripped == "steps:":
            data["steps"] = []
            current = None
            continue
        if not line.startswith(" ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
            continue
        if stripped.startswith("-"):
            current = {}
            data.setdefault("steps", []).append(current)
            entry = stripped[1:].strip()
            if ":" in entry:
                key, value = entry.split(":", 1)
                current[key.strip()] = value.strip().strip('"')
            continue
        if current is not None and stripped.startswith("args:"):
            rest = stripped.split(":", 1)[1].strip()
            if rest.startswith("[") and rest.endswith("]"):
                items = [item.strip().strip('"') for item in rest[1:-1].split(",") if item.strip()]
                current["args"] = items
            continue
        if current is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = value.strip().strip('"')
            continue
    return data


def latest_enum_json(engagement: str) -> str:
    parsed_dir = ROOT / "engagements" / engagement / "enum" / "parsed"
    if not parsed_dir.exists():
        return ""
    for pattern in PREFERRED_ENUM_JSON_PATTERNS:
        candidates = sorted(parsed_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
        if candidates:
            return str(candidates[-1])
    return ""


def ensure_reporting_dir(engagement: str) -> Path:
    path = ROOT / "engagements" / engagement / "quick-scan" / "reporting"
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_profile(profile: str) -> Path:
    candidate = Path(profile)
    if candidate.exists():
        return candidate
    candidate = ROOT / "scripts" / "quick-scan" / "profiles" / f"{profile}.yaml"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(profile)


def should_skip_step(step: dict, mode: str) -> bool:
    optional = step.get("optional", "false").lower() == "true"
    if mode == "fast" and optional:
        return True
    return False


def choose_profile(profile: str | None, hint: str | None) -> tuple[str, dict | None]:
    if profile:
        return profile, None
    if hint:
        recommender = load_recommender()
        recommendation = recommender.recommend(hint)
        return recommendation["profile"], recommendation
    raise ValueError("either --profile or --hint is required")


def run_optional(command: list[str], cwd: Path, label: str):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        if result.stdout.strip():
            print(result.stdout.strip())
    else:
        print(f"[WARN] {label} failed: {result.stderr.strip() or result.stdout.strip()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run quick security scan profile")
    parser.add_argument("--profile", default="", help="Quick-scan profile name or path")
    parser.add_argument("--hint", default="", help="Free-text target description used to auto-select a profile")
    parser.add_argument("--target", required=True, help="Target host, URL, or domain")
    parser.add_argument("--engagement", default="", help="Engagement folder name (defaults to quick-<profile>-<timestamp>)")
    parser.add_argument("--mode", choices=["safe", "fast"], default="safe", help="Execution mode")
    parser.add_argument("--account", default="hatlesswhite@gmail.com", help="Google account used for quick report publishing")
    parser.add_argument("--no-publish", action="store_true", help="Skip export/publish after report generation")
    args = parser.parse_args()

    chosen_profile, recommendation = choose_profile(args.profile or None, args.hint or None)
    manifest_path = resolve_profile(chosen_profile)
    manifest = load_quick_manifest(manifest_path)
    engagement = args.engagement or f"quick-{manifest.get('name', manifest_path.stem)}-{datetime.now().strftime('%Y-%m-%d_%H%M')}"
    ensure_reporting_dir(engagement)

    print(f"[*] Running quick scan profile: {manifest.get('name', manifest_path.stem)}")
    if recommendation:
        print(f"[*] Auto-selected from hint: {args.hint}")
        print(f"[*] Selection reason: {recommendation['reason']}")
    print(f"[*] Engagement: {engagement}")
    print(f"[*] Mode: {args.mode}")

    steps = manifest.get("steps", [])
    executed_steps = 0
    for idx, step in enumerate(steps, start=1):
        if should_skip_step(step, args.mode):
            print(f"[{idx}/{len(steps)}] SKIP optional step in {args.mode} mode: {step.get('script')}")
            continue
        mapping = {
            "target": args.target,
            "engagement": engagement,
            "latest_enum_json": latest_enum_json(engagement),
            "mode": args.mode,
            **MODE_DEFAULTS[args.mode],
        }
        argv = [str(ROOT / "scripts" / step["script"])] + [arg for arg in substitute(step.get("args", []), mapping) if arg]
        print(f"[{idx}/{len(steps)}] {' '.join(argv)}")
        result = subprocess.run(argv, cwd=ROOT)
        if result.returncode != 0:
            print(f"[!] Step failed with exit code {result.returncode}: {step['script']}", file=sys.stderr)
            return result.returncode
        executed_steps += 1

    for phase in ["recon", "enum", "vuln"]:
        phase_dir = ROOT / "engagements" / engagement / phase / "parsed"
        if phase_dir.exists() and any(phase_dir.glob("*.json")):
            subprocess.run([
                "python3",
                str(ROOT / "scripts" / "orchestration" / "generate_phase_summary.py"),
                "--engagement",
                engagement,
                "--phase",
                phase,
            ], cwd=ROOT, check=False)

    report_script = ROOT / "scripts" / "quick-scan" / "generate_quick_report.py"
    if report_script.exists():
        subprocess.run([
            "python3", str(report_script), "--engagement", engagement, "--profile", manifest.get("name", manifest_path.stem), "--target", args.target, "--mode", args.mode, "--steps", str(executed_steps)
        ], cwd=ROOT, check=False)

    if not args.no_publish:
        export_script = ROOT / "scripts" / "quick-scan" / "export_quick_report.py"
        publish_script = ROOT / "scripts" / "quick-scan" / "publish_quick_report.py"
        if export_script.exists():
            run_optional(["python3", str(export_script), "--engagement", engagement], ROOT, "quick report export")
        if publish_script.exists():
            run_optional(["python3", str(publish_script), "--engagement", engagement, "--account", args.account], ROOT, "quick report publish")

    print(f"[✓] Quick scan complete: engagements/{engagement}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
