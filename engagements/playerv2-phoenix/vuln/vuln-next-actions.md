# PlayerV2 Phoenix — Vulnerability Next Actions

Date: 2026-04-29

## Immediate next actions

1. **Promote PHX-V01 to PHX-V03 into reporting-ready finding drafts**
   - preserve the current separated structure
   - carry over the CVSS v4 label, vector, score, rationale, and assumptions exactly unless later evidence changes them

2. **Decide whether PHX-V04 stays standalone or becomes supporting root-cause text under PHX-V01**
   - current recommendation: supporting/root-cause unless distinct attacker benefit is later demonstrated

3. **Validate PHX-V05 safely**
   - determine exact repair-source structure
   - determine whether signature/authenticity checks exist
   - avoid destructive restore actions during first validation pass

4. **Re-test PHX-V06 only if needed**
   - reproduce the pre-lock race with exact timing notes
   - document what actions are actually possible before lock takeover

5. **Triage PHX-V07 for business relevance**
   - decide whether it is a true report finding or just a hardening observation

## Reporting guidance

- The current best first-wave report set is **PHX-V01**, **PHX-V02**, and **PHX-V03**.
- Do not flatten PHX-V01 and PHX-V02 into one giant blended finding.
- Keep PHX-V03 framed as both:
  - confirmed sensitive artifact exposure
  - potentially reusable attacker knowledge/material

## Validation constraints to remember

- Physical access is in scope, so do not under-prioritize physical-path findings purely because Base CVSS is moderated.
- Avoid double-counting the same exploit path across PHX-V01 and PHX-V02.
- Do not overclaim PHX-V05 to PHX-V07 until each path is re-validated live.
