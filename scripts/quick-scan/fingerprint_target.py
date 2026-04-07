#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]


def latest_file(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def load_json(path: Path | None) -> dict:
    if not path or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}


def normalize_target(target: str) -> tuple[str, str]:
    if re.match(r"^https?://", target, re.I):
        parsed = urlparse(target)
        return "web", parsed.netloc or target
    if re.match(r"^[A-Za-z0-9._-]+\.[A-Za-z]{2,}$", target):
        return "web", target
    return "host", target


def detect_from_headers(findings: list[dict], body_text: str) -> dict:
    headers = []
    titles = []
    whatweb = []
    for item in findings:
        t = str(item.get("type", "")).lower()
        val = str(item.get("value", ""))
        if t == "header":
            headers.append(val)
        elif t == "title":
            titles.append(val)
        elif t == "whatweb":
            whatweb.append(val)

    header_blob = "\n".join(headers).lower()
    whatweb_blob = "\n".join(whatweb).lower()
    body_blob = body_text.lower()

    frameworks: list[str] = []
    traits: list[str] = []
    deployments: list[str] = []
    surfaces: list[str] = []

    if "vercel" in header_blob or "x-vercel" in header_blob or "vercel" in whatweb_blob:
        deployments.append("vercel")
    if "netlify" in header_blob or "netlify" in whatweb_blob:
        deployments.append("netlify")
    if "cloudfront" in header_blob or "cloudfront" in whatweb_blob:
        deployments.append("cloudfront")
    if "nginx" in header_blob or "nginx" in whatweb_blob:
        deployments.append("nginx")
    if "apache" in header_blob or "apache" in whatweb_blob:
        deployments.append("apache")

    if "next.js" in whatweb_blob or "_next/" in body_blob or "next/static" in body_blob:
        frameworks.append("nextjs")
    if "nestjs" in whatweb_blob or "swagger-ui" in body_blob or "/api-json" in body_blob:
        frameworks.append("nestjs")
    if "graphql" in body_blob or "graphql" in whatweb_blob:
        frameworks.append("graphql")
        surfaces.append("graphql")
    if "openapi" in body_blob or "swagger" in body_blob or "swagger" in whatweb_blob:
        surfaces.append("api-docs")
    if any(token in body_blob for token in ["webhook", "callback endpoint", "signature verification"]):
        surfaces.append("webhook")
    if any(token in body_blob for token in ["login", "sign in", "auth", "oauth"]):
        traits.append("auth-facing")
    if any(token in body_blob for token in ["api", "json"]):
        traits.append("api-backed")
    if "__next_data__" in body_blob or "_next/" in body_blob:
        traits.append("ssr-or-hybrid")
    if "react" in whatweb_blob or "__next" in body_blob or "id=\"root\"" in body_blob:
        traits.append("spa-or-js-heavy")

    return {
        "frameworks": sorted(set(frameworks)),
        "deployments": sorted(set(deployments)),
        "surfaces": sorted(set(surfaces)),
        "traits": sorted(set(traits)),
        "titles": titles[:3],
    }


def detect_from_services(enum_text: str, vuln_text: str) -> dict:
    blob = f"{enum_text}\n{vuln_text}".lower()
    frameworks: list[str] = []
    traits: list[str] = []
    deployments: list[str] = []
    surfaces: list[str] = []

    if "3389/tcp" in blob or "rdp" in blob:
        surfaces.append("rdp")
        traits.append("windows-management")
    if "445/tcp" in blob or "smb" in blob:
        surfaces.append("smb")
        traits.append("windows-management")
    if "5985/tcp" in blob or "5986/tcp" in blob or "winrm" in blob:
        surfaces.append("winrm")
        traits.append("windows-management")
    if "22/tcp" in blob or "ssh" in blob:
        surfaces.append("ssh")
    if "1883" in blob or "8883" in blob or "mqtt" in blob:
        surfaces.append("mqtt")
        traits.append("broker-connected")
    if "pulselink" in blob:
        frameworks.append("pulselink")
        traits.append("player")
    if "rpcbind" in blob:
        traits.append("unix-service-surface")
    if "mysql" in blob or "3306/tcp" in blob:
        surfaces.append("mysql")

    return {
        "frameworks": sorted(set(frameworks)),
        "deployments": deployments,
        "surfaces": sorted(set(surfaces)),
        "traits": sorted(set(traits)),
        "titles": [],
    }


def build_overlay(profile: str, fp: dict) -> dict:
    extra_steps: list[dict] = []
    report_focus: list[str] = []
    profiles_considered: list[str] = []

    frameworks = set(fp.get("frameworks", []))
    surfaces = set(fp.get("surfaces", []))
    traits = set(fp.get("traits", []))
    deployments = set(fp.get("deployments", []))

    if profile in {"webapp", "webapp-deep", "api", "api-auth"}:
        if "graphql" in frameworks or "graphql" in surfaces:
            profiles_considered.append("graphql")
            extra_steps.extend([
                {"phase": "enum", "script": "enum/web/enum_graphql_basic.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
                {"phase": "vuln", "script": "vuln/web/vuln_graphql_baseline.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
            ])
            report_focus.append("graphql surface and schema exposure")
        if "nestjs" in frameworks or "api-docs" in surfaces:
            profiles_considered.append("nestjs-api")
            extra_steps.extend([
                {"phase": "enum", "script": "enum/web/enum_nestjs_api.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
                {"phase": "vuln", "script": "vuln/web/vuln_nestjs_baseline.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
            ])
            report_focus.append("swagger/openapi and framework-specific exposure")
        if "webhook" in surfaces:
            profiles_considered.append("webhook")
            extra_steps.extend([
                {"phase": "enum", "script": "enum/web/enum_webhook_basic.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
                {"phase": "vuln", "script": "vuln/web/vuln_webhook_baseline.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
            ])
            report_focus.append("callback authenticity and webhook trust boundaries")
        if "vercel" in deployments:
            report_focus.append("deployment-layer clues from vercel hosting")
        if "cloudfront" in deployments:
            report_focus.append("cdn-origin exposure and cache-facing behavior")
        if "auth-facing" in traits:
            report_focus.append("authentication flow and access-control surface")

    if profile in {"player", "player-pulselink", "host", "windows-host", "linux-host", "pc", "iot-mqtt"}:
        if "mqtt" in surfaces and profile != "iot-mqtt":
            profiles_considered.append("iot-mqtt")
            report_focus.append("broker exposure, topic trust, and device identity")
        if "pulselink" in frameworks:
            report_focus.append("PulseLink-specific player indicators")
        if "windows-management" in traits:
            report_focus.append("administrative remote management exposure")

    return {
        "extra_steps": extra_steps,
        "report_focus": sorted(set(report_focus)),
        "profiles_considered": sorted(set(profiles_considered)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fingerprint a quick-scan target and produce adaptive hints")
    parser.add_argument("--engagement", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    base = ROOT / "engagements" / args.engagement
    quickscan_dir = base / "quick-scan"
    quickscan_dir.mkdir(parents=True, exist_ok=True)

    recon_json = latest_file(base / "recon" / "parsed", "*.json") if (base / "recon" / "parsed").exists() else None
    enum_summary = latest_file(base / "enum", "ENUM_SUMMARY_*.md") if (base / "enum").exists() else None
    vuln_summary = latest_file(base / "vuln", "VULN_SUMMARY_*.md") if (base / "vuln").exists() else None
    raw_body_candidates = sorted((base / "vuln" / "raw").glob("*body.txt"), key=lambda p: p.stat().st_mtime) if (base / "vuln" / "raw").exists() else []

    target_kind, normalized = normalize_target(args.target)
    recon = load_json(recon_json)
    recon_findings = recon.get("findings", []) if isinstance(recon, dict) else []
    body_text = raw_body_candidates[-1].read_text(encoding="utf-8", errors="ignore") if raw_body_candidates else ""
    enum_text = enum_summary.read_text(encoding="utf-8", errors="ignore") if enum_summary else ""
    vuln_text = vuln_summary.read_text(encoding="utf-8", errors="ignore") if vuln_summary else ""

    if target_kind == "web":
        fp = detect_from_headers(recon_findings, body_text)
    else:
        fp = detect_from_services(enum_text, vuln_text)

    overlay = build_overlay(args.profile, fp)
    data = {
        "target": args.target,
        "normalized_target": normalized,
        "profile": args.profile,
        "target_kind": target_kind,
        "frameworks": fp.get("frameworks", []),
        "deployments": fp.get("deployments", []),
        "surfaces": fp.get("surfaces", []),
        "traits": fp.get("traits", []),
        "titles": fp.get("titles", []),
        "profiles_considered": overlay["profiles_considered"],
        "report_focus": overlay["report_focus"],
        "extra_steps": overlay["extra_steps"],
        "generated": datetime.now().astimezone().isoformat(),
    }

    out_path = quickscan_dir / "fingerprint.json"
    out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
