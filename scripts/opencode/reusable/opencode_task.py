#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WATCHER = ROOT / "scripts" / "opencode" / "reusable" / "opencode_watch.py"
MODE_DIR = ROOT / ".opencode" / "modes"

MODE_HINTS = {
    "plan": "Use plan mode. Focus on the smallest useful design before building.",
    "build": "Use build mode. Implement the requested coding task directly and keep it practical.",
}


def load_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_mode_text(mode: str) -> str:
    mode_map = {
        "plan": MODE_DIR / "authorized-scripting-plan.md",
        "build": MODE_DIR / "authorized-scripting-build.md",
    }
    path = mode_map.get(mode)
    if not path or not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def assemble_prompt(mode: str, utility_class: str, task_text: str, extra_context: str) -> str:
    parts = [
        "You are OpenCode assisting with an authorized coding workflow.",
        f"Mode: {mode}",
        f"Utility class: {utility_class}",
        MODE_HINTS.get(mode, ""),
        "Keep dependencies minimal unless clearly justified.",
        "Summarize what you planned or built, the assumptions, and how to reuse the result.",
    ]
    mode_text = load_mode_text(mode)
    if mode_text:
        parts.extend(["", "Mode guidance:", mode_text.strip()])
    if extra_context.strip():
        parts.extend(["", "Additional context:", extra_context.strip()])
    parts.extend(["", "Task:", task_text.strip()])
    return "\n".join([p for p in parts if p is not None])


def main() -> int:
    parser = argparse.ArgumentParser(description="Thin task wrapper for watcher-backed OpenCode runs")
    parser.add_argument("--task", default="", help="Task text to send to OpenCode")
    parser.add_argument("--task-file", default="", help="Path to a file containing the task text")
    parser.add_argument("--mode", choices=["plan", "build"], default="build")
    parser.add_argument("--utility-class", choices=["throwaway", "session", "reusable"], default="reusable")
    parser.add_argument("--context-file", action="append", default=[], help="Optional context file(s) to append")
    parser.add_argument("--cwd", default=str(ROOT), help="Working directory for OpenCode")
    parser.add_argument("--model", default="opencode/minimax-m2.5-free")
    parser.add_argument("--fallback-model", default="opencode/gpt-5-nano")
    parser.add_argument("--timeout", type=float, default=240.0)
    parser.add_argument("--stall-timeout", type=float, default=60.0)
    parser.add_argument("--thinking", action="store_true")
    parser.add_argument("--save", default="", help="Optional path to save watcher JSON output")
    parser.add_argument("--json", action="store_true", help="Emit watcher output as JSON")
    args = parser.parse_args()

    task_text = args.task.strip()
    if args.task_file:
        task_text = load_file(args.task_file).strip()
    if not task_text:
        raise SystemExit("Provide --task or --task-file")

    extra_context_parts = []
    for path in args.context_file:
        p = Path(path)
        extra_context_parts.append(f"# Context from {p}\n{p.read_text(encoding='utf-8', errors='ignore').strip()}")
    prompt = assemble_prompt(args.mode, args.utility_class, task_text, "\n\n".join(extra_context_parts))

    cmd = [
        sys.executable,
        str(WATCHER),
        "--prompt",
        prompt,
        "--model",
        args.model,
        "--fallback-model",
        args.fallback_model,
        "--cwd",
        args.cwd,
        "--timeout",
        str(args.timeout),
        "--stall-timeout",
        str(args.stall_timeout),
    ]
    if args.thinking:
        cmd.append("--thinking")
    if args.save:
        cmd.extend(["--save", args.save])
    if args.json:
        cmd.append("--json")

    raise SystemExit(subprocess.run(cmd, cwd=ROOT).returncode)


if __name__ == "__main__":
    main()
