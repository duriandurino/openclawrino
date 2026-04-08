#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "quick-scan" / "generate_quick_report.py"

spec = importlib.util.spec_from_file_location("generate_quick_report", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(module)


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
    csp = module.adapt_finding_to_fingerprint("missing CSP header", fp)
    assert_equal(csp["finding"], "CSP header not set in Vercel edge response (Next.js)", "vercel nextjs CSP rewrite")
    assert_equal(csp["evidence_tag"], "vercel-nextjs-headers", "vercel nextjs CSP tag")

    banner = module.adapt_finding_to_fingerprint("server banner exposed", fp)
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
    hsts = module.adapt_finding_to_fingerprint("missing HSTS header", fp)
    assert_equal(hsts["finding"], "HSTS missing on catalog surface", "catalog HSTS rewrite")
    assert_equal(hsts["severity"], "High", "catalog HSTS severity")

    nosniff = module.adapt_finding_to_fingerprint("missing X-Content-Type-Options header", fp)
    assert_contains(nosniff["finding"], "content surface", "catalog nosniff rewrite")

    banner = module.adapt_finding_to_fingerprint("server banner exposed", fp)
    assert_equal(banner["finding"], "Server banner exposed (nginx)", "server hint banner rewrite")


def main() -> int:
    test_vercel_nextjs_portfolio()
    test_catalog_surface()
    print("adaptive findings tests: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
