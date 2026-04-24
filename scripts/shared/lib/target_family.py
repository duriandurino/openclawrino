#!/usr/bin/env python3
"""Helpers for full-pentest target-family composition and recommendations."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FAMILIES_FILE = ROOT / "scripts" / "shared" / "target-types" / "families.yaml"

FAMILY_HINT_RULES = [
    {
        "family": "player-pulselink",
        "score": 120,
        "tokens": ["pulselink", "n-compass", "nctv", "player"],
        "reason": "Hints strongly match a PulseLink-style player environment.",
    },
    {
        "family": "player",
        "score": 100,
        "tokens": ["player", "kiosk", "signage", "embedded player"],
        "reason": "Hints match a composite player or kiosk target.",
    },
    {
        "family": "raspi",
        "score": 90,
        "tokens": ["raspi", "raspberry pi", "rpi", "gpio"],
        "reason": "Hints match a Raspberry Pi or embedded Linux device.",
    },
    {
        "family": "electron-app",
        "score": 88,
        "tokens": ["electron", "desktop app", "chromium shell", "kiosk ui"],
        "reason": "Hints match an Electron-based app surface.",
    },
    {
        "family": "python-app",
        "score": 84,
        "tokens": ["python", "flask", "fastapi", "django", "uvicorn", "gunicorn"],
        "reason": "Hints match a Python-backed application or service.",
    },
    {
        "family": "linux-host",
        "score": 75,
        "tokens": ["linux", "ubuntu", "debian", "ssh", "server"],
        "reason": "Hints match a Linux host baseline.",
    },
]


def _load_with_python_yaml(path: Path) -> dict | None:
    try:
        import yaml  # type: ignore
    except Exception:
        return None
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


def load_target_families(path: Path | None = None) -> dict:
    families_path = path or DEFAULT_FAMILIES_FILE
    data = _load_with_python_yaml(families_path)
    if data is None:
        raise RuntimeError(
            "PyYAML is required to load full-pentest target-family definitions. "
            "Install python3-yaml or ensure yaml is importable."
        )
    return data


def _merge_lists(*values):
    merged = []
    seen = set()
    for value in values:
        if not value:
            continue
        for item in value:
            marker = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
            if marker in seen:
                continue
            seen.add(marker)
            merged.append(deepcopy(item))
    return merged


def _merge_phase_block(base: dict | None, extra: dict | None) -> dict:
    out = deepcopy(base or {})
    extra = extra or {}
    for key, value in extra.items():
        if key in {"notes", "capabilities", "recommended_profiles", "manifests"}:
            out[key] = _merge_lists(out.get(key, []), value)
        elif isinstance(value, dict) and isinstance(out.get(key), dict):
            nested = deepcopy(out[key])
            nested.update(deepcopy(value))
            out[key] = nested
        else:
            out[key] = deepcopy(value)
    return out


def compose_family(name: str, data: dict | None = None, _seen: set[str] | None = None) -> dict:
    data = data or load_target_families()
    families = data.get("families", {})
    if name not in families:
        raise KeyError(f"unknown target family: {name}")

    seen = set(_seen or set())
    if name in seen:
        raise ValueError(f"cyclic target-family inheritance detected at: {name}")
    seen.add(name)

    raw = families[name]
    composed: dict = {
        "name": name,
        "description": raw.get("description", ""),
        "extends": list(raw.get("extends", [])),
        "tags": [],
        "target_kinds": [],
        "default_entrypoints": {},
        "phases": {},
        "lineage": [],
    }

    for parent_name in raw.get("extends", []):
        parent = compose_family(parent_name, data=data, _seen=seen)
        composed["tags"] = _merge_lists(composed["tags"], parent.get("tags", []))
        composed["target_kinds"] = _merge_lists(composed["target_kinds"], parent.get("target_kinds", []))
        composed["lineage"] = _merge_lists(composed["lineage"], parent.get("lineage", []), [parent_name])
        defaults = deepcopy(parent.get("default_entrypoints", {}))
        defaults.update(composed.get("default_entrypoints", {}))
        composed["default_entrypoints"] = defaults
        for phase_name, phase_block in parent.get("phases", {}).items():
            composed["phases"][phase_name] = _merge_phase_block(composed["phases"].get(phase_name), phase_block)

    composed["tags"] = _merge_lists(composed["tags"], raw.get("tags", []))
    composed["target_kinds"] = _merge_lists(composed["target_kinds"], raw.get("target_kinds", []))
    defaults = deepcopy(composed.get("default_entrypoints", {}))
    defaults.update(deepcopy(raw.get("default_entrypoints", {})))
    composed["default_entrypoints"] = defaults

    for phase_name, phase_block in raw.get("phases", {}).items():
        composed["phases"][phase_name] = _merge_phase_block(composed["phases"].get(phase_name), phase_block)

    composed["lineage"] = _merge_lists(composed["lineage"], [name])
    return composed


def normalize_hint(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def recommend_target_family(hint: str, data: dict | None = None) -> dict:
    data = data or load_target_families()
    normalized = normalize_hint(hint)
    matches = []

    for rule in FAMILY_HINT_RULES:
        matched = [token for token in rule["tokens"] if token in normalized]
        if matched:
            matches.append({
                "family": rule["family"],
                "score": rule["score"] + len(matched),
                "reason": rule["reason"],
                "matched": matched,
            })

    if not matches:
        fallback = compose_family("linux-host", data=data)
        return {
            "family": "linux-host",
            "score": 0,
            "reason": "No strong family hints matched; defaulting to linux-host as the safest generic full-pentest baseline.",
            "matched": [],
            "alternatives": ["raspi", "python-app", "electron-app"],
            "composed": fallback,
        }

    matches.sort(key=lambda item: item["score"], reverse=True)
    best = matches[0]
    best["alternatives"] = [item["family"] for item in matches[1:4]]
    best["composed"] = compose_family(best["family"], data=data)
    return best


def list_families(data: dict | None = None) -> list[dict]:
    data = data or load_target_families()
    out = []
    for name, info in sorted(data.get("families", {}).items()):
        out.append({
            "name": name,
            "description": info.get("description", ""),
            "extends": info.get("extends", []),
            "tags": info.get("tags", []),
        })
    return out
