#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PROFILE_RULES = [
    {
        "profile": "player-pulselink",
        "score": 100,
        "tokens": ["pulselink", "n-compass", "nctv", "player"],
        "reason": "Target hints strongly match a PulseLink / player environment.",
    },
    {
        "profile": "iot-mqtt",
        "score": 95,
        "tokens": ["mqtt", "broker", "iot", "telemetry"],
        "reason": "Target hints suggest MQTT or IoT messaging exposure.",
    },
    {
        "profile": "api-auth",
        "score": 90,
        "tokens": ["api auth", "api-auth", "swagger", "openapi", "token", "bearer", "jwt", "auth"],
        "reason": "Target hints suggest API authentication and docs surface concerns.",
    },
    {
        "profile": "api",
        "score": 80,
        "tokens": ["api", "/v1", "endpoint", "rest", "graphql"],
        "reason": "Target hints suggest an API surface.",
    },
    {
        "profile": "webapp-deep",
        "score": 78,
        "tokens": ["deep web", "deeper web", "webapp deep", "active paths"],
        "reason": "Target hints request deeper web triage.",
    },
    {
        "profile": "webapp",
        "score": 70,
        "tokens": ["webapp", "website", "http", "https", "frontend", "landing page"],
        "reason": "Target hints suggest a web application.",
    },
    {
        "profile": "windows-host",
        "score": 75,
        "tokens": ["windows", "rdp", "winrm", "smb", "workstation", "desktop"],
        "reason": "Target hints suggest a Windows host or workstation.",
    },
    {
        "profile": "linux-host",
        "score": 75,
        "tokens": ["linux", "ssh", "ubuntu", "debian", "centos", "server"],
        "reason": "Target hints suggest a Linux host.",
    },
    {
        "profile": "host",
        "score": 50,
        "tokens": ["host", "ip", "server", "machine", "device"],
        "reason": "Target hints suggest a generic host/service surface.",
    },
]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def recommend(text: str) -> dict:
    normalized = normalize(text)
    scored = []
    for rule in PROFILE_RULES:
        matched = [token for token in rule["tokens"] if token in normalized]
        if matched:
            scored.append({
                "profile": rule["profile"],
                "score": rule["score"] + len(matched),
                "reason": rule["reason"],
                "matched": matched,
            })
    if not scored:
        return {
            "profile": "host",
            "score": 0,
            "reason": "No strong target-type hints matched; defaulting to generic host triage.",
            "matched": [],
            "alternatives": ["webapp", "api", "windows-host", "linux-host"],
        }
    scored.sort(key=lambda item: item["score"], reverse=True)
    best = scored[0]
    best["alternatives"] = [item["profile"] for item in scored[1:4]]
    return best


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend a quick-scan profile from simple target hints")
    parser.add_argument("--hint", required=True, help="Free-text description of the target")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    result = recommend(args.hint)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Recommended profile: {result['profile']}")
        print(f"Reason: {result['reason']}")
        if result.get('matched'):
            print(f"Matched hints: {', '.join(result['matched'])}")
        if result.get('alternatives'):
            print(f"Alternatives: {', '.join(result['alternatives'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
