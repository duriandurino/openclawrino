# PHX-V04 — Disposition Decision

Date: 2026-04-29
Target: playerv2-phoenix
Finding candidate: PHX-V04 — Fragile vault authorization chain and dependency-only gating

## Decision

**Recommendation: keep PHX-V04 as supporting/root-cause material, not a primary standalone scored finding in the first-wave Phoenix report.**

## Why

PHX-V04 is meaningful, but the current evidence does not cleanly show a distinct attacker benefit that is separable from:
- **PHX-V01** — the storage-interface-dependent authorization failure
- **PHX-V02** — the fail-open local access after hardware-check crash

The current proof set shows that the vault-control chain:
- depends on `hardware-check.service`
- inherits the same fragile `mmcblk0`/CID assumption path
- can fail to unlock the vault when the dependency chain fails first

That is important architecture and explains why the broader trust design is brittle. But in its present state, the issue reads more like:
- root-cause amplification
- dependency-chain fragility
- security-boundary design weakness

rather than a separately bounded exploit effect with its own clean CVSS story.

## Evidence summary

- `vault-mount.service` required `hardware-check.service`
- in USB-presented mode, `hardware-check.service` failed before vault unlock proceeded
- `unlock_vault.py` repeated the same `/sys/block/mmcblk0/device/cid` assumption
- this means a critical security boundary inherited the same fragile identity-resolution design rather than independently validating or safely degrading

## Analyst judgment

### What PHX-V04 does add
- explains why the trust design is brittle in more than one place
- shows duplicated security assumptions across components
- supports the argument that the architecture lacks safe independent fallback around protected-content access
- strengthens remediation guidance for PHX-V01 and PHX-V02

### What PHX-V04 does not yet add cleanly enough
- a separate attacker-controlled action path with distinct reproducible impact
- a bounded exploit effect that is not already accounted for in PHX-V01 or PHX-V02
- a defensible final CVSS vector/score that would not mostly duplicate the same story

## Reporting recommendation

Use PHX-V04 in the report as:
- **supporting architecture / root-cause analysis**
- **design-fragility explanation**
- **remediation-shaping material**

Do **not** elevate it into the main scored finding list unless later testing demonstrates one of the following:
- the vault path independently exposes attacker leverage distinct from PHX-V01 and PHX-V02
- a semi-operational state around vault access creates a separate confidentiality/integrity issue
- a new bypass or recovery behavior tied specifically to vault gating is reproduced

## Suggested placement in final reporting

### Best fit
- beneath PHX-V01 and PHX-V02 as shared architectural root cause
- in technical narrative sections explaining duplicated trust assumptions
- in remediation sections discussing centralized identity resolution and fail-closed design

### Less ideal fit
- as a standalone scored finding in the same tier as PHX-V01 to PHX-V03

## Provisional structured record

- **finding_id:** PHX-V04
- **title:** Fragile vault authorization chain and dependency-only gating
- **severity:** Medium
- **validation_status:** Supported
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** null
- **cvss_vector:** null
- **cvss_severity:** Medium
- **cvss_rationale:** Supporting architectural weakness. The vault-control path duplicates the same fragile identity dependency and contributes to inconsistent security-state handling, but no distinct attacker benefit has yet been separated cleanly enough for final scoring.
- **cvss_assumptions:** Leave unscored unless later evidence shows a separate exploit path or impact that is not already captured by PHX-V01 and PHX-V02.
- **cve_ids:** []
- **cwe_ids:** ["CWE-693", "CWE-670"]

## Next step after this decision

Proceed to secondary validation items:
- PHX-V06
- PHX-V07

PHX-V05 should remain its own supported candidate because it still has a distinct potential integrity-impact story once live validation becomes possible.
