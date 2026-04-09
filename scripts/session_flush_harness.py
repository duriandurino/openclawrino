#!/usr/bin/env python3
"""Create a tracked reset snapshot, append a memory note, and optionally git commit/push.

This harness is meant to be called by the operator near context pressure, for example
when session usage is approaching 50 percent. It does not attempt to introspect live
model context directly. Instead, it packages the current verified session state into a
stable, git-tracked handoff artifact so the session can be reset safely.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
RESET_STATE_PATH = STATE_DIR / "session-reset-handoff.json"


def run(cmd: list[str], cwd: Path = ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


def now_local() -> dt.datetime:
    return dt.datetime.now().astimezone()


def iso_now() -> str:
    return now_local().isoformat(timespec="seconds")


def current_branch() -> str:
    proc = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return proc.stdout.strip()


def head_commit() -> str:
    proc = run(["git", "rev-parse", "--short", "HEAD"])
    return proc.stdout.strip()


def tracked_status_lines() -> list[str]:
    proc = run(["git", "status", "--short"])
    lines = [line.rstrip() for line in proc.stdout.splitlines() if line.strip()]
    return lines


def append_memory_note(memory_path: Path, handoff: dict) -> None:
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if memory_path.exists() and memory_path.stat().st_size > 0:
        existing = memory_path.read_text(encoding="utf-8")
        if not existing.endswith("\n"):
            lines.append("\n")
    else:
        lines.append(f"# Memory — {handoff['date']}\n\n")

    lines.extend(
        [
            f"## Session flush — {handoff['timestamp_local']}\n\n",
            f"- Trigger: {handoff['trigger']}\n",
            f"- Goal: preserve reset-ready context before session reset\n",
            f"- Summary: {handoff['summary']}\n",
        ]
    )

    if handoff["key_points"]:
        lines.append("- Key points:\n")
        for point in handoff["key_points"]:
            lines.append(f"  - {point}\n")

    if handoff["next_actions"]:
        lines.append("- Next actions:\n")
        for action in handoff["next_actions"]:
            lines.append(f"  - {action}\n")

    if handoff["files"]:
        lines.append("- Files of interest:\n")
        for file_path in handoff["files"]:
            lines.append(f"  - `{file_path}`\n")

    lines.append(
        f"- Tracked handoff artifact: `{handoff['handoff_path']}`\n"
    )
    lines.append(
        f"- Git state before flush commit: branch `{handoff['branch']}`, head `{handoff['head_before']}`\n\n"
    )

    with memory_path.open("a", encoding="utf-8") as f:
        f.writelines(lines)


def stage_paths(paths: Iterable[Path]) -> None:
    rels = [str(path.relative_to(ROOT)) for path in paths]
    if rels:
        run(["git", "add", *rels])


def commit_if_needed(message: str) -> str | None:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode == 0:
        return None
    run(["git", "commit", "-m", message])
    return head_commit()


def push_current_branch() -> None:
    branch = current_branch()
    run(["git", "push", "origin", branch])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save reset-ready session context and optionally git sync it.")
    parser.add_argument("--summary", required=True, help="One-line summary of the session state to preserve.")
    parser.add_argument("--key-point", action="append", default=[], help="Repeat for important verified context.")
    parser.add_argument("--next-action", action="append", default=[], help="Repeat for likely follow-up actions after reset.")
    parser.add_argument("--file", action="append", default=[], help="Repeat for important workspace files or artifacts.")
    parser.add_argument("--trigger", default="manual-near-50-percent", help="Why the flush was triggered.")
    parser.add_argument("--memory-date", help="Override memory file date as YYYY-MM-DD. Defaults to local today.")
    parser.add_argument("--no-push", action="store_true", help="Commit but do not push.")
    parser.add_argument("--dry-run", action="store_true", help="Write no files and perform no git changes.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    os.environ.setdefault("TZ", "Asia/Manila")
    try:
        import time
        time.tzset()
    except Exception:
        pass

    timestamp = now_local()
    date_str = args.memory_date or timestamp.strftime("%Y-%m-%d")
    memory_path = ROOT / "memory" / f"{date_str}.md"

    handoff = {
        "timestamp_local": timestamp.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "timestamp_iso": iso_now(),
        "date": date_str,
        "trigger": args.trigger,
        "summary": args.summary.strip(),
        "key_points": [item.strip() for item in args.key_point if item.strip()],
        "next_actions": [item.strip() for item in args.next_action if item.strip()],
        "files": [item.strip() for item in args.file if item.strip()],
        "branch": current_branch(),
        "head_before": head_commit(),
        "git_status_before": tracked_status_lines(),
        "handoff_path": str(RESET_STATE_PATH.relative_to(ROOT)),
    }

    if args.dry_run:
        print(json.dumps(handoff, indent=2))
        return 0

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    RESET_STATE_PATH.write_text(json.dumps(handoff, indent=2) + "\n", encoding="utf-8")
    append_memory_note(memory_path, handoff)

    stage_paths([RESET_STATE_PATH, memory_path])

    commit_message = f"Save reset handoff: {args.summary[:60]}".strip()
    new_commit = commit_if_needed(commit_message)
    if new_commit and not args.no_push:
        push_current_branch()

    result = {
        "handoff_path": str(RESET_STATE_PATH.relative_to(ROOT)),
        "memory_path": str(memory_path.relative_to(ROOT)),
        "branch": current_branch(),
        "head_before": handoff["head_before"],
        "head_after": new_commit or handoff["head_before"],
        "pushed": bool(new_commit) and not args.no_push,
        "committed": bool(new_commit),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
