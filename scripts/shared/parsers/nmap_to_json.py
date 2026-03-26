#!/usr/bin/env python3
"""Parse Nmap grepable output into a small JSON structure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_grepable(text: str) -> list[dict]:
    findings = []
    for line in text.splitlines():
        if "Ports:" not in line:
            continue
        try:
            _, ports_blob = line.split("Ports:", 1)
        except ValueError:
            continue
        for entry in [p.strip() for p in ports_blob.split(",") if p.strip()]:
            parts = entry.split("/")
            if len(parts) < 5:
                continue
            port, state, proto, _, service = parts[:5]
            if state != "open":
                continue
            findings.append({
                "port": int(port),
                "protocol": proto,
                "service": service or "unknown",
                "state": state,
            })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse Nmap grepable output into JSON")
    parser.add_argument("--input", required=True, help="Path to grepable Nmap output")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8", errors="ignore")
    payload = {"open_ports": parse_grepable(text)}
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
