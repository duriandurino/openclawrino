#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


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
    # Handle URLs with or without scheme
    if "://" in target:
        parsed = urlparse(target)
        return "web", parsed.netloc or parsed.path or target
    # Handle bare domains (including those with ports)
    if re.match(r"^[A-Za-z0-9._-]+\.[A-Za-z]{2,}(:\d+)?$", target):
        return "web", target
    return "host", target


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text or "")


def extract_titles_from_whatweb(whatweb_lines: list[str]) -> list[str]:
    titles: list[str] = []
    for raw in whatweb_lines:
        clean = strip_ansi(raw)
        for match in re.finditer(r"Title\[([^\]]+)\]", clean, re.I):
            title = match.group(1).strip()
            if title:
                titles.append(title)
    return list(dict.fromkeys(titles))[:3]


def extract_titles_from_body(body_text: str) -> list[str]:
    if not body_text:
        return []
    titles: list[str] = []
    title_match = re.search(r"<title>(.*?)</title>", body_text, re.I | re.S)
    if title_match:
        titles.append(re.sub(r"\s+", " ", title_match.group(1)).strip())
    for meta_name in ["og:title", "twitter:title"]:
        meta_match = re.search(
            rf'<meta[^>]+(?:property|name)=["\']{re.escape(meta_name)}["\'][^>]+content=["\']([^"\']+)["\']',
            body_text,
            re.I,
        )
        if meta_match:
            titles.append(meta_match.group(1).strip())
    return list(dict.fromkeys([t for t in titles if t]))[:3]


def detect_from_headers(findings: list[dict], body_text: str, raw_headers: str = "", raw_response: str = "") -> dict:
    headers = []
    titles = []
    whatweb = []
    raw_header_list = []
    status_code = ""
    cookies = []
    
    for item in findings:
        t = str(item.get("type", "")).lower()
        val = str(item.get("value", ""))
        if t == "header":
            headers.append(val)
        elif t == "title":
            titles.append(val)
        elif t == "whatweb":
            whatweb.append(val)
        elif t == "status":
            status_code = val
    
    if raw_headers:
        for line in raw_headers.split("\n"):
            if ":" in line:
                raw_header_list.append(line.strip().lower())
            if "set-cookie" in line.lower():
                cookie_line = line.split(":", 1)[-1].strip() if ":" in line else line.strip()
                name = cookie_line.split("=")[0].strip() if "=" in cookie_line else ""
                if name:
                    cookies.append(name.lower())
    
    if raw_response:
        resp_lower = raw_response.lower()
        if resp_line := [l for l in raw_response.split("\n") if l.strip().startswith("HTTP/")]:
            if match := re.search(r"HTTP/[\d.]+ (\d+)", resp_line[0]):
                status_code = match.group(1)
    
    if not titles and whatweb:
        titles.extend(extract_titles_from_whatweb(whatweb))
    if not titles and body_text:
        titles.extend(extract_titles_from_body(body_text))

    cookie_blob = "\n".join(cookies).lower()
    header_blob = "\n".join(headers).lower()
    raw_header_blob = "\n".join(raw_header_list)
    whatweb_blob = strip_ansi("\n".join(whatweb)).lower()
    body_blob = body_text.lower()

    frameworks: list[str] = []
    traits: list[str] = []
    deployments: list[str] = []
    surfaces: list[str] = []
    server_hints: list[str] = []

    if "vercel" in header_blob or "x-vercel-id" in raw_header_blob or "vercel" in whatweb_blob:
        deployments.append("vercel")
    if "netlify" in header_blob or "netlify" in raw_header_blob or "netlify" in whatweb_blob:
        deployments.append("netlify")
    if "cloudfront" in header_blob or "x-amz-cf-id" in raw_header_blob or "cloudfront" in whatweb_blob:
        deployments.append("cloudfront")
    if "nginx" in header_blob or "nginx" in raw_header_blob or "nginx" in whatweb_blob:
        deployments.append("nginx")
        server_hints.append("nginx")
    if "apache" in header_blob or "apache" in raw_header_blob or "apache" in whatweb_blob:
        deployments.append("apache")
        server_hints.append("apache")
    if "cloudflare" in header_blob or "cf-ray" in raw_header_blob or "cloudflare" in whatweb_blob:
        deployments.append("cloudflare")
    if "x-served-by" in raw_header_blob and "cache" in raw_header_blob:
        deployments.append("fastly")
    if "x-azure-ref" in raw_header_blob:
        deployments.append("azure-cdn")
    if "server: awselb" in raw_header_blob or "server: awselb" in header_blob:
        deployments.append("aws-elb")

    if "x-amz-fn" in raw_header_blob or "x-amz-fw" in raw_header_blob:
        deployments.append("aws-lambda")
        surfaces.append("serverless")
    if "x-google" in raw_header_blob or "x-appengine" in raw_header_blob:
        deployments.append("google-cloud")
        surfaces.append("serverless")
    if "x-functions-version" in raw_header_blob:
        deployments.append("azure-functions")
        surfaces.append("serverless")

    if any(token in whatweb_blob for token in ["next.js", "x-nextjs-", "next-router", "x-matched-path"]) or "_next/" in body_blob or "next/static" in body_blob:
        frameworks.append("nextjs")
    if "nestjs" in whatweb_blob or "swagger-ui" in body_blob or "/api-json" in body_blob:
        frameworks.append("nestjs")
    if "graphql" in body_blob or "graphql" in whatweb_blob:
        frameworks.append("graphql")
        surfaces.append("graphql")
    if "openapi" in body_blob or "swagger" in body_blob or "swagger" in whatweb_blob:
        surfaces.append("api-docs")
    if any(token in body_blob for token in ["/api/v1", "/api/v2", "/api/v3", "/rest/", "/graphql", "/api/"]):
        surfaces.append("api")
    if any(token in body_blob for token in ["webhook", "callback endpoint", "signature verification"]):
        surfaces.append("webhook")
    if any(token in body_blob for token in ["login", "sign in", "auth", "oauth"]) and any(token in body_blob for token in ["/auth", "/login", "/signin", "/oauth"]):
        traits.append("auth-facing")
    if any(token in body_blob for token in ["api", "json", "restful"]):
        traits.append("api-backed")
    if "__next_data__" in body_blob or "_next/" in body_blob:
        traits.append("ssr-or-hybrid")
    if "react" in whatweb_blob or "__next" in body_blob or "id=\"root\"" in body_blob:
        traits.append("spa-or-js-heavy")
    
    if "x-django" in raw_header_blob:
        frameworks.append("django")
    if "x-powered-by: express" in raw_header_blob or "express" in whatweb_blob:
        frameworks.append("express")
    if "x-powered-by: fastapi" in raw_header_blob or "fastapi" in whatweb_blob:
        frameworks.append("fastapi")
    if "x-powered-by: asp.net" in raw_header_blob or "x-aspnet-version" in raw_header_blob:
        frameworks.append("aspnet")
    if "x-powered-by: php" in raw_header_blob or "laravel" in whatweb_blob or "x-powered-by" in raw_header_blob and "php" in raw_header_blob:
        frameworks.append("php")
        if "laravel" in whatweb_blob or "laravel" in body_blob:
            frameworks.append("laravel")
    
    if "x-request-id" in raw_header_blob or "x-correlation-id" in raw_header_blob:
        traits.append("dist-tracing")
    if "strict-transport-security" in raw_header_blob or "hsts" in header_blob:
        traits.append("tls-enforced")
    if "content-security-policy" in raw_header_blob:
        traits.append("csp-enabled")

    if cookie_blob:
        if any(c in cookie_blob for c in ["jsessionid", "jsess", "glassfish", "payara"]):
            frameworks.append("java-ee")
        if "phpsessid" in cookie_blob:
            frameworks.append("php")
            traits.append("php-session")
        if "asp.net_sessionid" in cookie_blob or "asp.net_sessionid" in raw_header_blob.lower():
            frameworks.append("aspnet")
        if "connect.sid" in cookie_blob or "connect.sid" in raw_header_blob.lower():
            frameworks.append("nextjs")
        if "nuxt" in cookie_blob:
            frameworks.append("nuxt")
        if any(c in cookie_blob for c in ["_session", "sid", "sess"]):
            if "rails" in whatweb_blob or ".rails" in cookie_blob:
                frameworks.append("rails")
        if "__cf_bm" in cookie_blob or "__cfduid" in cookie_blob:
            deployments.append("cloudflare")
            traits.append("cf-bot-protection")

    if status_code:
        if status_code.startswith("4") or status_code.startswith("5"):
            traits.append("error-response")
        elif status_code == "301" or status_code == "302" or status_code == "307" or status_code == "308":
            traits.append("redirect-response")

    if titles:
        title_blob = " ".join(titles).lower()
        if any(token in title_blob for token in ["portfolio", "engineer", "developer", "designer", "consultant"]):
            traits.append("portfolio-like")
        if any(token in title_blob for token in ["book", "library", "catalog", "shop", "store", "market", "fair"]):
            traits.append("catalog-like")

    return {
        "frameworks": sorted(set(frameworks)),
        "deployments": sorted(set(deployments)),
        "surfaces": sorted(set(surfaces)),
        "traits": sorted(set(traits)),
        "titles": list(dict.fromkeys(titles))[:3],
        "server_hints": sorted(set(server_hints)),
        "status_code": status_code,
        "cookies_detected": len(cookies),
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
        "deployments": sorted(set(deployments)),
        "surfaces": sorted(set(surfaces)),
        "traits": sorted(set(traits)),
        "titles": [],
    }


def build_overlay(profile: str, fp: dict, executed_steps: list[dict] | None = None) -> dict:
    extra_steps: list[dict] = []
    report_focus: list[str] = []
    profiles_considered: list[str] = []

    frameworks = set(fp.get("frameworks", []))
    surfaces = set(fp.get("surfaces", []))
    traits = set(fp.get("traits", []))
    deployments = set(fp.get("deployments", []))

    # Build set of already-executed script patterns to avoid duplication
    executed_scripts: set[str] = set()
    executed_patterns: set[str] = set()
    if executed_steps:
        for step in executed_steps:
            script = step.get("script", "")
            executed_scripts.add(script)
            # Also track by pattern (e.g., enum_graphql_basic.sh -> graphql)
            if "graphql" in script:
                executed_patterns.add("graphql")
            if "nestjs" in script:
                executed_patterns.add("nestjs")
            if "swagger" in script or "openapi" in script:
                executed_patterns.add("api-docs")
            if "webhook" in script:
                executed_patterns.add("webhook")
    # Phase-3: guard webapp/api overlays; remove GraphQL lightweight fallback overlays to avoid loose fallbacks
    if profile in {"webapp", "webapp-deep", "api", "api-auth"}:
        # GraphQL overlay only if there is an explicit GraphQL signal in titles
        if "graphql" in frameworks or "graphql" in surfaces:
            has_graphql_title = any("graphql" in (t or "").lower() for t in fp.get("titles", []))
            if has_graphql_title:
                if "graphql" not in executed_patterns:
                    profiles_considered.append("graphql")
                    extra_steps.extend([
                        {"phase": "enum", "script": "enum/web/enum_graphql_basic.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
                        {"phase": "vuln", "script": "vuln/web/vuln_graphql_baseline.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
                    ])
                    report_focus.append("graphql surface and schema exposure")
                else:
                    report_focus.append("graphql surface (already covered by base profile)")
            else:
                # No explicit GraphQL signal in titles; skip GraphQL overlay
                pass
        
        if "nestjs" in frameworks or "api-docs" in surfaces:
            # Skip if NestJS/Swagger steps already executed
            if "nestjs" not in executed_patterns and "api-docs" not in executed_patterns:
                profiles_considered.append("nestjs-api")
                extra_steps.extend([
                    {"phase": "enum", "script": "enum/web/enum_nestjs_api.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
                    {"phase": "vuln", "script": "vuln/web/vuln_nestjs_baseline.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
                ])
                report_focus.append("swagger/openapi and framework-specific exposure")
            else:
                report_focus.append("swagger/openapi framework indicators (already covered)")
                
        if "webhook" in surfaces:
            # Skip if webhook steps already executed
            if "webhook" not in executed_patterns:
                profiles_considered.append("webhook")
                extra_steps.extend([
                    {"phase": "enum", "script": "enum/web/enum_webhook_basic.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
                    {"phase": "vuln", "script": "vuln/web/vuln_webhook_baseline.sh", "args": ["--target", "{{target}}", "--engagement", "{{engagement}}", "{{safe_flag}}"]},
                ])
                report_focus.append("callback authenticity and webhook trust boundaries")
            else:
                report_focus.append("webhook surface (already covered by base profile)")
                
        if "vercel" in deployments:
            report_focus.append("deployment-layer clues from vercel hosting")
        if "cloudfront" in deployments:
            report_focus.append("cdn-origin exposure and cache-facing behavior")
        if "auth-facing" in traits:
            report_focus.append("authentication flow and access-control surface")

    # Phase-3 safety net: skip lightweight fallback overlays without explicit fingerprint signals.
    # Preserve quick-scan speed and general-purpose behavior.
    # (Overlay addition only when fingerprint detects specific frameworks/surfaces)

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
    parser.add_argument("--executed-steps-context", default="", help="JSON-encoded dict of phase->steps already executed (for deduplication)")
    args = parser.parse_args()

    base = ROOT / "engagements" / args.engagement
    quickscan_dir = base / "quick-scan"
    quickscan_dir.mkdir(parents=True, exist_ok=True)

    # Parse executed steps context for deduplication
    executed_steps: list[dict] = []
    if args.executed_steps_context:
        try:
            phase_artifacts = json.loads(args.executed_steps_context)
            # Flatten phase->steps into single list
            for phase, steps in phase_artifacts.items():
                if isinstance(steps, list):
                    executed_steps.extend(steps)
        except json.JSONDecodeError:
            pass  # Continue without deduplication

    recon_json = latest_file(base / "recon" / "parsed", "*.json") if (base / "recon" / "parsed").exists() else None
    enum_summary = latest_file(base / "enum", "ENUM_SUMMARY_*.md") if (base / "enum").exists() else None
    vuln_summary = latest_file(base / "vuln", "VULN_SUMMARY_*.md") if (base / "vuln").exists() else None
    recon_raw_dir = base / "recon" / "raw"
    vuln_raw_dir = base / "vuln" / "raw"
    raw_body_candidates = []
    raw_headers_candidates = []
    raw_response_candidates = []
    if recon_raw_dir.exists():
        raw_body_candidates.extend(sorted(recon_raw_dir.glob("*body.txt"), key=lambda p: p.stat().st_mtime))
        raw_headers_candidates.extend(sorted(recon_raw_dir.glob("*headers.txt"), key=lambda p: p.stat().st_mtime))
        raw_response_candidates.extend(sorted(recon_raw_dir.glob("*response.txt"), key=lambda p: p.stat().st_mtime))
    if vuln_raw_dir.exists():
        raw_body_candidates.extend(sorted(vuln_raw_dir.glob("*body.txt"), key=lambda p: p.stat().st_mtime))
        raw_headers_candidates.extend(sorted(vuln_raw_dir.glob("*headers.txt"), key=lambda p: p.stat().st_mtime))
        raw_response_candidates.extend(sorted(vuln_raw_dir.glob("*response.txt"), key=lambda p: p.stat().st_mtime))

    target_kind, normalized = normalize_target(args.target)
    recon = load_json(recon_json)
    recon_findings = recon.get("findings", []) if isinstance(recon, dict) else []
    body_text = raw_body_candidates[-1].read_text(encoding="utf-8", errors="ignore") if raw_body_candidates else ""
    raw_headers = raw_headers_candidates[-1].read_text(encoding="utf-8", errors="ignore") if raw_headers_candidates else ""
    raw_response = raw_response_candidates[-1].read_text(encoding="utf-8", errors="ignore") if raw_response_candidates else ""
    if not raw_headers and raw_response:
        raw_headers = raw_response
    enum_text = enum_summary.read_text(encoding="utf-8", errors="ignore") if enum_summary else ""
    vuln_text = vuln_summary.read_text(encoding="utf-8", errors="ignore") if vuln_summary else ""

    if target_kind == "web":
        fp = detect_from_headers(recon_findings, body_text, raw_headers, raw_response)
    else:
        fp = detect_from_services(enum_text, vuln_text)

    overlay = build_overlay(args.profile, fp, executed_steps)
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
        "server_hints": fp.get("server_hints", []),
        "status_code": fp.get("status_code", ""),
        "cookies_detected": fp.get("cookies_detected", 0),
        "profiles_considered": overlay["profiles_considered"],
        "report_focus": overlay["report_focus"],
        "extra_steps": overlay["extra_steps"],
        "deduplication": {
            "executed_steps_analyzed": len(executed_steps),
            "overlays_skipped_due_to_dedup": len(overlay.get("extra_steps", [])) == 0 and len(overlay["profiles_considered"]) > 0
        },
        "generated": datetime.now().astimezone().isoformat(),
    }

    out_path = quickscan_dir / "fingerprint.json"
    out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
