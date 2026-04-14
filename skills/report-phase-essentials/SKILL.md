---
name: report-phase-essentials
description: "Methodology and quality framework for the penetration testing report phase. Use when: writing or QA-ing pentest reports, improving executive and technical readability, enforcing evidence completeness, adding remediation and retest guidance, including cleanup/restoration and residual risk, or securing report packaging and delivery. NOT for: running phase-specific testing tasks or replacing the specialized reporting implementation/publishing workflow."
---

# Report Phase Essentials

Use this skill to make pentest reports defensible, multi-audience, actionable, and securely handled. This is a **methodology and QA layer** for reporting, not a replacement for the concrete reporting/publishing pipeline.

## When to Use

✅ **USE this skill when:**
- "Write the pentest report properly"
- "Make the report stronger"
- "QA this report before delivery"
- "Make it useful for executives and engineers"
- "Make sure cleanup is included in the report"
- "Add remediation and retest guidance"
- A sub-agent needs stronger reporting discipline before finalizing deliverables

## When NOT to Use

❌ **DON'T use this skill when:**
- Running recon / enum / vuln / exploit / post work directly
- Replacing the specialist report generation and publishing workflow
- Using it as a substitute for validating findings first
- Treating it as permission to include unsafe secrets or raw exploit dumps in the final report

## Core Rules

1. **The report is the deliverable**
   - Technical work has limited value if the report does not drive action.
   - Optimize for decisions, remediation, and retesting.

2. **Write for multiple audiences**
   - Executives need risk, business impact, and roadmap.
   - Engineers need reproducible findings, evidence, and fix guidance.

3. **Cleanup must be explicit**
   - Every final report should state cleanup/restoration status.
   - Include tester-created artifacts removed, left in place, or not applicable.

4. **Curate evidence, do not dump tools**
   - Raw output belongs in controlled appendices if needed.
   - The report body should contain evidence that supports conclusions clearly.

5. **Secure handling is part of reporting**
   - Reports and evidence are sensitive by default.
   - Redaction, encryption, distribution control, retention, and destruction matter.

## Minimum Report Structure

Include at least:
- cover/classification
- version control / document history
- engagement overview
- scope and exclusions
- methodology and limitations
- executive summary
- findings summary table
- detailed findings
- remediation roadmap
- cleanup / restoration status
- retest guidance or retest results
- appendices / controlled evidence references

## Cleanup and Restoration Section (Required)

Every final report should include a dedicated section answering:
```text
Were tester-created artifacts introduced?
What was removed during cleanup?
What remains intentionally in place, if anything?
Was the environment restored to agreed state?
What residual risk remains after cleanup?
Any follow-up actions required by the client?
```

If nothing was introduced, say so explicitly.

## Detailed Finding Schema

Each finding should include:
```text
ID
Title
Affected Asset(s)
Severity
Technical Basis (include CVSS when the finding can be scored)
Business Impact / Priority Context
Evidence
Reproduction / Validation Steps
Remediation
Verification / Retest Guidance
References
```

### CVSS House Standard (Required)

Use this scoring policy unless the engagement explicitly requires something else:

- **Primary standard:** CVSS v4.0 Base for new internal reporting
- **Compatibility field:** CVSS v3.1 when a public CVE, NVD record, vendor advisory, scanner, or client workflow still depends on v3.1
- **Interpretation rule:** CVSS expresses **technical severity**, not business risk
- **Priority rule:** final remediation priority must also consider exploit evidence, KEV/EPSS, exposure, asset criticality, and attack chaining

For every scored finding, include:
```text
CVSS version
CVSS vector
CVSS numeric score
1-3 line metric rationale
Severity band (Low/Medium/High/Critical)
```

If the evidence is incomplete:
- mark the score as **Provisional**, or
- leave it unscored and explain why

Do not publish a naked score without its vector and rationale.

When relevant, also include:
- exploitability notes
- countermeasure effectiveness
- cleanup or side-effect notes
- detection / telemetry notes

## Executive Narrative

The executive material should answer quickly:
- what was tested?
- what is the overall posture?
- what are the top risks?
- what should leadership fund, fix, or accept?
- what systemic/root-cause themes emerged?

Rule:
- do not force executives to translate technical jargon into business meaning themselves

## Remediation Guidance

Good remediation should include:
- immediate containment options where relevant
- root cause explanation
- exact fix guidance (config/code/process)
- verification steps
- regression / implementation risk notes
- compensating controls if a full fix is delayed

## Retest Readiness

Write every finding so it can be retested deterministically.

Include:
- what "fixed" looks like
- how to verify the fix
- any prerequisites for retest
- affected asset owner or remediation owner if known

## Evidence Handling

Use these rules:
- mask secrets, personal data, and sensitive identifiers in the main report
- minimize data collected to what proves the claim
- separate sensitive annexes from the main report if needed
- link evidence to finding IDs and timestamps
- preserve enough context for reproducibility

## Delivery and Packaging

Before final delivery, check:
- version number updated
- report marked draft/final clearly
- distribution list is correct
- encrypted at rest and in transit where possible
- secure delivery path chosen
- debrief / walkthrough plan prepared

## QA Gates

### Gate 1 — Technical Integrity
- every finding is validated and in scope
- false positives removed
- evidence supports the claim

### Gate 2 — Consistency
- all findings use the same schema
- severity labels are consistent with the defined model
- references, IDs, and formatting are coherent

### Gate 3 — Risk Logic
- technical severity and business risk are not conflated blindly
- vectors / rationale are present for every scored finding
- CVSS version choice is explicit when a finding is scored
- prioritization is explainable using severity plus context

### Gate 4 — Sensitive Data Handling
- redaction done
- minimal necessary evidence retained
- secure handling expectations met

### Gate 5 — Delivery Readiness
- cleanup/restoration section present
- remediation roadmap present
- retest guidance present
- publishing/delivery artifacts ready

## Report KPIs

Useful quality metrics:
- completeness score
- client-disputed / reversed findings rate
- time-to-remediation-ticket creation
- retest pass rate
- executive comprehension / decision latency
- trend delta across assessments

## Publishing Linkage

For real finalized engagements, the report handoff should include:
- local report path
- Google Doc link
- PDF link
- Slides link
- note whether branded production path or fallback was used

## Anti-Patterns

Avoid:
- raw tool dumps in the main body
- findings without remediation or retest guidance
- severity labels or CVSS scores without rationale
- treating CVSS as the final risk decision by itself
- omitting cleanup/restoration status
- shipping unredacted secrets in screenshots or appendices
- writing only for technical readers or only for executives

## Sub-Agent Guidance

When a pentest sub-agent uses this skill, it should:
- treat cleanup/restoration as a mandatory reporting field
- preserve evidence quality while minimizing sensitive exposure
- produce findings that engineers can reproduce and leaders can prioritize
- make residual risk and next steps explicit
- ensure the final package is delivery-ready, not just text-complete

## References

Load on demand:
- `references/examples.md` — trigger phrases and expected use
- `references/finding-template.md` — standardized finding block
- `references/report-qa-checklist.md` — final release gate checklist
- `references/cleanup-section.md` — required cleanup/restoration section template
