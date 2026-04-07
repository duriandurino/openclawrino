#!/usr/bin/env python3
"""Run quick security scan profile.

Refactored to use quickscan_lib.py for shared functionality.
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add workspace root to path for quickscan_lib import
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import shared library functionality
def _load_quickscan_lib():
    """Load quickscan_lib using importlib to avoid module path issues."""
    import importlib.util
    import types
    
    lib_path = ROOT / "scripts" / "quick-scan" / "quickscan_lib.py"
    if not lib_path.exists():
        return None
    
    # Pre-register module to fix dataclass __module__ issues
    if "quickscan_lib" not in sys.modules:
        sys.modules["quickscan_lib"] = types.ModuleType("quickscan_lib")
    
    spec = importlib.util.spec_from_file_location("quickscan_lib", lib_path)
    if spec is None or spec.loader is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    sys.modules["quickscan_lib"] = module
    spec.loader.exec_module(module)
    return module


try:
    _quickscan_lib = _load_quickscan_lib()
    if _quickscan_lib:
        load_manifest = _quickscan_lib.load_manifest
        resolve_profile = _quickscan_lib.resolve_profile
        StepExecutor = _quickscan_lib.StepExecutor
        get_workspace_root = _quickscan_lib.get_workspace_root
        get_engagements_dir = _quickscan_lib.get_engagements_dir
        latest_file = _quickscan_lib.latest_file
        HAS_LIB = True
    else:
        HAS_LIB = False
except Exception as e:
    print(f"[WARN] Could not import quickscan_lib: {e}", file=sys.stderr)
    HAS_LIB = False

# Legacy fallback imports (used when quickscan_lib is not available)
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
    """Load the profile recommender module dynamically."""
    module_path = ROOT / "scripts" / "quick-scan" / "recommend_profile.py"
    spec = importlib.util.spec_from_file_location("quickscan_recommend_profile", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load recommender from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _legacy_load_quick_manifest(path: Path) -> dict:
    """Legacy manifest loader for backward compatibility."""
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


def _legacy_resolve_profile(profile: str) -> Path:
    """Legacy profile resolver for backward compatibility."""
    candidate = Path(profile)
    if candidate.exists():
        return candidate
    candidate = ROOT / "scripts" / "quick-scan" / "profiles" / f"{profile}.yaml"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(profile)


def load_quick_manifest(path: Path) -> dict:
    """Load manifest using shared library or legacy fallback."""
    if HAS_LIB:
        try:
            manifest = _quickscan_lib.load_manifest(path)
            # Convert dataclass to dict for backward compatibility
            return {
                "name": manifest.name,
                "kind": manifest.kind,
                "description": manifest.description,
                "steps": [
                    {
                        "phase": step.phase,
                        "script": step.script,
                        "args": step.args,
                        "optional": step.optional,
                    }
                    for step in manifest.steps
                ],
            }
        except Exception as e:
            print(f"[WARN] Shared library manifest load failed: {e}", file=sys.stderr)
    return _legacy_load_quick_manifest(path)


def resolve_profile_path(profile: str) -> Path:
    """Resolve profile using shared library or legacy fallback."""
    if HAS_LIB:
        try:
            return _quickscan_lib.resolve_profile(profile)
        except Exception as e:
            print(f"[WARN] Shared library profile resolution failed: {e}", file=sys.stderr)
    return _legacy_resolve_profile(profile)


def latest_enum_json(engagement: str) -> str:
    """Find the latest enum JSON file for an engagement."""
    parsed_dir = ROOT / "engagements" / engagement / "enum" / "parsed"
    if not parsed_dir.exists():
        return ""
    for pattern in PREFERRED_ENUM_JSON_PATTERNS:
        candidates = sorted(parsed_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
        if candidates:
            return str(candidates[-1])
    return ""


def load_fingerprint(engagement: str) -> dict:
    """Load quick-scan fingerprint data if present."""
    path = ROOT / "engagements" / engagement / "quick-scan" / "fingerprint.json"
    if not path.exists():
        return {}
    try:
        import json
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def run_fingerprint(engagement: str, profile: str, target: str) -> dict:
    """Run target fingerprinting and return adaptive hints."""
    script = ROOT / "scripts" / "quick-scan" / "fingerprint_target.py"
    if not script.exists():
        return {}
    subprocess.run([
        "python3", str(script),
        "--engagement", engagement,
        "--profile", profile,
        "--target", target,
    ], cwd=ROOT, check=False)
    return load_fingerprint(engagement)


def ensure_reporting_dir(engagement: str) -> Path:
    """Ensure the reporting directory exists for an engagement."""
    path = ROOT / "engagements" / engagement / "quick-scan" / "reporting"
    path.mkdir(parents=True, exist_ok=True)
    return path


def should_skip_step(step: dict, mode: str) -> bool:
    """Determine if a step should be skipped based on mode."""
    optional = step.get("optional", False)
    if isinstance(optional, str):
        optional = optional.lower() == "true"
    if mode == "fast" and optional:
        return True
    return False


def choose_profile(profile: str | None, hint: str | None) -> tuple[str, dict | None]:
    """Choose a profile based on explicit name or hint."""
    if profile:
        return profile, None
    if hint:
        recommender = load_recommender()
        recommendation = recommender.recommend(hint)
        return recommendation["profile"], recommendation
    raise ValueError("either --profile or --hint is required")


def run_optional(command: list[str], cwd: Path, label: str):
    """Run an optional command and report status."""
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        if result.stdout.strip():
            print(result.stdout.strip())
    else:
        print(f"[WARN] {label} failed: {result.stderr.strip() or result.stdout.strip()}")


def run_step_with_lib(step: dict, context: dict, index: int, total: int) -> bool:
    """Execute a step using the shared library StepExecutor."""
    ManifestStep = _quickscan_lib.ManifestStep
    
    executor = _quickscan_lib.StepExecutor()
    manifest_step = ManifestStep(
        phase=step.get("phase", "unknown"),
        script=step["script"],
        args=step.get("args", []),
        optional=step.get("optional", False),
    )
    
    result = executor.run_step(manifest_step, context, index)
    
    if not result.success:
        print(f"[!] Step failed with exit code {result.returncode}: {step['script']}", file=sys.stderr)
        if result.stderr:
            print(f"    stderr: {result.stderr}", file=sys.stderr)
        return False
    
    return True


def run_step_legacy(step: dict, context: dict, index: int, total: int) -> bool:
    """Execute a step using legacy subprocess approach."""
    argv = [str(ROOT / "scripts" / step["script"])] + [arg for arg in substitute(step.get("args", []), context) if arg]
    print(f"[{index}/{total}] {' '.join(argv)}")
    result = subprocess.run(argv, cwd=ROOT)
    if result.returncode != 0:
        print(f"[!] Step failed with exit code {result.returncode}: {step['script']}", file=sys.stderr)
        return False
    return True


def run_step(step: dict, context: dict, index: int, total: int) -> bool:
    """Execute a step using shared library or legacy fallback."""
    if HAS_LIB:
        try:
            return run_step_with_lib(step, context, index, total)
        except Exception as e:
            print(f"[WARN] Shared library step execution failed: {e}", file=sys.stderr)
    return run_step_legacy(step, context, index, total)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run quick security scan profile")
    parser.add_argument("--profile", default="", help="Quick-scan profile name or path")
    parser.add_argument("--hint", default="", help="Free-text target description used to auto-select a profile")
    parser.add_argument("--target", required=True, help="Target host, URL, or domain")
    parser.add_argument("--engagement", default="", help="Engagement folder name (defaults to quick-<profile>-<timestamp>)")
    parser.add_argument("--mode", choices=["safe", "fast"], default="safe", help="Execution mode")
    parser.add_argument("--account", default="hatlesswhite@gmail.com", help="Google account used for quick report publishing")
    parser.add_argument("--no-publish", action="store_true", help="Skip export/publish after report generation")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be executed without running")
    args = parser.parse_args()

    chosen_profile, recommendation = choose_profile(args.profile or None, args.hint or None)
    manifest_path = resolve_profile_path(chosen_profile)
    manifest = load_quick_manifest(manifest_path)
    engagement = args.engagement or f"quick-{manifest.get('name', manifest_path.stem)}-{datetime.now().strftime('%Y-%m-%d_%H%M')}"
    ensure_reporting_dir(engagement)

    print(f"[*] Running quick scan profile: {manifest.get('name', manifest_path.stem)}")
    if recommendation:
        print(f"[*] Auto-selected from hint: {args.hint}")
        print(f"[*] Selection reason: {recommendation['reason']}")
    print(f"[*] Engagement: {engagement}")
    print(f"[*] Mode: {args.mode}")
    if args.dry_run:
        print(f"[*] DRY-RUN: No commands will actually execute")

    steps = manifest.get("steps", [])
    executed_steps = 0
    fingerprint: dict = {}
    
    # Build execution context
    context = {
        "target": args.target,
        "engagement": engagement,
        "latest_enum_json": latest_enum_json(engagement),
        "mode": args.mode,
        **MODE_DEFAULTS[args.mode],
    }
    
    base_step_count = len(steps)
    idx = 0
    while idx < len(steps):
        step = steps[idx]
        display_idx = idx + 1
        if should_skip_step(step, args.mode):
            print(f"[{display_idx}/{len(steps)}] SKIP optional step in {args.mode} mode: {step.get('script')}")
            idx += 1
            continue
        
        if args.dry_run:
            argv = [str(ROOT / "scripts" / step["script"])] + [arg for arg in substitute(step.get("args", []), context) if arg]
            print(f"[{display_idx}/{len(steps)}] DRY-RUN: {' '.join(argv)}")
            executed_steps += 1
            idx += 1
            continue
        
        if run_step(step, context, display_idx, len(steps)):
            executed_steps += 1
        else:
            return 1

        if idx == base_step_count - 1:
            fingerprint = run_fingerprint(engagement, manifest.get("name", manifest_path.stem), args.target)
            extra_steps = fingerprint.get("extra_steps", []) if isinstance(fingerprint, dict) else []
            if extra_steps:
                print(f"[*] Adaptive quick-scan overlays detected: {', '.join(fingerprint.get('profiles_considered', [])) or 'target-specific checks'}")
                steps.extend(extra_steps)
        idx += 1

    # Generate phase summaries for recon, enum, vuln
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

    # Generate quick report
    report_script = ROOT / "scripts" / "quick-scan" / "generate_quick_report.py"
    if report_script.exists():
        subprocess.run([
            "python3", str(report_script), 
            "--engagement", engagement, 
            "--profile", manifest.get("name", manifest_path.stem), 
            "--target", args.target, 
            "--mode", args.mode, 
            "--steps", str(executed_steps)
        ], cwd=ROOT, check=False)

    # Export and publish (unless disabled)
    if not args.no_publish and not args.dry_run:
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
