# Penetration Test Report (Quick Scan) — onlinebookfair.net

- Profile: `webapp`
- Mode: `safe`
- Engagement: `quick-webapp-2026-04-08_1512`
- Steps executed: `3`
- Generated: `2026-04-08 15:13 PST`

## Scope
- Rapid triage / hygiene / exposure assessment
- Safe or low-impact checks where possible unless a profile explicitly broadens coverage
- This is not a substitute for a full pentest

## Executive Summary

- Quick scan profile `webapp` ran against `onlinebookfair.net` in `safe` mode and treated the target as a Vercel-hosted Next.js application serving as a public catalog or content-style surface, capturing 6 meaningful candidate observations with highest provisional severity `High`.
- These results are triage-oriented and should be manually validated before being treated as confirmed vulnerabilities.
- This quick scan adapted its framing toward: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages, deployment-layer clues from vercel hosting.

## Target Fingerprint

- Target appears to be a Vercel-hosted Next.js application serving as a public catalog or content-style surface.
- Observed framework indicators: `nextjs`
- Observed deployment indicators: `vercel`
- Target traits inferred from artifacts: `catalog-like`, `ssr-or-hybrid`
- Title hints: `Online Book Fair`
- Report emphasis for this target: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages
- Adaptive overlays: Analyzed 3 executed steps for deduplication

## Why This Quick Scan Varied

- This target was framed as a Vercel-hosted Next.js application serving as a public catalog or content-style surface based on lightweight fingerprint evidence.
- Focused on deployment metadata, response header posture, and frontend routing clues
- Focused on server-rendered route behavior and cache/header consistency across rendered pages
- Focused on deployment-layer clues from vercel hosting
- Reporting bias adjusted toward: Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
- Reporting bias adjusted toward: Validate whether search, content, and image-delivery routes expose data or caching behavior beyond the intended public catalog experience.

## Severity Buckets

- Critical: 0
- High: 5
- Medium: 1
- Low: 0
- Info: 0

## Candidate Findings

| Severity | Source | Confidence | Finding | Context |
|---|---|---|---|---|
| High | recon | candidate | Title: Adrian Alejandrino \| Product Solutions Engineer | - |
| High | vuln | candidate | CSP header not set in Vercel edge response (Next.js) | Next.js on Vercel typically sets security headers via vercel.json or next.config.js; absence suggests default deployment configuration |
| High | vuln | candidate | X-Frame-Options header not set (Next.js) | Next.js apps without explicit headers config may not set clickjacking protection; check for CSP frame-ancestors as alternative |
| High | vuln | candidate | X-Content-Type-Options: nosniff not set (JS-heavy app) | JavaScript-heavy applications benefit from MIME-type enforcement to prevent MIME-sniffing attacks on bundled assets |
| High | vuln | candidate | HSTS missing on catalog surface | E-commerce/catalog sites should enforce HTTPS via HSTS to prevent interception of browsing/purchase intent |
| Medium | vuln | candidate | Server banner exposed (Vercel) | Vercel returns Server header by default; low sensitivity but confirms hosting provider |

## What Needs Manual Validation

- Validate: Title: Adrian Alejandrino | Product Solutions Engineer
- Validate: CSP header not set in Vercel edge response (Next.js) (Next.js on Vercel typically sets security headers via vercel.json or next.config.js; absence suggests default deployment configuration)
- Validate: X-Frame-Options header not set (Next.js) (Next.js apps without explicit headers config may not set clickjacking protection; check for CSP frame-ancestors as alternative)
- Validate: X-Content-Type-Options: nosniff not set (JS-heavy app) (JavaScript-heavy applications benefit from MIME-type enforcement to prevent MIME-sniffing attacks on bundled assets)
- Validate: HSTS missing on catalog surface (E-commerce/catalog sites should enforce HTTPS via HSTS to prevent interception of browsing/purchase intent)
- Validate: Server banner exposed (Vercel) (Vercel returns Server header by default; low sensitivity but confirms hosting provider)

## Recommended Next Action

- Escalate to a full pentest workflow or targeted manual validation immediately for the highest-risk candidates on this Vercel-hosted Next.js application serving as a public catalog or content-style surface.
- Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
- Validate whether search, content, and image-delivery routes expose data or caching behavior beyond the intended public catalog experience.

## Recon Summary

# Phase Complete: Reconnaissance

**Engagement:** quick-webapp-2026-04-08_1512
**Phase:** recon
**Agent:** specter-recon
**Date:** 2026-04-08 15:13 PST
**Status:** complete

## Found

- A: 216.198.79.195, 64.29.17.195
- A: 216.198.79.65, 64.29.17.65
- MX: 10 mailstore1.secureserver.net., 0 smtp.secureserver.net.
- TXT: "v=spf1 include:secureserver.net -all", "T2834642"
- NS: ns1.vercel-dns.com., ns2.vercel-dns.com.
- Whois: Registrar WHOIS Server: whois.godaddy.com
- Whois: Registrar URL: http://www.godaddy.com
- Whois: Updated Date: 2026-02-15T15:12:31Z
- Whois: Creation Date: 2025-11-26T09:58:39Z
- Whois: Registrar: GoDaddy.com, LLC
- Whois: Registrar IANA ID: 146
- Whois: Registrar Abuse Contact Email: abuse@godaddy.com
- Whois: Registrar Abuse Contact Phone: 480-624-2505
- Whois: Domain Status: clientDeleteProhibited https://icann.org/epp#clientDeleteProhibited
- Whois: Domain Status: clientRenewProhibited https://icann.org/epp#clientRenewProhibited
- Whois: Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
- Whois: Domain Status: clientUpdateProhibited https://icann.org/epp#clientUpdateProhibited
- Whois: Name Server: NS1.VERCEL-DNS.COM
- Whois: Name Server: NS2.VERCEL-DNS.COM
- Whois: Registrar URL: https://www.godaddy.com

## Enumeration Summary

# Phase Complete: Enumeration

**Engagement:** quick-webapp-2026-04-08_1512
**Phase:** enum
**Agent:** specter-enum
**Date:** 2026-04-08 15:13 PST
**Status:** complete

## Found

- No significant structured findings captured by automation.

## Not Found

- Checked: fast/service scan → Result: no open ports confirmed in collected artifacts

## Recommended Next

- **Next Phase:** specter-vuln
- **Vector:** network
- **Reason:** Enumeration captured little attack surface; analyze collected evidence before deciding to pivot or stop.

## Key Data

### Network
- Target: durino.vercel.app
- Open ports / services: none captured

### Credentials
- None captured by automation

## Vulnerability Summary

# Phase Complete: Vulnerability Analysis

**Engagement:** quick-webapp-2026-04-08_1512
**Phase:** vuln
**Agent:** specter-vuln
**Date:** 2026-04-08 15:13 PST
**Status:** complete

## Found

- header: missing CSP header
- header: missing X-Frame-Options header
- header: missing X-Content-Type-Options header
- header: missing HSTS header
- banner: server banner exposed

## Not Found

- Checked: current automated artifacts → Result: no additional negative results explicitly captured

## Recommended Next

- **Next Phase:** specter-exploit
- **Vector:** network
- **Reason:** Automated vuln artifacts produced reusable evidence for the next phase.

## Key Data

### Network
- Target: durino.vercel.app

## Recommendations

- Validate candidate findings manually before escalation or reporting as confirmed issues.
- Escalate to a full pentest workflow if exposed services, weak posture, or high-risk candidates are found.
- Preserve engagement artifacts for follow-up analysis and retesting.
- Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
- Validate whether search, content, and image-delivery routes expose data or caching behavior beyond the intended public catalog experience.
- Use the discovered title/context (Online Book Fair) to decide whether this is primarily a marketing surface, operational app, or user-facing portal before prioritizing deeper testing.
