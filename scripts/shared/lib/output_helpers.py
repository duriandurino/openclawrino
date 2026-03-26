#!/usr/bin/env python3
"""Output path and artifact helpers for phase automation."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def timestamp_now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def slugify(value: str) -> str:
    cleaned = []
    for ch in value.lower().strip():
        if ch.isalnum():
            cleaned.append(ch)
        elif ch in ("-", "_", "."):
            cleaned.append("-")
        else:
            cleaned.append("-")
    slug = "".join(cleaned)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "target"


def ensure_phase_dirs(base_dir: str | Path, engagement: str, phase: str) -> dict[str, Path]:
    root = Path(base_dir) / "engagements" / engagement / phase
    raw_dir = root / "raw"
    parsed_dir = root / "parsed"
    summaries_dir = root / "summaries"
    for path in (raw_dir, parsed_dir, summaries_dir):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "root": root,
        "raw": raw_dir,
        "parsed": parsed_dir,
        "summaries": summaries_dir,
    }


def artifact_paths(base_dir: str | Path, engagement: str, phase: str, prefix: str, target: str, raw_ext: str = "txt") -> dict[str, Path]:
    dirs = ensure_phase_dirs(base_dir, engagement, phase)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    target_slug = slugify(target)
    stem = f"{prefix}-{target_slug}-{ts}"
    return {
        "root": dirs["root"],
        "raw": dirs["raw"] / f"{stem}.{raw_ext}",
        "parsed": dirs["parsed"] / f"{stem}.json",
        "summary": dirs["summaries"] / f"{stem}.md",
        "timestamp": ts,
    }


def write_json(path: str | Path, payload: dict) -> None:
    Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: str | Path, content: str) -> None:
    Path(path).write_text(content, encoding="utf-8")
