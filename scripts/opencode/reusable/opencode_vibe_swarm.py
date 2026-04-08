#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOOP = ROOT / "scripts" / "opencode" / "reusable" / "opencode_vibe_loop.py"
DEFAULT_SWARM_ROOT = ROOT / "engagements" / "tmp" / "vibe-swarm"


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch or continue a named OpenCode vibe-coding lane for main-agent or sub-agent swarm workflows.")
    parser.add_argument("message", nargs="*", help="Message for this lane's OpenCode turn")
    parser.add_argument("--lane", required=True, help="Short lane name, for example main, recon-helper, report-fix")
    parser.add_argument("--cwd", default=str(ROOT), help="Working directory for this lane")
    parser.add_argument("--root", default=str(DEFAULT_SWARM_ROOT), help="Root directory for swarm state/event files")
    parser.add_argument("--model", help="OpenCode model override")
    parser.add_argument("--continue-last", action="store_true", help="Continue the last OpenCode session for this lane")
    parser.add_argument("--notify-openclaw", action="store_true", help="Send an OpenClaw wake event after the lane turn finishes")
    args = parser.parse_args()

    if not args.message and not args.continue_last:
        parser.error("Provide a message or use --continue-last.")

    lane = args.lane.strip().replace("/", "-")
    swarm_root = Path(args.root).resolve()
    lane_dir = swarm_root / lane
    lane_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "python3",
        str(LOOP),
        "--cwd",
        str(Path(args.cwd).resolve()),
        "--label",
        lane,
        "--state-file",
        str(lane_dir / "state.json"),
        "--event-log",
        str(lane_dir / "events.jsonl"),
    ]
    if args.model:
        cmd.extend(["--model", args.model])
    if args.continue_last:
        cmd.append("--continue-last")
    if args.notify_openclaw:
        cmd.append("--notify-openclaw")
    cmd.extend(args.message)

    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
