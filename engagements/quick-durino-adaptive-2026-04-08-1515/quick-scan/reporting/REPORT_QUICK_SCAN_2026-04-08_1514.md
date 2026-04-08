# Penetration Test Report (Quick Scan) — durino.vercel.app

- Profile: `webapp`
- Mode: `safe`
- Engagement: `quick-durino-adaptive-2026-04-08-1515`
- Steps executed: `3`
- Generated: `2026-04-08 15:14 PST`

## Scope
- Rapid triage / hygiene / exposure assessment
- Safe or low-impact checks where possible unless a profile explicitly broadens coverage
- This is not a substitute for a full pentest

## Executive Summary

- Quick scan profile `webapp` ran against `durino.vercel.app` in `safe` mode and treated the target as a Vercel-hosted Next.js application serving as a public portfolio-style surface, capturing 6 meaningful candidate observations with highest provisional severity `High`.
- These results are triage-oriented and should be manually validated before being treated as confirmed vulnerabilities.
- This quick scan adapted its framing toward: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages, deployment-layer clues from vercel hosting.

## Target Fingerprint

- Target appears to be a Vercel-hosted Next.js application serving as a public portfolio-style surface.
- Observed framework indicators: `nextjs`
- Observed deployment indicators: `vercel`
- Target traits inferred from artifacts: `api-backed`, `portfolio-like`, `ssr-or-hybrid`
- Title hints: `Adrian Alejandrino | Product Solutions Engineer`
- Report emphasis for this target: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages
- Adaptive overlays: Analyzed 3 executed steps for deduplication

## Why This Quick Scan Varied

- This target was framed as a Vercel-hosted Next.js application serving as a public portfolio-style surface based on lightweight fingerprint evidence.
- Focused on deployment metadata, response header posture, and frontend routing clues
- Focused on server-rendered route behavior and cache/header consistency across rendered pages
- Focused on deployment-layer clues from vercel hosting
- Reporting bias adjusted toward: Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
- Reporting bias adjusted toward: Treat public profile and contact metadata as part of the exposed surface, especially if it influences impersonation, scraping, or social-engineering risk.

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
| High | vuln | candidate | header: missing HSTS header | HTTPS strict transport security not enforced |
| Medium | vuln | candidate | Server banner exposed (Vercel) | Vercel returns Server header by default; low sensitivity but confirms hosting provider |

## What Needs Manual Validation

- Validate: Title: Adrian Alejandrino | Product Solutions Engineer
- Validate: CSP header not set in Vercel edge response (Next.js) (Next.js on Vercel typically sets security headers via vercel.json or next.config.js; absence suggests default deployment configuration)
- Validate: X-Frame-Options header not set (Next.js) (Next.js apps without explicit headers config may not set clickjacking protection; check for CSP frame-ancestors as alternative)
- Validate: X-Content-Type-Options: nosniff not set (JS-heavy app) (JavaScript-heavy applications benefit from MIME-type enforcement to prevent MIME-sniffing attacks on bundled assets)
- Validate: header: missing HSTS header (HTTPS strict transport security not enforced)
- Validate: Server banner exposed (Vercel) (Vercel returns Server header by default; low sensitivity but confirms hosting provider)

## Recommended Next Action

- Escalate to a full pentest workflow or targeted manual validation immediately for the highest-risk candidates on this Vercel-hosted Next.js application serving as a public portfolio-style surface.
- Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
- Treat public profile and contact metadata as part of the exposed surface, especially if it influences impersonation, scraping, or social-engineering risk.

## Recon Summary

# Phase Complete: Reconnaissance

**Engagement:** quick-durino-adaptive-2026-04-08-1515
**Phase:** recon
**Agent:** specter-recon
**Date:** 2026-04-08 15:14 PST
**Status:** complete

## Found

- A: 216.198.79.3, 64.29.17.3
- Header: Location: https://durino.vercel.app/
- Header: server: Vercel
- Title: Adrian Alejandrino | Product Solutions Engineer
- Whatweb: [1m[34mhttp://durino.vercel.app[0m [308 Permanent Redirect] [1mCountry[0m[[0m[22mUNITED STATES[0m][[1m[31mUS[0m], [1mHTTPServer[0m[[1m[36mVercel[0m], [1mIP[0m[[0m[22m64.29.17.67[0m], [1mRedirectLocation[0m[[0m[22mhttps://durino.vercel.app/[0m]
[1m[34mhttps://durino.vercel.app/[0m [200 OK] [1mCountry[0m[[0m[22mUNITED STATES[0m][[1m[31mUS[0m], [1mEmail[0m[[0m[22madrian.alejandrino.1115@gmail.com[0m], [1mHTML5[0m, [1mHTTPServer[0m[[1m[36mVercel[0m], [1mIP[0m[[0m[22m64.29.17.195[0m], [1mMeta-Author[0m[[0m[22mAdrian Alejandrino[0m], [1mOpen-Graph-Protocol[0m[[1m[32mwebsite[0m], [1mScript[0m, [1mStrict-Transport-Security[0m[[0m[22mmax-age=63072000; includeSubDomains; preload[0m], [1mTitle[0m[[1m[33mAdrian Alejandrino | Product Solutions Engineer[0m], [1mUncommonHeaders[0m[[0m[22maccess-control-allow-origin,x-matched-path,x-vercel-cache,x-vercel-id[0m]

## Not Found

- Checked: current automated artifacts → Result: no additional negative results explicitly captured

## Recommended Next

- **Next Phase:** specter-enum
- **Vector:** network
- **Reason:** Automated recon artifacts produced reusable evidence for the next phase.

## Key Data

### Network

## Enumeration Summary

# Phase Complete: Enumeration

**Engagement:** quick-durino-adaptive-2026-04-08-1515
**Phase:** enum
**Agent:** specter-enum
**Date:** 2026-04-08 15:14 PST
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

**Engagement:** quick-durino-adaptive-2026-04-08-1515
**Phase:** vuln
**Agent:** specter-vuln
**Date:** 2026-04-08 15:14 PST
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
- Treat public profile and contact metadata as part of the exposed surface, especially if it influences impersonation, scraping, or social-engineering risk.
- Use the discovered title/context (Adrian Alejandrino | Product Solutions Engineer) to decide whether this is primarily a marketing surface, operational app, or user-facing portal before prioritizing deeper testing.
