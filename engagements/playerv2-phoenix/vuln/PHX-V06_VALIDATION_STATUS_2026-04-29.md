# PHX-V06 — Validation Status and Disposition

Date: 2026-04-29
Target: playerv2-phoenix
Finding candidate: PHX-V06 — Pre-lock startup race exposing shell/GUI access

## Current decision

**Keep PHX-V06 as a supported, partially observed candidate. Do not promote to a scored first-wave finding yet.**

## Why it does not graduate yet

The current evidence suggests a real pre-lock exposure window may exist, but the present record is still too loose in two important ways:

1. **Reproducibility is not yet bounded tightly enough**
   - We have prior observations of transient `tty1` shell exposure and temporary GUI visibility before the lock workflow took over.
   - We do not yet have a repeated, well-timed replay set showing how often the race occurs, how long it lasts, and under what exact boot conditions it appears.

2. **Attacker-action depth inside the window is not yet documented precisely enough**
   - It is not yet cleanly demonstrated what a local attacker can consistently do before the lock reasserts.
   - Without that, the impact narrative risks collapsing into speculation or overlapping too much with PHX-V02.

## Relationship to PHX-V02

PHX-V06 must stay carefully separated from PHX-V02:
- **PHX-V02** is about a crash-driven fail-open state after hardware-check failure
- **PHX-V06** is about a possible timing/race exposure before the intended lock state takes control during startup

If PHX-V06 is later confirmed, it should be framed as an **early-boot transient exposure condition**, not the same thing as the fail-open crash condition.

## Current evidence summary

- prior operator observations indicated transient `tty1` shell visibility
- temporary GUI exposure was observed before takeover
- systemd ordering-cycle clues suggested startup-order fragility in Phoenix boot handling

## Current analyst judgment

### What is supported
- there is enough signal to keep PHX-V06 alive as a real candidate
- the issue is plausible and consistent with the broader Phoenix startup/control fragility theme
- the observed behavior is relevant to local physical attack paths

### What is missing
- repeated boot-cycle evidence with timestamps or precise sequence notes
- proof of what interaction is reliably possible inside the exposure window
- a clean basis for final CVSS vector choices without over-guessing

## Recommended report handling right now

Use PHX-V06 as:
- a **secondary validation item**
- a **candidate vulnerability**
- optional supporting discussion under local startup-sequence hardening if needed

Do not place it in the main scored finding set unless reproducibility and attacker-action depth are documented.

## Provisional structured record

- **finding_id:** PHX-V06
- **title:** Pre-lock startup race exposing shell/GUI access
- **severity:** Medium
- **validation_status:** Supported / partially observed
- **affected_asset:** playerv2-phoenix
- **cvss_version:** 4.0
- **cvss_label:** CVSS-B
- **cvss_score:** null
- **cvss_vector:** null
- **cvss_severity:** Medium
- **cvss_rationale:** Candidate only. A transient startup exposure may exist before the intended lock state fully asserts, but reproducibility and attacker-action depth are not yet documented tightly enough for final scoring.
- **cvss_assumptions:** Leave unscored until repeated boot-cycle validation shows the exposure window is real, measurable, and operationally exploitable in a consistent way.
- **cve_ids:** []
- **cwe_ids:** ["CWE-362", "CWE-367"]

## Next validation step

If this item is revisited later, collect:
- repeated boot-cycle observations
- exact timing notes
- exact visible text or shell state reached
- whether local input is accepted before lock takeover
- whether the condition exists in both normal boot and alternate media/boot-order conditions
