# Vulnerability Phase Essentials Examples — Real User Triggers

## Example 1: Validate scan output
**User:** "Analyze these scan results properly before we call them findings"
**Expected:** Distinguish candidate vulnerabilities from validated findings and explain the verification workflow.

## Example 2: Explain CVE vs CWE vs CVSS
**User:** "What's the difference between CVE, CWE, and CVSS?"
**Expected:** Explain identity vs weakness category vs severity model and how they connect during analysis.

## Example 3: Prioritize findings correctly
**User:** "How should I prioritize vulnerabilities beyond CVSS?"
**Expected:** Use validation, asset exposure, KEV, EPSS, exploitability, and business impact.

## Example 4: Guide a vuln-analysis phase
**User:** "Do the vulnerability phase methodically"
**Expected:** Apply identification -> validation -> optional safe PoC -> prioritization -> reporting.

## Example 5: Avoid false positives
**User:** "This scanner says it's vulnerable. How do I confirm it?"
**Expected:** Explain applicability checks, reproduction, evidence gathering, and false-positive rejection.

## Example 6: Sub-agent needs stronger vuln discipline
**User:** "Research exploitability but keep it evidence-backed"
**Expected:** Separate hypothesis from confirmation, avoid CVE overclaiming, and prepare remediation-ready findings.

## Example 7: Reporting tie-in
**User:** "Make the vulnerability section of the report more defensible"
**Expected:** Include evidence, CVE/CWE references, CVSS context, KEV/EPSS/business context, and retest guidance.
