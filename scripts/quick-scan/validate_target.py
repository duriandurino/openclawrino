#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run focused validation checks after quick scan")
    parser.add_argument("--target", required=True)
    parser.add_argument("--engagement", required=True)
    parser.add_argument("--profile", required=True, choices=sorted(VALIDATION_PROFILES.keys()))
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
            return result.returncode

    summary_path = ROOT / "engagements" / args.engagement / "validation"
    summary_path.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    note = summary_path / f"VALIDATION_SUMMARY_{ts}.md"
    note.write_text(
        f"# Focused Validation Summary\n\n- Target: `{args.target}`\n- Profile: `{args.profile}`\n- Engagement: `{args.engagement}`\n- Status: complete\n\nReview the generated enum/vuln artifacts for confirmed posture details.\n",
        encoding="utf-8",
    )
    print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
