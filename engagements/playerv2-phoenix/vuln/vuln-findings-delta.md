# PlayerV2 Phoenix — Vulnerability Findings Delta

Date: 2026-04-29

## What changed in this pass

- Locked analyst decision to keep **PHX-V01** and **PHX-V02** as separate findings.
- Locked analyst decision to treat **PHX-V03** as still operationally useful in a real attack path if missed by defenders.
- Converted **PHX-V01**, **PHX-V02**, and **PHX-V03** into **score-ready CVSS v4.0 Base** entries.
- Converted **PHX-V04** through **PHX-V08** into structured candidate records with explicit provisional status instead of loose notes.
- Normalized Phoenix vuln handling around the report contract fields required by the local CVSS v4 finding schema.

## Finding-by-finding delta

### PHX-V01
- Status remains **Verified**
- Now explicitly score-ready with:
  - `cvss_label: CVSS-B`
  - populated vector
  - populated score
  - rationale and assumptions
- Final structure keeps this focused on the **authorization bypass condition itself**

### PHX-V02
- Status remains **Verified**
- Now explicitly score-ready with:
  - `cvss_label: CVSS-B`
  - populated vector
  - populated score
  - rationale and assumptions
- Final structure keeps this focused on the **fail-open consequence and preserved local access**

### PHX-V03
- Status remains **Verified**
- Analyst judgment updated from tentative historical exposure handling to **still operationally useful**
- Now explicitly score-ready with:
  - `cvss_label: CVSS-B`
  - populated vector
  - populated score
  - rationale and assumptions
- Current wording treats the passphrase/workflow exposure as meaningful chaining material

### PHX-V04
- Stayed **Supported**
- Converted into a structured provisional record
- Disposition tightened: best treated as **supporting/root-cause material** rather than a first-wave standalone scored finding
- Not numerically scored because distinct attacker leverage beyond PHX-V01 and PHX-V02 is not cleanly separated

### PHX-V05
- Stayed **Supported**
- Converted into a structured provisional record
- Kept unscored pending validation of authenticity/source-acceptance behavior

### PHX-V06
- Stayed **Supported / partially observed**
- Converted into a structured provisional record
- Kept unscored pending reproducibility and action-window validation

### PHX-V07
- Stayed **Supported**
- Converted into a structured provisional record
- Kept unscored pending stronger documentation of reliability and business impact framing

### PHX-V08
- Stayed **context only**
- Explicitly marked **Not Applicable** as a standalone scored finding for now

## Net reporting effect

If reporting started right now, the clean first-wave Phoenix findings set would be:
1. **PHX-V01**
2. **PHX-V02**
3. **PHX-V03**

Everything else remains available as:
- supporting architecture/root-cause material
- candidate findings awaiting validation
- environment context
