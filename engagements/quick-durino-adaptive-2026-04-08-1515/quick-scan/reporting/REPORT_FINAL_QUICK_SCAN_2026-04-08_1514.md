# Penetration Test Report — durino.vercel.app (Quick Scan)

**Date:** 2026-04-08
**Target:** durino.vercel.app (Quick Scan)
**Findings:** 0

---

## 1. Executive Summary

- Quick scan profile `webapp` ran against `durino.vercel.app` in `safe` mode and treated the target as a Vercel-hosted Next.js application serving as a public portfolio-style surface, capturing 6 meaningful candidate observations with highest provisional severity `High`.
- These results are triage-oriented and should be manually validated before being treated as confirmed vulnerabilities.
- This quick scan adapted its framing toward: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages, deployment-layer clues from vercel hosting.


---

## 2. Target Fingerprint

- Target appears to be a Vercel-hosted Next.js application serving as a public portfolio-style surface.
- Observed framework indicators: `nextjs`
- Observed deployment indicators: `vercel`
- Target traits inferred from artifacts: `api-backed`, `portfolio-like`, `ssr-or-hybrid`
- Title hints: `Adrian Alejandrino | Product Solutions Engineer`
- Report emphasis for this target: deployment metadata, response header posture, and frontend routing clues, server-rendered route behavior and cache/header consistency across rendered pages
- Adaptive overlays: Analyzed 3 executed steps for deduplication

---

## 3. Why This Quick Scan Varied

- This target was framed as a Vercel-hosted Next.js application serving as a public portfolio-style surface based on lightweight fingerprint evidence.
- Focused on deployment metadata, response header posture, and frontend routing clues
- Focused on server-rendered route behavior and cache/header consistency across rendered pages
- Focused on deployment-layer clues from vercel hosting
- Reporting bias adjusted toward: Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
- Reporting bias adjusted toward: Treat public profile and contact metadata as part of the exposed surface, especially if it influences impersonation, scraping, or social-engineering risk.

---

## 4. Methodology

This assessment used the quick-scan workflow, a rapid low-impact triage process rather than a full pentest:

1. **Reconnaissance** — Lightweight target and exposure fingerprinting
2. **Enumeration** — Safe surface validation and basic discovery
3. **Vulnerability Analysis** — Candidate weakness review from collected artifacts
4. **Reporting** — Triage-oriented findings with next-step guidance

---

## 5. Findings

---

## 6. Security Enhancement Recommendations

### Exposure Management

Use quick scan as triage only, then validate high-risk candidates manually before operational changes or client delivery.

### Patch and Validation Workflow

For candidate version-based matches, verify the real product/version before remediation, then patch and re-scan to confirm closure.

### Public Metadata Hygiene

Review public profile, author, and contact metadata as part of the exposed surface so personal or impersonation-relevant details are not over-shared by the deployment.

### Quick Scan Context

Validate candidate findings manually before escalation or reporting as confirmed issues.

### Quick Scan Context

Escalate to a full pentest workflow if exposed services, weak posture, or high-risk candidates are found.

### Quick Scan Context

Preserve engagement artifacts for follow-up analysis and retesting.

### Quick Scan Context

Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.

### Quick Scan Context

Treat public profile and contact metadata as part of the exposed surface, especially if it influences impersonation, scraping, or social-engineering risk.

### Quick Scan Context

Use the discovered title/context (Adrian Alejandrino | Product Solutions Engineer) to decide whether this is primarily a marketing surface, operational app, or user-facing portal before prioritizing deeper testing.

---

## 7. Recommended Next Action

- Escalate to a full pentest workflow or targeted manual validation immediately for the highest-risk candidates on this Vercel-hosted Next.js application serving as a public portfolio-style surface.
- Review framework-level security headers in the Vercel/Next.js deployment configuration rather than only at the application code layer.
- Treat public profile and contact metadata as part of the exposed surface, especially if it influences impersonation, scraping, or social-engineering risk.

---

## 8. Risk Summary Matrix

| ID | Finding | Severity | Remediation Priority |
|----|---------|----------|---------------------|

---

## 9. Appendices

### A. Tools Used

- nmap, masscan (enumeration)
- Metasploit, custom scripts (exploitation)
- Shodan, crt.sh (OSINT)
- Burp Suite, curl (web testing)

### B. Scope Boundaries

All testing was conducted within the authorized scope. No denial-of-service attacks were performed without explicit permission.
