#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "state"
LOG_DIR = ROOT / "logs"
PRESSURE_PATH = STATE_DIR / "context-pressure.json"
HANDOFF_PATH = STATE_DIR / "session-reset-handoff.json"
DEFAULT_WARNING = 40
DEFAULT_SNAPSHOT = 48
DEFAULT_COOLDOWN_MINUTES = 20
ALLOWED_STAGE_PATHS = [
    ROOT / "WORKING.md",
    ROOT / "STATE.md",
    ROOT / "DECISIONS.md",
    ROOT / "OPEN_LOOPS.md",
    ROOT / "docs" / "context-harness.md",
    ROOT / "state" / "context-pressure.json",
    ROOT / "state" / "session-reset-handoff.json",
]
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[a-z0-9._\-]+"),
]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=check)


def local_now() -> dt.datetime:
    os.environ.setdefault("TZ", "Asia/Manila")
    try:
        import time
        time.tzset()
    except Exception:
        pass
    return dt.datetime.now().astimezone()


def log_line(text: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = local_now().strftime("%Y-%m-%d %H:%M:%S %Z")
    with (LOG_DIR / "context-harness.log").open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {text}\n")


def sanitize(text: str) -> str:
    result = text
    for pattern in SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    return result.strip()


def current_session_key() -> str:
    return "agent:main:telegram:direct:6018252086"


def load_openclaw_status() -> dict[str, Any] | None:
    try:
        proc = run(["openclaw", "status", "--json"])
        return json.loads(proc.stdout)
    except Exception as exc:
        log_line(f"status-json unavailable: {exc}")
        return None


def load_sessions_store() -> dict[str, Any] | None:
    path = Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        log_line(f"sessions-store unavailable: {exc}")
        return None


def detect_pressure() -> dict[str, Any]:
    session_key = current_session_key()
    status = load_openclaw_status()
    if status:
        for item in status.get("sessions", {}).get("recent", []):
            if item.get("key") == session_key:
                percent = item.get("percentUsed")
                if percent is None:
                    total = item.get("totalTokens") or 0
                    window = item.get("contextTokens") or 0
                    percent = round((total / window) * 100) if window else None
                return {
                    "sessionKey": session_key,
                    "source": "openclaw-status",
                    "percentUsed": percent,
                    "totalTokens": item.get("totalTokens"),
                    "contextTokens": item.get("contextTokens"),
                    "remainingTokens": item.get("remainingTokens"),
                    "sessionId": item.get("sessionId"),
                }
    store = load_sessions_store() or {}
    entry = store.get(session_key)
    if isinstance(entry, dict):
        percent = entry.get("percentUsed")
        if percent is None:
            total = entry.get("totalTokens") or 0
            window = entry.get("contextTokens") or 0
            percent = round((total / window) * 100) if window else None
        return {
            "sessionKey": session_key,
            "source": "sessions-store",
            "percentUsed": percent,
            "totalTokens": entry.get("totalTokens"),
            "contextTokens": entry.get("contextTokens"),
            "remainingTokens": entry.get("remainingTokens"),
            "sessionId": entry.get("sessionId"),
        }
    transcript = transcript_path_from_store(store, session_key)
    size = transcript.stat().st_size if transcript and transcript.exists() else None
    return {
        "sessionKey": session_key,
        "source": "heuristic-transcript-size",
        "percentUsed": None,
        "transcriptBytes": size,
        "sessionId": None,
    }


def transcript_path_from_store(store: dict[str, Any], session_key: str) -> Path | None:
    entry = store.get(session_key)
    if isinstance(entry, dict) and entry.get("sessionFile"):
        return Path(entry["sessionFile"])
    return None


def git_branch() -> str:
    return run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()


def git_head() -> str:
    return run(["git", "rev-parse", "--short", "HEAD"]).stdout.strip()


def tracked_status() -> list[str]:
    return [line for line in run(["git", "status", "--short"]).stdout.splitlines() if line.strip()]


def content_hash(parts: list[str]) -> str:
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_markdown(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def render_list(items: list[str], empty: str = "- none") -> str:
    if not items:
        return empty
    return "\n".join(f"- {sanitize(item)}" for item in items)


def update_memory_append(summary: str, next_steps: list[str], files: list[str], trigger: str) -> Path:
    date_str = local_now().strftime("%Y-%m-%d")
    path = ROOT / "memory" / f"{date_str}.md"
    if path.exists():
        prefix = "\n"
    else:
        prefix = f"# Memory — {date_str}\n\n"
    lines = [
        prefix,
        f"## Context harness snapshot — {local_now().strftime('%Y-%m-%d %H:%M:%S %Z')}\n\n",
        f"- Trigger: {sanitize(trigger)}\n",
        f"- Summary: {sanitize(summary)}\n",
    ]
    if next_steps:
        lines.append("- Next steps:\n")
        for item in next_steps:
            lines.append(f"  - {sanitize(item)}\n")
    if files:
        lines.append("- Files of interest:\n")
        for item in files:
            lines.append(f"  - `{sanitize(item)}`\n")
    lines.append(f"- Handoff artifact: `{HANDOFF_PATH.relative_to(ROOT)}`\n\n")
    with path.open("a", encoding="utf-8") as f:
        f.writelines(lines)
    return path


def stage_allowed() -> None:
    rels = [str(path.relative_to(ROOT)) for path in ALLOWED_STAGE_PATHS if path.exists()]
    if rels:
        run(["git", "add", *rels])


def stage_extra(paths: list[Path]) -> None:
    rels = [str(path.relative_to(ROOT)) for path in paths if path.exists()]
    if rels:
        run(["git", "add", *rels])


def commit_if_needed(message: str) -> str | None:
    proc = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode == 0:
        return None
    run(["git", "commit", "-m", message])
    return git_head()


def push_safely() -> tuple[bool, str | None]:
    branch = git_branch()
    proc = subprocess.run(["git", "push", "origin", branch], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode == 0:
        return True, None
    log_line(f"push failed: {proc.stderr.strip() or proc.stdout.strip()}")
    return False, (proc.stderr.strip() or proc.stdout.strip() or "push failed")


def snapshot(args: argparse.Namespace) -> int:
    pressure = detect_pressure()
    warning_threshold = args.warning_threshold
    snapshot_threshold = args.snapshot_threshold
    percent = pressure.get("percentUsed")
    pressure_state = "unknown"
    if isinstance(percent, int | float):
        if percent >= snapshot_threshold:
            pressure_state = "snapshot"
        elif percent >= warning_threshold:
            pressure_state = "warning"
        else:
            pressure_state = "normal"

    branch = git_branch()
    head_before = git_head()
    existing = read_json(PRESSURE_PATH, {})

    key_points = [sanitize(x) for x in args.key_point]
    decisions = [sanitize(x) for x in args.decision]
    blockers = [sanitize(x) for x in args.blocker]
    next_steps = [sanitize(x) for x in args.next_step]
    files = [sanitize(x) for x in args.file]
    preferences = [sanitize(x) for x in args.preference]
    current_task = sanitize(args.current_task)
    objective = sanitize(args.objective)
    assumption_lines = [sanitize(x) for x in args.assumption]
    trigger = sanitize(args.trigger)

    assembled = [current_task, objective, *key_points, *decisions, *blockers, *next_steps, *files, *preferences, *assumption_lines, pressure_state, str(percent)]
    snapshot_hash = content_hash(assembled)
    last_hash = existing.get("lastSnapshotHash")
    last_snapshot_at = existing.get("lastSnapshotAt")

    cooldown_ok = True
    if last_snapshot_at:
        try:
            last_dt = dt.datetime.fromisoformat(last_snapshot_at)
            cooldown_ok = (local_now() - last_dt).total_seconds() >= args.cooldown_minutes * 60
        except Exception:
            cooldown_ok = True

    should_snapshot = args.force or pressure_state == "snapshot"
    if pressure_state == "warning" and args.allow_warning_snapshot:
        should_snapshot = True
    if snapshot_hash == last_hash and not args.force:
        should_snapshot = False
    if not cooldown_ok and not args.force:
        should_snapshot = False

    pressure_record = {
        "updatedAt": local_now().isoformat(timespec="seconds"),
        "sessionKey": pressure.get("sessionKey"),
        "sessionId": pressure.get("sessionId"),
        "source": pressure.get("source"),
        "percentUsed": percent,
        "totalTokens": pressure.get("totalTokens"),
        "contextTokens": pressure.get("contextTokens"),
        "remainingTokens": pressure.get("remainingTokens"),
        "warningThreshold": warning_threshold,
        "snapshotThreshold": snapshot_threshold,
        "pressureState": pressure_state,
        "lastSnapshotHash": last_hash,
        "lastSnapshotAt": last_snapshot_at,
        "shouldSnapshot": should_snapshot,
    }

    working_md = f"# WORKING.md\n\n## Current objective\n{objective}\n\n## Current task\n{current_task}\n\n## Key context\n{render_list(key_points)}\n\n## Exact next actions\n{render_list(next_steps)}\n\n## Critical files\n{render_list(files)}\n"
    state_md = f"# STATE.md\n\n## Session pressure\n- state: {pressure_state}\n- percent used: {percent if percent is not None else 'unknown'}\n- source: {pressure.get('source')}\n- branch: {branch}\n- head before snapshot: {head_before}\n\n## Blockers\n{render_list(blockers)}\n\n## Preferences in play\n{render_list(preferences)}\n"
    decisions_md = f"# DECISIONS.md\n\n## Current decisions\n{render_list(decisions)}\n\n## Assumptions to preserve\n{render_list(assumption_lines)}\n"
    open_loops_md = f"# OPEN_LOOPS.md\n\n## Open loops\n{render_list(blockers)}\n\n## Next steps\n{render_list(next_steps)}\n"

    handoff = {
        "updatedAt": local_now().isoformat(timespec="seconds"),
        "trigger": trigger,
        "pressure": pressure_record,
        "currentTask": current_task,
        "objective": objective,
        "keyPoints": key_points,
        "decisions": decisions,
        "blockers": blockers,
        "nextSteps": next_steps,
        "files": files,
        "preferences": preferences,
        "assumptions": assumption_lines,
        "branch": branch,
        "headBefore": head_before,
        "gitStatusBefore": tracked_status(),
        "snapshotHash": snapshot_hash,
    }

    if args.dry_run:
        print(json.dumps({"pressure": pressure_record, "shouldSnapshot": should_snapshot, "handoff": handoff}, indent=2))
        return 0

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    write_markdown(ROOT / "WORKING.md", working_md)
    write_markdown(ROOT / "STATE.md", state_md)
    write_markdown(ROOT / "DECISIONS.md", decisions_md)
    write_markdown(ROOT / "OPEN_LOOPS.md", open_loops_md)

    pressure_record["lastSnapshotHash"] = snapshot_hash if should_snapshot else last_hash
    pressure_record["lastSnapshotAt"] = local_now().isoformat(timespec="seconds") if should_snapshot else last_snapshot_at
    write_json(PRESSURE_PATH, pressure_record)

    memory_path = None
    if should_snapshot:
        write_json(HANDOFF_PATH, handoff)
        memory_path = update_memory_append(current_task, next_steps, files, trigger)
        log_line(f"snapshot written at {pressure_state} using {pressure.get('source')}")
    else:
        log_line(f"no snapshot needed, state={pressure_state}, changed={snapshot_hash != last_hash}, cooldown_ok={cooldown_ok}")

    stage_allowed()

    commit_sha = None
    pushed = False
    push_error = None
    if args.commit and should_snapshot:
        message = f"chore(harness): save session state at {percent if percent is not None else 'unknown'}pct context pressure"
        commit_sha = commit_if_needed(message)
        if commit_sha and args.push:
            pushed, push_error = push_safely()

    result = {
        "pressure": pressure_record,
        "shouldSnapshot": should_snapshot,
        "committed": bool(commit_sha),
        "commit": commit_sha,
        "pushed": pushed,
        "pushError": push_error,
        "handoffPath": str(HANDOFF_PATH.relative_to(ROOT)),
        "memoryPath": str(memory_path.relative_to(ROOT)) if memory_path else None,
        "memoryCommitted": False,
    }
    print(json.dumps(result, indent=2))
    return 0


def pressure_cmd(_: argparse.Namespace) -> int:
    print(json.dumps(detect_pressure(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Durable context pressure harness for OpenClaw workspace continuity.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_pressure = sub.add_parser("pressure", help="Read current session pressure.")
    p_pressure.set_defaults(func=pressure_cmd)

    p_snap = sub.add_parser("snapshot", help="Write/update working state and optionally git checkpoint it.")
    p_snap.add_argument("--current-task", required=True)
    p_snap.add_argument("--objective", required=True)
    p_snap.add_argument("--key-point", action="append", default=[])
    p_snap.add_argument("--decision", action="append", default=[])
    p_snap.add_argument("--blocker", action="append", default=[])
    p_snap.add_argument("--next-step", action="append", default=[])
    p_snap.add_argument("--file", action="append", default=[])
    p_snap.add_argument("--preference", action="append", default=[])
    p_snap.add_argument("--assumption", action="append", default=[])
    p_snap.add_argument("--trigger", default="manual")
    p_snap.add_argument("--warning-threshold", type=int, default=DEFAULT_WARNING)
    p_snap.add_argument("--snapshot-threshold", type=int, default=DEFAULT_SNAPSHOT)
    p_snap.add_argument("--cooldown-minutes", type=int, default=DEFAULT_COOLDOWN_MINUTES)
    p_snap.add_argument("--allow-warning-snapshot", action="store_true")
    p_snap.add_argument("--force", action="store_true")
    p_snap.add_argument("--commit", action="store_true")
    p_snap.add_argument("--push", action="store_true")
    p_snap.add_argument("--dry-run", action="store_true")
    p_snap.set_defaults(func=snapshot)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
