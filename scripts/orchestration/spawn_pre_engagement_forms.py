#!/usr/bin/env python3
"""Spawn Google Drive pre-engagement form documents for soft commands.

Supports:
- /clientform -> pre-engage-form-<MM-DD-YYYY>-<HH-mm>.md
- /pentesterform <titleFlag> -> user-engagement-input-template-<title>-<MM-DD-YYYY>-<HH-mm>.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DRIVE_PARENT = "0AFS1ouZ1oLMdUk9PVA"
TEMPLATE_IDS = {
    "clientform": "1gh6UTEoTSRnTqRmMu3IecgCJspQ-zSAERokPGwKt4NM",
    "pentesterform": "1zrp-1ncvUaXDHabxl0OgQhOkYWo6S6HkXmy3-5P9Zgs",
}


class SpawnError(Exception):
    pass


def now_parts() -> tuple[str, str]:
    stamp = datetime.now()
    return stamp.strftime("%m-%d-%Y"), stamp.strftime("%H-%M")


def sanitize_title(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-")
    if not lowered:
        raise SpawnError("title becomes empty after sanitization")
    return lowered


def build_name(kind: str, title_flag: str | None) -> str:
    date_part, time_part = now_parts()
    if kind == "clientform":
        return f"pre-engage-form-{date_part}-{time_part}.md"
    if kind == "pentesterform":
        if not title_flag:
            raise SpawnError("titleFlag is required for pentesterform")
        return f"user-engagement-input-template-{sanitize_title(title_flag)}-{date_part}-{time_part}.md"
    raise SpawnError(f"unsupported kind: {kind}")


def run_gog_json(command: list[str]) -> dict:
    env = os.environ.copy()
    if not env.get("GOG_KEYRING_PASSWORD"):
        env["GOG_KEYRING_PASSWORD"] = "hatlesswhite"
    proc = subprocess.run(command, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        stderr = (proc.stderr or proc.stdout).strip()
        raise SpawnError(f"gog command failed: {' '.join(command)} :: {stderr}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SpawnError(f"gog output was not valid JSON: {exc}") from exc


def resolve_gog_account(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    env_value = os.environ.get("GOG_ACCOUNT")
    if env_value:
        return env_value
    return "hatlesswhite@gmail.com"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["clientform", "pentesterform"])
    parser.add_argument("--title-flag")
    parser.add_argument("--drive-parent", default=DEFAULT_DRIVE_PARENT)
    parser.add_argument("--gog-account")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        output_name = build_name(args.kind, args.title_flag)
        template_id = TEMPLATE_IDS[args.kind]
        command = ["gog", "drive", "copy", template_id, output_name, "--json"]
        if args.drive_parent:
            command.extend(["--parent", args.drive_parent])
        gog_account = resolve_gog_account(args.gog_account)
        if gog_account:
            command.extend(["--account", gog_account])
        result = run_gog_json(command)
        file_info = result.get("file") or {}
        payload = {
            "ok": True,
            "kind": args.kind,
            "outputName": output_name,
            "templateId": template_id,
            "driveFileId": file_info.get("id"),
            "driveWebViewLink": file_info.get("webViewLink"),
            "driveParent": args.drive_parent,
            "gogAccount": gog_account,
        }
    except SpawnError as exc:
        payload = {"ok": False, "error": str(exc)}

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for k, v in payload.items():
            print(f"{k}: {v}")

    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
