# Penetration Test Report (Quick Scan) — https://vercel.com

- Profile: `webapp`
- Mode: `safe`
- Engagement: `quick-adaptive-test-vercel`
- Steps executed: `3`
- Generated: `2026-04-07 12:10 PST`

## Scope
- Rapid triage / hygiene / exposure assessment
- Safe or low-impact checks where possible unless a profile explicitly broadens coverage
- This is not a substitute for a full pentest

## Executive Summary

- Quick scan profile `webapp` ran against `https://vercel.com` in `safe` mode and captured 1 meaningful candidate observations, with highest provisional severity `Medium`.
- These results are triage-oriented and should be manually validated before being treated as confirmed vulnerabilities.
- This quick scan adapted its framing toward: deployment-layer clues from vercel hosting.

## Target Fingerprint

- Observed framework indicators: `nextjs`
- Observed deployment indicators: `vercel`
- Target traits inferred from artifacts: `ssr-or-hybrid`

## Why This Quick Scan Varied

- Focused on deployment-layer clues from vercel hosting

## Severity Buckets

- Critical: 0
- High: 0
- Medium: 1
- Low: 0
- Info: 0

## Candidate Findings

| Severity | Source | Confidence | Finding |
|---|---|---|---|
| Medium | vuln | candidate | banner: server banner exposed |

## What Needs Manual Validation

- Validate: banner: server banner exposed

## Recommended Next Action

- Perform focused manual validation on the medium-severity candidates and expand service-specific enumeration where relevant.

## Recon Summary

# Phase Complete: Reconnaissance

**Engagement:** quick-adaptive-test-vercel
**Phase:** recon
**Agent:** specter-recon
**Date:** 2026-04-07 12:10 PST
**Status:** complete

## Found

- A: 198.169.2.1, 198.169.1.193
- MX: 10 aspmx2.googlemail.com., 1 aspmx.l.google.com., 10 aspmx3.googlemail.com., 5 alt2.aspmx.l.google.com., 5 alt1.aspmx.l.google.com.
- TXT: "ahrefs-site-verification_774361e47cac589ba5ff743f90399b1e5792980bd22f0f4c56bfb1eaf571a7e0", "notion_verify_82^tYP%}6Q65dbszXu>V?@~stLe]Cm3Dmn8rqe7DZgT1m3o!+PyEbv+Jx04rb%v67BtbG>", "amp-by-sourcegraph-domain-verification-st5f9e=172nCAgVw3POSEMQGXOv24XWO", "serval-domain-verification-40ct5x=VbdjZnWHkRJwpBE0IwXuriy03", "ZOOM_verify_iAqiiWW1TdK-GwbJI7qn1g"
- NS: ns2.vercel-dns.com., ns1.vercel-dns.com.
- Header: server: Vercel
- Header: x-powered-by: Next.js, Payload
- Whatweb: [1m[34mhttps://vercel.com[0m [200 OK] [1mCookies[0m[[0m[22m_v-anonymous-id,_v-anonymous-id-renewed,_v-consent[0m], [1mCountry[0m[[0m[22mCANADA[0m][[1m[31mCA[0m], [1mHTML5[0m, [1mHTTPServer[0m[[1m[36mVercel[0m], [1mIP[0m[[0m[22m198.169.2.193[0m], [1mOpen-Graph-Protocol[0m[[1m[32mwebsite[0m], [1mScript[0m[[0m[22mapplication/json[0m], [1mStrict-Transport-Security[0m[[0m[22mmax-age=31536000; includeSubDomains; preload[0m], [1mTitle[0m[[1m[33mVercel: Build and deploy the best web experiences with the AI Cloud[0m], [1mUncommonHeaders[0m[[0m[22maccept-ch,content-security-policy,critical-ch,feature-policy,referrer-policy,x-content-type-options,x-dns-prefetch-control,x-download-options,x-matched-path,x-nextjs-prerender,x-nextjs-stale-time,x-vercel-cache,x-vercel-debug,x-vercel-id,x-vercel-lambda-service[0m], [1mX-Frame-Options[0m[[0m[22mDENY[0m], [1mX-Powered-By[0m[[0m[22mNext.js, Payload[0m], [1mX-XSS-Protection[0m[[0m[22m0[0m]

## Not Found

- Checked: current automated artifacts → Result: no additional negative results explicitly captured

## Recommended Next

- **Next Phase:** specter-enum
- **Vector:** network
- **Reason:** Automated recon artifacts produced reusable evidence for the next phase.

## Key Data


## Enumeration Summary

# Phase Complete: Enumeration

**Engagement:** quick-adaptive-test-vercel
**Phase:** enum
**Agent:** specter-enum
**Date:** 2026-04-07 12:10 PST
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
- Target: https://vercel.com
- Open ports / services: none captured

### Credentials
- None captured by automation

## Vulnerability Summary

# Phase Complete: Vulnerability Analysis

**Engagement:** quick-adaptive-test-vercel
**Phase:** vuln
**Agent:** specter-vuln
**Date:** 2026-04-07 12:10 PST
**Status:** complete

## Found

- banner: server banner exposed

## Not Found

- Checked: current automated artifacts → Result: no additional negative results explicitly captured

## Recommended Next

- **Next Phase:** specter-exploit
- **Vector:** network
- **Reason:** Automated vuln artifacts produced reusable evidence for the next phase.

## Key Data

### Network
- Target: https://vercel.com
- Open ports / services: none captured

### Credentials
- None captured by automation

## Recommendations

- Validate candidate findings manually before escalation or reporting as confirmed issues.
- Escalate to a full pentest workflow if exposed services, weak posture, or high-risk candidates are found.
- Preserve engagement artifacts for follow-up analysis and retesting.
