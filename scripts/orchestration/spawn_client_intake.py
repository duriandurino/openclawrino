#!/usr/bin/env python3
"""Spawn a client intake instance from an immutable master template.

Supports two modes:
- workspace copy mode from a local markdown template
- Google Drive copy mode from an existing Drive/Docs template via gog

Usage examples:
  python3 scripts/orchestration/spawn_client_intake.py \
    --template-type full \
    --pentester-name "Hatless White" \
    --google-drive

  python3 scripts/orchestration/spawn_client_intake.py \
    --template-type short \
    --pentester-name "Jane Doe" \
    --date-override 04-20-2026 \
    --source /path/to/client-intake-short.md \
    --destination-dir reports/intake

  python3 scripts/orchestration/spawn_client_intake.py \
    --template-type full \
    --pentester-name testrino \
    --google-drive \
    --drive-parent 0AFS1ouZ1oLMdUk9PVA
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DESTINATION_DIR = WORKSPACE_ROOT / "reports" / "intake"
DEFAULT_DRIVE_TEMPLATE_IDS = {
    "full": "11ELR6KlwL6xj3UMt4xOz4XyNm06YZ3s8FBefgdwEnGM",
    "short": "1cMPqzi8YgM5W1fEOhrr2oXpjVovWJngR0TSST6bKF4M",
}
DEFAULT_DRIVE_PARENT = "0AFS1ouZ1oLMdUk9PVA"


@dataclass
class SpawnResult:
    ok: bool
    template_type: str
    pentester_name: str
    sanitized_pentester_name: str
    date_stamp: str
    output_name: str
    output_path: str | None
    source_path: str | None
    created: bool
    mode: str
    message: str
    drive_file_id: str | None = None
    drive_web_view_link: str | None = None
    drive_parent: str | None = None


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
        "--google-drive",
        action="store_true",
        help="Copy from the configured Google Drive template instead of local filesystem templates",
    )
    parser.add_argument(
        "--drive-template-id",
        help="Explicit Google Drive template file ID to copy from",
    )
    parser.add_argument(
        "--drive-parent",
        default=DEFAULT_DRIVE_PARENT,
        help="Destination Google Drive folder ID for copied files",
    )
    parser.add_argument(
        "--gog-account",
        help="Optional gog account email to use for Drive commands",
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


def run_gog_json(command: list[str]) -> dict:
    env = os.environ.copy()
    if not env.get("GOG_KEYRING_PASSWORD"):
        fallback = WORKSPACE_ROOT / ".google-creds"
        if fallback.exists() and fallback.is_file():
            try:
                env["GOG_KEYRING_PASSWORD"] = fallback.read_text(encoding="utf-8").strip()
            except OSError:
                pass
    proc = subprocess.run(command, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        stderr = (proc.stderr or proc.stdout).strip()
        raise SpawnError(f"gog command failed: {' '.join(command)} :: {stderr}")

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SpawnError(f"gog output was not valid JSON: {exc}") from exc


def spawn_drive_copy(
    template_type: str,
    pentester_name: str,
    date_override: str | None,
    drive_template_id: str | None,
    drive_parent: str | None,
    gog_account: str | None,
) -> SpawnResult:
    normalized_type = normalize_template_type(template_type)
    pentester_slug = sanitize_name(pentester_name)
    date_stamp = normalize_date(date_override)
    output_name = build_output_name(normalized_type, date_stamp, pentester_slug)
    template_id = drive_template_id or DEFAULT_DRIVE_TEMPLATE_IDS.get(normalized_type)

    if not template_id:
        raise SpawnError(f"no Drive template id configured for template type '{normalized_type}'")

    command = ["gog", "drive", "copy", template_id, output_name, "--json"]
    if drive_parent:
        command.extend(["--parent", drive_parent])
    if gog_account:
        command.extend(["--account", gog_account])

    result = run_gog_json(command)
    file_info = result.get("file") or {}
    file_id = file_info.get("id")
    web_view = file_info.get("webViewLink")

    if not file_id:
        raise SpawnError("Drive copy succeeded but no file id was returned")

    return SpawnResult(
        ok=True,
        template_type=normalized_type,
        pentester_name=pentester_name,
        sanitized_pentester_name=pentester_slug,
        date_stamp=date_stamp,
        output_name=output_name,
        output_path=None,
        source_path=template_id,
        created=True,
        mode="google-drive-copy",
        message="Spawned a new client intake instance from the Google Drive template.",
        drive_file_id=file_id,
        drive_web_view_link=web_view,
        drive_parent=drive_parent,
    )


def main() -> int:
    args = parse_args()
    try:
        if args.google_drive:
            result = spawn_drive_copy(
                template_type=args.template_type,
                pentester_name=args.pentester_name,
                date_override=args.date_override,
                drive_template_id=args.drive_template_id,
                drive_parent=args.drive_parent,
                gog_account=args.gog_account,
            )
        else:
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
        "driveFileId": result.drive_file_id,
        "driveWebViewLink": result.drive_web_view_link,
        "driveParent": result.drive_parent,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
