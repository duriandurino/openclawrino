# Reporting Skill — Usage Examples (Phase 0)

## Example 1: Generate Full Report
- **User:** "Generate the pentest report for 192.168.1.105"
- **Action:** Read findings from loot/, format into structured markdown report with all sections
- **Resources:** scripts/generate_report.py, references/enhancement_template.md

## Example 2: Document a Vulnerability
- **User:** "Document this CVE we just exploited"
- **Action:** Create finding entry with severity, evidence, remediation, hardening recommendation
- **Resources:** references/enhancement_template.md

## Example 3: Executive Summary
- **User:** "Give me an executive summary of what we found"
- **Action:** Compile top findings into non-technical summary with risk counts
- **Resources:** scripts/generate_report.py

## Example 4: Remediation Guidance
- **User:** "What's the remediation for CVE-2024-XXXXX?"
- **Action:** Research specific CVE, provide exact fix steps, verification, and hardening
- **Resources:** references/enhancement_template.md

## Example 5: Format Notes into Report
- **User:** "Turn my pentest notes into a proper report"
- **Action:** Parse notes from loot/ directory, structure findings, generate report
- **Resources:** scripts/generate_report.py
