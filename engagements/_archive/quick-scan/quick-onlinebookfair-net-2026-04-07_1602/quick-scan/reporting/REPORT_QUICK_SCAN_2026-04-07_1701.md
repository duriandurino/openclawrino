# Penetration Test Report (Quick Scan) — https://onlinebookfair.net

- Profile: `webapp`
- Mode: `safe`
- Engagement: `quick-onlinebookfair-net-2026-04-07_1602`
- Steps executed: `3`
- Generated: `2026-04-07 17:01 PST`

## Scope
- Rapid triage / hygiene / exposure assessment
- Safe or low-impact checks where possible unless a profile explicitly broadens coverage
- This is not a substitute for a full pentest

## Executive Summary

- Quick scan profile `webapp` ran against `https://onlinebookfair.net` in `safe` mode and treated the target as a Vercel-hosted Next.js application, capturing 4 meaningful candidate observations with highest provisional severity `High`.
- These results are triage-oriented and should be manually validated before being treated as confirmed vulnerabilities.
- This quick scan adapted its framing toward: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages, deployment-layer clues from vercel hosting.

## Target Fingerprint

- Target appears to be a Vercel-hosted Next.js application.
- Observed framework indicators: `nextjs`
- Observed deployment indicators: `vercel`
- Target traits inferred from artifacts: `ssr-or-hybrid`, `tls-enforced`
- Report emphasis for this target: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages

## Why This Quick Scan Varied

- This target was framed as a Vercel-hosted Next.js application based on lightweight fingerprint evidence.
- Focused on deployment metadata, response header posture, and frontend routing clues
- Focused on server-rendered route behavior and cache/header consistency across rendered pages
- Focused on deployment-layer clues from vercel hosting
- Reporting bias adjusted toward: Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.

## Severity Buckets

- Critical: 0
- High: 1
- Medium: 1
- Low: 2
- Info: 0

## Candidate Findings

| Severity | Source | Confidence | Finding |
|---|---|---|---|
| High | vuln | candidate | header: missing CSP header |
| Low | vuln | candidate | header: missing X-Frame-Options header |
| Low | vuln | candidate | header: missing X-Content-Type-Options header |
| Medium | vuln | candidate | banner: server banner exposed |

## What Needs Manual Validation

- Validate: header: missing CSP header
- Validate: header: missing X-Frame-Options header
- Validate: header: missing X-Content-Type-Options header
- Validate: banner: server banner exposed

## Recommended Next Action

- Escalate to a full pentest workflow or targeted manual validation immediately for the highest-risk candidates on this Vercel-hosted Next.js application.
- Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.

## Recon Summary

# Phase Complete: Reconnaissance

**Engagement:** quick-onlinebookfair-net-2026-04-07_1602
**Phase:** recon
**Agent:** specter-recon
**Date:** 2026-04-07 16:04 PST
**Status:** complete

## Found

- A: 64.29.17.1, 216.198.79.1
- MX: 0 smtp.secureserver.net., 10 mailstore1.secureserver.net.
- TXT: "T2834642", "v=spf1 include:secureserver.net -all"
- NS: ns1.vercel-dns.com., ns2.vercel-dns.com.
- Header: location: https://www.onlinebookfair.net/
- Header: server: Vercel
- Whatweb: [1m[34mhttps://onlinebookfair.net[0m [307 Temporary Redirect] [1mCountry[0m[[0m[22mUNITED STATES[0m][[1m[31mUS[0m], [1mHTTPServer[0m[[1m[36mVercel[0m], [1mIP[0m[[0m[22m216.198.79.65[0m], [1mRedirectLocation[0m[[0m[22mhttps://www.onlinebookfair.net/[0m], [1mStrict-Transport-Security[0m[[0m[22mmax-age=63072000[0m], [1mUncommonHeaders[0m[[0m[22mx-vercel-id[0m]
[1m[34mhttps://www.onlinebookfair.net/[0m [200 OK] [1mCountry[0m[[0m[22mUNITED STATES[0m][[1m[31mUS[0m], [1mEmail[0m[[0m[22mbusiness@onlinebookfair.net[0m], [1mHTML5[0m, [1mHTTPServer[0m[[1m[36mVercel[0m], [1mIP[0m[[0m[22m216.198.79.1[0m], [1mScript[0m, [1mStrict-Transport-Security[0m[[0m[22mmax-age=63072000[0m], [1mTitle[0m[[1m[33mOnline Book Fair[0m], [1mUncommonHeaders[0m[[0m[22maccess-control-allow-origin,x-matched-path,x-nextjs-prerender,x-nextjs-stale-time,x-vercel-cache,x-vercel-id[0m]

## Not Found

- Checked: current automated artifacts → Result: no additional negative results explicitly captured

## Recommended Next

- **Next Phase:** specter-enum
- **Vector:** network
- **Reason:** Automated recon artifacts produced reusable evidence for the next phase.

## Key Data

## Enumeration Summary

# Phase Complete: Enumeration

**Engagement:** quick-onlinebookfair-net-2026-04-07_1602
**Phase:** enum
**Agent:** specter-enum
**Date:** 2026-04-07 16:04 PST
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
- Target: https://onlinebookfair.net
- Open ports / services: none captured

### Credentials
- None captured by automation

## Vulnerability Summary

# Phase Complete: Vulnerability Analysis

**Engagement:** quick-onlinebookfair-net-2026-04-07_1602
**Phase:** vuln
**Agent:** specter-vuln
**Date:** 2026-04-07 16:04 PST
**Status:** complete

## Found

- header: missing CSP header
- header: missing X-Frame-Options header
- header: missing X-Content-Type-Options header
- banner: server banner exposed

## Not Found

- Checked: current automated artifacts → Result: no additional negative results explicitly captured

## Recommended Next

- **Next Phase:** specter-exploit
- **Vector:** network
- **Reason:** Automated vuln artifacts produced reusable evidence for the next phase.

## Key Data

### Network
- Target: https://onlinebookfair.net
- Open ports / services: none captured

## Recommendations

- Validate candidate findings manually before escalation or reporting as confirmed issues.
- Escalate to a full pentest workflow if exposed services, weak posture, or high-risk candidates are found.
- Preserve engagement artifacts for follow-up analysis and retesting.
- Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
