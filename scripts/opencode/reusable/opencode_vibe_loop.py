#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RISKY_COMMAND_PATTERNS = [
    re.compile(r"\brm\s+-rf\b"),
    re.compile(r"\bgit\s+push\b"),
    re.compile(r"\bgit\s+reset\s+--hard\b"),
    re.compile(r"\bgit\s+clean\b"),
    re.compile(r"\bnpm\s+publish\b"),
    re.compile(r"\bpnpm\s+publish\b"),
    re.compile(r"\bgh\s+pr\s+merge\b"),
    re.compile(r"\bsudo\b"),
    re.compile(r"\bsystemctl\s+(restart|stop)\b"),
    re.compile(r"\bdocker\s+compose\s+down\b"),
]

QUESTION_PATTERNS = [
    re.compile(r"\?$"),
    re.compile(r"\bwhich (?:option|approach|one)\b", re.I),
    re.compile(r"\bshould i\b", re.I),
    re.compile(r"\bdo you want\b", re.I),
    re.compile(r"\bcan you confirm\b", re.I),
    re.compile(r"\bplease confirm\b", re.I),
    re.compile(r"\bhow would you like\b", re.I),
]


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def append_jsonl(path: Path | None, payload: dict[str, Any]) -> None:
    if not path:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def normalize_tool_event(part: dict[str, Any]) -> dict[str, Any]:
    state = part.get("state") or {}
    tool_name = part.get("tool") or part.get("type")
    input_payload = state.get("input") or {}
    command = input_payload.get("command") if isinstance(input_payload, dict) else None
    output = state.get("output")
    return {
        "tool": tool_name,
        "status": state.get("status"),
        "command": command,
        "title": state.get("title") or input_payload.get("description") if isinstance(input_payload, dict) else None,
        "output": output,
    }


def classify_turn(text: str, tool_events: list[dict[str, Any]], returncode: int) -> tuple[str, list[str]]:
    notes: list[str] = []
    if returncode != 0:
        return "failed", ["OpenCode exited with a non-zero status."]

    risky = []
    for event in tool_events:
        command = event.get("command") or ""
        if any(pattern.search(command) for pattern in RISKY_COMMAND_PATTERNS):
            risky.append(command)
    if risky:
        notes.append(f"Risky command attention: {len(risky)} command(s) matched review patterns.")
        return "needs_review", notes

    compact = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if compact and any(pattern.search(compact) for pattern in QUESTION_PATTERNS):
        notes.append("Assistant is asking for task guidance or confirmation.")
        return "needs_input", notes

    if compact:
        notes.append("Turn completed with a concrete assistant response.")
        return "turn_complete", notes

    notes.append("Turn finished without assistant text; inspect raw event log.")
    return "turn_complete", notes


def build_notify_text(label: str, status: str, session_id: str | None, text: str, tool_events: list[dict[str, Any]]) -> str:
    short_text = " ".join(line.strip() for line in text.splitlines() if line.strip())
    short_text = short_text[:280] + ("…" if len(short_text) > 280 else "")
    tool_count = len(tool_events)
    parts = [f"Vibe coder update ({label})", f"status={status}"]
    if session_id:
        parts.append(f"session={session_id}")
    parts.append(f"tools={tool_count}")
    if short_text:
        parts.append(f"message={short_text}")
    return " | ".join(parts)


def notify_openclaw(text: str) -> None:
    subprocess.run(
        ["openclaw", "system", "event", "--text", text, "--mode", "now"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or continue an OpenCode turn and summarize it for nested vibe-coding workflows.")
    parser.add_argument("message", nargs="*", help="Message to send to OpenCode for this turn")
    parser.add_argument("--continue-last", action="store_true", help="Continue the last OpenCode session in this working directory")
    parser.add_argument("--model", help="OpenCode model override")
    parser.add_argument("--cwd", default=".", help="Working directory for the OpenCode turn")
    parser.add_argument("--label", default="opencode-vibe", help="Short label used in state and notifications")
    parser.add_argument("--state-file", help="Write a compact JSON summary to this path")
    parser.add_argument("--event-log", help="Append raw OpenCode JSON events to this JSONL path")
    parser.add_argument("--notify-openclaw", action="store_true", help="Send an OpenClaw system event when the turn completes")
    args = parser.parse_args()

    if not args.message and not args.continue_last:
        parser.error("Provide a message or use --continue-last.")

    cwd = Path(args.cwd).resolve()
    state_file = Path(args.state_file).resolve() if args.state_file else None
    event_log = Path(args.event_log).resolve() if args.event_log else None

    cmd = ["opencode", "run", "--format", "json"]
    if args.model:
        cmd.extend(["-m", args.model])
    if args.continue_last:
        cmd.append("-c")
    cmd.extend(args.message)

    process = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assistant_parts: list[str] = []
    tool_events: list[dict[str, Any]] = []
    session_id: str | None = None
    raw_lines: list[str] = []

    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\n")
        raw_lines.append(line)
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            append_jsonl(event_log, {"type": "raw", "line": line, "timestamp": iso_now()})
            continue
        append_jsonl(event_log, payload)
        session_id = session_id or payload.get("sessionID")
        event_type = payload.get("type")
        part = payload.get("part") or {}
        if event_type == "text":
            assistant_parts.append(part.get("text") or "")
        elif event_type in {"tool_use", "tool"}:
            tool_events.append(normalize_tool_event(part))

    returncode = process.wait()
    assistant_text = "".join(assistant_parts).strip()
    status, notes = classify_turn(assistant_text, tool_events, returncode)

    summary = {
        "label": args.label,
        "cwd": str(cwd),
        "session_id": session_id,
        "status": status,
        "notes": notes,
        "assistant_text": assistant_text,
        "tool_events": tool_events,
        "raw_event_count": len(raw_lines),
        "returncode": returncode,
        "updated_at": iso_now(),
        "continue_hint": f"python3 {shlex.quote(str(Path(__file__).resolve()))} --cwd {shlex.quote(str(cwd))} --continue-last --label {shlex.quote(args.label)}",
    }

    if state_file:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.notify_openclaw:
        notify_openclaw(build_notify_text(args.label, status, session_id, assistant_text, tool_events))

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if returncode == 0 else returncode


if __name__ == "__main__":
    raise SystemExit(main())
