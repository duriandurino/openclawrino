#!/usr/bin/env python3
"""Spawn a client intake instance from an immutable master template.

This helper is intentionally workspace-first:
- it can duplicate a local markdown template file when available
- it can also prepare the target filename even when the real Drive-backed template
  lives outside the workspace and must be handled later by a Google/Drive flow

Usage examples:
  python3 scripts/orchestration/spawn_client_intake.py \
    --template-type full \
    --pentester-name "Hatless White"

  python3 scripts/orchestration/spawn_client_intake.py \
    --template-type short \
    --pentester-name "Jane Doe" \
    --date-override 04-20-2026 \
    --source /path/to/client-intake-short.md \
    --destination-dir reports/intake
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DESTINATION_DIR = WORKSPACE_ROOT / "reports" / "intake"


@dataclass
class SpawnResult:
    ok: bool
    template_type: str
    pentester_name: str
    sanitized_pentester_name: str
    date_stamp: str
    output_name: str
    output_path: str
    source_path: str | None
    created: bool
    mode: str
    message: str


class SpawnError(Exception):
    pass


def sanitize_name(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    if not lowered:
        raise SpawnError("Pentester name becomes empty after sanitization")
    return lowered


def normalize_template_type(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"full", "short"}:
        raise SpawnError("template type must be 'full' or 'short'")
    return normalized


def normalize_date(value: str | None) -> str:
    if not value:
        return datetime.now().strftime("%m-%d-%Y")

    for fmt in ("%m-%d-%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%m-%d-%Y")
        except ValueError:
            continue

    raise SpawnError("date override must be MM-DD-YYYY, YYYY-MM-DD, or MM/DD/YYYY")


def discover_default_source(template_type: str) -> Path | None:
    target_name = f"client-intake-{template_type}.md"
    candidates = [
        WORKSPACE_ROOT / "reports" / "templates" / target_name,
        WORKSPACE_ROOT / "templates" / target_name,
        WORKSPACE_ROOT / target_name,
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-type", required=True, help="full or short")
    parser.add_argument("--pentester-name", required=True, help="Pentester display name")
    parser.add_argument("--date-override", help="Optional date override")
    parser.add_argument(
        "--source",
        help="Optional explicit source template path. If omitted, local workspace discovery is attempted.",
    )
    parser.add_argument(
        "--destination-dir",
        default=str(DEFAULT_DESTINATION_DIR),
        help="Directory for the spawned markdown copy",
    )
    parser.add_argument(
        "--allow-overwrite",
        action="store_true",
        help="Overwrite an existing spawned file if it already exists",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output",
    )
    return parser.parse_args()


def build_output_name(template_type: str, date_stamp: str, pentester_slug: str) -> str:
    return f"client-intake-{template_type}-{date_stamp}-{pentester_slug}.md"


def spawn_copy(
    template_type: str,
    pentester_name: str,
    date_override: str | None,
    source: str | None,
    destination_dir: str,
    allow_overwrite: bool,
) -> SpawnResult:
    normalized_type = normalize_template_type(template_type)
    pentester_slug = sanitize_name(pentester_name)
    date_stamp = normalize_date(date_override)
    output_name = build_output_name(normalized_type, date_stamp, pentester_slug)
    destination = Path(destination_dir).expanduser().resolve()
    output_path = destination / output_name

    explicit_source = Path(source).expanduser().resolve() if source else None
    resolved_source = explicit_source or discover_default_source(normalized_type)

    if resolved_source is None:
        return SpawnResult(
            ok=True,
            template_type=normalized_type,
            pentester_name=pentester_name,
            sanitized_pentester_name=pentester_slug,
            date_stamp=date_stamp,
            output_name=output_name,
            output_path=str(output_path),
            source_path=None,
            created=False,
            mode="plan-only",
            message=(
                "No local source template was found. Prepared the target filename/path only. "
                "Use this with the Drive/Docs duplication flow once auth is available."
            ),
        )

    if not resolved_source.exists() or not resolved_source.is_file():
        raise SpawnError(f"source template does not exist: {resolved_source}")

    destination.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not allow_overwrite:
        raise SpawnError(
            f"destination already exists: {output_path}. Use --allow-overwrite to replace it."
        )

    shutil.copy2(resolved_source, output_path)

    return SpawnResult(
        ok=True,
        template_type=normalized_type,
        pentester_name=pentester_name,
        sanitized_pentester_name=pentester_slug,
        date_stamp=date_stamp,
        output_name=output_name,
        output_path=str(output_path),
        source_path=str(resolved_source),
        created=True,
        mode="workspace-copy",
        message="Spawned a new client intake instance from the local template.",
    )


def main() -> int:
    args = parse_args()
    try:
        result = spawn_copy(
            template_type=args.template_type,
            pentester_name=args.pentester_name,
            date_override=args.date_override,
            source=args.source,
            destination_dir=args.destination_dir,
            allow_overwrite=args.allow_overwrite,
        )
    except SpawnError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    payload = {
        "ok": result.ok,
        "templateType": result.template_type,
        "pentesterName": result.pentester_name,
        "sanitizedPentesterName": result.sanitized_pentester_name,
        "dateStamp": result.date_stamp,
        "outputName": result.output_name,
        "outputPath": result.output_path,
        "sourcePath": result.source_path,
        "created": result.created,
        "mode": result.mode,
        "message": result.message,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
