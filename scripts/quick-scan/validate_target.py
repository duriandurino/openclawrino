#!/usr/bin/env python3
"""Run focused validation checks after quick scan.

Refactored to use quickscan_lib.py for shared functionality.
"""
from __future__ import annotations

import argparse
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
        get_workspace_root = _quickscan_lib.get_workspace_root
        safe_write_text = _quickscan_lib.safe_write_text
        HAS_LIB = True
    else:
        HAS_LIB = False
except Exception as e:
    print(f"[WARN] Could not import quickscan_lib: {e}", file=sys.stderr)
    HAS_LIB = False

VALIDATION_PROFILES = {
    "windows-host": [
        ["scripts/enum/smb/enum_smb_basic.sh", "--safe"],
        ["scripts/enum/rdp/rdp_probe.sh"],
        ["scripts/enum/winrm/winrm_probe.sh"],
    ],
    "web": [
        ["scripts/enum/web/enum_web_basic.sh", "--safe"],
        ["scripts/vuln/web/web_baseline.sh", "--safe"],
    ],
    "api": [
        ["scripts/recon/web/api_auth_probe.sh", "--safe"],
        ["scripts/enum/web/enum_web_basic.sh", "--safe"],
        ["scripts/vuln/web/web_baseline.sh", "--safe"],
    ],
}


def _legacy_write_summary(path: Path, content: str) -> None:
    """Legacy file write for backward compatibility."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_summary(path: Path, content: str) -> None:
    """Write summary file using shared library or legacy fallback."""
    if HAS_LIB:
        try:
            _quickscan_lib.safe_write_text(path, content)
            return
        except Exception as e:
            print(f"[WARN] Shared library write failed: {e}", file=sys.stderr)
    _legacy_write_summary(path, content)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run focused validation checks after quick scan")
    parser.add_argument("--target", required=True, help="Target host or URL")
    parser.add_argument("--engagement", required=True, help="Engagement folder name")
    parser.add_argument("--profile", required=True, choices=sorted(VALIDATION_PROFILES.keys()), 
                       help="Validation profile to use")
    args = parser.parse_args()

    steps = VALIDATION_PROFILES[args.profile]
    print(f"[*] Focused validation profile: {args.profile}")
    print(f"[*] Target: {args.target}")
    print(f"[*] Engagement: {args.engagement}")

    for idx, step in enumerate(steps, start=1):
        script = ROOT / step[0]
        argv = [str(script), "--target", args.target, "--engagement", args.engagement, *step[1:]]
        print(f"[{idx}/{len(steps)}] {' '.join(argv)}")
        result = subprocess.run(argv, cwd=ROOT)
        if result.returncode != 0:
            print(f"[!] Step {idx} failed with exit code {result.returncode}", file=sys.stderr)
            return result.returncode

    # Write summary
    summary_path = ROOT / "engagements" / args.engagement / "validation"
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    note = summary_path / f"VALIDATION_SUMMARY_{ts}.md"
    
    content = f"""# Focused Validation Summary

- Target: `{args.target}`
- Profile: `{args.profile}`
- Engagement: `{args.engagement}`
- Status: complete
- Steps executed: {len(steps)}

Review the generated enum/vuln artifacts for confirmed posture details.
"""
    write_summary(note, content)
    print(f"[✓] Validation summary written to: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
