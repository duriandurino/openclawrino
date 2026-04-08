# Penetration Test Report — onlinebookfair.net (Quick Scan)

**Date:** 2026-04-08
**Target:** onlinebookfair.net (Quick Scan)
**Findings:** 4

---

## 1. Executive Summary

- Quick scan profile `webapp` ran against `onlinebookfair.net` in `safe` mode and treated the target as a Vercel-hosted Next.js application serving as a public catalog or content-style surface, capturing 4 meaningful candidate observations with highest provisional severity `High`.
- These results are triage-oriented and should be manually validated before being treated as confirmed vulnerabilities.
- This quick scan adapted its framing toward: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages, deployment-layer clues from vercel hosting.


---

## 2. Target Fingerprint

- Target appears to be a Vercel-hosted Next.js application serving as a public catalog or content-style surface.
- Observed framework indicators: `nextjs`
- Observed deployment indicators: `vercel`
- Target traits inferred from artifacts: `catalog-like`, `ssr-or-hybrid`, `tls-enforced`
- Title hints: `Online Book Fair`
- Report emphasis for this target: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages
- Adaptive overlays: Analyzed 3 executed steps for deduplication

---

## 3. Why This Quick Scan Varied

- This target was framed as a Vercel-hosted Next.js application serving as a public catalog or content-style surface based on lightweight fingerprint evidence.
- Focused on deployment metadata, response header posture, and frontend routing clues
- Focused on server-rendered route behavior and cache/header consistency across rendered pages
- Focused on deployment-layer clues from vercel hosting
- Reporting bias adjusted toward: Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
- Reporting bias adjusted toward: Validate whether search, content, and image-delivery routes expose data or caching behavior beyond the intended public catalog experience.

---

## 4. Methodology

This assessment used the quick-scan workflow, a rapid low-impact triage process rather than a full pentest:

1. **Reconnaissance** — Lightweight target and exposure fingerprinting
2. **Enumeration** — Safe surface validation and basic discovery
3. **Vulnerability Analysis** — Candidate weakness review from collected artifacts
4. **Reporting** — Triage-oriented findings with next-step guidance

---

## 5. Findings

### QS-001 — CSP header not set in Vercel edge response (Next.js)

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** onlinebookfair.net
- **Description:** Quick scan candidate from the vuln phase: CSP header not set in Vercel edge response (Next.js)
- **Evidence:** ```
Quick scan candidate finding (candidate) from vuln: CSP header not set in Vercel edge response (Next.js)
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Perform targeted validation immediately, patch or reconfigure the exposed service, and verify the issue is no longer reachable from the current network segment.
- **Hardening:** Keep public catalog/content routes, media delivery, and cache behavior documented so unexpected exposure or stale edge behavior stands out quickly during follow-up testing.
- **References:** Quick scan profile: webapp, Execution mode: safe

### QS-002 — X-Content-Type-Options: nosniff not set (JS-heavy app)

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** onlinebookfair.net
- **Description:** Quick scan candidate from the vuln phase: X-Content-Type-Options: nosniff not set (JS-heavy app)
- **Evidence:** ```
Quick scan candidate finding (candidate) from vuln: X-Content-Type-Options: nosniff not set (JS-heavy app)
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Perform targeted validation immediately, patch or reconfigure the exposed service, and verify the issue is no longer reachable from the current network segment.
- **Hardening:** Keep public catalog/content routes, media delivery, and cache behavior documented so unexpected exposure or stale edge behavior stands out quickly during follow-up testing.
- **References:** Quick scan profile: webapp, Execution mode: safe

### QS-003 — X-Frame-Options header not set (Next.js)

- **Severity:** High
- **CVSS Score:** N/A
- **Affected Target:** onlinebookfair.net
- **Description:** Quick scan candidate from the vuln phase: X-Frame-Options header not set (Next.js)
- **Evidence:** ```
Quick scan candidate finding (candidate) from vuln: X-Frame-Options header not set (Next.js)
```
- **Impact:** If confirmed, this exposure could significantly increase remote attack surface or allow unauthorized administrative or data-service access paths.
- **Remediation:** Perform targeted validation immediately, patch or reconfigure the exposed service, and verify the issue is no longer reachable from the current network segment.
- **Hardening:** Keep public catalog/content routes, media delivery, and cache behavior documented so unexpected exposure or stale edge behavior stands out quickly during follow-up testing.
- **References:** Quick scan profile: webapp, Execution mode: safe

### QS-004 — Server banner exposed (Vercel)

- **Severity:** Medium
- **CVSS Score:** N/A
- **Affected Target:** onlinebookfair.net
- **Description:** Quick scan candidate from the vuln phase: Server banner exposed (Vercel)
- **Evidence:** ```
Quick scan candidate finding (candidate) from vuln: Server banner exposed (Vercel)
```
- **Impact:** This may help attackers profile the public catalog deployment and target content-delivery or routing behavior more efficiently.
- **Remediation:** Reduce unnecessary banner and edge-routing disclosure where possible, then confirm externally visible headers only reveal what the deployment truly needs.
- **Hardening:** Keep public catalog/content routes, media delivery, and cache behavior documented so unexpected exposure or stale edge behavior stands out quickly during follow-up testing.
- **References:** Quick scan profile: webapp, Execution mode: safe

---

## 6. Security Enhancement Recommendations

### Exposure Management

Use quick scan as triage only, then validate high-risk candidates manually before operational changes or client delivery.

### Patch and Validation Workflow

For candidate version-based matches, verify the real product/version before remediation, then patch and re-scan to confirm closure.

### Catalog Route Review

Review public catalog, media, and content-delivery routes for caching, asset, and browser-hardening consistency across representative user-facing pages.

### Quick Scan Context

Validate candidate findings manually before escalation or reporting as confirmed issues.

### Quick Scan Context

Escalate to a full pentest workflow if exposed services, weak posture, or high-risk candidates are found.

### Quick Scan Context

Preserve engagement artifacts for follow-up analysis and retesting.

### Quick Scan Context

Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.

### Quick Scan Context

Validate whether search, content, and image-delivery routes expose data or caching behavior beyond the intended public catalog experience.

### Quick Scan Context

Use the discovered title/context (Online Book Fair) to decide whether this is primarily a marketing surface, operational app, or user-facing portal before prioritizing deeper testing.

---

## 7. Recommended Next Action

- Escalate to a full pentest workflow or targeted manual validation immediately for the highest-risk candidates on this Vercel-hosted Next.js application serving as a public catalog or content-style surface.
- Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
- Validate whether search, content, and image-delivery routes expose data or caching behavior beyond the intended public catalog experience.

---

## 8. Risk Summary Matrix

| ID | Finding | Severity | Remediation Priority |
|----|---------|----------|---------------------|
| QS-001 | CSP header not set in Vercel edge response (Next.js) | High | Immediate |
| QS-002 | X-Content-Type-Options: nosniff not set (JS-heavy app) | High | Immediate |
| QS-003 | X-Frame-Options header not set (Next.js) | High | Immediate |
| QS-004 | Server banner exposed (Vercel) | Medium | Scheduled |

---

## 9. Appendices

### A. Tools Used

- nmap, masscan (enumeration)
- Metasploit, custom scripts (exploitation)
- Shodan, crt.sh (OSINT)
- Burp Suite, curl (web testing)

### B. Scope Boundaries

All testing was conducted within the authorized scope. No denial-of-service attacks were performed without explicit permission.
