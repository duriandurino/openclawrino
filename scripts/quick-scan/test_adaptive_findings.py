#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "quick-scan" / "generate_quick_report.py"
PUBLISH_MODULE_PATH = ROOT / "scripts" / "quick-scan" / "publish_quick_report.py"

spec = importlib.util.spec_from_file_location("generate_quick_report", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(module)

publish_spec = importlib.util.spec_from_file_location("publish_quick_report", PUBLISH_MODULE_PATH)
publish_module = importlib.util.module_from_spec(publish_spec)
assert publish_spec is not None and publish_spec.loader is not None
publish_spec.loader.exec_module(publish_module)


def assert_equal(actual, expected, msg: str) -> None:
    if actual != expected:
        raise AssertionError(f"{msg}: expected={expected!r} actual={actual!r}")


def assert_contains(actual: str, expected_fragment: str, msg: str) -> None:
    if expected_fragment not in actual:
        raise AssertionError(f"{msg}: expected fragment {expected_fragment!r} in {actual!r}")


def test_vercel_nextjs_portfolio() -> None:
    fp = {
        "frameworks": ["nextjs"],
        "deployments": ["vercel"],
        "traits": ["portfolio-like", "ssr-or-hybrid", "tls-enforced"],
        "titles": ["Adrian Alejandrino | Product Solutions Engineer"],
        "server_hints": [],
    }
    csp = module.adapt_finding_to_fingerprint({"finding": "missing CSP header", "severity": "High", "confidence": "candidate"}, fp)
    assert_equal(csp["finding"], "CSP header not set in Vercel edge response (Next.js)", "vercel nextjs CSP rewrite")
    assert_equal(csp["evidence_tag"], "vercel-nextjs-headers", "vercel nextjs CSP tag")

    banner = module.adapt_finding_to_fingerprint({"finding": "server banner exposed", "severity": "Medium", "confidence": "observed"}, fp)
    assert_equal(banner["finding"], "Server banner exposed (Vercel)", "vercel banner rewrite")
    assert_contains(banner["context"], "Vercel returns Server header by default", "vercel banner context")


def test_catalog_surface() -> None:
    fp = {
        "frameworks": [],
        "deployments": [],
        "traits": ["catalog-like"],
        "titles": ["Online Book Fair"],
        "server_hints": ["nginx"],
    }
    hsts = module.adapt_finding_to_fingerprint({"finding": "missing HSTS header", "severity": "High", "confidence": "candidate"}, fp)
    assert_equal(hsts["finding"], "HSTS missing on catalog surface", "catalog HSTS rewrite")
    assert_equal(hsts["severity"], "High", "catalog HSTS severity")

    nosniff = module.adapt_finding_to_fingerprint({"finding": "missing X-Content-Type-Options header", "severity": "Low", "confidence": "candidate"}, fp)
    assert_contains(nosniff["finding"], "content surface", "catalog nosniff rewrite")

    banner = module.adapt_finding_to_fingerprint({"finding": "server banner exposed", "severity": "Medium", "confidence": "observed"}, fp)
    assert_equal(banner["finding"], "Server banner exposed (nginx)", "server hint banner rewrite")


def test_publish_parser_accepts_context_column() -> None:
    sample = r"""| Severity | Source | Confidence | Finding | Context |
|---|---|---|---|---|
| High | recon | observed | Title: Adrian Alejandrino \| Product Solutions Engineer | - |
| High | vuln | candidate | CSP header not set in Vercel edge response (Next.js) | Next.js on Vercel typically sets security headers via vercel.json or next.config.js |
| Medium | vuln | candidate | Server banner exposed (Vercel) | Vercel returns Server header by default |
"""
    rows = publish_module.parse_candidate_rows(sample)
    assert_equal(len(rows), 3, "publish parser should keep rows with context column")
    findings = {row["finding"] for row in rows}
    assert_equal(
        findings,
        {
            "Title: Adrian Alejandrino | Product Solutions Engineer",
            "CSP header not set in Vercel edge response (Next.js)",
            "Server banner exposed (Vercel)",
        },
        "publish parser escaped pipe handling",
    )


def main() -> int:
    test_vercel_nextjs_portfolio()
    test_catalog_surface()
    test_publish_parser_accepts_context_column()
    print("adaptive findings tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
