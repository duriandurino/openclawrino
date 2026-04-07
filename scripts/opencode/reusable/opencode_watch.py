#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class WatchResult:
    status: str
    model: str
    fallback_used: bool
    exit_code: int | None
    duration_seconds: float
    last_event_type: str | None
    event_count: int
    text_chunks: int
    final_text: str
    error: str | None
    command: list[str]


def build_command(model: str, prompt: str, cwd: str | None, thinking: bool) -> list[str]:
    cmd = [
        "opencode",
        "run",
        "-m",
        model,
        "--format",
        "json",
    ]
    if cwd:
        cmd.extend(["--dir", cwd])
    if thinking:
        cmd.append("--thinking")
    cmd.append(prompt)
    return cmd


def run_once(model: str, prompt: str, cwd: str | None, total_timeout: float, stall_timeout: float, thinking: bool) -> WatchResult:
    command = build_command(model, prompt, cwd, thinking)
    started = time.monotonic()
    proc = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    last_event_at = time.monotonic()
    last_event_type: str | None = None
    event_count = 0
    text_chunks = 0
    text_parts: list[str] = []
    stderr_parts: list[str] = []
    error: str | None = None
    saw_error_event = False

    assert proc.stdout is not None
    assert proc.stderr is not None

    while True:
        if proc.poll() is not None:
            break

        now = time.monotonic()
        if now - started > total_timeout:
            error = f"total timeout after {total_timeout:.1f}s"
            proc.kill()
            break
        if now - last_event_at > stall_timeout:
            error = f"stall timeout after {stall_timeout:.1f}s without JSON event"
            proc.kill()
            break

        line = proc.stdout.readline()
        if not line:
            time.sleep(0.05)
            continue

        line = line.strip()
        if not line:
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            stderr_parts.append(f"non-json stdout: {line}")
            continue

        event_count += 1
        last_event_at = time.monotonic()
        last_event_type = str(event.get("type") or "unknown")

        if event.get("type") == "text":
            part = event.get("part") or {}
            text = part.get("text") or ""
            if text:
                text_chunks += 1
                text_parts.append(str(text))
        elif event.get("type") == "error":
            saw_error_event = True
            part = event.get("part") or {}
            message = part.get("message") or event.get("error") or line
            if message:
                error = str(message)

    try:
        _, stderr = proc.communicate(timeout=2)
        if stderr:
            stderr_parts.append(stderr.strip())
    except Exception:
        pass

    exit_code = proc.returncode
    duration = time.monotonic() - started
    final_text = "".join(text_parts).strip()

    if error and "timeout" in error:
        status = "timeout"
    elif saw_error_event:
        status = "failed"
    elif exit_code == 0:
        status = "success"
    else:
        status = "failed"
        if not stderr_parts and not final_text:
            error = "process exited without usable output"

    if stderr_parts and not error:
        joined = " | ".join([p for p in stderr_parts if p])
        if joined:
            error = joined

    return WatchResult(
        status=status,
        model=model,
        fallback_used=False,
        exit_code=exit_code,
        duration_seconds=round(duration, 3),
        last_event_type=last_event_type,
        event_count=event_count,
        text_chunks=text_chunks,
        final_text=final_text,
        error=error,
        command=command,
    )


def print_human(result: WatchResult) -> None:
    print(f"status: {result.status}")
    print(f"model: {result.model}")
    print(f"fallback_used: {result.fallback_used}")
    print(f"duration_seconds: {result.duration_seconds}")
    print(f"event_count: {result.event_count}")
    print(f"last_event_type: {result.last_event_type}")
    if result.final_text:
        print("final_text:")
        print(result.final_text)
    if result.error:
        print(f"error: {result.error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch an OpenCode run and return structured results")
    parser.add_argument("--prompt", required=True, help="Prompt to send to OpenCode")
    parser.add_argument("--model", default="opencode/minimax-m2.5-free", help="Primary model")
    parser.add_argument("--fallback-model", default="opencode/gpt-5-nano", help="Fallback model")
    parser.add_argument("--timeout", type=float, default=180.0, help="Hard timeout in seconds")
    parser.add_argument("--stall-timeout", type=float, default=45.0, help="Stall timeout in seconds")
    parser.add_argument("--cwd", default="", help="Working directory for OpenCode")
    parser.add_argument("--thinking", action="store_true", help="Enable OpenCode thinking output")
    parser.add_argument("--json", action="store_true", help="Emit final result as JSON")
    parser.add_argument("--save", default="", help="Optional path to save the JSON result")
    args = parser.parse_args()

    cwd = args.cwd or None
    primary = run_once(args.model, args.prompt, cwd, args.timeout, args.stall_timeout, args.thinking)
    result = primary

    fallback_allowed = bool(args.fallback_model and args.fallback_model != args.model)
    should_fallback = primary.status != "success"

    if should_fallback and fallback_allowed:
        fallback = run_once(args.fallback_model, args.prompt, cwd, args.timeout, args.stall_timeout, args.thinking)
        fallback.fallback_used = True
        result = fallback
        if primary.error and not fallback.error:
            fallback.error = f"primary_failed: {primary.error}"
        elif primary.error and fallback.error:
            fallback.error = f"primary_failed: {primary.error} | fallback_failed: {fallback.error}"

    payload = asdict(result)
    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_human(result)

    return 0 if result.status == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
