#!/usr/bin/env python3
"""Target validation and normalization helpers for phase automation."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse


def normalize_target(value: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError("target is empty")

    if value.startswith(("http://", "https://")):
        parsed = urlparse(value)
        if not parsed.netloc:
            raise ValueError(f"invalid URL target: {value}")
        return parsed.netloc.lower()

    return value.lower()


def detect_target_kind(value: str) -> str:
    target = normalize_target(value)

    try:
        ipaddress.ip_address(target)
        return "ip"
    except ValueError:
        pass

    try:
        ipaddress.ip_network(target, strict=False)
        return "cidr"
    except ValueError:
        pass

    if "." in target and "/" not in target:
        return "domain"

    return "host"


def validate_target(value: str, allowed_kinds: list[str] | None = None) -> tuple[str, str]:
    target = normalize_target(value)
    kind = detect_target_kind(target)
    if allowed_kinds and kind not in allowed_kinds:
        allowed = ", ".join(allowed_kinds)
        raise ValueError(f"target kind '{kind}' not allowed; expected one of: {allowed}")
    return target, kind
